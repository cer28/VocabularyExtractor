'''
Copyright 2025 by Chad Redman <chad at zhtoolkit.com>
License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
'''

import re
import os
from itertools import filterfalse

from segmenter import charset
from segmenter.plugins import SegmentMethodPlugin
from segmenter.charset import charsets
from segmenter.enums import (
    Charset,
    DictionaryFormat, CharacterType, StatisticsFormat,
    SegmentationMethod, TokenMatchType, DictionaryOperationType, DataType,
)

print(SegmentMethodPlugin.__subclasses__())

try:
    WindowsError
except NameError:
    WindowsError = OSError


class CJK:
    # http://en.wikipedia.org/wiki/CJK_Unified_Ideographs
    cjkUnifiedIdeographs = u'\u4E00-\u9FFF'
    cjkUnifiedIdeographsExtA = u'\u3400-\u4DBF'
    # cjkUnifiedIdeographsExtB = u'\u20000-2A6DF'
    # cjkEnclosedLettersAndMonths = u'\u3200-\u32FF'
    cjkCompatibilityIdeographs = u'\uF900-\uFAFF'

    # Non-CJK characters used in simplified/traditional field
    # Some of these are covered in Halfwidth and Fullwidth Forms. But this makes a stricter filter
    cjkMiddleDot = u'\u00B7'
    cjkFullwidthComma = u'\uFF0C'
    cjkLingZero = u'\u3007'
    cjkFullwidthLatin = u'\uFF21-\uFF3A\uFF41-\uFF5A'
    cjkKatakanaMiddleDot = u'\u30FB'

    # Bopomofo and zhuyin
    cjkBopomofo = u'\u3105-\u312D\u31A0-\u31A5\u02EA\u02EB\u02CA\u02C7\u02CB\u02D9'


class DictionaryWord:
    '''
    A single word of a dictionary, with expression, reading, and meaning
    '''

    def __init__(self, entry, english, pinyin=None):
        self.entry = entry
        self.english = english
    
    def __str__(self):
        return f'{self.entry}\t{self.english}'




class Dictionary:
    '''
    Parses a file containing lexical entries
    '''

    def getWordCount(self):
        return len(self.words)

    def read_cedict_line(self, line, lineno):
        if re.match('\\s*#', line):
            # A comment line
            return None

        cjkRange = u'%s%s%s%s%s%s%s%s' % (
        CJK.cjkKatakanaMiddleDot, CJK.cjkFullwidthComma, CJK.cjkLingZero, CJK.cjkUnifiedIdeographsExtA,
        CJK.cjkUnifiedIdeographs, CJK.cjkCompatibilityIdeographs, CJK.cjkFullwidthLatin, CJK.cjkBopomofo)

        # Allow semicolons in pinyin, because the chardict has them that way
        # pat = u'([%s]+)[ \t]([%s]+)[ \t]\[([a-zA-Z0-9,\xb7: ]+)\][ \t]/(.*)/\s*$' % (cjkRange, cjkRange)
        pat = u'([%s]+)[ \t]([%s]+)[ \t]\[([a-zA-Z0-9,\xb7:; ]+)\][ \t]/(.*)/\s*$' % (cjkRange, cjkRange)

        m = re.match(pat, line)
        if m:
            return DictionaryWord((m.group(1), m.group(2)), m.group(4), m.group(3))
        else:
            if self.verbose:
                self.messages.append(f"Warning: Invalid CEDICT entry in line {lineno} of {self.filename}: '{line}'")

            return None

    def read_cedict_file(self, filename, updatefunction):
        '''
        The CEDICT format is traditional simplified [pinyin] english
        throws: IOError
        '''
        progresspct = 0
        try:
            filebytes = os.path.getsize(filename)
            fh = open(filename, encoding='utf-8')  # throws IOError
        except (WindowsError, OSError, IOError) as e:
            self.messages.append("Warning: Failed to load dictionary %s: %s" % (filename, e.message))
            return
        try:
            lineno = 0
            for line in fh.read().splitlines():
                lineno += 1
                # This doesn't exactly equal 100% due to unicode vs. byte comparisons
                progresspct += len(line)*100.0/filebytes
                if updatefunction and progresspct > 0:
                    updatefunction(progresspct)

                word = self.read_cedict_line(line, lineno)
                if word is not None:
                    self.words.append(word)
        finally:
            fh.close()


    def read_edict_line(self, line, lineno):
        if re.match('\\s*#', line):
            # A comment line
            return None

        # Entry: vietnamese : english
        parts = re.split(r'\s*:\s*', line, 1)
        # pat = '(.+) ?: ?(.+)\\s*'
        #
        # m = re.match(pat, line)
        # if m:
        #     return DictionaryWord(m.group(1), m.group(2))
        if len(parts) == 2:
            return DictionaryWord(parts[0], parts[1])
        else:
            if self.verbose:
                self.messages.append(f'Warning: Invalid dictionary entry in line {lineno} of {self.filename}: "{line}"')
                print(f'Warning: Invalid dictionary entry in line {lineno} of {self.filename}: "{line}"')

                
            return None

    def read_edict_file(self, filename, updatefunction):
        '''
        The CEDICT format is traditional simplified [pinyin] english
        throws: IOError
        '''
        progresspct = 0
        try:
            filebytes = os.path.getsize(filename)
            fh = open(filename, encoding="utf-8")  #throws IOError
        except WindowsError | OSError | IOError as e:
            self.messages.append("Warning: Failed to load dictionary %s: %s" % (filename, e.message))
            return
        try:
            lineno = 0
            for line in fh.read().splitlines():
                lineno += 1
                # This doesn't exactly equal 100% due to unicode vs. byte comparisons
                progresspct += len(line)*100.0/filebytes
                if updatefunction and progresspct > 0:
                    updatefunction(progresspct)

                #if lineno > 100: break  #TODO temp debugging delete
                word = self.read_edict_line(line, lineno)
                if word != None:
                    self.words.append(word)
        finally:
            fh.close()

    @classmethod
    def _detect_format(cls, filename):
        '''Read the first line of the file; if it is %<format>, return that DictionaryFormat.'''
        with open(filename, encoding='utf-8') as fh:
            first = fh.readline().rstrip('\n')
        if first.startswith('#%format: '):
            return DictionaryFormat(first[len('#%format: '):])
        raise Exception("Cannot detect dictionary format for %s: first line is not '#%%format: <format>'" % filename)

    def __init__(self, filename, format, character=None, dataType='words', description=None, tag=None, verbose=False, updatefunction=None):
        self.words = []
        self.messages = []
        self.filename = filename
        try:
            self.format = DictionaryFormat(format)
        except ValueError:
            self.messages.append("Unknown dictionary format %s" % format)
            raise Exception("Unknown dictionary format %s" % format)

        self.dataType = dataType

        if description == None:
            self.description = self.filename
        else:
            self.description = description

        self.tag = tag
        self.verbose = verbose

        if self.format == DictionaryFormat.EDICT:
            self.read_edict_file(filename, updatefunction)
        elif self.format == DictionaryFormat.CEDICT:
            self.read_cedict_file(filename, updatefunction)
        else:
            self.messages.append("Dictionary format '%s' is not yet implemented" % self.format)
            raise Exception("Dictionary format '%s' is not yet implemented" % self.format)

    def __str__(self):
        return 'Dictionary %s (%s), %d Entries' % (self.description, self.filename, len(self.words))



class Statistics:
    '''
    For the storage of a list of words and an associated value
    '''
#    statisticsTypes = ('hsk_level', 'frequency_per_million', 'is_chengyu')

    class Statistic:
        def __init__(self, word, value):
            self.word = word
            self.value = value

    def __init__(self, filename, formatType, character):
        '''note: charset 'combined' here means 3 columns: trad-expression simp-expression value
           Charsets traditional or simplified means that the columns are expression value
           TODO: make statistics type a list so that multiple fields can be defined 
        '''
        self.statisticType = filename

        try:
            self.character = CharacterType(character)
        except ValueError:
            raise Exception("Unknown character type %s" % character)

        try:
            self.formatType = StatisticsFormat(formatType)
        except ValueError:
            raise Exception("Unknown formatType %s" % formatType)
        
        self.filename = filename

        self.words = []
        fh = open(self.filename, encoding='utf-8')  #throws IOError
        try:
            curline = 0
            for line in fh.read().splitlines():
                curline += 1
                if self.formatType == StatisticsFormat.TAB:
                    m = re.match('^# Heading: ', line)
                    if m:
                        self.statisticType = line[m.end():]
                        continue
                    if re.match('\\s*#', line):
                        # These are comment lines
                        continue
                    ar = line.split('\t')
                    if len(ar) >= 2:
                        self.words.append(self.Statistic(ar[0], ar[1]))
                    else:
                        #TODO add self.messages to pass errors to the message tab
                        #self.messages.append("Warning: statistic in %s, line %d is missing a value" % (self.filename, curline))
                        pass
                    
        finally:
            fh.close()

    def __repr__(self):
        return "<Statistics> Filename '%s', heading '%s', %d entries" % (self.filename, self.statisticType, len(self.words)) 


class SegmenterResults:
    '''
    Stores results of segmentation
    '''
    
    class Token:
        def __init__(self, text, index):
            self.text = text
            self.index = index
            
        def __repr__(self):
            return "<Token> '%s' (%d)" % (self.text, self.index)
            
    class Lexical:
        def __init__(self, text):
            self.text = text
            self.indexes = []
        
        def __repr__(self):
            return "<Lexical> %s (%d tokens)" % (self.text, len(self.indexes))

    class Sentence:
        def __init__(self, text, idx, is_whitespace=False):
            self.text = text.strip()
            self.start_idx = idx
            self.end_idx = idx + len(text) - 1
            self.is_whitespace = is_whitespace



        def contains(self, idx):
            return (idx >= self.start_idx and idx <= self.end_idx)

        def __repr__(self):
            return "<Sentence> (index %d -> %d) %s" % (self.start_idx, self.end_idx, self.text)

    def __init__(self, text):
        self.text = text
        self.tokens = []     #  : Token[]
        self.lexList = []    # : Lexical[]. The unique words in the order of first index (shadowing lexicals for performace)
        self.lexicals = {}       # : {string => Lexical} 
        self.words = {}       # : {string => Segmenter::Word} 
        self.sentences: list[SegmenterResults.Sentence] = []   # : Sentence[]
        # note words are only set when the Segmenter had it in it's dictionary. So it's not for foreign words
        
        self.debugCountSize = 0

    def __str__(self):
        return "<SegmenterResults>\n\ttokens = %s,\n\tlexList = %s,\n\tlexicals = %s,\n\twords = %s" % (self.tokens, self.lexList, self.lexicals, self.words)  

    def filterWords(self, wordArray):
        pass

    # def addSentence(self, text, position):
    #     lex = self.Sentence(text, position)
    #     #print "Found sentence: %s" % lex
    #     self.sentences.append(lex)

    def addLexical(self, text, position, segword=None, isCJK=True):
        'public method called by Segmenter.'
        self.debugCountSize += len(text)
        if self.debugCountSize > 1000:
            #print "#",
            self.debugCountSize = 0

        self.tokens.append(self.Token(text, position))

        #if segword != None:
        if isCJK:
            'lexicals are Chinese words, so only store them when a definition (Segmenter::Word) exists for them'
            lex = None  #TODO need this?

            if text in self.lexicals and segword.__class__.__name__ != 'SectionBreakWord':
                'we want to add all section breaks to the word list, not just the first instance'
                lex = self.lexicals[text]
            else:
                lex = self.Lexical(text)
                self.lexicals[text] = lex
                self.lexList.append(lex)
                #if segword != None:
                if True:
                    self.words[text] = segword

            lex.indexes.append(position)

    def findFirstSentence(self, lex):
        for sentence in self.sentences:
            if sentence.contains(lex.indexes[0]):
                m = re.search(lex.text, sentence.text)
                result = "*ERROR: Sentence not found"
                if m:
                    result = sentence.text[:m.start()] + '*' + sentence.text[m.start():m.end()] + '*' + sentence.text[m.end():]  
                else:
                    result = sentence.text
                # do a cheap escape of initial quote, in case importing into Excel
                if result[0] == '"':
                    return ' ' + result
                else:
                    return result
        #return None
        return ''

class Segmenter:
    '''
    This class parses dictionaries and statistics files, and stores the resulting
    lexical entries. It then can accept any arbirtary text, parse it into tokens,
    and return the result set to the caller
    '''

    sectionBreakChar = u'\u00A7' #(Section Sign)
    sectionBreakPattern = f"{sectionBreakChar}\\s*(\\[([^\\]]*)\\])?"


    class Word:
        '''
        A general word class. Type is EITHER simplified or traditional. Stores
        multiple trad/simp/pinyin/english, and the dictionary source it was found in
        '''
    
        def __init__(self, key, character):
            self.key = key
            self.character = character  #TODO check the value
            self.stats = {}
            self.definitions = []
            self.definition = DictionaryWord(None, None)
    
        def isSectionBreak(self):
            return False

        def addStatistic(self, statisticType, value):
            #TODO make sure we're adding for the right charSet
            self.stats[statisticType] = value
            
        def getStatistic(self, statisticType):
            #TODO make sure we're adding for the right charSet
            return self.stats[statisticType] if statisticType in self.stats else '' 

        def addDictionaryWord(self, dictWord, operationType):
            #TODO make sure we're adding for the right charSet
            #TODO handle operation types. For now, just default to append
            self.definitions.append(dictWord)

#        def addDefinition(self, dictWord, operationType):
#            if operationType == 'replace':
#                self.definition.simplified = dictWord.simplified
#                self.definition.traditional = dictWord.traditional
#                self.definition.pinyin = dictWord.pinyin
#                self.definition.english = dictWord.english
            
        def mergeDefinitions(self):
            entry = []
            english = []
            
            for d in self.definitions:
                if d.entry not in entry:
                    entry.append(d.entry)
                if d.english not in english:
                    english.append(d.english)

            self.definition.entry = '; '.join(e[1] if isinstance(e, tuple) else e for e in entry)
            self.definition.english = '; '.join(english)
    
        def getDefinition(self):
            #TODO make sure we're adding for the right charSet
            return self.definition.english   # Return only the English meaning, not the full entry\tmeaning format

        def __str__(self):
            return 'Word:\n\tkey=%s,\n\tcharacter=%s\n\tstatistics={%s}, definitions=[%s]' % (self.key, self.character, self.stats, self.definitions)

    class SectionBreakWord(Word):
        def __init__(self, key, character):
            Segmenter.Word.__init__(self, key, character)

        def isSectionBreak(self):
            return True

    def __init__(self, charset, dictArray, statDict, method=SegmentationMethod.SIMPLE_LONGEST_MATCH, tokenMatchType=TokenMatchType.CJK, dictionaryOperationType=DictionaryOperationType.REPLACE, verbose=False):
        '''
        Constructor
        Note that the Segmenter knows whether to allow just CJK or CJK + A-Z,
        but the dictionary has it's own separate regexp for what is a valid character string.
        '''
        if charset not in charsets.keys():
            raise Exception("Unknown character type '%s'" % charset)
        self.charset = charset

        try:
            self.segmentationMethod = SegmentationMethod(method)
        except ValueError:
            raise Exception("Unknown segmentation method %s" % method)

        try:
            self.tokenMatchType = TokenMatchType(tokenMatchType)
        except ValueError:
            raise Exception("Unknown token match type %s" % tokenMatchType)

        self.dictionaries = dictArray
        self.statistics = statDict
        self.verbose = verbose

        try:
            self.dictionaryOperationType = DictionaryOperationType(dictionaryOperationType)
        except ValueError:
            raise Exception("Unknown dictionaryOperationType %s" % dictionaryOperationType)

        self.loadPlugins("segmenter/plugins")

        self.words = {};
        self._buildWordList();
        self._buildStatistics();

    def setStatistics(self, statDict):
        self.statistics = statDict
        self._buildStatistics();

    def _buildWordList(self):
        for dict in self.dictionaries:
            'note: words in the same dictionary get merged, while words in different dictionaries are handled depending on dictionaryOperationType'
            for dictword in dict.words:
                entry = dictword.entry
                if isinstance(entry, tuple):
                    trad, simp = entry
                    self._addWord(simp, dict.description, dictword)
                    if trad != simp:
                        self._addWord(trad, dict.description, dictword)
                else:
                    self._addWord(entry, dict.description, dictword)
        for word in self.words:
            self.getWord(word).mergeDefinitions()
        
        # if some wiseacre tries to define the section break, override it
        
        self.words[self.sectionBreakChar] = self.SectionBreakWord(self.sectionBreakChar, self.charset)

    def _buildStatistics(self):
        #TODO verify character set matches
        for statItem in self.statistics.values():
            for stat in statItem.words:
                word = self.getWord(stat.word)
                if word:
                    word.addStatistic(statItem.statisticType, stat.value)



    def getWord(self, key, autoCreate=False):
        if key not in self.words:
            if autoCreate:
                self.words[key] = self.Word(key, self.charset)
            else:
                return None

        return self.words[key]
        
        

    def _addWord(self, key, dict, word):
        '''
        The format of the words data structure is words{key} : Word
        Each word can be found in multiple dictionaries, and even in the same dictionary multiple times
        It will be up to output functions to format the data here into a compact formatted string
        '''

#        if not key in self.words:
#            self.words[key] = {}
#        
#        if not dict in self.words[key]:
#            self.words[key][dict] = []

        #self.getWord(key).[dict].append(word)
        self.getWord(key, True).addDictionaryWord(word, self.dictionaryOperationType)
        ###self.getWord(key, True).addDefinition(word, self.dictionaryOperationType)


    

    def segmentBySentence(self, text):
        """
        returns a list of Sentence for the text split by sentence markers
        """

        # For now, we will assume no hard wrapping; i.e., linefeeds can mark the end of a sentence
        #notTokens = u"(([.!?????]+)|[ \t]{2,}|\s+)"
        notTokens = "(([\.!\?\"\r\n]+)|[\s]{2,}|\u00A7\s*\[[^\]]*\])"
        "Note: the stop delimiters are group 2; add these to the original sentence if found"

        results: list[SegmenterResults.Sentence] = list()

        idx = 0
        length = len(text)

        while idx < length:
            m = re.search(notTokens, text[idx:])
            if m:
                "There is a possible sentence, and a definite stopchar"
                tmptext = ''
                if m.start(1):
                    tmptext = text[idx:idx+m.start(1)]
                    if m.end(2) > 0:
                        "ending punctuation"
                        tmptext += m.group(2)
                    results.append(SegmenterResults.Sentence(tmptext, idx))
                # todo does this repeat the last sentence?
                if len(tmptext) != m.end(1):
                    sentence_str = text[idx+len(tmptext):idx+m.end(1)]
                    is_label = sentence_str.startswith("\u00A7")
                    results.append(SegmenterResults.Sentence(sentence_str, idx+len(tmptext), is_label))
                idx += m.end(1)
            else:
                "There is no stopchar, so the remaining text is the final sentence"
                results.append(SegmenterResults.Sentence(text[idx:], idx))
                idx = length
        
        return results
    
    def segment(self, text, updatefunction=None, method=None):  #"ReversedLongestMatch"
        if method == None:
            return self.segmentMethodBuiltin(text, updatefunction)
        else:
            methods = {}
            for m in SegmentMethodPlugin.__subclasses__():
                methods[m.key] = m
            print(methods)
            cls = methods[method]
            seg = cls()
            return seg.segment(self, text, updatefunction)

    def segmentMethodBuiltin(self, text, updatefunction=None):
        if self.tokenMatchType == TokenMatchType.CJK:
            # https://stackoverflow.com/a/46265018
            tokenPattern = charsets[self.charset][0]
        else:
            #TODO add a self.messages and display it in the log tab
            #print "Unknown token match type %s" % self.tokenMatchType
            return None

        # initialize
        results = SegmenterResults(text=text)

        results.sentences = self.segmentBySentence(text)

        progress = 0
        prog100 = len(results.sentences)

        is_chinese = (self.charset == Charset.CHINESE)

        for sentence in results.sentences:

            progress += 1
            if updatefunction:
                updatefunction(progress * 100 / prog100)

            if sentence.is_whitespace:
                continue

            phrases = re.split(f"[^{tokenPattern}]+", sentence.text)

            for phrase in filterfalse(lambda p: p.isspace(), phrases):

                if is_chinese:
                    words = list(phrase)
                else:
                    words = re.split(r"\s+", phrase.strip())

                    # weak attempt to detect names; lowercase the first word unless the second word is also capitalized
                    if len(words) == 1:
                        words[0].lower()
                    elif not words[1].istitle():
                        words[0] = words[0].lower()
                        words[1] = words[1].lower()

                lex_idx = 0
                char_idx = 0
                length = len(words)
                while lex_idx < length:
                    j = (length - lex_idx) if (lex_idx + 6 > length) else 6
                    while j > 1:
                        tmpword = ''.join(words[lex_idx:lex_idx + j]) if is_chinese else ' '.join(words[lex_idx:lex_idx + j])
                        if self.getWord(tmpword):
                            results.addLexical(tmpword, sentence.start_idx + char_idx, self.getWord(tmpword), isCJK=True)
                            lex_idx += j
                            char_idx += len(tmpword)

                            j = -666  # No *&^*@# labeled loops in Python
                            continue
                        j -= 1

                    if j == 1:
                        tmpword = ''.join(words[lex_idx:lex_idx + 1]) if is_chinese else words[lex_idx]
                        results.addLexical(tmpword, sentence.start_idx + char_idx, self.getWord(tmpword), isCJK=True)
                        lex_idx += 1
                        char_idx += len(tmpword)
        return results


    def loadPlugins(self, pluginFolder):
        import sys
        loadedPlugins = []

        if not os.path.exists(pluginFolder):
            print("Plugin folder does not exist")
            return loadedPlugins
        sys.path.insert(0, pluginFolder)
        #plugins = self.enabledPlugins()
        print(os.listdir(pluginFolder))
        plugins = [i for i in os.listdir(pluginFolder) if i.endswith(".py") and i != "__init__.py"]
        plugins.sort()
        for plugin in plugins:
            try:
                nopy = plugin.replace(".py", "")
                __import__(nopy)
                #self.addMessage("Plugin %s loaded" % (plugin))
                loadedPlugins.append(nopy)
                print("Segmenter plugin %s loaded" % (plugin))
                
            except:
                #print "Error in %s" % plugin
                print(f"Plugin {plugin} failed to load: {sys.exc_info()[0]}")
                import traceback
                traceback.print_exc()

