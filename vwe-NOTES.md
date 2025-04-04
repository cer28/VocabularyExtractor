
```
wget http://www.denisowski.org/Vietnamese/vnedict.txt

sudo apt update && sudo apt upgrade -y

sudo apt install -y build-essential libgtk-3-dev libglib2.0-dev libgl1-mesa-dev \
    libglu1-mesa-dev libjpeg-dev libtiff-dev libgstreamer1.0-dev \
    libgstreamer-plugins-base1.0-dev libnotify-dev

source venv/Scripts/activate

pip install -U pip setuptools wheel


# pip install -U wxPython
# Downloading wxPython-4.2.2.tar.gz
# Building takes a really long time. try this first

DISPLAY= pip install -U keyring
pip install --verbose -U wxPython
```


# Forget it, trying PySimpleGUI

python -m pip install --force-reinstall --extra-index-url https://PySimpleGUI.net/install PySimpleGUI

No, the project has ended

# Try tkinter

sudo apt install python3-tk


# NO install MS fonts

FAIL sudo apt-get install ttf-mscorefonts-installer


# Install on Windows

cd "\\wsl.localhost\Ubuntu\home\chad\Git\VietnameseWordExtractor"

# installs from store
python3

pip install chardet
python.exe main.py
