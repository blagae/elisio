""" special Exceptions module omg """


class ScansionException(Exception):
    """description of class"""

    def __init__(self, message, *exceptions):
        super().__init__(message, *exceptions)
        self.message = message
        self.exceptions = []
        if exceptions:
            self.exceptions = list(exceptions)

    def __str__(self):
        result = self.message
        if self.exceptions:
            for excepts in self.exceptions:
                for exc in excepts:
                    result += str("\n{0}: {1}".format(exc.__class__.__name__, exc))
        return result


class LetterException(ScansionException):
    """description of class"""
    pass


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


class PentameterException(VerseException):
    """description of class"""
    pass


class IllegalFootException(ScansionException):
    """description of class"""
    pass
