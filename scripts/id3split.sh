#!/bin/bash
# This file splits an mp3 file into id3 and the rest.

#   First argument is the path of input mp3 file.
#   Second, if supplied,  a destination file for id3
#   Third, if supplied, a destination file for the rest of the file
#

id3_header_size=$(python ./id3size.py $1) ;

if [ -n "$2" ]; then
    head -c+$id3_header_size $1 > $2
fi

if [ -n "$3" ]; then
    tail -c+$((id3_header_size+1)) $1 > $3
fi