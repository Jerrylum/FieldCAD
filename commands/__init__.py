# Here you define the commands that will be added to your add-in.

from .panel import get_panel_in_design_workspace, get_panel_in_render_workspace
from .anchorGameObject import entry as anchorGameObject
from .placeOnField import entry as placeOnField
from .inspectGameObject import entry as inspectGameObject
from .fieldAppearance import entry as fieldAppearance
from .setCamera import entry as setCamera

# Fusion will automatically call the start() and stop() functions.
commands = [
    anchorGameObject,
    placeOnField,
    inspectGameObject,
    fieldAppearance,
    setCamera,
]


# Assumes you defined a "start" function in each of your modules.
# The start function will be run when the add-in is started.
def start():
    panel = get_panel_in_design_workspace()
    if panel:
        panel.deleteMe()

    panel = get_panel_in_render_workspace()
    if panel:
        panel.deleteMe()

    for command in commands:
        command.start()


# Assumes you defined a "stop" function in each of your modules.
# The stop function will be run when the add-in is stopped.
def stop():
    for command in commands:
        command.stop()
