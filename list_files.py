#!/usr/bin/env python

from datetime import datetime
import logging
import os
import sys

import gphoto2 as gp

def list_files(camera, path='/'):
    result = []
    # get files
    for name, value in camera.folder_list_files(path):
        result.append(os.path.join(path, name))
    # read folders
    folders = []
    for name, value in camera.folder_list_folders(path):
        folders.append(name)
    # recurse over subfolders
    for name in folders:
        result.extend(list_files(camera, os.path.join(path, name)))
    return result

def get_file_info(camera, path):
    folder, name = os.path.split(path)
    return camera.file_get_info(folder, name)

def main():
    logging.basicConfig(
        format='%(levelname)s: %(name)s: %(message)s', level=logging.WARNING)
    callback_obj = gp.check_result(gp.use_python_logging())
    camera = gp.Camera()
    camera.init()
    files = list_files(camera)
    if not files:
        print('No files found')
        return 1
    print('File list')
    print('=========')
    for path in files:
        print(path)
    info = get_file_info(camera, files[-2])
    print('file mtime:', datetime.fromtimestamp(info.file.mtime).isoformat(' '))
    camera.exit()
    return 0

if __name__ == "__main__":
    sys.exit(main())
