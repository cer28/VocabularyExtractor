'''
Copyright 2026 by Chad Redman <chad at zhtoolkit.com>
License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
'''

import tkinter as tk
from tkinter import ttk
import re
import webbrowser

_URL_RE = re.compile(r'https?://\S+')


class AboutDialog(tk.Toplevel):
    def __init__(self, parent, title, text):
        super().__init__(parent)
        self.title(title)
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        text_widget = tk.Text(self, wrap='word', width=55, height=14,
                              relief='flat', cursor='arrow',
                              padx=12, pady=12, font=('Times', 11))
        text_widget.tag_configure('link', foreground='blue', underline=True)
        text_widget.tag_bind('link', '<Enter>', lambda e: text_widget.configure(cursor='hand2'))
        text_widget.tag_bind('link', '<Leave>', lambda e: text_widget.configure(cursor='arrow'))

        last = 0
        for i, m in enumerate(_URL_RE.finditer(text)):
            if m.start() > last:
                text_widget.insert(tk.END, text[last:m.start()])
            url_tag = f'url{i}'
            text_widget.tag_bind(url_tag, '<Button-1>',
                                 lambda e, url=m.group(): webbrowser.open(url))
            text_widget.insert(tk.END, m.group(), ('link', url_tag))
            last = m.end()
        if last < len(text):
            text_widget.insert(tk.END, text[last:])

        text_widget.configure(state='disabled')
        text_widget.pack(padx=10, pady=(10, 0), fill='both', expand=True)

        ttk.Button(self, text="OK", command=self.destroy).pack(pady=10)
