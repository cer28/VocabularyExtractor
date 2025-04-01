'''
Copyright 2025 by Chad Redman <chad at zhtoolkit.com>
License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
'''

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import version
from tkapp.ui import prefsdialog


# non-standard menus
# ID_REFRESH_RESULTS = 101

## Constants for identifying control keys and classes of keys:
# WXK_CTRL_A = ord('A')


class EditorPanel1(tk.Text):
    def SetValue(self, text):
        self.delete("1.0", tk.END)
        self.insert(tk.END, text)
        # self.entry_text.set(text)

    def GetValue(self):
        return self.get("1.0", tk.END)
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.entry_text = tk.StringVar()
        entry = tk.Entry(self, textvariable=self.entry_text)
        self.pack(expand=True, fill="both")


class ResultPanel1(tk.Text):
    def SetValue(self, text):
        self.delete("1.0", tk.END)
        self.insert(tk.END, text)
        # self.entry_text.set(text)

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.entry_text = tk.StringVar()
        entry = tk.Entry(self, textvariable=self.entry_text)
        self.pack(expand=True, fill="both")


class SummaryPanel1(tk.Text):
    def SetValue(self, text):
        self.delete("1.0", tk.END)
        self.insert(tk.END, text)
        # self.entry_text.set(text)

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.entry_text = tk.StringVar()
        entry = tk.Entry(self, textvariable=self.entry_text)
        self.pack(expand=True, fill="both")


class MessagePanel1(tk.Text):
    def SetValue(self, text):
        self.delete("1.0", tk.END)
        self.insert(tk.END, text)
        # self.entry_text.set(text)

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.entry_text = tk.StringVar()
        entry = tk.Entry(self, textvariable=self.entry_text)
        self.pack(expand=True, fill="both")


class TokenPanel1(tk.Text):
    def SetValue(self, text):
        self.delete("1.0", tk.END)
        self.insert(tk.END, text)
        # self.entry_text.set(text)

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.entry_text = tk.StringVar()
        entry = tk.Entry(self, textvariable=self.entry_text)
        self.pack(expand=True, fill="both")


class NoteBook1(ttk.Notebook):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.pack(expand=True, fill="both")

        # self.pack(expand=True, fill="both")

        # wx.Notebook.__init__(self, parent, id, size=(21,21), style=
        #                      wx.BK_DEFAULT
        #                      wx.BK_TOP
        #                      wx.BK_BOTTOM
        #                      wx.BK_LEFT
        #                      wx.BK_RIGHT
        #                       | wx.NB_MULTILINE
        #                      )

        self.editorPanel = EditorPanel1(self)
        self.add(self.editorPanel, text="Source")

        self.summaryPanel = SummaryPanel1(self)
        self.add(self.summaryPanel, text="Summary")

        self.resultPanel = ResultPanel1(self)
        self.add(self.resultPanel, text="Results")

        self.tokenPanel = TokenPanel1(self)
        self.add(self.tokenPanel, text="Segmented")

        self.messagePanel = ResultPanel1(self)
        self.add(self.messagePanel, text="Messages")
        self.pack(expand=True, fill="both")


class MainWindow(ttk.Frame):
    segHelper = None

    def __init__(self, root, *args, **kwargs):
        super().__init__(root, *args, **kwargs)

        self.root_window = root

        menu_bar = tk.Menu(root)
        file_menu = tk.Menu(menu_bar, tearoff=0)
        help_menu = tk.Menu(menu_bar, tearoff=0)

        file_menu.add_command(label="Open", accelerator="O", command=self.OnOpen)  # 'Open a file'
        file_menu.add_command(label="Analyze", accelerator="A", command=self.OnRefreshResults)  # 'Analyze Results'
        file_menu.add_command(label="Preferences", accelerator="R",
                              command=self.OnPreferences)  # 'Configure application settings'
        file_menu.add_command(label="Exit", accelerator="X", command=self.OnExit)  # 'Terminate the program'

        help_menu.add_command(label="Documentation", accelerator="D",
                              command=self.OnDocumentation)  # 'Launches a web browser to view online instructions'
        help_menu.add_command(label="About", accelerator="A", command=self.OnAbout)  # 'Information about this program'

        menu_bar.add_cascade(label="File", accelerator="F", menu=file_menu)
        menu_bar.add_cascade(label="Help", accelerator="H", menu=help_menu)

        root.config(menu=menu_bar)

        self.notebook = NoteBook1(self)

        self.pack(expand=True, fill="both")

    def OnRefreshResults(self):
        self.segHelper.set_text(self.notebook.editorPanel.GetValue())

        progress_var = tk.IntVar()
        progress_bar = ttk.Progressbar(self, variable=progress_var, maximum=100)
        progress_bar.pack(pady=10)

        self.segHelper.summarize_results(updatefunction=progress_var.set)
        progress_bar.destroy()

        # st = wx.StaticText(self.notebook.resultPanel, -1, self.segHelper.summary, (10, 10))
        self.notebook.summaryPanel.SetValue(self.segHelper.summary)
        self.notebook.resultPanel.SetValue(self.segHelper.results)
        self.notebook.tokenPanel.SetValue(self.segHelper.tokens)
        self.notebook.messagePanel.SetValue(self.segHelper.get_messages())

    def OnAbout(self):
        messagebox.showinfo(
            "About Application",
            f"Vietnamese Word Extractor\n"
            f"Version: {version.APP_VERSION}\n"
            "Author: Chad Redman\n"
            f"Copyright: {version.COPYRIGHT_DATE}\n\n"
            "This is a tool to extract vocabulary from Vietnamese text, summarizing "
            "the unique words with word count, English definition, and other useful "
            "statistics.\n\n"
            "Website: http://www.zhtoolkit.com/apps/Vietnamese_Word_Extractor\n\n"
            "This program is licensed under the terms of the "
            "GPL v.3.0; see http://www.gnu.org/licenses/gpl-3.0.html for details.",
        )

    def OnDocumentation(self):
        import webbrowser
        webbrowser.open("http://www.zhtoolkit.com/apps/Chinese Word Extractor/help.html")

    def OnOpen(self):
        """ Open a file """

        dirname = self.config.currentdir

        # self.withdraw()  # Hide the main window

        file_path = filedialog.askopenfilename(
            title="Choose one or more files",
            filetypes=(("Text files", "*.txt"), ("All files", "*.*")),
            initialdir=dirname
        )

        if file_path:
            print("File selected:", file_path)

            self.notebook.editorPanel.SetValue(self.segHelper.read_files([file_path]))

            self.notebook.messagePanel.SetValue(self.segHelper.get_messages())

            self.config.currentdir = os.path.dirname(file_path)
            self.config.save()

    def OnExit(self):
        self.config.save()
        self.destroy()

    def OnPreferences(self):
        d = prefsdialog.PrefsDialog(self.root_window, self.config)
        self.root_window.wait_window(d)

        if self.config.dirtyDicts:
            progress_var = tk.IntVar()
            progress_bar = ttk.Progressbar(self, name="Loading Dictionary", variable=progress_var, maximum=100)
            progress_bar.pack(pady=10)

            self.segHelper.load_data(updatefunction=progress_var.set)
            progress_bar.destroy()

            # self.segHelper.LoadData(self.config, updatefunction=wx.ProgressDialog(title="Progress", message="Loading Dictionary", style=wx.PD_AUTO_HIDE|wx.PD_SMOOTH).Update)
            self.config.dirtyDicts = False

        if self.config.dirtyFilters:
            self.segHelper.load_known_words()
            # self.segHelper.LoadData(self.config, updatefunction=wx.ProgressDialog(title="Progress", message="Loading Dictionary", style=wx.PD_AUTO_HIDE|wx.PD_SMOOTH).Update)
            self.config.dirtyFilters = False

        if self.config.dirtyExtraCols:
            self.segHelper.load_extra_columns()
            self.config.dirtyExtraCols = False

        self.notebook.messagePanel.SetValue(self.segHelper.get_messages())
