#!/usr/bin/env python

import gphoto2 as gp
import shutil, time
import sys, os
from pathlib import Path

copy_start = '/tmp/camera_copy_start'
copy_end = '/tmp/camera_copy_end'

mnt_dest = '/media/dest'
media_dest =  mnt_dest + '/camera_bup'

# this file gets touched to the lcd daemon can determine if
# we're regularly updating.
sd_service_working = '/tmp/sd_backup_working'

# udev creates this file when camera is plugged in. this script
# touches this file to indicate it is running
camera_plugged_in = '/tmp/camera_plugged_in'

# how many files we detected need copied
files_to_copy = '/tmp/files_to_copy'

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

def get_destination_files():
  global media_dest

  output = []
  for entry in os.scandir(media_dest):
    if entry.is_file():
      output.append(entry.name)

  return output


# clean up files that a previous run may have left laying around
cleanup_status()

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

# does the camera have any files?
files = list_files(cam)
if not files:
  with open(error_output,'w') as error_file: error_file.write('ERR04')
  print('No files found on camera.')
  sys.exit(0)

to_copy = []
existing_files = get_destination_files()
for path in files:
  filename = os.path.basename(path)
  if filename not in existing_files:
    to_copy.append(path)

# this gets used by lcd daemon for calculating transfer speed
total, used, free = shutil.disk_usage(mnt_dest)
with open(copy_start,'w') as f: f.write("%d" % (used))

# run the gphoto2 backup
if len(to_copy):
  for path in to_copy:
    # touch this so the lcd daemon can tell we're still running
    Path(sd_service_working).touch()

    folder, name = os.path.split(path)
    dest = media_dest + '/' + name

    print("copying %s" % (name))
    try:
      file = cam.file_get(folder,name,gp.GP_FILE_TYPE_NORMAL)
      file.save(dest)
    except:
      with open(error_output,'w') as error_file: error_file.write('ERR05')
      print("Lost connection to camera mid-copy.")
      sys.exit(1)
      
    copy_tally = copy_tally + 1

    with open(status_output,'w') as f: f.write("%d/%d" % (copy_tally,len(to_copy)))
    print("%d files copied." % (copy_tally))

with open(copy_end,'w') as f: f.write("%d" % (time.time()))
cleanup_status()

os.sync()
cam.exit()
