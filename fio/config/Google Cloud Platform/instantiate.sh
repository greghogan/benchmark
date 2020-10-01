#!/usr/bin/env sh

if [ $# -lt 3 ]; then
    echo "Usage: $0 <NVME|SCSI> <# of disks> <# of cores>"
    exit 1
fi

PROTOCOL=$1
NUMDISKS=$2
NUMCORES=$3

COMMAND="gcloud compute instances create ssd-test-instance
--image-project ubuntu-os-cloud
--image ubuntu-1804-bionic-v20190612
--preemptible
--machine-type n1-highcpu-${NUMCORES}"

for _ in $(seq 1 "$NUMDISKS"); do
    COMMAND="${COMMAND} --local-ssd interface=${PROTOCOL}"
done

echo "$COMMAND"
$COMMAND
