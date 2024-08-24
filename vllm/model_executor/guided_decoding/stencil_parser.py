from typing import List, Optional, Set, Union

from lmformatenforcer import CharacterLevelParser
from pydantic import BaseModel


class StencilOptions(BaseModel):
    stencil: List[Union[str, int]]
    charsets: Optional[List[str]]


class StencilParser(CharacterLevelParser):
    target_set: List[Set[str]]
    index: int

    def __init__(self, options: Union[dict, 'StencilParser']):
        if isinstance(options, StencilParser):
            self.target_set = options.target_set
            self.index = options.index
            return

        opt = StencilOptions.model_validate(options)
        self.target_set = []
        self.index = 0
        charsets = list(map(set, opt.charsets)) if opt.charsets else []
        for char in opt.stencil:
            if isinstance(char, str):
                self.target_set.append(set(char))
            else:
                if char >= len(charsets):
                    raise ValueError(
                        f"Stencil charset index {char} out of range")
                self.target_set.append(charsets[char])

    def _move_forward(self, cnt: int) -> 'StencilParser':
        clone = StencilParser(self)
        clone.index += cnt
        return clone

    def add_character(self, new_character: str) -> CharacterLevelParser:
        for idx, ch in enumerate(new_character):
            if ch not in self.target_set[self.index + idx]:
                raise ValueError(
                    f"Expected '{self.target[0]}' but got '{new_character}'")
        return self._move_forward(len(new_character))

    def get_allowed_characters(self) -> Set[str]:
        return self.target_set[self.index] if self.index < len(
            self.target_set) else set()

    def can_end(self) -> bool:
        return self.index >= len(self.target_set)
