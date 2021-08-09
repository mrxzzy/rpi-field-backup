#!/bin/bash

echo "copying udev rules.."
cp 50-sd-card.rules /etc/udev/rules.d/
cp 51-storage.rules /etc/udev/rules.d/
echo "copying mount script.."
cp sd-backup.sh /usr/local/bin/
echo "copying systemd unit.."
cp media-source.mount /etc/systemd/system/
cp media-dest.mount /etc/systemd/system/
cp sd-backup.service /etc/systemd/system/

echo "reloading configs.."
systemctl daemon-reload
systemctl enable media-dest.mount
systemctl enable media-source.mount
systemctl enable sd-backup.service
udevadm control --reload-rules

echo "chmod sd-backup script.."
chmod 755 /usr/local/bin/sd-backup.sh

