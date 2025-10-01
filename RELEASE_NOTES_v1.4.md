# FabricStudio Controller - Release Notes v1.4

## 🎉 New Features

### 📥 CSV Export Functionality
- **Export Button**: Added "Export IPs to CSV" button in VM Management header
- **Smart Selection**: Only exports IP addresses from selected RUNNING VMs
- **Automatic Download**: Generates CSV file with date in filename (vm-ips-YYYY-MM-DD.csv)
- **User Feedback**: Shows success message with count of exported IPs
- **Button State**: Disabled when no VMs with IP addresses are selected

### 🎛️ Enhanced VM Selection Controls
- **Select Started Button**: New button to select only RUNNING VMs
- **Improved Select All**: Renamed from "Select All VMs" to "Select All" for brevity
- **Smart Button Logic**: Start button only enables when selected VMs are TERMINATED and no RUNNING VMs are selected
- **Predictable Behavior**: Select Started always selects only started VMs, regardless of previous state

### 🚫 Command Hiding Feature
- **Disabled Property**: Commands can now be hidden from dropdown menu using `"disabled": true`
- **Template Filtering**: Dropdown automatically filters out disabled commands
- **Documentation**: Updated editor help with disabled property usage and examples

## 🔧 UI/UX Improvements

### Button Layout & Positioning
- **Export Button**: Moved to VM Management header for better visibility
- **Button Renaming**: "Fetch VM Status" → "Fetch Status" for cleaner interface
- **Consistent Styling**: All new buttons follow existing design patterns

### Smart State Management
- **Export Button**: Only enabled when VMs with IP addresses are selected
- **Start Button**: Prevents accidental starting of already running VMs
- **Select Started**: Always results in only started VMs being selected

## 🐛 Bug Fixes

### Selection Logic Fixes
- **Fixed**: Start button incorrectly enabled when selecting all VMs (including running ones)
- **Fixed**: Select Started button toggle behavior causing unexpected deselection
- **Fixed**: Select Started now properly deselects terminated VMs when selecting only started ones

### Button State Management
- **Improved**: Button states now update correctly based on VM status
- **Enhanced**: Clear visual feedback for all button states
- **Fixed**: Prevented conflicting button states that could confuse users

## 📚 Documentation Updates

### Editor Help Section
- **Added**: Documentation for `disabled` property in commands.json
- **Added**: Example showing how to use disabled commands
- **Updated**: Command properties list with new disabled option

## 🔄 Technical Improvements

### JavaScript Enhancements
- **New Functions**: `exportIpsToCsv()`, `selectStartedVms()`
- **Improved Logic**: Better state management in `updateUiState()`
- **Enhanced UX**: Clear success/error messaging for all actions

### Code Organization
- **Cleaner Structure**: Better separation of concerns in button handlers
- **Consistent Patterns**: All new features follow existing code patterns
- **Maintainable**: Clear, readable code with proper comments

## 🎯 User Experience

### Workflow Improvements
- **Faster VM Management**: Quick selection of only started VMs
- **Easy IP Export**: One-click export of selected VM IPs to CSV
- **Safer Operations**: Prevented accidental operations on wrong VM states
- **Clear Feedback**: Users always know what each button will do

### Interface Polish
- **Consistent Naming**: Shorter, clearer button labels
- **Logical Grouping**: Related buttons grouped together
- **Visual Hierarchy**: Important actions prominently displayed

---

## 🚀 Migration Notes

### For Existing Users
- **No Breaking Changes**: All existing functionality preserved
- **New Features**: Optional - can be used as needed
- **Commands**: Existing commands.json files work without changes
- **UI**: Interface remains familiar with new enhancements

### New Configuration Options
- **Disabled Commands**: Add `"disabled": true` to any command to hide it from dropdown
- **Export Feature**: No configuration needed - works automatically

---

**Version**: 1.4  
**Release Date**: September 2025  
**Compatibility**: Backward compatible with v1.3  
**Developer**: Sander Ruiter
