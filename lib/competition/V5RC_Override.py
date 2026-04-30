import adsk.core
import adsk.fusion
from ..fusionAddInUtils import occurrence_utils as futil
from .base import AnchorAction

app = adsk.core.Application.get()
ui = app.userInterface

# Constants for validation
PIN_PREFIX = "276-9250-80x"
CUP_PREFIX = "276-9250-81x"
GOAL_PREFIX = "276-9250-003"


def get_game_object_prefixes() -> list[str]:
    return [PIN_PREFIX, CUP_PREFIX, GOAL_PREFIX]

class ConnectPinAndCup(AnchorAction):
    def is_acceptable_game_object(self, candidate: adsk.fusion.Occurrence) -> bool:
        self.game_object, _ = futil.find_matching_instance2(candidate, [PIN_PREFIX, CUP_PREFIX])
        return self.game_object is not None

    def is_acceptable_anchor_target(self, candidate: adsk.fusion.Occurrence) -> bool:
        self.anchor_target, _ = futil.find_matching_instance2(candidate, [PIN_PREFIX, CUP_PREFIX, GOAL_PREFIX])
        return self.anchor_target is not None

    def execute(self):
        game_object: adsk.fusion.Occurrence = self.game_object  # type: ignore
        anchor_target: adsk.fusion.Occurrence = self.anchor_target  # type: ignore

        anchor_bbox = futil.get_bbox(anchor_target)
        anchor_center = futil.get_bbox_center(anchor_bbox)

        # Fusion API distances are centimeters, so 84 mm = 8.4 cm.
        target_z = anchor_bbox.maxPoint.z + 0.5

        # Keep the object's current orientation; only update position.
        new_transform = game_object.transform2.copy()
        new_transform.translation = adsk.core.Vector3D.create(anchor_center.x, anchor_center.y, target_z)

        game_object.transform2 = new_transform
        