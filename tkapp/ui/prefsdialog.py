'''
Copyright 2011 by Chad Redman <chad at zhtoolkit.com>
License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
'''

import os
import pathlib
import tkinter
import tkinter.dialog
from tkinter import StringVar, Listbox, PanedWindow, Frame, Label, Radiobutton

import segmenter


class PrefsDialog(tkinter.Toplevel):

    def __init__(self, root, config, *args, **kwargs):
        super().__init__(root, *args, **kwargs)

        self.grab_set()
        self.focus_set()

        self.title("Preferences")
        self.config = config

        charsets = segmenter.charset.charsets.keys()
        current_charset = config.charset
        if current_charset not in charsets:
            assert ("English" in charsets)
            current_charset = "English"


        main_frame = Frame(self, padx=20, pady=20, height=500, width=500)
        main_frame.pack()

        # dictionary ListBox
        dict_panel = tkinter.LabelFrame(main_frame)
        dict_panel.pack()
        dict_panel.title = "Dictionaries"

        # self.m_staticText3 = tkinter.Label(self.dict_panel, text="Dictionaries")

        dict_listbox = Listbox(dict_panel, height=4, selectmode='multiple')
        dict_options: list = self.get_file_items(os.path.join(self.config.appDir, 'dict'))
        for item in dict_options:
            dict_listbox.insert(dict_options.index(item), item)

        dict_listbox.pack(padx=10, pady=10)

        # pre-select current options
        for idx, val in enumerate(dict_options):
            if val in self.config.dictionaries:
                dict_listbox.selection_set(idx)

        # Filtered Words file ListBox
        filter_panel = tkinter.LabelFrame(main_frame)
        filter_panel.pack()
        filter_panel.title = "Filtered word lists"

        # self.m_staticText3 = tkinter.Label(self.filter_panel, text="Dictionaries")

        filters_listbox = Listbox(filter_panel, height=4, selectmode='multiple')
        filters_listbox.pack(padx=10, pady=10)
        filter_options: list = self.get_file_items(os.path.join(self.config.appDir, 'filter'))
        for item in filter_options:
            filters_listbox.insert(filter_options.index(item), item)

        # pre-select current options
        for idx, val in enumerate(filter_options):
            if val in self.config.filters:
                filters_listbox.selection_set(idx)

        # Extra Column ListBox
        extra_col_panel = Frame(main_frame)
        extra_col_panel.pack()
        extra_col_label = Label(extra_col_panel, text="Extra Column(s)")

        extracol_listbox = Listbox(extra_col_panel, height=4, selectmode='multiple')
        extracol_listbox.pack()

        extracol_options: list = self.get_file_items(os.path.join(self.config.appDir, 'data', current_charset))
        for item in extracol_options:
            extracol_listbox.insert(extracol_options.index(item), item)

        # pre-select current options
        for idx, val in enumerate(extracol_options):
            if val in self.config.extracolumns:
                extracol_listbox.selection_set(idx)

        # Character set RadioBox
        charset_panel = Frame(main_frame)
        charset_panel.pack()

        charset_label = Label(charset_panel, text="Character set identifying words")
        charset_label.pack()

        self.selected_charset_svar = tkinter.StringVar()
        self.selected_charset_svar.set(current_charset)

        for idx, val in enumerate(charsets):
            radio = Radiobutton(charset_panel,
                                text=val, variable=self.selected_charset_svar, value=val)
            radio.pack()

        button_frame = Frame(main_frame)
        button_frame.pack()

        ok_button = tkinter.Button(button_frame, text="OK", command=self.OnOk)
        ok_button.pack()

        cancel_button = tkinter.Button(button_frame, text="Cancel", command=self.destroy)
        cancel_button.pack()

        self.dict_options = dict_options
        self.dict_listbox = dict_listbox

        self.filter_options = filter_options
        self.filters_listbox = filters_listbox

        self.extracol_options = extracol_options
        self.extracol_listbox = extracol_listbox



    def _RefreshExtraColumnListBox(self, charset):
        extraColList = self.get_file_items(os.path.join(self.config.appDir, 'data', charset))
        self.extracol_listbox.SetItems(extraColList)

    def OnOk(self):
        # Check for dictionary changes and set reload if necessary
        dictSelected = []
        dictItems = self.dict_listbox.curselection()
        for idx in dictItems:
            dictSelected.append(self.dict_options[idx])

        if self.config.dictionaries != dictSelected:
            # need to reload dictionaries. This should be in an subscribed event
            self.config.dirtyDicts = True
            self.config.setDicts(dictSelected)

        # Check for filter file changes and set reload if necessary
        filterSelected = []
        filterItems = self.filters_listbox.curselection()
        for idx in filterItems:
            filterSelected.append(self.filter_options[idx])

        if self.config.filters != filterSelected:
            # need to reload dictionaries. This should be in an subscribed event
            self.config.dirtyFilters = True
            self.config.setFilters(filterSelected)

        # Check for extra column changes and set reload if necessary
        extracolSelected = []
        extracolItems = self.extracol_listbox.curselection()
        for idx in extracolItems:
            extracolSelected.append(self.extracol_options[idx])

        if self.config.extracolumns != extracolSelected:
            # need to reload dictionaries. This should be in an subscribed event
            self.config.dirtyExtraCols = True
            self.config.setExtraColumns(extracolSelected)

        newcharset = self.selected_charset_svar.get()
        if self.config.charset != newcharset:
            self.config.charset = newcharset
            # self.config.dirtyDicts = True
            # self.config.dirtyExtraCols = True  # The data needs to be reloaded from the new files, even if the filenames have not changed
            # self.config.setExtraColumns(extracolSelected)

        (saveStatus, ex) = self.config.save()
        if not saveStatus:
            # print "Error in prefsDialog.OnOk calling config.save: %s" % ex
            dlg = tkinter.messagebox(self, text='Unable to save configuration file. Error was (%s)' % ex)
            # , 'Error', wx.OK | wx.ICON_EXCLAMATION
            dlg.ShowModal()
            dlg.Destroy()

        self.destroy()

    def get_file_items(self, directory):
        import stat

        choices = []
        filenames = []

        if not pathlib.Path(directory).is_dir():
            """
            Directory does not exist; maybe no subdirectory for the charset 
            """
            print(f"Unable to read files in directory {directory} (directory not found)")
            return choices
        try:
            filenames = os.listdir(directory)
        except Exception as e:
            print(f"Error in get_file_items: {e}")
            dlg = tkinter.messagebox(self, f"Unable to read files in directory {directory} ({e})")
            dlg.ShowModal()
            dlg.Destroy()
            return choices

        for filename in filenames:
            if filename[0] != "_":
                try:
                    st = os.stat(os.path.join(directory, filename))
                except os.error:
                    continue
                if stat.S_ISREG(st.st_mode):
                    choices.append(filename)
        return choices
