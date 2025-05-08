from typing import Optional, List, Tuple, Union
import adsk.core
import adsk.fusion


def get_appearance_by_name(design: adsk.fusion.Design, appearance_name: str) -> Optional[adsk.core.Appearance]:
    """
    Get an appearance from the design by name.

    Args:
        design: The design to search for the appearance
        appearance_name: The name of the appearance to find

    Returns:
        The appearance if found, or None if not found
    """
    # First search in the design appearances
    for i in range(design.appearances.count):
        appearance = design.appearances.item(i)
        if appearance.name == appearance_name:
            return appearance

    # If not found in design, check material libraries
    # app = adsk.core.Application.get()
    # material_libs = app.materialLibraries

    # for i in range(material_libs.count):
    #     material_lib = material_libs.item(i)
    #     for j in range(material_lib.appearances.count):
    #         appearance = material_lib.appearances.item(j)
    #         if appearance.name == appearance_name:
    #             return appearance

    return None


def find_appearance_by_name(design: adsk.fusion.Design, name_prefix: str) -> Optional[adsk.core.Appearance]:
    """
    Find an appearance by name in the design.

    Args:
        design: The design to search for the appearance
        name_prefix: The prefix of the appearance to find

    Returns:
        The appearance if found, or None if not found
    """
    # First search in the design appearances
    for i in range(design.appearances.count):
        appearance = design.appearances.item(i)
        if appearance.name.startswith(name_prefix):
            return appearance

    return None


def create_custom_appearance(
    design: adsk.fusion.Design, base: adsk.core.Appearance, new_name: str, rgb_color: Tuple[int, int, int]
) -> adsk.core.Appearance:
    """
    Create a custom appearance based on an existing one with a new color.

    Args:
        design: The design to add the appearance to
        base: The appearance to use as a base
        new_name: The name for the new appearance
        rgb_color: A tuple of (r, g, b) values (0-255)

    Returns:
        The newly created appearance
    """

    # Create a copy with the new name
    custom_appearance = design.appearances.addByCopy(base, new_name)

    # Look for the color property - property name may vary depending on material type
    color_props = ["opaque_albedo", "color", "main_color"]

    for prop_name in color_props:
        color_prop = custom_appearance.appearanceProperties.itemById(prop_name)
        if color_prop and color_prop.objectType == adsk.core.ColorProperty.classType():
            # Cast to the correct property type
            color_prop = adsk.core.ColorProperty.cast(color_prop)

            # Get the color value and set it
            color_value = color_prop.value
            r, g, b = rgb_color
            color_value.setColor(r, g, b, 255)  # Full opacity

            # Set the modified color back to the property
            color_prop.value = color_value
            return custom_appearance

    return custom_appearance


def apply_appearance_to_components(components: List[adsk.fusion.Component], appearance: adsk.core.Appearance) -> int:
    """
    Apply an appearance to all bodies in the provided components.

    Args:
        components: List of components to apply the appearance to
        appearance: The appearance to apply

    Returns:
        The number of bodies that had the appearance applied
    """
    count = 0

    for component in components:
        for body in component.bRepBodies:
            body.appearance = appearance
            count += 1

    return count
