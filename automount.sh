#!/bin/bash

# stolen from https://www.andreafortuna.org/2019/06/26/automount-usb-devices-on-linux-using-udev-and-systemd/

ACTION=$1
MEDIA=$2

if [[ $MEDIA -eq "SD" ]]; then
  MOUNT="/media/source"
else
  MOUNT="/media/dest"
fi

# See if this drive is already mounted
MOUNT_POINT=$(/bin/mount | /bin/grep ${MOUNT} | /usr/bin/awk '{ print $3 }')

do_mount()
{
    if [[ -n ${MOUNT_POINT} ]]; then
        # Already mounted, exit
        exit 1
    fi

    if [[ ! -d /media/source ]]; then
        echo "directory /media/source does not exist. please create"
        exit 1
    fi
    if [[ ! -d /media/dest ]]; then
        echo "directory /media/dest does not exist. please create"
        exit 1
    fi
	
    # Get info for this drive: $ID_FS_LABEL, $ID_FS_UUID, and $ID_FS_TYPE
    eval $(/sbin/blkid -o udev ${DEVICE})

    # for the mount point, at this point in this tool's illustrious 
    # development: assume if it's exfat it's an SD card, so mount
    # at /media/source. that's how canon formatted SD cards show up
    if [[ $ID_FS_TYPE -eq 'exfat ]]; then
        LABEL='source'
    else
        LABEL='dest'
    fi

    MOUNT_POINT="/media/${LABEL}"

    /bin/mkdir -p ${MOUNT_POINT}

    # Global mount options
    OPTS="rw,relatime"

    # File system type specific mount options
    if [[ ${ID_FS_TYPE} == "vfat" ]]; then
        OPTS+=",users,gid=100,umask=000,shortname=mixed,utf8=1,flush"
    fi

    if ! /bin/mount -o ${OPTS} ${DEVICE} ${MOUNT_POINT}; then
        echo "mount failed, cannot handle, exiting"
        exit 1
    fi
	
    # todo: updated LCD display
}

do_unmount()
{
    if [[ -n ${MOUNT_POINT} ]]; then
        /bin/umount -l ${DEVICE}
    fi

}
case "${ACTION}" in
    add)
        do_mount
        ;;
    remove)
        do_unmount
        ;;
esac
