#!/bin/bash

dir=/home/a001257/CODE/cf-conventions/cf-convention.github.io/Data/cf-standard-names
for ver in $(seq 1 84); do
    if [[ "$ver" != "38" ]]; then
        d="$dir/$ver/src"
        diff -c1 --color=always $d/cf-standard-name-table__ORIGINAL.xml $d/cf-standard-name-table.xml > ./DIFF-LOGS/diff_${ver}.txt
    fi
done
