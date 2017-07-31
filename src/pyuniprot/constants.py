# -*- coding: utf-8 -*-

import os

PYUNIPROT_DIR = os.path.expanduser('~/.pyuniprot')
if not os.path.exists(PYUNIPROT_DIR):
    os.mkdir(PYUNIPROT_DIR)

PYUNIPROT_DATA_DIR = os.path.join(PYUNIPROT_DIR, 'data')
if not os.path.exists(PYUNIPROT_DATA_DIR):
    os.mkdir(PYUNIPROT_DATA_DIR)


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'