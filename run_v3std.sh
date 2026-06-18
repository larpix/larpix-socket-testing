#!/bin/bash
cd $1/baselines
for file in bpsraw*.h5 ; do
    cp $file testing.h5
    python ../../socket_baselines_v3std.py | grep -i entries > $file.dst
done
