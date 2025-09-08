# FabricStudio Controller

A modern web interface for managing FortiAnalyzer Fabric Studio VMs and executing SSH commands. Features a sleek dark theme with a two-column layout for efficient workflow.

## Features

- **VM Management**: View and manage Google Cloud VMs with real-time status updates
- **SSH Command Execution**: Execute FabricStudio commands across multiple VMs
- **Modern UI**: Dark theme with responsive two-column layout
- **Real-time Updates**: Automatic VM status polling and live feedback
- **Command Confirmation**: Safety prompts for critical operations

## Prerequisites

### 1. Python 3.8+
```bash
python --version
```

### 2. Google Cloud CLI
Install and configure the Google Cloud CLI:
```bash
# Install gcloud CLI (macOS)
brew install google-cloud-sdk

# Or download from: https://cloud.google.com/sdk/docs/install

# Authenticate
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
```

### 3. Google Cloud Service Account
1. Create a service account in Google Cloud Console
2. Download the credentials JSON file
3. Place it as `gcp-credentials.json` in the project root
4. Set the environment variable:
```bash
export GOOGLE_APPLICATION_CREDENTIALS="path/to/gcp-credentials.json"
```

## Installation

1. **Clone the repository**
```bash
git clone https://github.com/s-ruiter/FabricStudioController.git
cd FabricStudioController
```

2. **Install Python dependencies**
```bash
pip install -r requirements.txt
```

3. **Add your Google Cloud credentials**
```bash
# Place your service account JSON file in the project root
cp /path/to/your/credentials.json gcp-credentials.json
```

## Usage

1. **Start the application**
```bash
python app.py
```

2. **Open your browser**
Navigate to `http://localhost:5000`

3. **Use the interface**
   - **Left Column**: Execute FabricStudio commands
   - **Right Column**: Manage VMs (fetch status, start VMs)
   - **Bottom**: View command output

## Available Commands

- **Start FAZ workshop POC**: Install and power on FAZ-Workshop2025
- **Stop FAZ workshop POC**: Uninstall the workshop environment
- **Shutdown Fabric Studio and VM**: Shutdown the entire system
- **Fabric Studio Upgrade**: Upgrade Fabric Studio (requires confirmation)
- **Change guest user password**: Update guest user password

## Configuration

### VM Filter
The app filters VMs by name pattern: `sru-fstudio-faz*`

To modify the filter, edit `app.py`:
```python
'--filter=name~^sru-fstudio-faz',  # Change this pattern
```

### Commands
Add new commands in `app.py`:
```python
COMMAND_OPTIONS = {
    'Your New Command': {
        'command': 'your command here',
        'responses': {},
        'disconnect': False
    }
}
```

## Project Structure

```
FabricStudioController/
├── app.py                 # Flask application
├── requirements.txt       # Python dependencies
├── gcp-credentials.json   # Google Cloud credentials (not in repo)
├── static/
│   ├── style.css         # Modern dark theme
│   └── favicon.ico       # Application icon
└── templates/
    └── index.html        # Two-column web interface
```

## Security Notes

- **Credentials**: Never commit `gcp-credentials.json` to version control
- **Network**: The app runs on localhost by default
- **Permissions**: Ensure your service account has necessary VM management permissions

## Troubleshooting

### Common Issues

1. **"gcloud command not found"**
   - Install Google Cloud CLI
   - Add to PATH: `export PATH=$PATH:/path/to/google-cloud-sdk/bin`

2. **"Authentication failed"**
   - Run `gcloud auth login`
   - Set `GOOGLE_APPLICATION_CREDENTIALS` environment variable

3. **"No VMs found"**
   - Check your project ID: `gcloud config get-value project`
   - Verify VM names match the filter pattern
   - Ensure VMs exist in the specified region

4. **SSH connection fails**
   - Verify VM IP addresses are correct
   - Check username/password credentials
   - Ensure VMs are in RUNNING state

### Debug Mode
Run with debug logging:
```bash
FLASK_DEBUG=1 python app.py
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is for internal use. Please ensure compliance with your organization's policies.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review Google Cloud documentation
3. Create an issue in this repository
