# Commands Configuration

The FabricStudio Controller uses a JSON configuration file to define the available commands in the dropdown menu. This makes it easy to add, remove, or modify commands without changing the application code.

## Configuration File

Commands are defined in `commands.json` in the root directory of the project.

## Adding a New Command

To add a new command, edit `commands.json` and add a new entry:

```json
{
  "Your Command Name": {
    "command": "your-command-here",
    "responses": {},
    "disconnect": false
  }
}
```

## Command Properties

Each command can have the following properties:

- **`command`** (required): The actual command to execute on the remote VM
- **`responses`** (optional): Dictionary of response patterns for interactive commands
- **`disconnect`** (optional): Set to `true` if the command will disconnect (like reboot)
- **`requires_extra_input`** (optional): Set to `true` if the command needs additional user input
- **`prompt`** (optional): The prompt text to show when `requires_extra_input` is true
- **`warning`** (optional): Set to `true` if the command should show "Are you sure?" confirmation

## Examples

### Simple Command
```json
"Restart Service": {
  "command": "systemctl restart myservice",
  "responses": {},
  "disconnect": false
}
```

### Command with Extra Input
```json
"Set Hostname": {
  "command": "hostnamectl set-hostname {extra_input}",
  "requires_extra_input": true,
  "prompt": "Enter new hostname:",
  "responses": {},
  "disconnect": false
}
```

### Command that Disconnects
```json
"Reboot System": {
  "command": "systemctl reboot",
  "responses": {},
  "disconnect": true
}
```

### Command with Warning
```json
"Delete All Data": {
  "command": "rm -rf /data/*",
  "responses": {},
  "warning": true
}
```

### Interactive Command with Responses
```json
"Install Package": {
  "command": "apt install {extra_input}",
  "requires_extra_input": true,
  "prompt": "Package name to install:",
  "responses": {
    "Do you want to continue?": "y"
  },
  "disconnect": false
}
```

## Special Variables

- **`{extra_input}`**: Replaced with the user's input when `requires_extra_input` is true

## After Making Changes

1. Save the `commands.json` file
2. Restart the application (or Docker container if using Docker)
3. The new commands will appear in the dropdown menu

## Validation

The application will validate the JSON file on startup. If there are any syntax errors, it will show an error message and fall back to default commands.
