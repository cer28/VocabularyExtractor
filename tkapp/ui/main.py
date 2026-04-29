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

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.pack(expand=True, fill="both")


class ResultGridPanel(ttk.Frame):
    _COL_WIDTHS = {
        'Word num.': 70,
        'Running total words': 130,
        'text': 100,
        'num. occur.': 90,
        '1st occur.': 80,
        'simplified': 80,
        'traditional': 80,
        'reading': 130,
        'meaning': 220,
        'sample sentence': 320,
    }

    def SetValue(self, text):
        self.tree.delete(*self.tree.get_children())
        self._sort_col = None
        self._sort_reverse = False
        if not text or not text.strip():
            return

        lines = text.split('\n')
        headers = lines[0].rstrip('\n').split('\t')

        self.tree['columns'] = headers
        self.tree['show'] = 'headings'
        for col in headers:
            self.tree.heading(col, text=col, command=lambda c=col: self._sort_column(c))
            w = self._COL_WIDTHS.get(col, 100)
            self.tree.column(col, width=w, minwidth=40, stretch=False)

        for line in lines[1:]:
            if not line.strip():
                continue
            values = line.rstrip('\n').split('\t')
            while len(values) < len(headers):
                values.append('')
            self.tree.insert('', tk.END, values=values[:len(headers)])

    def _sort_column(self, col):
        if self._sort_col == col:
            self._sort_reverse = not self._sort_reverse
        else:
            self._sort_col = col
            self._sort_reverse = False

        items = [(self.tree.set(item, col), item) for item in self.tree.get_children('')]
        try:
            items.sort(key=lambda x: float(x[0]) if x[0] != '' else float('-inf'), reverse=self._sort_reverse)
        except ValueError:
            items.sort(key=lambda x: x[0].lower(), reverse=self._sort_reverse)

        for index, (_, item) in enumerate(items):
            self.tree.move(item, '', index)

        for c in self.tree['columns']:
            self.tree.heading(c, text=c)
        arrow = ' ▼' if self._sort_reverse else ' ▲'
        self.tree.heading(col, text=col + arrow)

    def _select_all(self, event=None):
        self.tree.selection_set(self.tree.get_children())
        return 'break'

    def _copy_selection(self, event=None):
        selected = set(self.tree.selection())
        if not selected:
            return 'break'
        cols = self.tree['columns']
        header = '\t'.join(cols)
        rows = [
            '\t'.join(str(v) for v in self.tree.item(item)['values'])
            for item in self.tree.get_children()
            if item in selected
        ]
        self.tree.clipboard_clear()
        self.tree.clipboard_append(header + '\n' + '\n'.join(rows))
        return 'break'

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self._sort_col = None
        self._sort_reverse = False
        self.tree = ttk.Treeview(self, show='headings', selectmode='extended')

        vsb = ttk.Scrollbar(self, orient='vertical', command=self.tree.yview)
        hsb = ttk.Scrollbar(self, orient='horizontal', command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')

        self.tree.bind('<Control-a>', self._select_all)
        self.tree.bind('<Control-c>', self._copy_selection)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_propagate(False)
        self.pack(expand=True, fill='both')


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

        self.resultPanel = ResultGridPanel(self)
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

        # Create progress dialog
        progress_dialog = tk.Toplevel(self.root_window)
        progress_dialog.title("Analyzing Text")
        progress_dialog.geometry("300x100")
        progress_dialog.transient(self.root_window)
        progress_dialog.grab_set()

        tk.Label(progress_dialog, text="Analyzing text...").pack(pady=10)
        progress_var = tk.IntVar()
        progress_bar = ttk.Progressbar(progress_dialog, variable=progress_var, maximum=100)
        progress_bar.pack(pady=10, padx=20, fill='x')

        def update_progress(value):
            progress_var.set(value)
            progress_dialog.update_idletasks()

        self.segHelper.summarize_results(updatefunction=update_progress)
        progress_dialog.destroy()

        # st = wx.StaticText(self.notebook.resultPanel, -1, self.segHelper.summary, (10, 10))
        self.notebook.summaryPanel.SetValue(self.segHelper.summary)
        self.notebook.resultPanel.SetValue(self.segHelper.results)
        self.notebook.tokenPanel.SetValue(self.segHelper.tokens)
        self.notebook.messagePanel.SetValue(self.segHelper.get_messages())

    def OnAbout(self):
        messagebox.showinfo(
            "About Application",
            f"Vocabulary Extractor\n"
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
        webbrowser.open("http://www.zhtoolkit.com/apps/Vocabulary Extractor/help.html")

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
            # Create progress dialog
            progress_dialog = tk.Toplevel(self.root_window)
            progress_dialog.title("Loading Dictionary")
            progress_dialog.geometry("300x100")
            progress_dialog.transient(self.root_window)
            progress_dialog.grab_set()

            tk.Label(progress_dialog, text="Loading dictionary...").pack(pady=10)
            progress_var = tk.IntVar()
            progress_bar = ttk.Progressbar(progress_dialog, variable=progress_var, maximum=100)
            progress_bar.pack(pady=10, padx=20, fill='x')

            def update_progress(value):
                progress_var.set(value)
                progress_dialog.update_idletasks()

            self.segHelper.load_data(
                updatefunction=update_progress,
                error_callback=lambda msg: messagebox.showerror("Dictionary Error", msg),
            )
            progress_dialog.destroy()

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
