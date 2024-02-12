#/bin/bash

# to run this script:
# bash ../omorfi-inflect/permute-case-number-person.sh \
#     ../expts/preliminary/lemmas.txt \
#     ../expts/preliminary/cases.txt \
#     ../expts/preliminary/numbers.txt \
#     ../expts/preliminary/persons.txt \
#     ../expts/preliminary/inflected

lemmas=$1
cases=$2
numbers=$3
persons=$4
output_dir=$5

for lemma in $(cat $lemmas)
do
    for case in $(cat $cases)
    do
        for number in $(cat $numbers)
        do
            for person in $(cat $persons)
            do
                output_file="${output_dir}/${lemma}-${case}.txt"
                omorstring="[WORD_ID=${lemma}][UPOS=NOUN][NUM=${number}][CASE=${case}][POSS=${person}]"
                # skip if omorstring in output file
                if [ ! -f $output_file ] || ! grep -qF "$omorstring" $output_file;
                then
                    echo "$omorstring"
                    printf "$omorstring" | bash src/bash/omorfi-generate.sh | \
                        grep WORD_ID=${lemma} | cut -f 1,2 \
                        >> $output_file
                fi
            done
        done
    done
done

#  grep -v inf |

# remove lines with question marks
# for file in $output_dir/*
# for file in inflected/*
# do
#     sed -i '/?/d' "$file"
# done

# for file in inflected/*
# do
#     sort -u "$file" > "${file}.tmp"
#     mv "${file}.tmp" "$file"
# done
