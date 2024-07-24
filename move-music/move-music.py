#!/usr/bin/env python3
import shutil
import subprocess
from tinytag import TinyTag
from collections import Counter
import os, sys
from pathlib import Path

# You can set any hitherto unset env values using this dict
# Do not delete any lines.
ENV_DEFAULT = {
    "TR_TORRENT_DIR": None, 
    "TR_TORRENT_NAME": None, 
    "TR_TORRENT_ID": None, 
    "TR_TORRENT_LABELS": None,
    "TR_MOVE_TO_ROOT": None, 
    "TR_USER": None, 
    "TR_PASS": None,
    "TR_MOVE_TO_FALLBACK_SUFFIX": "unsorted"
}

def print_exit(s: str, err:bool=True):
    print(f'{"<move_music.py> Error: " if err else "<move_music.py>:" } {s}; exiting ') 
    exit(2 if err else 0)

def default_value_or_fail(key: str): 
    if ENV_DEFAULT[key] is None:
        print_exit(f"Env var {key} is required, but is unset")
    return ENV_DEFAULT[key] 

def main():
    vars = {k: os.environ.get(k, default_value_or_fail(k)) for k in ENV_DEFAULT}
    
    if not "music" in vars["TR_TORRENT_LABELS"].split(','): 
        print_exit("Torrent not tagged music", False)

    if shutil.which("transmission-remote") is None: 
        print_exit("transmission-remote not in PATH")
        

    path_move = Path(vars["TR_MOVE_TO_ROOT"])
    path_source = Path(vars["TR_TORRENT_DIR"]).joinpath(vars["TR_TORRENT_NAME"]).resolve()
    
    if not path_source.is_dir(): 
        print_exit(f"Error: path to torrent {path_source} is not directory")
    if path_move in path_source.parents or path_move.samefile(path_source): 
        print_exit(
            f"Error: download dir of this torrent is relative to (subdir of) TR_MOVE_TO_ROOT"
        )
    
    artist_count=Counter()
    for file in path_source.iterdir(): 
        if not TinyTag.is_supported(file):
            continue
        artist_count[TinyTag.get(file).artist] += 1
    
    try: 
        path_move_suffix = artist_count.most_common(1)[0][0]
    # if failed to get any artist from any file, most_common() returns []
    except IndexError: 
        path_move_suffix = vars["TR_MOVE_TO_ROOT"]
    
    path_move = path_move.joinpath(path_move_suffix)
    path_move.mkdir(exist_ok=True)
    cmd = [
        "transmission-remote",
        "localhost:9091", 
        "-n", f'{vars["TR_USER"]}:{vars:["TR_PASS"]}'
        "-t", vars["TR_TORRENT_ID"],
        "--move", str(path_move)
    ] 
    
    ret = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    err = False if ret.returncode == 0 else True
    info_string = (
        f'Move operation {'failed' if err else 'completed sucessfully'}\n'
        f'command: {ret.args}\n'
        f'output: {ret.stdout}'
    ) 
    print_exit(info_string, err)
    
if __name__ == "__main__":
    main()