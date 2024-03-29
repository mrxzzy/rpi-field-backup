# rpi-field-backup
Let's back up SD cards to USB storage on an RPI.


# rpi setup

as root:

```
apt-get install python3-pip
update-alternatives --install $(which python) python $(readlink -f $(which python3)) 3
update-alternatives --config python
pip3 install --upgrade setuptoolsp
pip3 install --uprade adafruit-python-shell
wget https://raw.githubusercontent.com/adafruit/Raspberry-Pi-Installer-Scripts/master/raspi-blinka.py
python3 raspi-blinka.py
reboot
```

post reboot (as root still)
```
pip3 install adafruit-circuitpython-charlcd
```

# pinouts

```
pi         adafruit shield
     __________
    |          |
 __________    |
|          |   |
2 4 6 8    2 4 6 8
. . . .    . . . .
. . . .    . . . .
1 3 5 9    1 3 5 9
  | |__________|
  |__________|
```

# commands

lcd-daemon.py responds to these buttons on the lcd hat:

* "SELECT" (leftmost button) = system shutdown
* "LEFT" (button right of select) = kill any running rsync
* "RIGHT" (rightmost button) = umount everything and kill any rsyncs

# notes for dummies like the person that wrote this

udev attributes: `udevadm info --attribute-walk --path=$(udevadm info --query=path --name=/dev/sda)`
or: `udevadm info --attribute-walk --name=/dev/sda1`
get ENV: `udevadm info --export --name=/dev/sda1`
