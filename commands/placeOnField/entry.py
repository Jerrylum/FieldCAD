import os
import adsk.core

import adsk.fusion
from ...commands.panel import get_panel_in_design_workspace
from ...lib import fusionAddInUtils as futil
from ... import config
from ...lib.competition import V5RC
from ...lib.tokens.tokens import CodePointBuffer, NumberUOL, UnitConverter, UnitOfLength, Computation

app = adsk.core.Application.get()
ui = app.userInterface

CMD_ID = f"{config.COMPANY_NAME}_{config.ADDIN_NAME}_placeOnField"
CMD_NAME = "Place On Field"
CMD_Description = "Place a game object on the field at specified coordinates"
IS_PROMOTED = True

ICON_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resources", "")

# List of game object name prefixes
GAME_OBJECT_PREFIXES = V5RC.get_all_v5rc_game_object_prefixes()

FIELD_PREFIX = "276-7596-000_With Tiles"

TILE_HEIGHT = 1.6003  # in cm

# Field size (V5 field is 140.41 inches square, or about 356.64 cm)
FIELD_SIZE_IN = 140.41  # in inches
FIELD_HALF_SIZE_IN = 70.205  # in inches

local_handlers = []
previous_x_value: str = "0"
previous_y_value: str = "0"
previous_z_value: str = "0"
previous_copy_value: bool = True
previous_use_center_origin: bool = True


def start():
    cmd_def = ui.commandDefinitions.addButtonDefinition(CMD_ID, CMD_NAME, CMD_Description, ICON_FOLDER)
    futil.add_handler(cmd_def.commandCreated, command_created)

    panel = get_panel_in_design_workspace()

    # Add command to panel
    control = panel.controls.addCommand(cmd_def)
    control.isPromoted = IS_PROMOTED

    global previous_x_value
    global previous_y_value
    global previous_z_value

    default_unit = futil.get_default_unit(app.activeProduct)
    previous_x_value = f"0 {default_unit}"
    previous_y_value = f"0 {default_unit}"
    previous_z_value = f"0 {default_unit}"


def stop():
    command_definition = ui.commandDefinitions.itemById(CMD_ID)
    if command_definition:
        command_definition.deleteMe()


def command_created(args: adsk.core.CommandCreatedEventArgs):
    futil.log(f"{CMD_NAME} Command Created Event")

    inputs = args.command.commandInputs

    # Create selection input for game object
    game_object_input = inputs.addSelectionInput("select_game_object", "Game Object", "Select a game object to place")
    game_object_input.addSelectionFilter("Occurrences")
    game_object_input.setSelectionLimits(1, 1)

    # Create toggle input for coordinate origin
    origin_input = inputs.addBoolValueInput("use_center_origin", "Origin Point", True, "", previous_use_center_origin)
    origin_input.tooltip = (
        "Toggle between field center (ON) and bottom left corner (OFF) as the origin point for coordinates"
    )

    # Create value inputs for coordinates
    inputs.addStringValueInput("x_coord", "X", previous_x_value)
    inputs.addStringValueInput("y_coord", "Y", previous_y_value)
    inputs.addStringValueInput("z_coord", "Z", previous_z_value)

    # Create boolean input for copy
    inputs.addBoolValueInput("copy_object", "Copy", previous_copy_value, "", True)

    # Connect to the events
    futil.add_handler(args.command.execute, command_execute, local_handlers=local_handlers)
    futil.add_handler(args.command.inputChanged, command_input_changed, local_handlers=local_handlers)
    futil.add_handler(
        args.command.validateInputs,
        command_validate_input,
        local_handlers=local_handlers,
    )
    futil.add_handler(args.command.destroy, command_destroy, local_handlers=local_handlers)


def command_execute(args: adsk.core.CommandEventArgs):
    futil.log(f"{CMD_NAME} Command Execute Event")

    try:
        inputs = args.command.commandInputs

        # Get the selected game object
        game_object_input = adsk.core.SelectionCommandInput.cast(inputs.itemById("select_game_object"))
        game_object = futil.get_occurrence(game_object_input.selection(0).entity)

        # Get origin mode
        origin_input = adsk.core.BoolValueCommandInput.cast(inputs.itemById("use_center_origin"))
        use_center_origin = origin_input.value

        # Save the previous value
        global previous_use_center_origin
        previous_use_center_origin = use_center_origin

        # Get x, y, z coordinates
        x_input = adsk.core.StringValueCommandInput.cast(inputs.itemById("x_coord"))
        y_input = adsk.core.StringValueCommandInput.cast(inputs.itemById("y_coord"))
        z_input = adsk.core.StringValueCommandInput.cast(inputs.itemById("z_coord"))

        # Save the previous values
        global previous_x_value
        global previous_y_value
        global previous_z_value
        previous_x_value = x_input.value
        previous_y_value = y_input.value
        previous_z_value = z_input.value

        # Parse coordinates using NumberUOL
        x_buffer = CodePointBuffer(x_input.value)
        y_buffer = CodePointBuffer(y_input.value)
        z_buffer = CodePointBuffer(z_input.value)

        # Try to parse as computations first, then as simple numbers
        x_comp = Computation.parse_with(x_buffer, NumberUOL.parse)
        y_comp = Computation.parse_with(y_buffer, NumberUOL.parse)
        z_comp = Computation.parse_with(z_buffer, NumberUOL.parse)

        # Compute values with product's default unit and convert to cm (database unit)
        default_unit = UnitOfLength.from_string(futil.get_default_unit(app.activeProduct))
        converter = UnitConverter(default_unit, UnitOfLength.Centimeter)
        x_value = converter.from_a_to_b(x_comp.compute(default_unit)) if x_comp else 0
        y_value = converter.from_a_to_b(y_comp.compute(default_unit)) if y_comp else 0
        z_value = converter.from_a_to_b(z_comp.compute(default_unit)) if z_comp else 0

        # Get the copy input
        copy_input: adsk.core.BoolValueCommandInput = inputs.itemById("copy_object")  # type: ignore
        should_copy = copy_input.value

        # Save the previous value
        global previous_copy_value
        previous_copy_value = should_copy

        # Find the field occurrence
        field_occurrence = V5RC.get_V5RC_field(app.activeProduct)

        if field_occurrence is None:
            raise ValueError("No field occurrence found")

        # Get the field's bounding box
        field_bbox = futil.get_bbox(field_occurrence)

        # Get the field's center point and bottom Z, use bbox center but not transform origin
        field_center = futil.get_bbox_center(field_bbox)
        field_bottom_z = field_bbox.minPoint.z + TILE_HEIGHT

        # Get the game object's bounding box
        game_object_bbox = futil.get_bbox(game_object)

        # Calculate the offset between transform origin and bbox center
        origin_offset = futil.get_origin_offset(game_object)

        # Calculate the height of the game object
        game_object_height = game_object_bbox.maxPoint.z - game_object_bbox.minPoint.z

        # Adjust coordinates based on selected origin
        if not use_center_origin:
            # Convert field_half_size from inches to cm
            inch_to_cm = UnitConverter(UnitOfLength.Inch, UnitOfLength.Centimeter)
            field_half_size_cm = inch_to_cm.from_a_to_b(FIELD_HALF_SIZE_IN)

            # If using bottom left corner, subtract half field size to x and y
            x_value -= field_half_size_cm
            y_value -= field_half_size_cm

        # Create a new transform for the game object
        new_transform = game_object.transform2.copy()  # Preserve original rotation
        new_position = adsk.core.Vector3D.create(
            field_center.x + x_value - origin_offset.x,  # Apply offset to center
            field_center.y + y_value - origin_offset.y,  # Apply offset to center
            field_bottom_z + z_value + (game_object_height / 2) - origin_offset.z,  # Apply offset to bottom
        )
        new_transform.translation = new_position

        # Apply the transform to the game object or its copy
        if should_copy:
            # Create a copy of the game object
            design = adsk.fusion.Design.cast(app.activeProduct)
            root_comp = design.rootComponent
            transform = game_object.transform2.copy()
            new_occ = root_comp.occurrences.addExistingComponent(game_object.component, transform)
            # Apply transform to the new copy
            new_occ.transform2 = new_transform
            # Ensure the occurrence is visible in the assembly context
            if not new_occ.isLightBulbOn:
                new_occ.isLightBulbOn = True
        else:
            # Apply transform to the original
            game_object.transform2 = new_transform

    except Exception as e:
        ui.messageBox(f"Failed to place game object: {str(e)}")


def command_input_changed(args: adsk.core.InputChangedEventArgs):
    inputs = args.inputs

    # Get all inputs
    x_input = adsk.core.StringValueCommandInput.cast(inputs.itemById("x_coord"))
    y_input = adsk.core.StringValueCommandInput.cast(inputs.itemById("y_coord"))
    z_input = adsk.core.StringValueCommandInput.cast(inputs.itemById("z_coord"))

    # Try to parse the inputs using NumberUOL
    x_buffer = CodePointBuffer(x_input.value)
    y_buffer = CodePointBuffer(y_input.value)
    z_buffer = CodePointBuffer(z_input.value)

    x_comp = Computation.parse_with(x_buffer, NumberUOL.parse)
    x_input.isValueError = x_comp is None

    y_comp = Computation.parse_with(y_buffer, NumberUOL.parse)
    y_input.isValueError = y_comp is None

    z_comp = Computation.parse_with(z_buffer, NumberUOL.parse)
    z_input.isValueError = z_comp is None

    changed_input = args.input

    futil.log(f"{CMD_NAME} Input Changed Event fired from a change to {changed_input.id}")


def command_validate_input(args: adsk.core.ValidateInputsEventArgs):
    futil.log(f"{CMD_NAME} Validate Input Event")

    inputs = args.inputs
    game_object_input = adsk.core.SelectionCommandInput.cast(inputs.itemById("select_game_object"))
    are_all_inputs_valid = True

    # Validate that a game object is selected
    if game_object_input.selectionCount == 0:
        are_all_inputs_valid = False
    else:
        # Validate that the selected object matches one of our prefixes
        selected_entity = futil.get_occurrence(game_object_input.selection(0).entity)
        matched, _ = futil.find_matching_instance2(selected_entity, GAME_OBJECT_PREFIXES)
        if matched is None:
            are_all_inputs_valid = False
        else:
            futil.update_input(game_object_input, matched)

    args.areInputsValid = are_all_inputs_valid


def command_destroy(_args: adsk.core.CommandEventArgs):
    futil.log(f"{CMD_NAME} Command Destroy Event")

    global local_handlers
    local_handlers = []
