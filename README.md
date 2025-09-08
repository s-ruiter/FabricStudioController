# FabricStudio Controller

A modern web interface for managing Fabric Studio VMs and executing SSH commands. Features a sleek dark theme with a two-column layout for efficient workflow.

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


## Installation

### **Option 1: Docker (Recommended)**

1. **Clone the repository**
```bash
git clone https://github.com/s-ruiter/FabricStudioController.git
cd FabricStudioController
```

2. **Set up Google Cloud authentication**
```bash
# Install gcloud CLI if not already installed
# macOS: brew install google-cloud-sdk
# Or download from: https://cloud.google.com/sdk/docs/install

# Authenticate with Google Cloud
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
```

3. **Run with Docker**
```bash
# Use the automated deployment script
./deploy.sh

# Or run manually
docker build -t fabricstudio-controller .
docker run -d -p 8000:8000 --name fabricstudio \
  -v ~/.config/gcloud:/root/.config/gcloud \
  fabricstudio-controller
```

4. **Access the application**
Open your browser to: http://localhost:8000

### **Option 2: Local Python Installation**

1. **Clone the repository**
```bash
git clone https://github.com/s-ruiter/FabricStudioController.git
cd FabricStudioController
```

2. **Install Python dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up Google Cloud authentication**
```bash
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
```

4. **Run the application**
```bash
python app.py
```

## Usage

1. **Start the application** (see Installation section above)

2. **Open your browser**
   - Docker: Navigate to `http://localhost:8000`
   - Local Python: Navigate to `http://localhost:5000`

3. **Use the interface**
   - **Left Column**: Execute FabricStudio commands
   - **Right Column**: Manage VMs (fetch status, start VMs)
   - **Bottom**: View command output

## Available Commands

Commands are defined in `commands.json` and can be easily customized:

- **Start FAZ workshop POC**: Install and power on FAZ-Workshop2025
- **Stop FAZ workshop POC**: Uninstall the workshop environment
- **Shutdown Fabric Studio and VM**: Shutdown the entire system (requires confirmation)
- **Fabric Studio Upgrade**: Upgrade Fabric Studio (requires confirmation)
- **Change guest user password**: Update guest user password

### Adding New Commands

To add or modify commands, edit `commands.json`:

```json
{
  "Your New Command": {
    "command": "your command here",
    "responses": {},
    "disconnect": false,
    "warning": false
  }
}
```

See [COMMANDS.md](COMMANDS.md) for detailed documentation on command configuration.

## Configuration

### VM Filter
The app includes a user-configurable VM filter in the web interface:

- **Default Filter**: `sru-fstudio-faz` (searches for VMs containing this text)
- **User-Friendly**: Simply type text to search in VM names
- **Advanced Support**: Supports full gcloud filter syntax for power users
- **Real-time**: Filter is applied when clicking "Fetch VM Status"

#### Filter Usage:
- **Simple Text**: Type `workshop` to find VMs containing "workshop"
- **Advanced Syntax**: Use `status=RUNNING` to show only running VMs
- **Pattern Matching**: Use `name~^prod` to find VMs starting with "prod"

The filter input field is located in the VM Management section on the right side of the interface.

### Commands
Commands are now managed through `commands.json` - see the [Available Commands](#available-commands) section above for details.

## Deployment to Another Machine

### **Quick Setup (Recommended)**

1. **On the new machine, install prerequisites:**
```bash
# Install Docker
# macOS: brew install --cask docker
# Or download from: https://docs.docker.com/get-docker/

# Install Google Cloud CLI
# macOS: brew install google-cloud-sdk
# Or download from: https://cloud.google.com/sdk/docs/install
```

2. **Clone and deploy:**
```bash
git clone https://github.com/s-ruiter/FabricStudioController.git
cd FabricStudioController

# Set up Google Cloud authentication
gcloud auth login
gcloud config set project YOUR_PROJECT_ID

# Deploy automatically
./deploy.sh
```

3. **Access the application:**
Open your browser to: http://localhost:8000

### **Alternative: Docker Compose**

```bash
# Clone the repository
git clone https://github.com/s-ruiter/FabricStudioController.git
cd FabricStudioController

# Set up authentication
gcloud auth login
gcloud config set project YOUR_PROJECT_ID

# Run with Docker Compose
docker-compose up -d
```

### **Container Management**

```bash
# View logs
docker logs fabricstudio

# Stop the application
docker stop fabricstudio

# Start the application
docker start fabricstudio

# Remove the container
docker stop fabricstudio && docker rm fabricstudio

# Rebuild and restart
docker stop fabricstudio && docker rm fabricstudio
docker build -t fabricstudio-controller .
docker run -d -p 8000:8000 --name fabricstudio \
  -v ~/.config/gcloud:/root/.config/gcloud \
  fabricstudio-controller
```

## Project Structure

```
FabricStudioController/
├── app.py                 # Flask application
├── requirements.txt       # Python dependencies
├── Dockerfile            # Docker container definition
├── docker-compose.yml    # Docker Compose configuration
├── deploy.sh             # Automated deployment script
├── run-docker.sh         # Docker run script
├── setup-auth.sh         # Authentication setup script
├── static/
│   ├── style.css         # Modern dark theme
│   └── favicon.ico       # Application icon
└── templates/
    └── index.html        # Two-column web interface
```

## Security Notes

- **Network**: The app runs on localhost by default
- **Permissions**: Ensure your gcloud CLI has necessary VM management permissions

## Troubleshooting

### Common Issues

1. **"gcloud command not found"**
   - Install Google Cloud CLI
   - Add to PATH: `export PATH=$PATH:/path/to/google-cloud-sdk/bin`

2. **"Authentication failed"**
   - Run `gcloud auth login`
   - Verify your project is set: `gcloud config get-value project`

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
