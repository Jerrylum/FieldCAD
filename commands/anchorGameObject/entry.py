from typing import Optional
import adsk.core
import os

import adsk.fusion
from ...commands.panel import get_panel_in_design_workspace
from ...lib import competition
from ...lib import fusionAddInUtils as futil
from ...lib.competition.base import AnchorAction
from ... import config

app = adsk.core.Application.get()
ui = app.userInterface

CMD_ID = f"{config.COMPANY_NAME}_{config.ADDIN_NAME}_anchorGameObject"
CMD_NAME = "Anchor Game Object"
CMD_Description = "Select a game object and anchor it to an element"
IS_PROMOTED = True

ICON_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resources", "")


available_action_types: list[type[AnchorAction]] = [
    competition.V5RC_HighStakes.EncircleRingToMobileGoal,
]

current_action: Optional[AnchorAction] = None

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

    inputs = args.command.commandInputs

    # Create selection input for game object
    game_object_input = inputs.addSelectionInput("select_game_object", "Game Object", "Select a game object to anchor")
    game_object_input.addSelectionFilter("Occurrences")
    game_object_input.setSelectionLimits(1, 1)

    # Create selection input for anchor target
    anchor_target_input = inputs.addSelectionInput(
        "select_anchor_target",
        "Anchor Target",
        "Select where to anchor the game object",
    )
    anchor_target_input.addSelectionFilter("Occurrences")
    anchor_target_input.setSelectionLimits(1, 1)
    # anchor_target_input.isEnabled = False

    # Check if there are pre-selected occurrences
    selections = ui.activeSelections
    if selections.count == 1:
        occurrence = futil.get_occurrence(selections.item(0).entity)

        # If we found an occurrence, check if it matches the game object criteria
        if occurrence:
            for action_type in available_action_types:
                action = action_type()
                accept_game_object = action.is_acceptable_game_object(occurrence)
                if accept_game_object:
                    futil.update_input(game_object_input, action.game_object)  # type: ignore
                    anchor_target_input.isEnabled = True
                    break

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

    try:
        if current_action is not None:
            current_action.execute()
        else:
            ui.messageBox("No action to execute")
    except Exception as e:  # pylint: disable=broad-except
        ui.messageBox(f"Failed to transform game object: {str(e)}")


def validate_inputs(inputs: adsk.core.CommandInputs):
    global current_action
    current_action = None

    game_object_input = adsk.core.SelectionCommandInput.cast(inputs.itemById("select_game_object"))
    anchor_target_input = adsk.core.SelectionCommandInput.cast(inputs.itemById("select_anchor_target"))

    selected_game_object = None
    if game_object_input.selectionCount > 0:
        selected_game_object = futil.get_occurrence(game_object_input.selection(0).entity)

    selected_anchor_target = None
    if anchor_target_input.selectionCount > 0:
        selected_anchor_target = futil.get_occurrence(anchor_target_input.selection(0).entity)

    for action_type in available_action_types:
        action = action_type()

        accept_game_object = False
        if selected_game_object:
            accept_game_object = action.is_acceptable_game_object(selected_game_object)

        accept_anchor_target = False
        if selected_anchor_target:
            accept_anchor_target = action.is_acceptable_anchor_target(selected_anchor_target)

        if accept_game_object:
            futil.update_input(game_object_input, action.game_object)  # type: ignore
            anchor_target_input.isEnabled = True

        if accept_game_object and accept_anchor_target:
            futil.update_input(anchor_target_input, action.anchor_target)  # type: ignore
            current_action = action
            return True  # enable the command

    # IMPORTANT UX: do not update anchor_target_input
    # game_object_input.clearSelection()
    # anchor_target_input.clearSelection()
    # anchor_target_input.isEnabled = False
    return False  # disable the command


def command_input_changed(args: adsk.core.InputChangedEventArgs):
    changed_input = args.input
    inputs = args.inputs

    futil.log(f"{CMD_NAME} Input Changed Event fired from a change to {changed_input.id}")

    validate_inputs(inputs)


def command_validate_input(args: adsk.core.ValidateInputsEventArgs):
    futil.log(f"{CMD_NAME} Validate Input Event")

    inputs = args.inputs
    args.areInputsValid = validate_inputs(inputs)


def command_destroy(_args: adsk.core.CommandEventArgs):
    futil.log(f"{CMD_NAME} Command Destroy Event")

    global local_handlers
    local_handlers = []
