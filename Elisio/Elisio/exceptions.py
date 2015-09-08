""" special Exceptions module omg """
class ScansionException(Exception):
    """description of class"""
    pass

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
