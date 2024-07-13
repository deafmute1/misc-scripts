#!/bin/bash

root=$(awk '$5 == "/" { print $10 }' /proc/self/mountinfo)
date=$(date +"%d-%b-%Y_%H-%M-%S")
backupDir="/export/mergerfs/backup/add-sources/sysinfo"

# clean pkg caches
apt-get clean
rm -f /var/cache/openmediavault/archives/*
touch /var/cache/openmediavault/archives/Packages

mkdir -p "${backupDir}/"{fdisk,blkid,omvpkg,grub,grubparts,u-boot,apt-explicit}

# save helpful information
fdisk -l ${root} > "${backupDir}/fdisk/${date}"
blkid > "${backupDir}/blkid/${date}"
dpkg -l | grep openmediavault > "${backupDir}/omvpkg/${date}"

# calculate partition table size to accommodate GPT and MBR.
part_type=$(blkid -p ${root} | cut -d \" -f4)
if [ "${part_type}" = "gpt" ]; then
    num_parts=$(parted -m ${root} print | tail -n1 | cut -b1)
    grubparts_bs_calc=$(((128 * ${num_parts}) + 1024))
else
    grubparts_bs_calc=512
fi

# save partition table and mbr
dd if=${root} of="${backupDir}/grub/${date}" bs=446 count=1
dd if=${root} of="${backupDir}/grubparts/${date}" bs=${grubparts_bs_calc} count=1

# backup u-boot if platform_install.sh exists
if [ -f "/usr/lib/u-boot/platform_install.sh" ]; then
    . /usr/lib/u-boot/platform_install.sh
    if [ -d "${DIR}" ]; then
        tar cjf "${backupDir}/u-boot/${date}.tar.bz" ${DIR}/*
    fi
fi

# apt packages (explictly installed by user only)
# this is a somewhat imperfect method.
#
# explanation:
# NOTE: comm -23 is used to discard stuff from the proc sub.
# - First, our base list is generated from apt-mark showmanual
# - Then we discard packages in /var/log/installer/initial-status.gz
# - Finally, we discard packages installed locally only (no repo) using apt list --installed  | grep "local]"
comm -23 <(comm -23 <(apt-mark showmanual | sort -u) \
    <(gzip -dc /var/log/installer/initial-status.gz | sed -n 's/^Package: //p' | sort -u)) \
    <(apt list --installed 2>/dev/null  | grep "local]" | cut -d'/' -f1 | sort  -u) \
    > "${backupDir}/apt-explicit/${date}"