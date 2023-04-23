#!/usr/bin/env python

import gphoto2 as gp
import shutil
import sys, os
from pathlib import Path

mnt_dest = '/media/dest'
media_dest =  mnt_dest + '/camera_bup'
sd_service_output = '/tmp/sd_backup_status'
camera_plugged_in = '/tmp/camera_plugged_in'
error_output = '/tmp/camera_errors'
status_output = '/tmp/camera_status'
final_output = '/tmp/camera_done'
copy_tally = 0

def cleanup_status():
  global error_output
  global status_output

  if os.path.isfile(error_output):
    os.remove(error_output)
  if os.path.isfile(status_output):
    os.remove(status_output)

# functions ripped straight from the python gphoto2 examples directory..

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


# clean up files that a previous run may have left laying around
cleanup_status()

# check that camera plugged in
Path(sd_service_output).touch()
cam = gp.Camera()

try: 
  cam.init()
except gp.GPhoto2Error:
  with open(error_output,'w') as error_file: error_file.write('ERR01')
  print("It appears no camera is plugged in.")
  sys.exit(1)

# check that destination has folder set up

if not os.path.ismount(mnt_dest):
  with open(error_output,'w') as error_file: error_file.write('ERR02')
  print("It appears destination is not mounted.")
  sys.exit(1)
  
if not os.path.isdir(media_dest):
  try:
    Path(media_dest).mkdir()
  except:
    with open(error_output,'w') as error_file: error_file.write('ERR03')
    print("Failure creating destination directory.")
    sys.exit(1)


# does the camera have any files to transfer?
files = list_files(cam)
if not files:
  with open(error_output,'w') as error_file: error_file.write('ERR04')
  print('No files found on camera.')
  sys.exit(0)

# run the gphoto2 backup
for path in files:
  Path(sd_service_output).touch()
  folder, name = os.path.split(path)
  dest = media_dest + '/' + name
  if os.path.isfile(dest):
    print("%s exists in destination, not copying." % (name))
    continue
  else:
    print("%s does not exist, copying.." % (name))
    file = cam.file_get(folder,name,gp.GP_FILE_TYPE_NORMAL)
    file.save(dest)
    copy_tally = copy_tally + 1
    with open(status_output,'w') as f: f.write("%d" % (copy_tally))
    print("%d files copied." % (copy_tally))

with open(final_output,'w') as f: f.write("%d" % (copy_tally))

cleanup_status()

os.sync()
cam.exit()
