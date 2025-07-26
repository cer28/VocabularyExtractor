'''
Copyright 2011 by Chad Redman <chad at zhtoolkit.com>
License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
'''
import json
import os
import errno

class Config(dict):

    def __init__(self, configFileFullPath):
        self.filters = list()
        self.extracolumns = list()
        self.currentdir = "samples"
        self.dictionaries = ['vnedict.txt.u8']
        self.charset = 'Vietnamese'

        # TODO platform-independent
        #self.configFileFullPath = os.path.join(self.configPath, self.configFileName)
        self.configFileFullPath = configFileFullPath

#        self.makeWorkingDir()
        self.load()

    def __setattr__(self, key, value):
        """
        This is so that json.load set the attributes not string keys of the dict
        """
        self[key] = value

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(f"'Config' object has no attribute '{key}'")

    def setDefaults(self):
        fields = {
            #'dicts': {"cedict_ts.u8" : "cedict"},
            'filters': [],
            'extracolumns': [],
            'currentdir': "samples",
            'dictionaries': ['vnedict.txt.u8'],
            'charset': 'English',
            'dirtyDicts': False,
            'dirtyFilters': False,
            'dirtyExtraCols': False,
            }

        for (k, v) in fields.items():
            try:
                if self[k] is None:
                    self[k] = v
            except KeyError:
                self[k] = v

    #    def makeWorkingDir(self):
#        base = self.configPath
#        for x in (base,
#                  os.path.join(base, "plugins"),
#                  os.path.join(base, "backups")):
#            try:
#                os.mkdir(x)
#            except:
#                pass


    def _makedir(self, dirpath):
        try:            
            #os.makedirs(dirpath)
            #os.mkdir(dirpath, 0700)
            os.mkdir(dirpath)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise
        
    def save(self):
        # create directory if it doesn't exist
        
        configDir = os.path.dirname(self.configFileFullPath)
        try:            
            self._makedir(configDir)
            # write to a temp file
            from tempfile import mkstemp
            (fd, tmpname) = mkstemp(dir=configDir)
            tmpfile = os.fdopen(fd, 'w')
            # Save both instance attributes and dictionary data
            save_data = dict(self)  # Get dictionary data
            save_data.update(self.__dict__)  # Add instance attributes
            json.dump(save_data, tmpfile)
            tmpfile.close()
            # the write was successful, delete config file (if exists) and rename
            if os.path.isfile(self.configFileFullPath):
                os.unlink(self.configFileFullPath)
            os.rename(tmpname, self.configFileFullPath)
            return (True, None)
        except Exception as e:
            #print u"Error saving preferences file %s (%s)" % (self.configFileFullPath, e)
            return (False, e)


    def load(self):
        if os.path.isfile(self.configFileFullPath):
            try:
                f = open(self.configFileFullPath)
                self.update(json.load(f))
            except (IOError, EOFError):
                # Corrupted format
                #print u"DEBUG: config.load(): unable to read file %s: (%s)" % (self.configFileFullPath, ex)
                #print u"DEBUG:   Using the defaults instead"
                pass

        self.setDefaults()

    def setDicts(self, dict_ar):
        # TODO move setting of dirtyDict here instead of caller
        self["dictionaries"] = dict_ar

    def setFilters(self, filter_ar):
        self["filters"] = filter_ar

    def setExtraColumns(self, extracols_ar):
        self["extracolumns"] = extracols_ar
