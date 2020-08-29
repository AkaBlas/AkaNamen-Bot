#!/usr/bin/env python
import os


def check_file_path(path: str) -> str:
    if os.path.isfile(path):
        return path
    path = path.lstrip('tests/')
    if os.path.isfile(path):
        return path
    raise FileNotFoundError(f'No such file or directory: {path}')
