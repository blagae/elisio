import enum


class VerseType(enum.Enum):
    UNKNOWN = 0
    HEXAMETER = 1
    PENTAMETER = 2

    def get_creators(self):
        from Elisio.engine.Hexameter import HexameterCreator
        from Elisio.engine.Pentameter import PentameterCreator
        if self == VerseType.HEXAMETER:
            return [HexameterCreator]
        if self == VerseType.PENTAMETER:
            return [PentameterCreator]
        return [HexameterCreator, PentameterCreator]


class VerseForm(enum.Enum):
    UNKNOWN = 0
    HEXAMETRIC = 1
    ELEGIAC_DISTICHON = 2
    # SAPPHIC_STOPHE = 3

    def get_verse_types(self):
        if self == VerseForm.UNKNOWN:
            return [VerseType.UNKNOWN]
        if self == VerseForm.HEXAMETRIC:
            return [VerseType.HEXAMETER]
        if self == VerseForm.ELEGIAC_DISTICHON:
            return [VerseType.HEXAMETER, VerseType.PENTAMETER]
        # if self == VerseForm.SAPPHIC_STOPHE:
        return [VerseType.UNKNOWN]
