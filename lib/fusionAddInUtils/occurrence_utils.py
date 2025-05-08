from typing import Optional, Protocol
import adsk.core
import adsk.fusion


class OccurrenceLike(Protocol):
    """Protocol defining the interface for classes that behave like an Occurrence."""

    @property
    def name(self) -> str:
        """The name of the occurrence-like object."""
        ...

    @property
    def boundingBox(self) -> Optional[adsk.core.BoundingBox3D]:
        """The bounding box of the occurrence-like object."""
        ...


def get_default_unit(product: adsk.core.Product) -> str:
    """Get the default unit of the product."""
    return product.unitsManager.defaultLengthUnits


def get_all_occurrences(product: adsk.core.Product) -> adsk.fusion.OccurrenceList:
    """Get all occurrences in the product."""
    design = adsk.fusion.Design.cast(product)
    if not design:
        raise ValueError("Could not find the design in the assembly")
    return design.rootComponent.allOccurrences


def get_occurrence_like(entity: adsk.core.Base) -> OccurrenceLike:
    """Get the occurrence-like object from the entity.

    Args:
        entity: The entity to get the occurrence-like object from.

    Returns:
        The occurrence-like object from the entity.
    """

    if entity.objectType == adsk.fusion.Component.classType():
        # Component selection - get its occurrences
        component = adsk.fusion.Component.cast(entity)
        return component

    return get_occurrence(entity)


def get_occurrence(entity: adsk.core.Base) -> adsk.fusion.Occurrence:
    """Get the occurrence from the entity.

    Args:
        entity: The entity to get the occurrence from. It can be an occurrence, a face, an edge, or a vertex.

    Returns:
        The occurrence from the entity.
    """

    if entity.objectType == adsk.fusion.Occurrence.classType():
        # Direct occurrence selection
        return adsk.fusion.Occurrence.cast(entity)
    if entity.objectType == adsk.fusion.BRepFace.classType():
        # Face selection - get its parent component
        face = adsk.fusion.BRepFace.cast(entity)
        body = face.body

        if body and body.assemblyContext:
            # The body's assemblyContext gives us the occurrence
            return body.assemblyContext
    if entity.objectType == adsk.fusion.BRepEdge.classType():
        # Edge selection - get its parent component
        edge = adsk.fusion.BRepEdge.cast(entity)
        body = edge.body

        if body and body.assemblyContext:
            return body.assemblyContext
    if entity.objectType == adsk.fusion.BRepVertex.classType():
        # Vertex selection - get its parent component
        vertex = adsk.fusion.BRepVertex.cast(entity)
        body = vertex.body

        if body and body.assemblyContext:
            return body.assemblyContext

    raise ValueError("Could not obtain an occurrence from the entity")


def find_matching_instance[o: OccurrenceLike](occ_like: o, target_prefix: str) -> Optional[o]:
    """Find the first occurrence in the parent hierarchy that matches the target prefix."""

    # Check current occurrence name
    if occ_like.name.startswith(target_prefix):
        return occ_like

    if isinstance(occ_like, adsk.fusion.Occurrence):
        # Check parent occurrences recursively
        current = occ_like
        while current.assemblyContext:
            current = current.assemblyContext
            if current.name.startswith(target_prefix):
                return current

    return None


def find_matching_instance2[o: OccurrenceLike](
    occ_like: o, target_prefix_list: list[str]
) -> tuple[Optional[o], Optional[str]]:
    """Find the first occurrence in the parent hierarchy that matches the target prefix."""

    # Check current occurrence name
    for target_prefix in target_prefix_list:
        if occ_like.name.startswith(target_prefix):
            return occ_like, target_prefix

    if isinstance(occ_like, adsk.fusion.Occurrence):
        # Check parent occurrences recursively
        current = occ_like
        while current.assemblyContext:
            current = current.assemblyContext
            for target_prefix in target_prefix_list:
                if current.name.startswith(target_prefix):
                    return current, target_prefix

    return None, None


def find_matching_instances[o: OccurrenceLike](
    occ_like_list: list[o],
    target_prefix_list: list[str],
) -> list[o]:
    """Find all occurrences in the list that match the target prefix."""

    result: list[o] = []
    for occ_like in occ_like_list:
        for target_prefix in target_prefix_list:
            if occ_like.name.startswith(target_prefix):
                result.append(occ_like)
                break

    return result


def find_closest_occurrence(
    origin: adsk.core.Matrix3D,
    occurrences: list[adsk.fusion.Occurrence],
    target_prefix: str,
) -> Optional[adsk.fusion.Occurrence]:
    """Find the closest occurrence to the origin that matches the target prefix."""

    closest_occurrence = None
    closest_distance = float("inf")

    for occurrence in occurrences:
        if occurrence.name.startswith(target_prefix):
            # Use the built-in distance calculation
            origin_point = origin.translation.asPoint()
            occurrence_point = occurrence.transform2.translation.asPoint()
            distance = origin_point.distanceTo(occurrence_point)

            if distance < closest_distance:
                closest_distance = distance
                closest_occurrence = occurrence

    return closest_occurrence


def validate_instance_name(occurrence: adsk.fusion.Occurrence, target_prefix: str) -> bool:
    """Check if the occurrence or any of its parents match the target prefix."""
    return find_matching_instance(occurrence, target_prefix) is not None


def is_close_to_position(transform1: adsk.core.Matrix3D, transform2: adsk.core.Matrix3D, tolerance_cm: float) -> bool:
    """
    Check if two transforms are close in position (within tolerance).

    Args:
        transform1: First transform
        transform2: Second transform
        tolerance_cm: Distance tolerance in centimeters

    Returns:
        bool: True if positions are within tolerance
    """
    # Get positions
    pos1 = transform1.translation
    pos2 = transform2.translation

    # Calculate distance
    delta_x = pos1.x - pos2.x
    delta_y = pos1.y - pos2.y
    delta_z = pos1.z - pos2.z

    distance = (delta_x**2 + delta_y**2 + delta_z**2) ** 0.5

    return distance < tolerance_cm


def get_bbox(occ_like: OccurrenceLike) -> adsk.core.BoundingBox3D:
    """Get the bounding box of the occurrence.

    Args:
        occurrence: The occurrence to get the bounding box from.

    Returns:
        The bounding box of the occurrence.

    Raises:
        ValueError: If the bounding box is None.
    """
    temp = occ_like.boundingBox
    if temp is None:
        raise ValueError("Bounding box is None")
    return temp


def get_bbox_center(bbox: adsk.core.BoundingBox3D) -> adsk.core.Point3D:
    """Get the center of the bounding box.

    Args:
        bbox: The bounding box to get the center from.

    Returns:
        The center of the bounding box.
    """
    return adsk.core.Point3D.create(
        (bbox.minPoint.x + bbox.maxPoint.x) / 2,
        (bbox.minPoint.y + bbox.maxPoint.y) / 2,
        (bbox.minPoint.z + bbox.maxPoint.z) / 2,
    )


def get_origin_offset(occurrence: adsk.fusion.Occurrence) -> adsk.core.Vector3D:
    """Get the offset between the occurrence's transform origin and its bounding box center.

    Args:
        occurrence: The occurrence to get the offset from.

    Returns:
        The offset between the occurrence's transform origin and its bounding box center.
    """
    bbox = get_bbox(occurrence)
    bbox_center = get_bbox_center(bbox)
    transform_origin = occurrence.transform2.translation
    return adsk.core.Vector3D.create(
        bbox_center.x - transform_origin.x,
        bbox_center.y - transform_origin.y,
        bbox_center.z - transform_origin.z,
    )
