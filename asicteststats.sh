#/usr/bin/bash
#
#
export datadir='/data'
export batch=$1
export file=$datadir/$batch/netconfig$batch.csv
echo checking file $file
head -n 2 $file 
tail -n 1 $file
((asics=`awk -F , '{print $2}'  $file  | uniq |grep -c ''` - 1 ))
#echo $asics1
#(( asics= $asics1 - 1 ))
echo $asics
