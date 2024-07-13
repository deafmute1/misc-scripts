#!/usr/bin/env python3
import shutil
import subprocess
from tinytag import TinyTag
from collections import Counter
import os, sys
from pathlib import Path

# You can overwrite env using this dict
ENV_VARS = {
    "TR_TORRENT_DIR": None, 
    "TR_TORRENT_NAME": None, 
    "TR_TORRENT_ID": None, 
    "TR_TORRENT_LABELS": None,
    "TR_MOVE_TO_PREFIX": None, 
    "TR_USER": None, 
    "TR_PASS": None,
    "TR_DRY_RUN": None
}

def print_exit(s: str, err:bool=True):
    print(f'{"<move_music.py> Error: " if err else "<move_music.py>:" } {s}; exiting ')
    os.environ["RUN_PY_SUPPRESS_RERUN"] = "True"
    exit(2 if err else 0)

def main():
    vars = {k: v if v is not None else os.environ.get(k, v) for k, v in ENV_VARS.items()}
    print(vars)
    
    if vars["TR_DRY_RUN"].lower() in ("yes", "true", "t", "1"):
        vars["TR_DRY_RUN"] = True

    if not "music" in vars["TR_TORRENT_LABELS"].split(','): 
        print_exit("Torrent not tagged music", False)

    if shutil.which("transmission-remote") is None: 
        print_exit("transmission-remote not in PATH")
        
    path_move = Path(vars["TR_MOVE_TO_PREFIX"])
    path_source = Path(vars["TR_TORRENT_DIR"]).joinpath(vars["TR_TORRENT_NAME"]).resolve()
    
    if not path_source.is_dir(): 
        print_exit(f"Error: path to torrent {path_source} is not directory")
    if path_move in path_source.parents or path_move.samefile(path_source): 
        print_exit(
            f"Error: download dir of this torrent is relative to (subdir of) TR_MOVE_TO_PREFIX"
        )
    
    artist_count=Counter()
    for file in path_source.iterdir(): 
        if not TinyTag.is_supported(file):
            continue
        artist_count[TinyTag.get(file).artist] += 1
        
    path_move = path_move.joinpath(artist_count.most_common(1)[0])
    path_move.mkdir(exist_ok=True)
    cmd = [
        "transmission-remote",
        "localhost:9091", 
        "-n", "admin:password", 
        "-t", vars["TR_TORRENT_ID"],
        "--move", str(path_move)
    ] 
    if vars["TR_DRY_RUN"]:
        print_exit("Generated cmd: {cmd}", False)
    
    ret = subprocess.run(cmd, capture_output=True, stderr=subprocess.STDOUT)
    err = False if ret.returncode == 0 else True
    info_string = (
        f'Move operation {'failed' if err else 'completed sucessfully'}\n'
        f'command: {ret.args}\n'
        f'output: {ret.stdout}\n'
    ) 
    print_exit(info_string, err)
    
if __name__ == "__main__":
    main()