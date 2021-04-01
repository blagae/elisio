import enum


class VerseType(enum.Enum):
    UNKNOWN = 0
    HEXAMETER = 1
    PENTAMETER = 2
    HENDECASYLLABUS = 3

    def get_creators(self):
        from elisio.engine.verse.Hexameter import HexameterCreator
        from elisio.engine.verse.Pentameter import PentameterCreator
        from elisio.engine.verse.Hendeca import HendecaCreator
        if self == VerseType.HEXAMETER:
            return [HexameterCreator]
        if self == VerseType.PENTAMETER:
            return [PentameterCreator]
        if self == VerseType.HENDECASYLLABUS:
            return [HendecaCreator]
        return [HexameterCreator, PentameterCreator]


class VerseForm(enum.Enum):
    UNKNOWN = 0
    HEXAMETRIC = 1
    ELEGIAC_DISTICHON = 2
    HENDECASYLLABUS = 3

    def get_verse_types(self):
        if self == VerseForm.UNKNOWN:
            return [VerseType.UNKNOWN]
        if self == VerseForm.HEXAMETRIC:
            return [VerseType.HEXAMETER]
        if self == VerseForm.ELEGIAC_DISTICHON:
            return [VerseType.HEXAMETER, VerseType.PENTAMETER]
        if self == VerseForm.HENDECASYLLABUS:
            return [VerseType.HENDECASYLLABUS]
        return [VerseType.UNKNOWN]
