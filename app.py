import io
import json
import subprocess
import logging
import os
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_from_directory
from fabric import Group
from invoke.watchers import Responder
from invoke.exceptions import CommandTimedOut
from logging.handlers import RotatingFileHandler
from functools import wraps

# --- Logging Setup ---
def setup_logging():
    """Configure logging for access and events."""
    # Create logs directory if it doesn't exist (race-condition safe for gunicorn workers)
    try:
        os.makedirs('logs', exist_ok=True)
    except OSError:
        pass  # Directory already exists or permission issue
    
    # Access log configuration
    access_logger = logging.getLogger('access')
    access_logger.setLevel(logging.INFO)
    access_handler = RotatingFileHandler(
        'logs/access.log',
        maxBytes=10*1024*1024,  # 10MB
        backupCount=10
    )
    access_formatter = logging.Formatter(
        '%(asctime)s | %(remote_addr)s | %(method)s | %(path)s | %(status)s | %(user_agent)s'
    )
    access_handler.setFormatter(access_formatter)
    access_logger.addHandler(access_handler)
    
    # Events log configuration (errors, important events)
    event_logger = logging.getLogger('events')
    event_logger.setLevel(logging.INFO)
    event_handler = RotatingFileHandler(
        'logs/events.log',
        maxBytes=10*1024*1024,  # 10MB
        backupCount=10
    )
    event_formatter = logging.Formatter(
        '%(asctime)s | %(levelname)s | %(message)s'
    )
    event_handler.setFormatter(event_formatter)
    event_logger.addHandler(event_handler)
    
    return access_logger, event_logger

access_log, event_log = setup_logging()

# --- Flask Application Setup ---
app = Flask(__name__)

# --- Logging Middleware ---
@app.before_request
def log_request():
    """Log all incoming requests."""
    request.start_time = datetime.now()

@app.after_request
def log_response(response):
    """Log all responses with timing information."""
    if request.endpoint != 'static' and request.endpoint != 'favicon':
        duration = datetime.now() - request.start_time
        access_log.info('', extra={
            'remote_addr': request.remote_addr,
            'method': request.method,
            'path': request.full_path if request.query_string else request.path,
            'status': response.status_code,
            'user_agent': request.headers.get('User-Agent', 'Unknown')[:200]
        })
        
        # Log slow requests as events
        if duration.total_seconds() > 2:
            event_log.warning(f"Slow request: {request.method} {request.path} took {duration.total_seconds():.2f}s from {request.remote_addr}")
    
    return response

def log_event(level, message, **kwargs):
    """Helper function to log events with additional context."""
    context = " | ".join([f"{k}={v}" for k, v in kwargs.items()])
    full_message = f"{message} | {context}" if context else message
    
    if level == 'info':
        event_log.info(full_message)
    elif level == 'warning':
        event_log.warning(full_message)
    elif level == 'error':
        event_log.error(full_message)
    elif level == 'critical':
        event_log.critical(full_message)

# --- Error Handlers ---
@app.errorhandler(404)
def not_found_error(error):
    log_event('warning', 'Page not found', 
              path=request.path, 
              remote_addr=request.remote_addr)
    return jsonify({'error': 'Page not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    log_event('error', 'Internal server error', 
              error=str(error), 
              path=request.path,
              remote_addr=request.remote_addr)
    return jsonify({'error': 'Internal server error'}), 500

@app.errorhandler(Exception)
def handle_exception(e):
    log_event('error', 'Unhandled exception',
              error=str(e),
              error_type=type(e).__name__,
              path=request.path,
              remote_addr=request.remote_addr)
    return jsonify({'error': 'An unexpected error occurred'}), 500

# --- Load commands from configuration file ---
def load_commands():
    """Load commands from commands.json file."""
    try:
        with open('commands.json', 'r') as f:
            commands = json.load(f)
            log_event('info', 'Commands loaded successfully', 
                     command_count=len(commands))
            return commands
    except FileNotFoundError:
        log_event('warning', 'commands.json not found, using default commands')
        print("⚠️  commands.json not found, using default commands")
        return {
            'Start FAZ workshop POC': {
                'command': 'runtime fabric install --power-on-vms FAZ-Workshop2025',
                'responses': {},
                'disconnect': False
            }
        }
    except json.JSONDecodeError as e:
        log_event('error', 'Error parsing commands.json', error=str(e))
        print(f"❌ Error parsing commands.json: {e}")
        return {}

COMMAND_OPTIONS = load_commands()

# Extract configuration from commands file
def get_config():
    """Extract configuration from commands.json file."""
    config = {
        'default_vm_filter': 'sru-fstudio-faz'
    }
    
    if '_config' in COMMAND_OPTIONS:
        config.update(COMMAND_OPTIONS['_config'])
    
    return config

CONFIG = get_config()

def reload_application_state():
    """Reload commands and configuration from files."""
    global COMMAND_OPTIONS, CONFIG
    COMMAND_OPTIONS = load_commands()
    CONFIG = get_config()
    log_event('info', 'Application state reloaded', 
             command_count=len(COMMAND_OPTIONS),
             config=str(CONFIG))
    print(f"🔄 Application state reloaded: {len(COMMAND_OPTIONS)} commands, config: {CONFIG}")

# --- API Endpoints for Google Cloud ---

@app.route('/get-vms')
def get_gcp_vms():
    """Fetch a detailed list of VMs including name, zone, status and IP."""
    try:
        # Get filter from query parameter, default to configured filter
        default_filter = f"name~^{CONFIG['default_vm_filter']}"
        filter_value = request.args.get('filter', default_filter)
        
        # Ensure filter always contains "sru" - if user provides custom filter, combine with sru
        if filter_value != default_filter and 'sru' not in filter_value.lower():
            # If custom filter doesn't contain sru, combine it with sru filter
            if filter_value.startswith('name~'):
                # Extract the pattern after name~
                pattern = filter_value[5:]
                filter_value = f"name~sru AND name~{pattern}"
            else:
                # Simple text search, combine with sru
                filter_value = f"name~sru AND name~{filter_value}"
        
        gcloud_command = [
            'gcloud', 'compute', 'instances', 'list',
            f'--filter={filter_value}',
            '--format=json(name,zone,status,networkInterfaces[0].accessConfigs[0].natIP)'
        ]
        result = subprocess.run(gcloud_command, capture_output=True, text=True, check=True, timeout=30)
        vms = json.loads(result.stdout)
        
        log_event('info', 'VMs fetched successfully',
                 vm_count=len(vms),
                 filter=filter_value,
                 remote_addr=request.remote_addr)
        
        return jsonify(vms)
    except FileNotFoundError:
        log_event('error', 'gcloud command not found', remote_addr=request.remote_addr)
        return jsonify({'error': 'The "gcloud" command was not found. Is the Google Cloud CLI installed?'}), 500
    except subprocess.CalledProcessError as e:
        log_event('error', 'gcloud command failed',
                 error=e.stderr,
                 remote_addr=request.remote_addr)
        return jsonify({'error': f"Error executing gcloud (check login/project): {e.stderr}"}), 500
    except Exception as e:
        log_event('error', 'Unexpected error fetching VMs',
                 error=str(e),
                 error_type=type(e).__name__,
                 remote_addr=request.remote_addr)
        return jsonify({'error': f'An unexpected error occurred: {str(e)}'}), 500

@app.route('/start-vms', methods=['POST'])
def start_gcp_vms():
    """Start a list of specific VMs by name and zone."""
    data = request.json
    vms_to_start = data.get('vms')
    if not vms_to_start:
        log_event('warning', 'Start VMs called with no VMs', remote_addr=request.remote_addr)
        return jsonify({'error': 'No VMs provided to start.'}), 400
    
    log_event('info', 'Starting VMs',
             vm_count=len(vms_to_start),
             vm_names=[vm['name'] for vm in vms_to_start],
             remote_addr=request.remote_addr)
    
    errors = []
    for vm in vms_to_start:
        try:
            # Use --async to send commands quickly one after another
            gcloud_command = ['gcloud', 'compute', 'instances', 'start', vm['name'], f'--zone={vm["zone"]}', '--async']
            subprocess.run(gcloud_command, capture_output=True, text=True, check=True, timeout=60)
        except Exception as e:
            error_msg = f"Could not start VM {vm['name']}: {str(e)}"
            errors.append(error_msg)
            log_event('error', 'Failed to start VM',
                     vm_name=vm['name'],
                     zone=vm['zone'],
                     error=str(e),
                     remote_addr=request.remote_addr)

    if errors:
        return jsonify({'error': '. '.join(errors)}), 500

    log_event('info', 'VMs start commands sent successfully',
             vm_count=len(vms_to_start),
             remote_addr=request.remote_addr)
    
    return jsonify({'success': f'Start command for {len(vms_to_start)} VM(s) sent.'})


# --- Core function for SSH commands ---
def execute_remote_command(hosts, username, password, command_string):
    output_buffer = io.StringIO()
    selected_command_info = None
    for key, info in COMMAND_OPTIONS.items():
        if not key.startswith('_') and isinstance(info, dict) and 'command' in info:
            if command_string.startswith(info['command'].split('{')[0]):
                selected_command_info = info
                break
    if not selected_command_info:
        error_msg = f"❌ Error: The selected command '{command_string}' could not be found."
        output_buffer.write(error_msg)
        log_event('error', 'Command not found',
                 command=command_string,
                 remote_addr=request.remote_addr)
        return output_buffer.getvalue()
    
    log_event('info', 'Executing SSH command',
             command=command_string,
             host_count=len(hosts),
             username=username,
             remote_addr=request.remote_addr)
    
    watchers = []
    if selected_command_info.get('responses'):
        for pattern, response in selected_command_info['responses'].items():
            watchers.append(Responder(pattern=pattern, response=response))
    try:
        group = Group(*hosts, user=username, connect_kwargs={"password": password, "look_for_keys": False, "allow_agent": False})
        output_buffer.write(f"▶️ Executing command: '{command_string}'\n\n--- RESULTS ---\n")
        for conn in group:
            output_buffer.write("="*20 + f"\nHost: {conn.host}\n" + "="*20 + "\n")
            try:
                if selected_command_info.get('disconnect'):
                    try:
                        conn.run(command_string, hide=True, warn=True, pty=True, watchers=watchers, timeout=10)
                    except CommandTimedOut:
                        output_buffer.write("✅ Command successfully started. Server rebooted, connection dropped as expected.\n\n")
                        log_event('info', 'Command completed with disconnect',
                                 host=conn.host,
                                 command=command_string)
                        continue
                else:
                    result = conn.run(command_string, hide=True, warn=True, pty=True, watchers=watchers)
                    stdout, stderr = result.stdout.strip(), result.stderr.strip()
                    if stdout: output_buffer.write(f"Output:\n{stdout}\n\n")
                    if stderr: output_buffer.write(f"Errors:\n{stderr}\n\n")
                    if not stdout and not stderr: output_buffer.write("No output received.\n\n")
                    
                    log_event('info', 'Command executed successfully',
                             host=conn.host,
                             command=command_string,
                             has_stdout=bool(stdout),
                             has_stderr=bool(stderr))
            except Exception as e:
                error_msg = f"❌ Error on {conn.host}: {e}\n\n"
                output_buffer.write(error_msg)
                log_event('error', 'SSH command failed',
                         host=conn.host,
                         command=command_string,
                         error=str(e),
                         error_type=type(e).__name__)
    except Exception as e:
        error_msg = f"\n❌ General error:\nType: {type(e).__name__}\nDetails: {e}\n"
        output_buffer.write(error_msg)
        log_event('error', 'SSH execution failed',
                 command=command_string,
                 error=str(e),
                 error_type=type(e).__name__,
                 remote_addr=request.remote_addr)
    
    return output_buffer.getvalue()

# --- Web Interface (Routes) ---
@app.route('/', methods=['GET', 'POST'])
def index():
    output = ""
    gcloud_status = check_gcloud_cli()
    
    if request.method == 'POST':
        ips_string = request.form.get('ips')
        username = request.form.get('username')
        password = request.form.get('password')
        command_template = request.form.get('command')
        hosts = [ip.strip() for ip in ips_string.splitlines() if ip.strip()]
        final_command = command_template
        selected_command_info = next((info for key, info in COMMAND_OPTIONS.items() if not key.startswith('_') and isinstance(info, dict) and info.get('command') == command_template), None)
        if selected_command_info and selected_command_info.get('requires_extra_input'):
            extra_input = request.form.get('extra_input')
            if not extra_input:
                output = "Error: This command requires additional input."
                log_event('warning', 'Command requires additional input',
                         command=command_template,
                         remote_addr=request.remote_addr)
                return render_template('index.html', output=output, commands=COMMAND_OPTIONS, gcloud_status=gcloud_status, config=CONFIG)
            final_command = command_template.format(extra_input=extra_input)
        if not all([hosts, username, password, command_template]):
            output = "Error: Please fill in all fields."
            log_event('warning', 'Form submitted with missing fields',
                     remote_addr=request.remote_addr)
        else:
            output = execute_remote_command(hosts, username, password, final_command)
    return render_template('index.html', output=output, commands=COMMAND_OPTIONS, gcloud_status=gcloud_status, config=CONFIG)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(app.static_folder, 'favicon.ico')

@app.route('/editor')
def editor():
    """JSON editor page for managing commands.json"""
    log_event('info', 'Editor page accessed', remote_addr=request.remote_addr)
    return render_template('editor.html', commands=COMMAND_OPTIONS, config=CONFIG)

@app.route('/planning')
def planning():
    """VM planning page for scheduling VM usage"""
    log_event('info', 'Planning page accessed', remote_addr=request.remote_addr)
    return render_template('planning.html')

@app.route('/api/workshops', methods=['GET'])
def get_workshops():
    """API endpoint to get current workshop schedule"""
    try:
        with open('workshop_schedule.json', 'r') as f:
            content = f.read()
        log_event('info', 'Workshop schedule retrieved', remote_addr=request.remote_addr)
        return jsonify({'success': True, 'content': content})
    except FileNotFoundError:
        log_event('info', 'Workshop schedule file not found, returning empty', 
                 remote_addr=request.remote_addr)
        return jsonify({'success': True, 'content': '[]'})
    except Exception as e:
        log_event('error', 'Failed to retrieve workshop schedule',
                 error=str(e),
                 remote_addr=request.remote_addr)
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/workshops', methods=['POST'])
def save_workshops():
    """API endpoint to save workshop schedule"""
    try:
        data = request.json
        content = data.get('content', '')
        
        # Validate JSON before saving
        try:
            parsed = json.loads(content)
            entry_count = len(parsed) if isinstance(parsed, list) else 0
        except json.JSONDecodeError as e:
            log_event('error', 'Invalid JSON in workshop schedule',
                     error=str(e),
                     remote_addr=request.remote_addr)
            return jsonify({'success': False, 'error': f'Invalid JSON: {str(e)}'}), 400
        
        # Save new content with proper formatting
        with open('workshop_schedule.json', 'w') as f:
            json.dump(parsed, f, indent=4)
        
        log_event('info', 'Workshop schedule saved',
                 entry_count=entry_count,
                 remote_addr=request.remote_addr)
        
        return jsonify({
            'success': True, 
            'message': 'Workshop schedule saved successfully'
        })
    except Exception as e:
        log_event('error', 'Failed to save workshop schedule',
                 error=str(e),
                 remote_addr=request.remote_addr)
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/commands', methods=['GET'])
def get_commands():
    """API endpoint to get current commands.json content"""
    try:
        with open('commands.json', 'r') as f:
            content = f.read()
        log_event('info', 'Commands retrieved', remote_addr=request.remote_addr)
        return jsonify({'success': True, 'content': content})
    except Exception as e:
        log_event('error', 'Failed to retrieve commands',
                 error=str(e),
                 remote_addr=request.remote_addr)
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/commands', methods=['POST'])
def save_commands():
    """API endpoint to save commands.json content"""
    try:
        data = request.json
        content = data.get('content', '')
        
        # Validate JSON before saving
        try:
            parsed = json.loads(content)
        except json.JSONDecodeError as e:
            log_event('error', 'Invalid JSON in commands',
                     error=str(e),
                     remote_addr=request.remote_addr)
            return jsonify({'success': False, 'error': f'Invalid JSON: {str(e)}'}), 400
        
        # Backup current file
        import shutil
        shutil.copy('commands.json', 'commands.json.backup')
        
        # Save new content
        with open('commands.json', 'w') as f:
            f.write(content)
        
        # Reload application state
        reload_application_state()
        
        log_event('info', 'Commands saved and reloaded',
                 command_count=len(COMMAND_OPTIONS),
                 remote_addr=request.remote_addr)
        
        return jsonify({
            'success': True, 
            'message': 'Commands saved successfully',
            'reloaded_commands': len(COMMAND_OPTIONS),
            'current_config': CONFIG
        })
    except Exception as e:
        log_event('error', 'Failed to save commands',
                 error=str(e),
                 remote_addr=request.remote_addr)
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/status')
def get_status():
    """API endpoint to check current application state."""
    log_event('info', 'Status check requested', remote_addr=request.remote_addr)
    return jsonify({
        'commands_count': len(COMMAND_OPTIONS),
        'config': CONFIG,
        'available_commands': [name for name, info in COMMAND_OPTIONS.items() if not name.startswith('_') and isinstance(info, dict)]
    })

# --- GCloud CLI Check ---
def check_gcloud_cli():
    """Check if gcloud CLI is installed and working."""
    status = {
        'installed': False,
        'authenticated': False,
        'project_set': False,
        'account': '',
        'project': '',
        'errors': [],
        'warnings': []
    }
    
    try:
        result = subprocess.run(['gcloud', '--version'], capture_output=True, text=True, timeout=10)
        if result.returncode != 0:
            status['errors'].append(f"gcloud CLI is not working properly: {result.stderr}")
            return status
        
        status['installed'] = True
        
        # Check if user is authenticated
        auth_result = subprocess.run(['gcloud', 'auth', 'list', '--filter=status:ACTIVE', '--format=value(account)'], 
                                   capture_output=True, text=True, timeout=10)
        if not auth_result.stdout.strip():
            status['warnings'].append("No active gcloud authentication found. Please run: gcloud auth login")
        else:
            status['authenticated'] = True
            status['account'] = auth_result.stdout.strip()
            
        # Check if project is set
        project_result = subprocess.run(['gcloud', 'config', 'get-value', 'project'], 
                                      capture_output=True, text=True, timeout=10)
        if not project_result.stdout.strip():
            status['warnings'].append("No gcloud project configured. Please run: gcloud config set project YOUR_PROJECT_ID")
        else:
            status['project_set'] = True
            status['project'] = project_result.stdout.strip()
            
        return status
        
    except FileNotFoundError:
        status['errors'].append("gcloud CLI is not installed. Please install Google Cloud CLI: https://cloud.google.com/sdk/docs/install")
        return status
    except subprocess.TimeoutExpired:
        status['errors'].append("gcloud CLI check timed out")
        return status
    except Exception as e:
        status['errors'].append(f"Error checking gcloud CLI: {e}")
        return status

# --- Applicatie Startpunt ---
if __name__ == '__main__':
    print("🔍 Checking gcloud CLI...")
    gcloud_status = check_gcloud_cli()
    
    if gcloud_status['errors']:
        print("❌ gcloud CLI issues found:")
        for error in gcloud_status['errors']:
            print(f"   {error}")
        print("\n⚠️  The application will start but VM management features may not work.")
        print("   Please fix the gcloud CLI issues above before using VM features.\n")
        log_event('warning', 'Application started with gcloud CLI errors',
                 errors=gcloud_status['errors'])
    elif gcloud_status['warnings']:
        print("⚠️  gcloud CLI warnings:")
        for warning in gcloud_status['warnings']:
            print(f"   {warning}")
        print("\n⚠️  VM management features may not work properly.\n")
        log_event('warning', 'Application started with gcloud CLI warnings',
                 warnings=gcloud_status['warnings'])
    else:
        print("✅ gcloud CLI is installed and configured")
        print(f"   Active account: {gcloud_status['account']}")
        print(f"   Project: {gcloud_status['project']}\n")
        log_event('info', 'Application started successfully',
                 account=gcloud_status['account'],
                 project=gcloud_status['project'])
    
    print("📝 Logging enabled:")
    print("   Access log: logs/access.log")
    print("   Events log: logs/events.log\n")
    
    port = int(os.environ.get("FLASK_RUN_PORT", 5000))
    app.run(debug=True, port=port, host="0.0.0.0")
