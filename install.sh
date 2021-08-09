#!/bin/bash

echo "copying udev rules.."
cp 50-sd-card.rules /etc/udev/rules.d/
echo "copying mount script.."
cp automount.sh /usr/local/bin/
echo "copying systemd unit.."
cp mount-source@.service /etc/systemd/system/

echo "reloading configs.."
systemctl daemon-reload
systemctl enable mount-source@.service
udevadm control --reload-rules

echo "chmod automount script.."
chmod 755 /usr/local/bin/automount.sh

