#!/usr/bin/env python

import stat
import os
import sched, time

import board
import busio
import adafruit_character_lcd.character_lcd_rgb_i2c as character_lcd
lcd_columns = 16
lcd_rows = 2
i2c = busio.I2C(board.SCL, board.SDA)
lcd = character_lcd.Character_LCD_RGB_I2C(i2c, lcd_columns, lcd_rows)
lcd.create_char(0,bytes([0x0,0x10,0x8,0x4,0x2,0x1,0x0,0x0]))

# read rsync status from /tmp/rsync_status
# * figure out files synced
# * files to sync
# * transfer rate

rsync_status_location = '/tmp/rsync_status'
rsync_timeout = 5
media_source = '/dev/MediaSource'
mnt_source = '/media/source'
media_dest = '/dev/MediaDest'
mnt_dest = '/media/dest'
sequence_current = 0
task_current = 'I'
line1 = 'STARTUP'

def StatusRsync():
  global task_current

  if os.path.isfile(rsync_status_location): 
    stats = os.stat(rsync_status_location)
    elapsed = time.time() - stats.st_mtime

    if elapsed > rsync_timeout:
      #print('rsync log, but out of date')
      with open(rsync_status_location, 'r') as f:
        for line in f: pass

      data = line.split()
      return '%s %s DONE' % (data[1],data[0])
    else:
      task_current = 'I'
      with open(rsync_status_location, 'r') as f:
        for line in f: pass

      data = line.split()
      return '%s %s' % (data[1],data[0])
  else:
    #print('rsync is not running')
    return 'NOT RUNNING'

# icon for SD card inserted/missing
# * check if /dev/MediaSource exists
# icon for SSD attached/missing
# * check if /dev/MediaDest exists

def StatusSource():
  global task_current 

  if os.path.ismount(mnt_source):
    #print("source mounted")
    task_current = 'I'
    return 'M'
  elif os.path.exists(media_source):
    if stat.S_ISBLK(os.stat(media_source).st_mode):
      #print('source present, not mounted')
      return 'U'
    else:
      #print('Source missing')
      return 'X'
  else:
    #print('source missing')
    return 'X'

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

# scan for button presses
# * shutdown (status icon: down arrow)
# * abort sync (status icon: X)
# * unmount everything (status icon: U)
# * idle (status icon: I)

# spinner icon to indicate this script is working

def UpdateSpinner():
  global sequence_current

  sequence = ['-','\x00','|','/']
  sequence_current = (sequence_current + 1) % (len(sequence))
  return sequence[sequence_current]

# icon to indicate startup/shutdown/performin

# 0001/9999 55mb/s
# x V SD:M SSD:M

def UpdateLCD(schedule):
  global task_current
  global line1

  if task_current == 'S':
    line1 = 'SHUTDOWN ISSUED'
    lcd.message = '%-16s\n%s %s SRC:%1s DST:%1s' % (line1,UpdateSpinner(),task_current,StatusSource(),StatusDest())
    os.system("/usr/sbin/shutdown -h now")
    task_current = 'D'
  elif task_current == 'K':
    os.system("/usr/bin/systemctl stop sd-backup.service")
    line1 = 'BACKUP STOPPED'
    task_current = 'D'
  elif task_current == 'D':
    pass
  else:
    line1 = StatusRsync()

  lcd.message = '%-16s\n%s %s SRC:%1s DST:%1s' % (line1,UpdateSpinner(),task_current,StatusSource(),StatusDest())
  lcdupdater.enter(1,2, UpdateLCD, (schedule,))

def ReadInput(schedule):
  global task_current

  # Button mapping:
  # * select_button == shutdown
  # * left_button == kill rsync
  # * right_button == unmount source/dest

  if lcd.select_button:
    #shutdown system
    task_current = 'S'
  elif lcd.left_button:
    #Kill backup
    task_current = 'K'

  lcdupdater.enter(0.05,1,ReadInput, (schedule,))
    

lcdupdater = sched.scheduler(time.time, time.sleep)
lcdupdater.enter(1,1, UpdateLCD, (lcdupdater,))
lcdupdater.enter(0.05,1, ReadInput, (lcdupdater,))
lcdupdater.run()

