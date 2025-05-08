import adsk.core

def update_input(sel: adsk.core.SelectionCommandInput, new_entity: adsk.core.Base):
    if sel.selectionCount == 0 or sel.selection(0).entity != new_entity:
        sel.clearSelection()
        sel.addSelection(new_entity)