import os
import adsk.core
import adsk.fusion
from ...commands.panel import get_panel_in_render_workspace
from ...lib import fusionAddInUtils as futil
from ... import config

app = adsk.core.Application.get()
ui = app.userInterface

CMD_ID = f"{config.COMPANY_NAME}_{config.ADDIN_NAME}_setCamera"
CMD_NAME = "Set Camera"
CMD_Description = "Set the camera to a standard top-down view with specified extents"
IS_PROMOTED = True

ICON_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resources", "")

# Field tile prefix for checking v5 field
FIELD_TILE_PREFIX = "276-6904-001"

local_handlers = []


def start():
    cmd_def = ui.commandDefinitions.addButtonDefinition(CMD_ID, CMD_NAME, CMD_Description, ICON_FOLDER)
    futil.add_handler(cmd_def.commandCreated, command_created)

    panel = get_panel_in_render_workspace()

    # Add command to panel
    control = panel.controls.addCommand(cmd_def)
    control.isPromoted = IS_PROMOTED


def stop():
    command_definition = ui.commandDefinitions.itemById(CMD_ID)
    if command_definition:
        command_definition.deleteMe()


def command_created(args: adsk.core.CommandCreatedEventArgs):
    futil.log(f"{CMD_NAME} Command Created Event")

    # Get the command inputs
    cmd = args.command
    inputs = cmd.commandInputs

    # Check if field tiles are found to determine default value
    default_extent = 192  # VEX IQ field

    # Get the active design
    product = app.activeProduct
    design = adsk.fusion.Design.cast(product)
    if design:
        #  check if design.rootComponent.boundingBox with > 3000mm in any direction
        bounding_box = design.rootComponent.boundingBox
        if bounding_box.maxPoint.x - bounding_box.minPoint.x > 300:
            default_extent = 369  # VEX V5 field

    # Create extent input
    extent_input = inputs.addValueInput(
        "extentInput", "Camera Extent", "mm", adsk.core.ValueInput.createByReal(default_extent)
    )

    # Connect to the events
    futil.add_handler(args.command.execute, command_execute, local_handlers=local_handlers)
    futil.add_handler(args.command.destroy, command_destroy, local_handlers=local_handlers)


def set_camera_to_standard_top_down_view(viewport: adsk.core.Viewport, extents: float):
    """Set the camera to a standard top-down view with specified extents."""
    # IMPORTANT: The following steps are important to follow in order.

    # Step 1: Set the camera to orthographic
    cameraCopy = viewport.camera
    cameraCopy.cameraType = adsk.core.CameraTypes.OrthographicCameraType  # type: ignore
    viewport.camera = cameraCopy

    # Step 2: Set the camera to home position
    viewport.goHome(transition=False)

    # Step 3: Set the camera to top view, and set the extents
    cameraCopy = viewport.camera
    cameraCopy.cameraType = adsk.core.CameraTypes.OrthographicCameraType  # type: ignore
    cameraCopy.viewOrientation = adsk.core.ViewOrientations.TopViewOrientation  # type: ignore
    cameraCopy.setExtents(extents, extents)
    viewport.camera = cameraCopy


def command_execute(args: adsk.core.CommandEventArgs):
    futil.log(f"{CMD_NAME} Command Execute Event")

    try:
        # Get the extent input value
        inputs = args.command.commandInputs
        extent_input = adsk.core.ValueCommandInput.cast(inputs.itemById("extentInput"))
        extent_value = extent_input.value

        # Call the function to set the camera
        set_camera_to_standard_top_down_view(app.activeViewport, extent_value)

        # ui.messageBox(f"Camera set to standard top-down view with extent {extent_value} mm", "Success")
    except Exception as e:
        ui.messageBox(f"Failed to set camera: {str(e)}")


def command_destroy(_args: adsk.core.CommandEventArgs):
    futil.log(f"{CMD_NAME} Command Destroy Event")

    global local_handlers
    local_handlers = []
