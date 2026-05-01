'''
Copyright 2025 by Chad Redman <chad at zhtoolkit.com>
License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
'''

import tkinter as tk
from tkinter import *
from tkinter import ttk

try:
    WindowsError
except NameError:
    WindowsError = OSError

config = None


def run(segHelper):
    import os
    import sys
    import argparse
    from .config import Config
    from segmenter.enums import Charset

    parser = argparse.ArgumentParser(description='Vocabulary Extractor')
    parser.add_argument("-c", "--config", help="path to config file", required=False,
                        default=os.path.expanduser("~/.Vocabulary Extractor/config.db"))
    parser.add_argument("--headless", action="store_true",
                        help="Run without UI, output tab-delimited results; requires --inputfile")
    parser.add_argument("-i", "--inputfile", help="Path to input file", required=False)
    parser.add_argument("-o", "--outputfile",
                        help="Output file for results (use '-' for stdout). Defaults to stdout in headless mode.",
                        required=False)
    parser.add_argument("--appdir",
                        help="Base directory of the application. It must contain subdirectories dict, data, and filter",
                        default=segHelper.runningDir, required=False)
    parser.add_argument("--dict", dest="dict", metavar="PATH", action="append",
                        help="Path to a dictionary file. Can be used multiple times.")
    parser.add_argument("--charset", choices=[c.value for c in Charset],
                        help=f"Character set to use for segmentation. Valid values: {', '.join(c.value for c in Charset)}")
    parser.add_argument("--filter", dest="filter", metavar="PATH", action="append",
                        help="Path to a filter file. Can be used multiple times.")
    parser.add_argument("--extracolumn", metavar="PATH", action="append",
                        help="Path to an extra column data file. Can be used multiple times.")

    opts = parser.parse_args()

    if opts.headless:
        if not opts.inputfile:
            parser.error("--headless requires --inputfile")
        _run_headless(segHelper, opts, Config, Charset)
    else:
        _run_ui(segHelper, opts, Config, Charset)


def _build_config(segHelper, opts, Config, Charset):
    import os
    config = Config(os.path.abspath(opts.config))
    config.appDir = opts.appdir

    if opts.dict:
        config.dictionaries = [os.path.abspath(p) for p in opts.dict]
        config.dirtyDicts = True
    if opts.charset:
        config.charset = Charset(opts.charset)
    if opts.filter:
        config.filters = [os.path.abspath(p) for p in opts.filter]
        config.dirtyFilters = True
    if opts.extracolumn:
        config.extracolumns = [os.path.abspath(p) for p in opts.extracolumn]
        config.dirtyExtraCols = True

    return config


def _run_headless(segHelper, opts, Config, Charset):
    import sys
    import codecs

    config = _build_config(segHelper, opts, Config, Charset)
    segHelper.config = config
    segHelper.load_data()
    segHelper.load_known_words()
    segHelper.load_extra_columns()

    segHelper.read_files([opts.inputfile])
    segHelper.summarize_results()

    output = segHelper.results

    if opts.outputfile and opts.outputfile != '-':
        try:
            with codecs.open(opts.outputfile, encoding='utf-8', mode='w') as f:
                f.write(output)
        except (OSError, IOError) as e:
            print(f"Error: Failed to write to output file {opts.outputfile}: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        sys.stdout.write(output)

    sys.exit(0)


def _run_ui(segHelper, opts, Config, Charset):
    import os
    import sys
    from .ui import main

    config = _build_config(segHelper, opts, Config, Charset)
    segHelper.config = config

    app = Tk()
    app.title("Vocabulary Extractor")

    loading_dialog = tk.Toplevel(app)
    loading_dialog.title("Loading")
    loading_dialog.geometry("300x100")
    loading_dialog.transient(app)
    loading_dialog.grab_set()

    tk.Label(loading_dialog, text="Loading dictionaries...").pack(pady=10)
    progress_var = tk.IntVar()
    progress_bar = ttk.Progressbar(loading_dialog, variable=progress_var, maximum=100)
    progress_bar.pack(pady=10, padx=20, fill='x')

    def update_progress(value):
        progress_var.set(value)
        loading_dialog.update_idletasks()

    segHelper.load_data(
        updatefunction=update_progress,
        error_callback=lambda msg: tk.messagebox.showerror("Dictionary Error", msg),
    )
    loading_dialog.destroy()

    segHelper.load_known_words()
    segHelper.load_extra_columns()

    frame = main.MainWindow(app, height=750, width=500)
    frame.segHelper = segHelper
    frame.config = config

    if opts.inputfile:
        frame.notebook.editorPanel.SetValue(segHelper.read_files([opts.inputfile]))

    if opts.outputfile:
        segHelper.summarize_results()
        if opts.outputfile == "-":
            sys.stdout.write(segHelper.results)
        else:
            import codecs
            try:
                with codecs.open(opts.outputfile, encoding='utf-8', mode='w') as f:
                    f.write(segHelper.summary + "\n\n" + segHelper.results)
            except (WindowsError, OSError, IOError) as e:
                print(f"Warning: Failed to write to output file {opts.outputfile}: {e}")
        sys.exit()

    frame.notebook.messagePanel.SetValue(frame.segHelper.get_messages())
    app.mainloop()
