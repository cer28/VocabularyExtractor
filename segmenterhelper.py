"""
Copyright 2011 by Chad Redman <chad at zhtoolkit.com>
License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
"""

import segmenter
import os
from segmenter.enums import Charset, StatisticsFormat


# The data here gets refreshed when called
class SegmenterHelper:
    # from segmenter import Dictionary, Statistics, Segmenter

    def add_message(self, text):
        try:
            self.messages.append(text)
        except TypeError:
            try:
                self.messages.append(text)
            except:
                print(f"Failed to log error message for {text}")
                self.messages.append("Failed to log error message! Run in console to see details")

    def get_messages(self):
        return "\n".join(self.messages)

    def set_text(self, text):
        self.text = text

    def __init__(self, runningDir):
        self.seg = None
        self.tokens = None
        self.text = ''
        self.results = ''
        self.summary = ''
        self.messages = []
        self.runningDir = runningDir
        self.dicts = []
        self.filterwords = []
        self.config = None
        self.stats = {}  # a mapping between filenames and data list
        self.statFiles = {}  # a mapping between filenames and heading

    def load_data(self, updatefunction=None, error_callback=None):
        """
        Called when first starting the program, or when preference change sets dirtyDicts
        """

        config = self.config
        # if config.charset:
        #     charset = config.charset
        # else:
        #     charset = 'simplified'

        self.dicts = []

        for dictname in config.dictionaries:
            self.add_message("Loading dictionary %s ..." % dictname)
            dictFile = os.path.join(config.appDir, 'dict', dictname)
            try:
                fmt = segmenter.Dictionary._detect_format(dictFile)
            except Exception as e:
                msg = f"**Error: {e}"
                self.add_message(msg)
                if error_callback:
                    error_callback(msg)
                continue
            try:
                dict = segmenter.Dictionary(dictFile, format=fmt, verbose=True, updatefunction=updatefunction)
            except Exception as e:
                msg = f"**Error: {e}"
                self.add_message(msg)
                if error_callback:
                    error_callback(msg)
                continue

            if dict.messages != None:
                for elem in dict.messages:
                    self.add_message(elem)
                # add a blank line

            self.add_message(f"Loaded dictionary {dictname}, {dict.getWordCount()} words")
            self.dicts.append(dict)

        self.seg = segmenter.Segmenter(config.charset, self.dicts, self.stats)
        self.add_message("")

    def load_known_words(self, updatefunction=None):
        self.filterwords = []
        for filtername in self.config.filters:
            self.load_filter_file(os.path.join(self.config.appDir, 'filter', filtername))
            self.add_message(f"Loaded filtered word file {filtername}")
        self.add_message("")

    def load_extra_columns(self):
        charset = self.config.charset
        self.stats = {}
        for statfile in self.config.extracolumns:
            self.load_statistics_file(self.config, statfile, charset)

        self.seg.setStatistics(self.stats)

    def load_filter_file(self, filename):
        import re
        try:
            fh = open(filename, 'r', encoding='utf-8')  # throws IOError
        except Exception as ex:
            self.add_message(f"**Error: Failed to load filter file {filename}: ({ex})")
            return 0

        lineno = 0
        try:
            for line in fh.read().splitlines():
                lineno += 1
                if not re.match(r'\s*#', line):
                    m = re.match('[^ \t]+', line)
                    if m:
                        self.filterwords.append(m.group(0))
        finally:
            fh.close()

        return lineno

    def load_statistics_file(self, config, filename, charset):
        fullpath = os.path.join(config.appDir, 'data', filename)
        print(f"DEBUG: Attempting to load statistics file: {fullpath}")
        print(f"DEBUG: charset={charset}, filename={filename}")
        try:
            stat = segmenter.Statistics(fullpath, StatisticsFormat.TAB)
            self.stats[filename] = stat
            self.statFiles[filename] = stat.statisticType
            print(f"DEBUG: Successfully loaded {filename} into statFiles")
            self.add_message(f"Loaded extra column data file {filename}")
        except IOError as e:
            print(f"DEBUG: IOError loading {filename}: {e}")
            self.add_message(f"**Failed to load data file {fullpath}: {e}")
        except Exception as e:
            print(f"DEBUG: Other exception loading {filename}: {e}")
            self.add_message(f"**Failed to load data file {fullpath}: {e}")

    def read_files(self, filelist):
        # Autodetect the encoding, so that the user doesn't need to worry about utf8 vs. utf16, little endian, etc
        # uses the chardet module from:
        # http://chardet.feedparser.org/
        # Universal Encoding Detector: character encoding auto-detection in Python
        import chardet

        text = ''
        filelist.sort()
        for f in filelist:
            try:
                # text += '%s [%s]\n%s' % (segmenter.Segmenter.sectionBreakChar, f, unicode(open(f, 'r').read(), encoding))
                rawdata = open(f, 'rb').read(-1)

                detector = chardet.detect(rawdata)
                self.add_message("File %s loaded: %i bytes" % (f.encode('utf-8'), len(rawdata)))
                self.add_message("Detected encoding: %s\n" % detector)
                # text += '%s [%s]\n%s' % (segmenter.Segmenter.sectionBreakChar, f, rawdata.decode(detector["encoding"]))

                if len(filelist) > 1:
                    text += f'{segmenter.Segmenter.sectionBreakChar} [{f}]\n'

                text += rawdata.decode(detector["encoding"])
            except UnicodeDecodeError as e:
                self.add_message(
                    "%s error while loading file %s: failed to decode from encoding '%s'. Filesize was %d" % (
                        type(e), f, detector["encoding"], len(rawdata)))

        self.text = text
        return self.text

    def summarize_results(self, updatefunction=None):
        self.summary = ''
        self.results = ''

        self.add_message("Analyzing text ...")

        self.summary += "Length of text = %d" % len(self.text) + "\n"
        results = self.seg.segment(self.text, updatefunction, None)  # "ReversedLongestMatch"
        self.summary += "\n\nResults.tokens (%d)" % len(results.tokens) + "\n"

        self.tokens = ' | '.join(t.text for t in results.tokens)

        is_chinese = (self.config.charset == Charset.CHINESE)
        self.results += '\t'.join(
            [
                "Word num.",
                "Running total words",
                "text",
                "num. occur.",
                "1st occur."
            ] +
            [self.statFiles[filename] for filename in self.config.extracolumns if filename in self.statFiles] +
            (["simplified", "traditional"] if is_chinese else []) +
            [
                "reading",
                "meaning",
                "sample sentence"
            ]) + "\n"

        wordctGross = 0
        wordctNet = 0
        wordUniqueGross = 0
        wordUniqueNet = 0

        for lex in results.lexList:
            if not lex.text or not lex.text.strip():
                continue
            word = results.words[lex.text]
            if word is None:
                context = '' if is_chinese else self._get_unknown_context(lex.text, lex.indexes[0])
                self.results += '\t'.join(
                    [
                        '',
                        '',
                        lex.text,
                        str(len(lex.indexes)),
                        str(lex.indexes[0])
                    ] +
                    ['' for y in self.config.extracolumns] +
                    (['', ''] if is_chinese else []) +
                    [
                        'Unknown',
                        '',
                        context
                    ]
                ) + "\n"
            elif word.isSectionBreak():
                self.results += f"-------------------\t{lex.text}\n"
            else:
                wordctGross += len(lex.indexes)
                wordUniqueGross += 1
                if lex.text not in self.filterwords:
                    wordUniqueNet += 1
                    wordctNet += len(lex.indexes)
                    self.results += '\t'.join(
                        [
                            str(wordUniqueNet),
                            str(wordctNet),
                            lex.text,
                            str(len(lex.indexes)),
                            str(lex.indexes[0])
                        ] +
                        [word.getStatistic(self.statFiles[y]) for y in self.config.extracolumns if y in self.statFiles] +
                        ([word.getSimplified() or '', word.getTraditional() or ''] if is_chinese else []) +
                        [
                            word.getReading() or word.key,
                            word.getDefinition(),
                            results.findFirstSentence(lex)
                        ]

                    ) + "\n"

        self.summary += "\n\nTotal count of words in text: %d" % wordctGross + "\n"
        self.summary += "Total count of filtered words: %d" % wordctNet + "\n"
        self.summary += "\nTotal count of unique words: %d" % wordUniqueGross + "\n"
        self.summary += "Total count of unique filtered words: %d" % wordUniqueNet + "\n"

    def _get_unknown_context(self, word_text, position):
        before = self.text[:position]
        after = self.text[position + len(word_text):]

        before_words = before.split()
        if before_words:
            before_str = ' '.join(before_words[-10:])
        else:
            before_str = before[-50:]

        after_words = after.split()
        if after_words:
            after_str = ' '.join(after_words[:10])
        else:
            after_str = after[:50]

        return f"{before_str} *{word_text}* {after_str}".strip()

    def get_file_items(self, directory):
        import stat

        choices = []
        for filename in os.listdir(directory):
            try:
                st = os.stat(os.path.join(directory, filename))
            except os.error:
                continue
            if stat.S_ISREG(st.st_mode):
                choices.append(filename)
        return choices
