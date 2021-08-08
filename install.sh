#!/bin/bash

cp 50-sd-card.rules /etc/udev/rules.d/
cp automount.sh /usr/local/bin/
cp sd-mount@.service /etc/systemd/system/

systemctl daemon-reload
udevadm control --reload-rules
chmod 755 /usr/local/bin/automount.sh

