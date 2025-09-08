import io
import json
import subprocess
from flask import Flask, render_template, request, jsonify, send_from_directory
from fabric import Group
from invoke.watchers import Responder
from invoke.exceptions import CommandTimedOut

# --- Flask Application Setup ---
app = Flask(__name__)

# --- Define your commands here ---
COMMAND_OPTIONS = {
    'Start FAZ workshop POC': {
        'command': 'runtime fabric install --power-on-vms FAZ-Workshop2025',
        'responses': {},
        'disconnect': False
    },
    'Stop FAZ workshop POC': {
        'command': 'runtime fabric uninstall',
        'responses': {}
    },
    'Shutdown Fabric Studio and VM': {
        'command': 'system execute shutdown --no-interactive',
        'responses': {}
    },
    'Fabric Studio Upgrade': {
        'command': 'system execute upgrade --no-interactive',
        'responses': {},
        'disconnect': True
    },
    'Change guest user password': {
        'command': 'execute password guest {extra_input}',
        'requires_extra_input': True,
        'prompt': 'New password for guest user:',
        'responses': {},
        'disconnect': False
    }
}

# --- API Endpoints for Google Cloud ---

@app.route('/get-vms')
def get_gcp_vms():
    """Fetch a detailed list of VMs including name, zone, status and IP."""
    try:
        gcloud_command = [
            'gcloud', 'compute', 'instances', 'list',
            '--filter=name~^sru-fstudio-faz',
            '--format=json(name,zone,status,networkInterfaces[0].accessConfigs[0].natIP)'
        ]
        result = subprocess.run(gcloud_command, capture_output=True, text=True, check=True, timeout=30)
        vms = json.loads(result.stdout)
        return jsonify(vms)
    except FileNotFoundError:
        return jsonify({'error': 'The "gcloud" command was not found. Is the Google Cloud CLI installed?'}), 500
    except subprocess.CalledProcessError as e:
        return jsonify({'error': f"Error executing gcloud (check login/project): {e.stderr}"}), 500
    except Exception as e:
        return jsonify({'error': f'An unexpected error occurred: {str(e)}'}), 500

@app.route('/start-vms', methods=['POST'])
def start_gcp_vms():
    """Start a list of specific VMs by name and zone."""
    data = request.json
    vms_to_start = data.get('vms')
    if not vms_to_start:
        return jsonify({'error': 'No VMs provided to start.'}), 400
    
    errors = []
    for vm in vms_to_start:
        try:
            # Use --async to send commands quickly one after another
            gcloud_command = ['gcloud', 'compute', 'instances', 'start', vm['name'], f'--zone={vm["zone"]}', '--async']
            subprocess.run(gcloud_command, capture_output=True, text=True, check=True, timeout=60)
        except Exception as e:
            errors.append(f"Could not start VM {vm['name']}: {str(e)}")

    if errors:
        return jsonify({'error': '. '.join(errors)}), 500

    return jsonify({'success': f'Start command for {len(vms_to_start)} VM(s) sent.'})


# --- Core function for SSH commands ---
def execute_remote_command(hosts, username, password, command_string):
    output_buffer = io.StringIO()
    selected_command_info = None
    for info in COMMAND_OPTIONS.values():
        if command_string.startswith(info['command'].split('{')[0]):
            selected_command_info = info
            break
    if not selected_command_info:
        output_buffer.write(f"❌ Error: The selected command '{command_string}' could not be found.")
        return output_buffer.getvalue()
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
                        continue
                else:
                    result = conn.run(command_string, hide=True, warn=True, pty=True, watchers=watchers)
                    stdout, stderr = result.stdout.strip(), result.stderr.strip()
                    if stdout: output_buffer.write(f"Output:\n{stdout}\n\n")
                    if stderr: output_buffer.write(f"Errors:\n{stderr}\n\n")
                    if not stdout and not stderr: output_buffer.write("No output received.\n\n")
            except Exception as e:
                output_buffer.write(f"❌ Error on {conn.host}: {e}\n\n")
    except Exception as e:
        output_buffer.write(f"\n❌ General error:\nType: {type(e).__name__}\nDetails: {e}\n")
    return output_buffer.getvalue()

# --- Web Interface (Routes) ---
@app.route('/', methods=['GET', 'POST'])
def index():
    output = ""
    if request.method == 'POST':
        ips_string = request.form.get('ips')
        username = request.form.get('username')
        password = request.form.get('password')
        command_template = request.form.get('command')
        hosts = [ip.strip() for ip in ips_string.splitlines() if ip.strip()]
        final_command = command_template
        selected_command_info = next((info for info in COMMAND_OPTIONS.values() if info['command'] == command_template), None)
        if selected_command_info and selected_command_info.get('requires_extra_input'):
            extra_input = request.form.get('extra_input')
            if not extra_input:
                output = "Error: This command requires additional input."
                return render_template('index.html', output=output, commands=COMMAND_OPTIONS)
            final_command = command_template.format(extra_input=extra_input)
        if not all([hosts, username, password, command_template]):
            output = "Error: Please fill in all fields."
        else:
            output = execute_remote_command(hosts, username, password, final_command)
    return render_template('index.html', output=output, commands=COMMAND_OPTIONS)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(app.static_folder, 'favicon.ico')

# --- Applicatie Startpunt ---
if __name__ == '__main__':
    app.run(debug=True)

