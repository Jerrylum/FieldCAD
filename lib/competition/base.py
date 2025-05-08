import adsk.fusion


class AnchorAction:
    def __init__(self):
        self.game_object = None
        self.anchor_target = None

    def is_acceptable_game_object(self, _candidate: adsk.fusion.Occurrence) -> bool:
        return False

    def is_acceptable_anchor_target(self, _candidate: adsk.fusion.Occurrence) -> bool:
        return False

    def execute(self):
        pass
