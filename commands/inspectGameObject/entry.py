import os
import adsk.core

import adsk.fusion
from ...commands.panel import get_panel_in_design_workspace
from ...lib import fusionAddInUtils as futil
from ... import config
from ...lib.competition import V5RC

app = adsk.core.Application.get()
ui = app.userInterface

CMD_ID = f"{config.COMPANY_NAME}_{config.ADDIN_NAME}_inspectGameObject"
CMD_NAME = "Inspect Game Object"
CMD_Description = "Display information about a selected game object"
IS_PROMOTED = True

ICON_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resources", "")

# List of game object name prefixes
GAME_OBJECT_PREFIXES = V5RC.get_all_v5rc_game_object_prefixes()

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

    # Set dialog options - hide OK button and rename Cancel to Close
    args.command.isOKButtonVisible = False
    args.command.cancelButtonText = "Close"

    inputs = args.command.commandInputs

    # Create selection input for game object
    game_object_input = inputs.addSelectionInput("select_game_object", "Game Object", "Select a game object to inspect")
    game_object_input.addSelectionFilter("Occurrences")
    game_object_input.setSelectionLimits(1, 1)

    # Create read-only text boxes for displaying information
    inputs.addTextBoxCommandInput("object_name", "Object Name", "", 1, True)
    inputs.addTextBoxCommandInput("bbox_info", "Bounding Box", "", 3, True)

    # Connect to the events
    futil.add_handler(args.command.execute, command_execute, local_handlers=local_handlers)
    futil.add_handler(args.command.inputChanged, command_input_changed, local_handlers=local_handlers)
    futil.add_handler(
        args.command.validateInputs,
        command_validate_input,
        local_handlers=local_handlers,
    )
    futil.add_handler(args.command.destroy, command_destroy, local_handlers=local_handlers)


def command_execute(_args: adsk.core.CommandEventArgs):
    futil.log(f"{CMD_NAME} Command Execute Event")
    # Nothing to do on execute as we're just displaying information


def command_input_changed(args: adsk.core.InputChangedEventArgs):
    futil.log(f"{CMD_NAME} Input Changed Event fired from a change to {args.input.id}")

    if args.input.id == "select_game_object":
        inputs = args.inputs
        game_object_input = adsk.core.SelectionCommandInput.cast(inputs.itemById("select_game_object"))
        name_input = adsk.core.TextBoxCommandInput.cast(inputs.itemById("object_name"))
        bbox_input = adsk.core.TextBoxCommandInput.cast(inputs.itemById("bbox_info"))

        if game_object_input.selectionCount > 0:
            try:
                # Get selected entity
                selected_entity = futil.get_occurrence_like(game_object_input.selection(0).entity)

                # Check and display the object name
                matched, _ = futil.find_matching_instance2(selected_entity, GAME_OBJECT_PREFIXES)
                if matched and (
                    isinstance(matched, adsk.fusion.Occurrence) or isinstance(matched, adsk.fusion.Component)
                ):
                    selected_entity = matched
                    name_input.text = f"{selected_entity.name}"
                    futil.update_input(game_object_input, selected_entity)
                else:
                    name_input.text = f"{selected_entity.name} (Not a recognized game object)"

                # Get and display bounding box information
                bbox = futil.get_bbox(selected_entity)

                min_point = bbox.minPoint
                max_point = bbox.maxPoint

                # Calculate dimensions
                width = max_point.x - min_point.x
                depth = max_point.y - min_point.y
                height = max_point.z - min_point.z

                product = app.activeProduct
                default_unit = futil.get_default_unit(product)
                converted_width = product.unitsManager.convert(width, "cm", default_unit)
                converted_depth = product.unitsManager.convert(depth, "cm", default_unit)
                converted_height = product.unitsManager.convert(height, "cm", default_unit)

                bbox_text = f"Width (X): {converted_width:.3f} {default_unit}\n"
                bbox_text += f"Depth (Y): {converted_depth:.3f} {default_unit}\n"
                bbox_text += f"Height (Z): {converted_height:.3f} {default_unit}"

                bbox_input.text = bbox_text
            except Exception as e:
                ui.messageBox(f"Error getting object information: {str(e)}")
        else:
            # Clear displays if no selection
            name_input.text = ""
            bbox_input.text = ""


def command_validate_input(args: adsk.core.ValidateInputsEventArgs):
    futil.log(f"{CMD_NAME} Validate Input Event")

    inputs = args.inputs
    game_object_input = adsk.core.SelectionCommandInput.cast(inputs.itemById("select_game_object"))
    are_all_inputs_valid = True

    # Validate that a game object is selected
    if game_object_input.selectionCount == 0:
        are_all_inputs_valid = False
    else:
        # We'll allow any object to be selected for inspection
        pass

    args.areInputsValid = are_all_inputs_valid


def command_destroy(_args: adsk.core.CommandEventArgs):
    futil.log(f"{CMD_NAME} Command Destroy Event")

    global local_handlers
    local_handlers = []
