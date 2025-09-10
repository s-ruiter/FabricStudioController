# FabricStudio Controller - Release Notes

## Version 1.3 (Latest)
*Released: January 2025*

### 🎯 **Enhanced User Experience**
- **Improved VM Success Message**: Updated success message to "All selected VMs are running and have an IP address. Please wait for the VM to become ready before sending commands." for clearer user guidance
- **Better Message Flow**: Restored VM count information in start messages while maintaining clear success guidance

### 🔧 **Filter Management Improvements**
- **Clickable Filter Buttons**: Replaced confusing dropdown boxes with intuitive clickable text fields for common filters
- **Quick Filter Selection**: One-click selection for "sru-fstudio-faz" and "sru-fpoc" filters
- **Visual Feedback**: Hover effects and selection highlighting for better user experience
- **Smart Filter Logic**: Select boxes clear each other, text input clears selections

### ⏱️ **VM Management Enhancements**
- **Extended Timeout**: Increased VM start timeout from 10 to 20 seconds for better reliability
- **Timeout Protection**: Prevents infinite page refreshing when VMs fail to start
- **Clear Error Messages**: Shows "Unable to start VM. Check on Google Cloud console" on timeout

---

## Version 1.2
*Released: January 2025*

### 🔗 **IP Address Management**
- **Clickable IP Addresses**: IP addresses in VM list are now clickable hyperlinks
- **HTTPS Links**: All IP links open with HTTPS protocol for security
- **New Tab Opening**: Links open in new browser tab with proper security attributes
- **Selective Hyperlinks**: IPs clickable in VM list, plain text in selected IPs display

### 🎨 **UI/UX Improvements**
- **Footer Cleanup**: Removed email address from footer for cleaner appearance
- **GitHub Integration**: Made "FabricStudio Controller" title clickable, linking to GitHub repository
- **Professional Styling**: Enhanced hover effects and visual feedback throughout the interface

---

## Version 1.1
*Released: January 2025*

### 🎨 **Visual Design Updates**
- **Button Sizing**: Reduced button sizes to fit "Select all VMs" and "Start Selected VMs" on single row
- **Background Image**: Updated background image with 100% width scaling
- **Modern UI**: Improved overall visual design and layout

### ⚙️ **Configuration Management**
- **Web-based Editor**: Added JSON editor page for in-browser command editing
- **Real-time Updates**: Command changes take effect immediately without restart
- **Configuration Cleanup**: Moved documentation from commands.json to editor help section
- **Filter Configuration**: Made default VM filter configurable through commands.json

### 🔧 **Technical Improvements**
- **State Management**: Fixed application state reloading for immediate command updates
- **Error Handling**: Improved error handling and user feedback
- **Code Organization**: Better separation of concerns and cleaner code structure

---

## Key Features Across All Versions

### 🖥️ **VM Management**
- Real-time VM status monitoring
- One-click VM starting with progress tracking
- Configurable VM filtering with common filter shortcuts
- IP address management with clickable links

### ⚡ **Command Execution**
- SSH command execution across multiple VMs
- Interactive command support with response patterns
- Command validation and error handling
- Real-time output display

### 🎨 **User Interface**
- Modern dark theme with professional styling
- Responsive design for different screen sizes
- Intuitive two-column layout
- Comprehensive help and documentation

### 🔧 **Configuration**
- Web-based JSON editor for command management
- Configurable VM filters and settings
- Real-time configuration updates
- Backup and restore functionality

---

## Installation & Usage

### Quick Start
```bash
# Clone the repository
git clone https://github.com/s-ruiter/FabricStudioController.git
cd FabricStudioController

# Deploy with Docker
./deploy.sh

# Access the application
open http://localhost:8000
```

### Requirements
- Docker or Python 3.7+
- Google Cloud CLI configured
- Appropriate GCP permissions for VM management

---

## Support & Documentation

- **GitHub Repository**: [https://github.com/s-ruiter/FabricStudioController](https://github.com/s-ruiter/FabricStudioController)
- **Developer**: Sander Ruiter
- **Documentation**: See README.md and COMMANDS.md for detailed usage instructions

---

*For issues and feature requests, please visit the GitHub repository.*
