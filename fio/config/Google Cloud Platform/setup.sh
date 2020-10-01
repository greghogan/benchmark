#!/usr/bin/env sh

# Derived from https://cloud.google.com/compute/docs/disks/performance#comparing_local_ssd_performance

if [ $# -lt 2 ]; then
    echo "Usage: $0 <NVME|SCSI> <# of disks>"
    exit 1
fi

PROTOCOL=$1
NUMDISKS=$2


echo "Installing dependencies ..."

sudo apt-get update -y
sudo apt-get install -y build-essential git libtool gettext autoconf \
libgconf2-dev libncurses5-dev python-dev fio bison autopoint


echo "Building and installing 'blkdiscard' ..."

git clone https://git.kernel.org/pub/scm/utils/util-linux/util-linux.git
cd util-linux/
./autogen.sh
./configure --disable-libblkid
make
sudo mv blkdiscard /usr/bin/


echo "Running 'blkdiscard' ..."

DISK=0
while [ $DISK -lt $NUMDISKS ]; do
    if [ "$PROTOCOL" = "NVME" ]; then
        echo "google-local-nvme-ssd-${DISK}"
        sudo blkdiscard /dev/disk/by-id/google-local-nvme-ssd-${DISK}
    elif [ "$PROTOCOL" = "SCSI" ]; then
        echo "google-local-ssd-${DISK}"
        sudo blkdiscard /dev/disk/by-id/google-local-ssd-${DISK}
    else
        echo "Unknown protocol: $PROTOCOL"
    fi
    DISK=$((DISK+1))
done
