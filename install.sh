#!/bin/bash

echo "copying udev rules.."
cp 99-field-backup.rules /etc/udev/rules.d/
echo "copying mount script.."
cp sd-backup.py /usr/local/bin/
echo "copying systemd unit.."
cp media-dest.mount /etc/systemd/system/
cp sd-backup.service /etc/systemd/system/
cp lcd.service /etc/systemd/system/
cp lcd-daemon.py /usr/local/bin/lcd-daemon.py

echo "enabling units and reloading configs.."
systemctl daemon-reload
systemctl enable media-dest.mount
systemctl enable sd-backup.service
systemctl enable lcd.service
systemctl restart lcd.service
udevadm control --reload-rules

echo "chmod scripts.."
chmod 755 /usr/local/bin/sd-backup.py
chmod 755 /usr/local/bin/lcd-daemon.py
