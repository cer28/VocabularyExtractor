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

    # import config
    from .ui import main
    from .config import Config

    # parse args
    parser = argparse.ArgumentParser(description='A sample program with options')

    parser.add_argument("-c", "--config", help="path to config file", required=False,
                        default=os.path.expanduser("~/.Vocabulary Extractor/config.db"))
    parser.add_argument("-i", "--inputfile", help="Path to input file", required=False)
    parser.add_argument("-o", "--outputfile",
                        help="When using an inputfile parameter, print summary output to a file (use '-' as filename to print to the console), and do not show an application window",
                        required=False)
    parser.add_argument("--appdir",
                        help="Base directory of the application. It must contain subdirectories dict, data, and filter",
                        default=segHelper.runningDir, required=False)

    opts = parser.parse_args()


    # Notes on icon bundles:
    # 1) can't be 256x256 because too big to import within the application
    # 2) the 16x16 object will be the shown in taskbar , Explorer list view, application context menu, etc.
    #     - It will choose the 16-color icon if it exists. I don't know why anyone would want this
    #     - the 256 color works fine. I haven't tried other sizes.

    # pre-load icons; they need to be set for the load dictionary progress, since it happens before the main frame shows
    # ib = wx.IconBundle()
    # ib.AddIconFromFile(os.path.join(segHelper.runningDir, "application-icon.ico"), wx.BITMAP_TYPE_ANY)

    # configuration
    config = Config(os.path.abspath(opts.config))

    # config.appDir = segHelper.runningDir
    config.appDir = opts.appdir

    # prog = wx.ProgressDialog(parent=None, title="Progress", message="Loading Dictionary",
    #                          style=wx.PD_AUTO_HIDE | wx.PD_SMOOTH)

    app = Tk()
    app.title("Vocabulary Extractor")

    # Create initial loading dialog
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

    # prog.SetIcons(ib)
    segHelper.config = config
    segHelper.load_data(
        updatefunction=update_progress,
        error_callback=lambda msg: tk.messagebox.showerror("Dictionary Error", msg),
    )
    loading_dialog.destroy()

    segHelper.load_known_words()
    segHelper.load_extra_columns()

    # loads main window
    frame = main.MainWindow(app, height=750, width=500)

    # frame.SetIcons(ib)

    frame.segHelper = segHelper
    frame.config = config

    if opts.inputfile:
        frame.notebook.editorPanel.SetValue(segHelper.read_files([opts.inputfile]))

    if opts.outputfile:
        segHelper.summarize_results()
        if opts.outputfile == "-":
            print(f"""            
            {segHelper.summary}
            
            {segHelper.results}""")
        else:
            import codecs
            try:
                f = codecs.open(opts.outputfile, encoding='utf-8', mode='w')
                f.write(segHelper.summary + "\n\n" + segHelper.results)
                f.close()
            except (WindowsError | OSError | IOError) as e:
                print(f"Warning: Failed to write to output file {opts.outputfile}: {e}")
        # frame.DestroyChildren()
        # frame.Destroy()
        sys.exit()

    frame.notebook.messagePanel.SetValue(frame.segHelper.get_messages())
    # frame.Show(True)

    # app.MainLoop()
    app.mainloop()


# if __name__ == "__main__":
#    run()
