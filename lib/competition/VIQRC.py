from ...lib.competition import VIQRC_MixAndMatch


def get_all_viqrc_game_object_prefixes() -> list[str]:
    return [
        *VIQRC_MixAndMatch.get_game_object_prefixes(),
    ]
