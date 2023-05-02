#!/usr/bin/env python

import stat
import os
import sched, time
import shutil
import datetime
import math

import board
import busio
import adafruit_character_lcd.character_lcd_rgb_i2c as character_lcd
lcd_columns = 16
lcd_rows = 2
i2c = busio.I2C(board.SCL, board.SDA)
lcd = character_lcd.Character_LCD_RGB_I2C(i2c, lcd_columns, lcd_rows)
lcd.create_char(0,bytes([0x0,0x10,0x8,0x4,0x2,0x1,0x0,0x0]))

# how many seconds to wait before assuming the sd-backup script has 
# stopped working
watchdog_timer = 15

sd_service_working = '/tmp/sd_backup_working'

camera_plugged_in = '/tmp/camera_plugged_in'
camera_errors = '/tmp/camera_errors'
camera_tally = '/tmp/camera_status'
camera_done = '/tmp/camera_done'

copy_start = '/tmp/camera_copy_start'
copy_end = '/tmp/camera_copy_end'

media_dest = '/dev/MediaDest'
mnt_dest = '/media/dest'
sequence_current = 0
task_current = 'I'
line1 = 'STARTUP'

prev_usage = 0
transfer_rate = 0

def StatusMedia():

  status = StatusDest()
  if status == 'M':
    # mounted, report usage
    total, used, free = shutil.disk_usage(mnt_dest)

    return '%d%% full' % (math.ceil((used / total) * 100))
  else:
    return ''

def StatusDaemons():
  global watchdog_timer
  global sd_service_working
  global copy_end
  
  if os.path.isfile(copy_end):
    return 'D'
  elif os.path.isfile(sd_service_working):
    mtime = datetime.datetime.fromtimestamp(os.path.getmtime(sd_service_working))
    now = datetime.datetime.now()
    elapsed = now - mtime
    age = elapsed.total_seconds()

    if age > watchdog_timer:
      print("sd-backup.py hasn't updated in %d seconds, assuming it crashed." % (watchdog_timer))
      return 'E'
    else:
      return 'R'
  else:
    return 'I'

def StatusCamera():
  global camera_plugged_in
  global camera_errors
  global camera_tally
  global copy_start
  global copy_end

  if os.path.isfile(camera_plugged_in):
    return 'M'
  elif os.path.isfile(camera_errors):
    return 'E'
  elif os.path.isfile(camera_tally):
    return 'A'
  elif os.path.isfile(copy_end):
    return 'D'
  else:
    return 'U'

def CopyCount():
  global camera_tally

  if os.path.isfile(camera_tally):
    with open(camera_tally,'r') as f: tally = f.readlines()
    return tally[0]

  return '0/0'

def DataRate():
  global copy_start

  if os.path.isfile(copy_start):
    mtime = os.path.getmtime(copy_start)
    now = time.time()
    with open(copy_start,'r') as f: data = f.readlines()
    start_used = int(data[0])

    total, used, free = shutil.disk_usage(mnt_dest)

    copied = used - start_used
    elapsed = now - mtime

    rate = (copied / elapsed) / 1024 / 1024

    return "%.0f MB/s" % (rate)

  return "0 MB/s"
  

def StatusDest():
  global task_current

  if os.path.ismount(mnt_dest):
    #print("destination mounted")
    return 'M'
  elif os.path.exists(media_dest):
    if stat.S_ISBLK(os.stat(media_dest).st_mode):
      #print("destination present, not mounted")
      return 'U'
    else:
      #print('Destination storage missing')
      return 'X'
  else:
    #print('destination storage missing')
    return 'X'

# spinner icon to indicate this script is working

def UpdateSpinner():
  global sequence_current

  sequence = ['-','\x00','|','/']
  sequence_current = (sequence_current + 1) % (len(sequence))
  return sequence[sequence_current]

def UpdateLCD(schedule):
  global task_current
  global line1
  global camera_errors
  issue_shutdown = False

  if task_current == 'S':
    line1 = 'SHUTDOWN ISSUED'
    issue_shutdown = True
    task_current = 'D'
  elif StatusDaemons() == 'D':
    line1 = 'COPY DONE'
  elif StatusDaemons() == 'I':
    line1 = 'SYSTEM IDLE'
  elif os.path.isfile(camera_errors):
    with open(camera_errors) as f: line1 = f.read().replace('\n','')
  else:
    line1 = "%s %s" % (DataRate(),CopyCount())

  line2 = '%s %s%1s%1s %s' % (UpdateSpinner(),StatusDaemons(),StatusDest(),StatusCamera(),StatusMedia())

  lcd.message = '%-16s\n%-16s' % (line1,line2)
  lcdupdater.enter(1,2, UpdateLCD, (schedule,))

  if issue_shutdown:
    os.system("/usr/sbin/shutdown -h now")

def ReadInput(schedule):
  global task_current

  # Button mapping:
  # * select_button == shutdown

  if lcd.select_button:
    #shutdown system
    task_current = 'S'

  lcdupdater.enter(0.05,1,ReadInput, (schedule,))

lcdupdater = sched.scheduler(time.time, time.sleep)
lcdupdater.enter(1,1, UpdateLCD, (lcdupdater,))
lcdupdater.enter(0.05,1, ReadInput, (lcdupdater,))
lcdupdater.run()

