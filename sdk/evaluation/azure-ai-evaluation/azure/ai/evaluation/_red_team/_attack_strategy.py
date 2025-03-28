# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from enum import Enum
from typing import List

class AttackStrategy(Enum):
    """Strategies for attacks."""
    EASY = "easy"
    MODERATE = "moderate"
    DIFFICULT = "difficult"
    AnsiAttack = "ansi_attack"
    AsciiArt = "ascii_art"
    AsciiSmuggler = "ascii_smuggler"
    Atbash = "atbash"
    Base64 = "base64"
    Binary = "binary"
    Caesar = "caesar"
    CharacterSpace = "character_space"
    CharSwap = "char_swap"
    Diacritic = "diacritic"
    Flip = "flip"
    Leetspeak = "leetspeak"
    Morse = "morse"
    ROT13 = "rot13"
    SuffixAppend = "suffix_append"
    StringJoin = "string_join"
    Tense = "tense"
    UnicodeConfusable = "unicode_confusable"
    UnicodeSubstitution = "unicode_substitution"
    Url = "url"
    Baseline = "baseline"
    Jailbreak = "jailbreak"

    @classmethod
    def Compose(cls, items: List["AttackStrategy"]) -> List["AttackStrategy"]:
        for item in items:
            if not isinstance(item, cls):
                raise ValueError("All items must be instances of AttackStrategy")
        if len(items) > 2: 
            raise ValueError("Composed strategies must have at most 2 items")
        return items