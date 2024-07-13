#!/bin/bash
# Version: 0.1
# shellcheck disable=SC1091
# Standard runner for python scripts with requirements.txt
# Automatically sets up venv and install requirements

# Force settings for custom deployment:
# Contains ./requirements.txt and ./env; defaults to parent dir of python file
# RUN_PY_WORK_DIR=
# Python code to run
# RUN_PY_FORCE_FILE=

# USAGE: run-py.sh  <python.py> <params for python.py>
# Looks for venv and requirements.txt inside folder containing python.py by default,
# override by setting env var RUN_PY_WORK_DIR

# shellcheck disable=SC2034
py_file="${RUN_PY_FORCE_FILE:-$1}"
default_dir="$(dirname "$(realpath "$py_file")")"
work_dir=${RUN_PY_WORK_DIR:-$default_dir}
env_dir="${work_dir}/env"

if [ "$py_file" == "$1" ]; then 
    params=( "${@:2}" )
else 
    params=( "$@" )
fi 

set -a # export all vars following, including activation script
# Allows for js/pytohn-dotenv like .env file
if [ -f "${work_dir}/.env" ]; then 
    . "${work_dir}/.env"  
fi 
# create venv if doesn't exist
if [ ! -d "$env_dir" ]; then 
    /usr/bin/env python3 -m venv "$env_dir"
    source "${env_dir}/bin/activate"
    pip3 install -r "${work_dir}/requirements.txt" 
fi
. "${env_dir}/bin/activate"
set +a

"${env_dir}/bin/python" "$py_file" "${params[@]}"
