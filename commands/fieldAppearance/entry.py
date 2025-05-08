import os
import adsk.core
import adsk.fusion
from typing import Tuple
from ...commands.panel import get_panel_in_design_workspace
from ...lib import fusionAddInUtils as futil
from ... import config

app = adsk.core.Application.get()
ui = app.userInterface

CMD_ID = f"{config.COMPANY_NAME}_{config.ADDIN_NAME}_fieldAppearance"
CMD_NAME = "Field Appearance"
CMD_Description = "Set appearance to field tiles with a checkerboard pattern of two colors"
IS_PROMOTED = True

ICON_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resources", "")

# Target prefix
TARGET_PREFIX = "SBT0832_276-4997-001"
FIELD_TILE_PREFIX = "276-6904-001"

local_handlers = []


def start():
    cmd_def = ui.commandDefinitions.addButtonDefinition(CMD_ID, CMD_NAME, CMD_Description, ICON_FOLDER)
    futil.add_handler(cmd_def.commandCreated, command_created)

    panel = get_panel_in_design_workspace()

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

    # Create RGB integer inputs for color 1
    color1_group = inputs.addGroupCommandInput("color1Group", "Tile Color 1")
    color1_group.isExpanded = True
    color1_inputs = color1_group.children

    color1_red = color1_inputs.addIntegerSpinnerCommandInput("color1Red", "Red", 0, 255, 1, 66)
    color1_green = color1_inputs.addIntegerSpinnerCommandInput("color1Green", "Green", 0, 255, 1, 66)
    color1_blue = color1_inputs.addIntegerSpinnerCommandInput("color1Blue", "Blue", 0, 255, 1, 66)

    # Create RGB integer inputs for color 2
    color2_group = inputs.addGroupCommandInput("color2Group", "Tile Color 2")
    color2_group.isExpanded = True
    color2_inputs = color2_group.children

    color2_red = color2_inputs.addIntegerSpinnerCommandInput("color2Red", "Red", 0, 255, 1, 71)
    color2_green = color2_inputs.addIntegerSpinnerCommandInput("color2Green", "Green", 0, 255, 1, 71)
    color2_blue = color2_inputs.addIntegerSpinnerCommandInput("color2Blue", "Blue", 0, 255, 1, 71)

    # Connect to the events
    futil.add_handler(args.command.execute, command_execute, local_handlers=local_handlers)
    futil.add_handler(args.command.destroy, command_destroy, local_handlers=local_handlers)


def find_all_field_tiles(design: adsk.fusion.Design) -> list[adsk.fusion.Occurrence]:
    """
    Find all occurrences with the 276-6904-001 prefix and sort them by Y position (ascending),
    then X position (ascending), so the top-left tile is the first element.

    Args:
        design: The active Fusion design

    Returns:
        A list of occurrences sorted by position, with top-left tile first
    """
    # Get all occurrences
    all_occurrences = design.rootComponent.allOccurrences

    # Find occurrences with the target prefix
    field_occurrences = futil.find_matching_instances(
        [all_occurrences.item(i) for i in range(all_occurrences.count)], [FIELD_TILE_PREFIX]
    )

    # Sort occurrences by Y position first, then X position
    # This ensures the top-left tile comes first in the list
    def get_position_key(occ):
        bbox = futil.get_bbox(occ)
        center = futil.get_bbox_center(bbox)
        # Return a tuple that will be used for sorting (y, x)
        return (center.y, center.x)

    # Sort using the position key function
    sorted_occurrences = sorted(field_occurrences, key=get_position_key)

    return sorted_occurrences


def find_or_create_appearance(
    design: adsk.fusion.Design, name: str, rgb_color: Tuple[int, int, int]
) -> adsk.core.Appearance:
    """
    Find or create an appearance with the given name.

    Args:
        design: The active Fusion design
        name: The name of the appearance to find or create

    Returns:
        The appearance object
    """
    # Check if the appearance already exists
    existing_appearance = futil.get_appearance_by_name(design, name)
    if existing_appearance:
        return existing_appearance

    based_appearance = futil.find_appearance_by_name(design, "Opaque")
    if not based_appearance:
        raise ValueError(
            "Could not find 'Opaque' appearance in the current design. Make sure it is used at least once in the design."
        )

    new_appearance = futil.create_custom_appearance(design, based_appearance, name, rgb_color)

    return new_appearance


def command_execute(args: adsk.core.CommandEventArgs):
    futil.log(f"{CMD_NAME} Command Execute Event")

    try:
        # Get the active design
        product = app.activeProduct
        design = adsk.fusion.Design.cast(product)
        if not design:
            ui.messageBox("No active Fusion design", "No Design")
            return

        # # Get all components with the target prefix
        # target_components = futil.find_matching_instances([*design.allComponents], [TARGET_PREFIX])

        # # Get the Steel Stain appearance
        # appearance_steel_satin = futil.get_appearance_by_name(design, "Steel - Satin")
        # if not appearance_steel_satin:
        #     ui.messageBox(
        #         "Could not find 'Steel Stain' appearance from the current design. Make sure it is used at least once in the design.",
        #         "Appearance Not Found",
        #     )
        #     return

        # # Apply the appearance to all target components
        # count = 0
        # for component in target_components:
        #     for body in component.bRepBodies:
        #         body.appearance = appearance_steel_satin
        #     count += 1

        # ui.messageBox(f"Applied 'Steel Stain' appearance to {count} components", "Success")

        # Get color inputs
        inputs = args.command.commandInputs

        # Get color 1 RGB values
        color1_red = adsk.core.IntegerSpinnerCommandInput.cast(inputs.itemById("color1Red"))
        color1_green = adsk.core.IntegerSpinnerCommandInput.cast(inputs.itemById("color1Green"))
        color1_blue = adsk.core.IntegerSpinnerCommandInput.cast(inputs.itemById("color1Blue"))
        color1 = (color1_red.value, color1_green.value, color1_blue.value)

        # Get color 2 RGB values
        color2_red = adsk.core.IntegerSpinnerCommandInput.cast(inputs.itemById("color2Red"))
        color2_green = adsk.core.IntegerSpinnerCommandInput.cast(inputs.itemById("color2Green"))
        color2_blue = adsk.core.IntegerSpinnerCommandInput.cast(inputs.itemById("color2Blue"))
        color2 = (color2_red.value, color2_green.value, color2_blue.value)

        field_tiles = find_all_field_tiles(design)

        appearance_color1 = find_or_create_appearance(design, f"Tile Color 1 ({color1})", color1)
        appearance_color2 = find_or_create_appearance(design, f"Tile Color 2 ({color2})", color2)

        pattern = [0, 1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0]

        for i, tile in enumerate(field_tiles):
            if pattern[i % len(pattern)] == 1:
                tile.appearance = appearance_color1
            else:
                tile.appearance = appearance_color2

    except Exception as e:
        ui.messageBox(f"Failed to apply appearance: {str(e)}")


def command_destroy(_args: adsk.core.CommandEventArgs):
    futil.log(f"{CMD_NAME} Command Destroy Event")

    global local_handlers
    local_handlers = []
