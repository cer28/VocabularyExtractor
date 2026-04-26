'''
Copyright 2026 by Chad Redman <chad at zhtoolkit.com>
License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
'''

from enum import Enum


class DictionaryFormat(str, Enum):
    CEDICT = 'cedict'
    EDICT = 'edict'
    SQLITE3 = 'sqlite3'
    TAB = 'tab'

    def __str__(self): return self.value


class CharacterType(str, Enum):
    SIMPLIFIED = 'simplified'
    TRADITIONAL = 'traditional'
    COMBINED = 'combined'
    VIETNAMESE = 'Vietnamese'

    def __str__(self): return self.value


class StatisticsFormat(str, Enum):
    TAB = 'tab'

    def __str__(self): return self.value


class Charset(str, Enum):
    VIETNAMESE = 'Vietnamese'
    ENGLISH = 'English'

    def __str__(self): return self.value


class SegmentationMethod(str, Enum):
    SIMPLE_LONGEST_MATCH = 'simpleLongestMatch'
    LONGEST_MATCH_PLUS_TRANSLITERATIONS = 'longestMatchPlusTransliterations'
    LONGEST_MATCH_PLUS_TRANSLIT_PLUS_CH_NAMES = 'longestMatchPlusTranslitPlusChNames'

    def __str__(self): return self.value


class TokenMatchType(str, Enum):
    CJK = 'cjk'
    CJK_PLUS_AZ = 'cjk_plus_az'

    def __str__(self): return self.value


class DictionaryOperationType(str, Enum):
    REPLACE = 'replace'
    APPEND = 'append'
    ADD_IF_EMPTY = 'addifempty'

    def __str__(self): return self.value


class DataType(str, Enum):
    WORDS = 'words'
    CHINESE_NAMES = 'chinese_names'
    FOREIGN_NAMES = 'foreign_names'
    CHINESE_PLACE_NAMES = 'chinese_place_names'
    CHENGYU = 'chengyu'

    def __str__(self): return self.value
