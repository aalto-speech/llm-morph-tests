#!/bin/bash
# adapted from omorfi/src/bash/generate-wordlist.sh

if test $# -lt 3 ; then
    echo Usage $0 LEMMAFILE OUTFILE TEMPFILE
    exit 1
fi
cat $1 | while read l; do
    echo ${l}...
    echo ${l} |\
        sed -e 's/./\0 /g' |\
        sed -e 's/[$_]/%\0/g' |\
        sed -e 's/   / %  /g' |\
        sed -e 's/^/%[WORD%_ID%= /' -e 's/$/%] \\%[WORD%_ID%=* ;/' |\
        hfst-regexp2fst -o omorfi/src/generated/${3}.wordform.hfst
        hfst-compose -v -F omorfi/src/generated/temporary.describe.hfst \
            omorfi/src/generated/${3}.wordform.hfst \
            -o omorfi/src/generated/${3}.wordgen.hfst
        hfst-fst2strings omorfi/src/generated/${3}.wordgen.hfst |\
        grep -v CLIT= |\
        grep -v DRV= |\
        grep -v STYLE= |\
        grep -v POSITION= |\
        uniq >> $2
    echo >> $2
done
