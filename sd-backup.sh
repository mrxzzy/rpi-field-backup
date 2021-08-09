#!/bin/bash

SOURCE=/media/source
DEST=/media/dest

SRC_CONFIG=.uuid
LOG_FILE=${DEST}/SDBackup/rsync.log

# check if directories are mounted
if [ -n $(/bin/mount | /bin/grep ${SOURCE} | /usr/bin/awk '{print $3}') ]; then
  echo "${SOURCE} is mounted, we happy"
else
  echo "${SOURCE} not mounted, exiting"
  exit 1
fi

if [ -n $(/bin/mount | /bin/grep ${DEST} | /usr/bin/awk '{print $3}') ]; then
  echo "${DEST} is mounted, we happy"
else
  echo "${DEST} not mounted, exiting"
  exit 1
fi

# check if sd is read only

# get/generate UUID of SD card
if [ -f ${SOURCE}/${SRC_CONFIG} ]; then
  UUID=$( cat ${SOURCE}/${SRC_CONFIG} )
else
  UUID=$( cat /proc/sys/kernel/random/uuid )
  echo ${UUID} > ${SOURCE}/${SRC_CONFIG}
fi

# check if destination has the necessary folder structure set up
if [ ! -d ${DEST}/SDBackup ]; then
  mkdir ${DEST}/SDBackup
fi

if [ ! -d ${DEST}/SDBackup/${UUID} ]; then
  mkdir ${DEST}/SDBackup/${UUID}
fi

# run an rsync

rsync --recursive \
      --times \
      --prune-empty-dirs \
      --ignore-existing \
      --info=progress2 \
      --stats \
      --human-readable \
      --log-file="${LOG_FILE}" \
      --exclude="${SRC_CONFIG}" \
      "${SOURCE}/DCIM/" \
      "${DEST}/SDBackup/${UUID}" 2>/dev/null 

sync

# unmount the two directories

