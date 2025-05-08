# FieldCAD - Fusion 360 Add-in

A Fusion 360 add-in designed for modifying and customizing VEX Robotics Competition (V5RC) and VIQRC field CAD files. FieldCAD is a sister project to [PATH.JERRYIO](https://github.com/Jerrylum/path.jerryio).

## About

FieldCAD allows you to modify official VEX field CAD files by positioning game objects in custom layouts, applying different color schemes to field tiles, and setting standardized camera positions for consistent field visualization. The rendered fields can then be used as field images in PATH.JERRYIO, enabling precise path planning directly on accurate field representations.

By using both tools together, teams can:
- Design different game scenarios with precise object placement
- Create field backgrounds with various themes (light/dark mode)
- Plan and visualize autonomous routes with greater accuracy

## Features

- **Anchor Game Object**: Secure game objects in place
- **Place On Field**: Position game objects on the field using precise coordinates
- **Field Appearance**: Apply customizable checkerboard pattern appearances to field tiles
- **Inspect Game Object**: Examine game object properties
- **Set Camera**: Configure camera views for the field

## Installation

1. Download the latest release from the releases page
2. Extract the ZIP file
3. In Fusion 360, go to the Utilities tab
4. Select Add-Ins > Scripts and Add-Ins
5. In the Add-Ins tab, click the green + icon
6. Navigate to the extracted folder and select the folder
7. Click "Run" to start the add-in

## Usage

After installation, the FieldCAD toolbar will appear in the Fusion 360 interface with the following tools:

### Anchor Game Object

Secure game objects in place:
- Select a game object
- Choose between center or corner-based coordinates
- Enter X, Y, Z coordinates (supports unit conversion)
- Option to create a copy or move the original

### Place On Field

Position game objects on the field:
- Select a game object
- Choose between center or corner-based coordinates
- Enter X, Y, Z coordinates (supports unit conversion)
- Option to create a copy or move the original

### Field Appearance

Apply customizable appearances to field tiles:
- Set two different colors for a checkerboard pattern
- Colors are applied automatically to the field tiles in an alternating pattern

### Inspect Game Object

View detailed information about selected game objects:
- Display name, bounding box, and other properties
- Supports unit conversion for coordinates

### Set Camera

Set the camera to a standard top-down view with specified extents:
- Extents are automatically set to 192mm for VEX IQ fields
- Extents are automatically set to 369mm for VEX V5 fields

## Integration with PATH.JERRYIO

FieldCAD works seamlessly with [PATH.JERRYIO](https://github.com/Jerrylum/path.jerryio). You can then import the rendered output into PATH.JERRYIO as a background for precise path planning. See [PATH.JERRYIO - Field Images](https://docs.path.jerryio.com/docs/user-guides/user-interface#field-images) for more information.

## Requirements

- Autodesk Fusion 360
- Compatible with both Windows and macOS

## Development

### Project Structure

- `FieldCAD.py`: Main add-in entry point
- `commands/`: Contains all command implementations
  - `fieldAppearance/`: Field tile appearance customization
  - `placeOnField/`: Object positioning tools
  - `anchorGameObject/`: Object anchoring functionality
  - `inspectGameObject/`: Object inspection tools
  - `setCamera/`: Camera control utilities
- `lib/`: Utility functions and helper classes

### Building from Source

1. Clone the repository
2. Modify the configuration in `config.py` if needed
3. Test using Fusion 360's Script and Add-In development tools

## License

This project is licensed under the GNU General Public License v3.0. See the [LICENSE](LICENSE) file for details.
