# Running VocabularyExtractor

## Windows

### Setup

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

If you get the error:

> File ...\venv\Scripts\Activate.ps1 cannot be loaded because running scripts is disabled on this system

Run the following command first, then re-run `venv\Scripts\Activate.ps1`:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

When prompted, choose **Run Once** or **Always Run** as appropriate.

### Run

```powershell
python main.py
```

### Build Windows Executable

After completing setup above:

```powershell
.\Build-Exe.ps1
```

If the script is blocked because it is accessed via a UNC path (e.g. `\\wsl.localhost\...`),
set the execution policy for the current session first:

```powershell
Set-ExecutionPolicy -ExecutionPolicy Unrestricted -Scope Process
.\Build-Exe.ps1
```

This produces `dist\Vocabulary Extractor\` containing `Vocabulary Extractor.exe`
and all required data files. Zip that folder to distribute.

## Linux

### Setup

tkinter is part of the Python standard library but requires a separate system package:

```bash
sudo apt install python3-tk
```

Then set up the virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Run

```bash
python main.py
```

## Headless / Command-Line Mode

The `--headless` flag runs the program without any UI and writes tab-delimited results to a file or stdout. This is useful for scripting or batch processing.

```bash
# Output to stdout
python main.py --headless -i samples/VN/mytext.txt

# Output to a file
python main.py --headless -i samples/VN/mytext.txt -o results.tsv
```

Additional options let you specify dictionaries, charset, filters, and extra column data directly on the command line, overriding whatever is in the config file:

```bash
python main.py --headless \
    -i samples/VN/mytext.txt \
    -o results.tsv \
    --dict dict/VN/vnedict.txt \
    --charset Vietnamese \
    --filter filter/VN/known-words.txt \
    --extracolumn data/VN/Freq_per_Million.txt
```

Run `python main.py --help` for the full list of options. See `doc/help.html` for detailed documentation.
