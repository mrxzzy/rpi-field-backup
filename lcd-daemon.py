#!/usr/bin/env python

import stat
import os
import sched, time
import shutil
import datetime

import board
import busio
import adafruit_character_lcd.character_lcd_rgb_i2c as character_lcd
lcd_columns = 16
lcd_rows = 2
i2c = busio.I2C(board.SCL, board.SDA)
lcd = character_lcd.Character_LCD_RGB_I2C(i2c, lcd_columns, lcd_rows)
lcd.create_char(0,bytes([0x0,0x10,0x8,0x4,0x2,0x1,0x0,0x0]))

sd_service_status = '/tmp/sd_backup_status'

camera_status = '/tmp/camera_plugged_in'
camera_errors = '/tmp/camera_errors'
camera_tally = '/tmp/camera_status'
camera_done = '/tmp/camera_done'

media_dest = '/dev/MediaDest'
mnt_dest = '/media/dest'
sequence_current = 0
task_current = 'I'
line1 = 'STARTUP'

prev_usage = 0
transfer_rate = 0

# looks at the destination media and determines usage and transfer rate
def StatusMedia():
  global prev_usage
  global transfer_rate

  status = StatusDest()
  if status == 'M':
    # mounted, report usage and maybe data rate
    total, used, free = shutil.disk_usage(mnt_dest)

    if prev_usage == 0:
      rate = 0
    else:
      # estimate transfer rate in MB/s
      transfer_rate = (used - prev_usage) / 1024 / 1024
      if transfer_rate < 0:
        transfer_rate = 0

    prev_usage = used

    return '%.2f/%.1f GB' % (used / 1024 / 1024 / 1024,total / 1024 / 1024 / 1024)

  elif status == 'U':
    # disk is not mounted
    return 'SSD Unmounted'
  elif status == 'X':
    # disk not plugged in
    return 'SSD Unplugged'

def StatusDaemons():
  global sd_service_status
  global camera_done
  
  if os.path.isfile(camera_done):
    return 'D'
  elif os.path.isfile(sd_service_status):
    mtime = datetime.datetime.fromtimestamp(os.path.getmtime(sd_service_status))
    now = datetime.datetime.now()
    elapsed = now - mtime
    age = elapsed.total_seconds()

    if age > 10:
      print("sd-backup.py hasn't updated in 10 seconds, assuming it crashed.")
      return 'E'
    else:
      return 'R'
  else:
    return 'I'

def StatusCamera():
  global camera_status
  global camera_errors
  global camera_tally
  global camera_done

  if os.path.isfile(camera_status):
    return 'M'
  elif os.path.isfile(camera_errors):
    return 'E'
  elif os.path.isfile(camera_tally):
    return 'A'
  elif os.path.isfile(camera_done):
    return 'D'
  else:
    return 'U'

def StatusDest():
  global task_current

  if os.path.ismount(mnt_dest):
    #print("destination mounted")
    task_current = 'I'
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
  elif task_current == 'D':
    pass
  elif os.path.isfile(camera_errors):
    with open(camera_errors) as f: line1 = f.read().replace('\n','')
  else:
    line1 = StatusMedia()


  line2 = '%s %s%1s%1s %.0f MB/s' % (UpdateSpinner(),StatusDaemons(),StatusDest(),StatusCamera(),transfer_rate)

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

