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
