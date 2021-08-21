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


