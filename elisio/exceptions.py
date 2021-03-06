""" special Exceptions module omg """


class ScansionException(Exception):
    """description of class"""

    def __init__(self, message: str, *exceptions: Exception):
        super().__init__(message, *exceptions)
        self.message = message
        self.exceptions = []
        if exceptions:
            self.exceptions = list(exceptions)

    def __repr__(self) -> str:
        result = self.message
        if self.exceptions:
            for excepts in self.exceptions:
                for exc in excepts:
                    result += f"\n{exc.__class__.__name__}: {exc}"
        return result


class SoundException(ScansionException):
    """description of class"""
    pass


class SyllableException(ScansionException):
    """description of class"""
    pass


class WordException(ScansionException):
    """description of class"""
    pass


class VerseException(ScansionException):
    """description of class"""
    pass


class HexameterException(VerseException):
    """description of class"""
    pass


class VerseCreatorException(VerseException):
    """description of class"""
    pass


class PentameterException(VerseException):
    """description of class"""
    pass


class IllegalFootException(ScansionException):
    """description of class"""
    pass


class HendecaException(VerseException):
    """description of class"""
    pass
