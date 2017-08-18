# -*- coding: utf-8 -*-

import os

PYUNIPROT_DIR = os.path.expanduser('~/.pyuniprot')
if not os.path.exists(PYUNIPROT_DIR):
    os.mkdir(PYUNIPROT_DIR)

PYUNIPROT_DATA_DIR = os.path.join(PYUNIPROT_DIR, 'data')
if not os.path.exists(PYUNIPROT_DATA_DIR):
    os.mkdir(PYUNIPROT_DATA_DIR)