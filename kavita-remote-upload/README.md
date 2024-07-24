# README
kavita-epub-uploader is a tkinter GUI to prepare and upload epubs to kavita.

It script was originally written by @duplaja, with heavy edits by @deafmute1. 
[Link to original](https://github.com/duplaja/kavita-scripts/blob/main/epub-fix-gui-remote.py)

# Installation
Some dependancies must be installed manually: python-tkinter, pipx, python (for windows users)
- On MacOS: `brew install python-tk pipx  && pipx ensurepath` (requires homebrew) 
- On Debian-based/apt: `sudo apt update && sudo apt install python3-tk pipx && pipx ensurepath`
- On Fedora-based/dnf: `sudo dnf install python3-tkinter pipx && pipx ensurepath`

For remote access, `rsync` should also be installed.
Warning: MacOS ships with an ancient version of rsync from 2006 that is incompatible!
MacOS users, please update your rsync, `brew install rsync` is sufficent to do this!

Simply [download](https://raw.githubusercontent.com/deafmute1/misc-scripts/main/kavita-remote-upload/kavita-epub-uploader.py) the script to your pc and run it. If you download it to ~/.local/bin on unix-like systems and `chmod +x` it, it will automatically show up in your path!

# Running it
First make a .env file. kavita-epub-uploader looks for this file in this order:
1. Any file specified by `--env-file` option (override)
2. Fie named `.env` in directory you are currently in ($PWD)
3. file named `.env` in directory kavita-epub-uploader.py is in 

Two ways to call it
1. `chmod +x ./kavita-remote-upload.py` (on first run only), `./kavita-remote-upload.py` 
2. `pipx run kavita-remote-upload.py`

CLI usage (`./kavita-epub-uploader.py --help`) :
```
usage: kavita-epub-uploader.py [-h] [--path PATH] [--env-file ENV_FILE] [--author-folder]
                               [--with-file WITH_FILE] [--library LIBRARY]

options:
  -h, --help            show this help message and exit
  --path PATH, -p PATH  Overrides kavita_base_path in env.py
  --env-file ENV_FILE, -f ENV_FILE
                        Specify custom env file location
  --author-folder, -a   Sort by author e.g. author/series/book.epub
  --with-file WITH_FILE, -w WITH_FILE
                        Open this epub at launch
  --library LIBRARY, -l LIBRARY
                        Set a default library
```

# TODO
- Support multiple files?
  1: support looping thru an array of files from cli and recreate GUI each time - fairly hacky, but works!
  2: Rework UI to take and act on multiple UIs, one at a time? 
  3: maybe add option to batch upload without apply fixes - in addition to 1 to avoid reworks?
- Support device upload
  1: get /api/device, display devices in dropdown menu to select; add options to pass device id on cli
  2: get /api/Series/recently-updated-series and /api/Series/recently-added-v2, and look for our upload there to get id
  3: push id to /api/Device/send-to
