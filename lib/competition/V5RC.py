from typing import Optional
import adsk.core
import adsk.fusion
from ...lib import fusionAddInUtils as futil
from ...lib.competition import V5RC_PushBack
from ...lib.competition import V5RC_HighStakes
from ...lib.competition import V5RC_OverUnder

FIELD_PREFIX = "276-7596-000_With Tiles"


def get_all_v5rc_game_object_prefixes() -> list[str]:
    return [
        *V5RC_PushBack.get_game_object_prefixes(),
        *V5RC_HighStakes.get_game_object_prefixes(),
        *V5RC_OverUnder.get_game_object_prefixes(),
    ]


def get_v5rc_field(product: adsk.core.Product) -> Optional[adsk.fusion.Occurrence]:
    field_occurrence = None

    for occurrence in futil.get_all_occurrences(product):
        if occurrence.name.startswith(FIELD_PREFIX):
            field_occurrence = occurrence
            break

    return field_occurrence


def is_likely_v5rc_field(product: adsk.core.Product) -> bool:
    design = adsk.fusion.Design.cast(product)
    if design:
        bounding_box = design.rootComponent.boundingBox
        # check if bounding box is greater than 300mm
        if bounding_box.maxPoint.x - bounding_box.minPoint.x > 360:
            return True  # VEX V5 field
    return False  # VEX IQ field
