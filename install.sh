#!/bin/bash

echo "copying udev rules.."
cp 50-sd-card.rules /etc/udev/rules.d/
cp 51-storage.rules /etc/udev/rules.d/
echo "copying mount script.."
cp automount.sh /usr/local/bin/
echo "copying systemd unit.."
cp mount-source@.service /etc/systemd/system/
cp mount-dest@.service /etc/systemd/system/

echo "reloading configs.."
systemctl daemon-reload
systemctl enable mount-dest@.service
systemctl enable mount-source@.service
udevadm control --reload-rules

echo "chmod automount script.."
chmod 755 /usr/local/bin/automount.sh

