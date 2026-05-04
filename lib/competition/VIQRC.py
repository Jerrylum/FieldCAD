from typing import Optional
import adsk.core
import adsk.fusion
from ...lib import fusionAddInUtils as futil
from ...lib.competition import VIQRC_LevelUp
from ...lib.competition import VIQRC_MixAndMatch

FIELD_PREFIX = "228-7396-000"


def get_all_viqrc_game_object_prefixes() -> list[str]:
    return [
        *VIQRC_LevelUp.get_game_object_prefixes(),
        *VIQRC_MixAndMatch.get_game_object_prefixes(),
    ]


def get_viqrc_field(product: adsk.core.Product) -> Optional[adsk.fusion.Occurrence]:
    field_occurrence = None

    for occurrence in futil.get_all_occurrences(product):
        if occurrence.name.startswith(FIELD_PREFIX):
            field_occurrence = occurrence
            break

    return field_occurrence
