from elisio.Syllable import Syllable
# from elisio.verse.Verse import Verse


class Bridge:
    def split_from_deviant_word(self, lexeme: str) -> list[Syllable]:
        raise Exception("must be overridden")

    def use_dictionary(self, word: str) -> list[str]:
        raise Exception("must be overridden")

    def save(self, verse, db_id: int) -> None:
        raise Exception("must be overridden")


class DummyBridge(Bridge):
    def split_from_deviant_word(self, lexeme: str) -> list[Syllable]:
        return []

    def use_dictionary(self, word: str) -> list[str]:
        return []

    def save(self, verse, db_id: int) -> None:
        pass


class LocalDictionaryBridge(DummyBridge):
    """ Mock Bridge to mock database access """

    def __init__(self, cache: dict[str, list[str]] = {}):
        if not cache:
            cache = dict()
        self.cache = cache

    def use_dictionary(self, word: str) -> list[str]:
        return self.cache[word]
