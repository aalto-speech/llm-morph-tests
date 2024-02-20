#/bin/bash

# to run this script:
# bash ../omorfi-inflect/permute-case-number-person.sh \
#     ../expts/preliminary/lemmas.txt \
#     ../expts/preliminary/cases.txt \
#     ../expts/preliminary/numbers.txt \
#     ../expts/preliminary/persons.txt \
#     ../expts/preliminary/inflected

# lemmas=$1
# cases=$2
# numbers=$3
# persons=$4
# output_dir=$5

for lemma in su
do
    for case in acc abl gen dat loc nom
    do
        for number in sg pl
        do
            for person in 1s 2s 3s 1p 2p 3p
            do
                output_file="${output_dir}/${lemma}-${case}.txt"
                feat_string="lemma<n><${number}><${case}><${person}>"
                # skip if omorstring in output file
                if [ ! -f $output_file ] || ! grep -qF "$feat_string" $output_file;
                then
                    echo "$feat_string"
                    echo "$feat_string" | turkish-generate-words >> $output_file
                fi
            done
        done
    done
done
