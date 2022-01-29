#!/bin/bash

echo "delete udev rules.."
rm -f /etc/udev/rules.d/99-field-backup.rules
#cp 51-storage.rules /etc/udev/rules.d/
echo "delete mount script.."
rm -f /usr/local/bin/sd-backup.sh
echo "disable systemd units.."
systemctl disable media-dest.mount
systemctl disable media-source.mount
systemctl disable sd-backup.service
systemctl disable lcd.service
echo "delete systemd units.."
rm -f /etc/systemd/system/media-source.mount
rm -f /etc/systemd/system/media-dest.mount
rm -f /etc/systemd/system/sd-backup.service
rm -f /etc/systemd/system/lcd.service
rm -f /usr/local/bin/lcd-daemon.py

echo "reloading configs.."
systemctl daemon-reload
udevadm control --reload-rules
