#!/bin/bash -x

# exit immediately on failure (even when piping), treat unset variables and
# parameters as an error, and disable filename expansion (globbing)
set -eufo pipefail

# disable mitigations
#   verify with: awk 'FNR==1{print "==>"FILENAME"\n"}1' /sys/devices/system/cpu/vulnerabilities/*
sed -i -E 's/^(GRUB_CMDLINE_LINUX_DEFAULT=".*)"/\1 mitigations=off"/' /etc/sysconfig/grub
grub2-mkconfig -o /etc/grub2.cfg

# install newer kernel
amazon-linux-extras install -y \
  epel \
  kernel-ng

# update all installed packages
yum install -y deltarpm
yum update -y

# install new packages
yum install -y \
  amazon-efs-utils \
  htop \
  iotop \
  libhugetlbfs-devel \
  libhugetlbfs-utils \
  perf

# enable and set PAM limits
cat <<EOF >> /etc/pam.d/common-session
session required pam_limits.so
EOF

cat <<EOF >> /etc/security/limits.conf
soft nofile 1048576
hard nofile 1048576
soft core unlimited
hard core unlimited
EOF


# mount attached volumes on startup
chmod +x /etc/rc.local
cat <<"EOF" >> /etc/rc.local
mkdir -p /volumes

format_and_mount() {
    disk=$1
    mount_options=$2

    if [ -b "/dev/${disk}" ]
    then
        blockdev --setra 512 /dev/${disk}
        echo 1024 > /sys/block/${disk}/queue/nr_requests

        # attempt to format disk
        /sbin/mkfs.ext4 -E lazy_itable_init=0,lazy_journal_init=0 -m 0 ${mount_options} /dev/${disk}

        # mount if format successful
        if [ $? -eq 0 ]
        then
            mkdir /volumes/${disk}
            mount -o init_itable=0 /dev/${disk} /volumes/${disk}

            mkdir /volumes/${disk}/tmp
            chmod 777 /volumes/${disk}/tmp
        fi
    fi
}

for id in {a..z}; do
    format_and_mount xvd${id} &
done

for id in {0..31}; do
    format_and_mount nvme${id}n1 "-E nodiscard" &
done
EOF

reboot