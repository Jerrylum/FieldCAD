import adsk.core

DESIGN_WORKSPACE_ID = "FusionSolidEnvironment"
RENDER_WORKSPACE_ID = "FusionRenderEnvironment"
DESIGN_PANEL_ID = "DesignFieldCAD"
RENDER_PANEL_ID = "RenderFieldCAD"
DESIGN_TOOLBAR_TAB_ID = "ToolsTab"
RENDER_TOOLBAR_TAB_ID = "RenderTab"


def get_panel_in_design_workspace():
    app = adsk.core.Application.get()
    ui = app.userInterface

    workspace = ui.workspaces.itemById(DESIGN_WORKSPACE_ID)
    panel = workspace.toolbarPanels.itemById(DESIGN_PANEL_ID)
    if not panel:
        panel = workspace.toolbarTabs.itemById(DESIGN_TOOLBAR_TAB_ID).toolbarPanels.add(DESIGN_PANEL_ID, "Field CAD")
    return panel


def get_panel_in_render_workspace():
    app = adsk.core.Application.get()
    ui = app.userInterface

    workspace = ui.workspaces.itemById(RENDER_WORKSPACE_ID)
    panel = workspace.toolbarPanels.itemById(RENDER_PANEL_ID)
    if not panel:
        panel = workspace.toolbarTabs.itemById(RENDER_TOOLBAR_TAB_ID).toolbarPanels.add(RENDER_PANEL_ID, "Field CAD")
    return panel
