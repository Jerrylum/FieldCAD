import adsk.core
import adsk.fusion
from ..fusionAddInUtils import occurrence_utils as futil
from .base import AnchorAction

app = adsk.core.Application.get()
ui = app.userInterface

# Constants for validation
RING_PREFIX = "276-8868-001"
MOBILE_GOAL_PREFIX = "276-8868-200"


def get_ring_height(ring: adsk.fusion.Occurrence) -> float:
    bbox = ring.boundingBox
    if bbox:
        return bbox.maxPoint.z - bbox.minPoint.z
    return 5  # Default height in cm if we can't determine from geometry


def get_game_object_prefixes() -> list[str]:
    return [RING_PREFIX, MOBILE_GOAL_PREFIX]


class EncircleRingToMobileGoal(AnchorAction):
    def is_acceptable_game_object(self, candidate: adsk.fusion.Occurrence) -> bool:
        self.game_object = futil.find_matching_instance(candidate, RING_PREFIX)
        return self.game_object is not None

    def is_acceptable_anchor_target(self, candidate: adsk.fusion.Occurrence) -> bool:
        self.anchor_target = futil.find_matching_instance(candidate, MOBILE_GOAL_PREFIX)
        return self.anchor_target is not None

    def execute(self):
        """
        Position a ring around a mobile goal, avoiding collisions with existing rings.

        Args:
            ring: The ring occurrence to position
            mobile_goal: The mobile goal to position the ring around
        """

        ring: adsk.fusion.Occurrence = self.game_object  # type: ignore
        mobile_goal: adsk.fusion.Occurrence = self.anchor_target  # type: ignore
        print(ring.name)

        # Get the anchor's transform
        anchor_transform = mobile_goal.transform2

        # Create a copy of the anchor's transform for initial positioning
        new_transform = anchor_transform.copy()

        # Get the height of the ring for offset calculations (approximation)
        ring_height = get_ring_height(ring)

        # Maximum number of positioning attempts
        max_attempts = 6

        # Get all occurrences to check for collisions
        all_occurrences = []

        product = app.activeProduct
        design = adsk.fusion.Design.cast(product)
        if not design:
            ui.messageBox("No active Fusion design")
            return

        root = design.rootComponent

        for occ in root.occurrences:
            if occ.name != ring.name and (occ.name.startswith(RING_PREFIX) or "ring" in occ.name.lower()):
                all_occurrences.append(occ)

        # Extract the Y-axis vector for vertical stacking
        local_y_axis = adsk.core.Vector3D.create(
            anchor_transform.getCell(0, 1),  # X component of Y axis
            anchor_transform.getCell(1, 1),  # Y component of Y axis
            anchor_transform.getCell(2, 1),  # Z component of Y axis
        )
        local_y_axis.normalize()

        # Try different positions
        found_valid_position = False
        current_offset = 0

        for attempt in range(max_attempts):
            # Calculate new position with current offset
            current_transform = new_transform.copy()

            if attempt > 0:  # Skip offset for first attempt
                offset_vector = local_y_axis.copy()
                offset_vector.scaleBy(current_offset)

                new_position = adsk.core.Vector3D.create(
                    current_transform.translation.x + offset_vector.x,
                    current_transform.translation.y + offset_vector.y,
                    current_transform.translation.z + offset_vector.z,
                )
                current_transform.translation = new_position

            # Check for collisions
            collision_found = False

            for occ in all_occurrences:
                if futil.is_close_to_position(occ.transform2, current_transform, 1):
                    collision_found = True
                    break

            if not collision_found:
                found_valid_position = True
                # Apply the transform to the ring
                ring.transform2 = current_transform
                break

            # Increment offset for next attempt
            current_offset += ring_height

        if not found_valid_position:
            ui.messageBox(
                "Could not find a valid position for the ring after multiple attempts. Try manually positioning it."
            )
