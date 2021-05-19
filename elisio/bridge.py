from typing import Any

from .syllable import Syllable


class Bridge:
    def split_from_deviant_word(self, lexeme: str) -> list[Syllable]:
        raise Exception("must be overridden")

    def use_dictionary(self, word: str) -> list[str]:
        raise Exception("must be overridden")

    def make_entry(self, txt: str, struct: str, db_id: int) -> Any:
        raise Exception("must be overridden")

    def dump(self, entries: list[Any]) -> None:
        raise Exception("must be overridden")


class DummyBridge(Bridge):
    def split_from_deviant_word(self, lexeme: str) -> list[Syllable]:
        return []

    def use_dictionary(self, word: str) -> list[str]:
        return []

    def make_entry(self, txt: str, struct: str, db_id: int) -> Any:
        return {}

    def dump(self, entries: list[Any]) -> None:
        pass


class LocalDictionaryBridge(DummyBridge):
    """ Mock Bridge to mock database access """

    def __init__(self, cache: dict[str, list[str]] = {}):
        if not cache:
            cache = dict()
        self.cache = cache  # TODO deepcopy

    def use_dictionary(self, word: str) -> list[str]:
        return self.cache[word]
