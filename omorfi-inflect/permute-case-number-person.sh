#/bin/bash

for lemma in vesi talo auto
do
    for case in GEN # GEN PAR ABE ABL ALL ADE INE ILL ESS TRA INS COM
    do
        for number in SG PL
        do
            for person in SG1 SG2 SG3 PL1 PL2 PL3 1 2 3
            do
                # printf "$number $case $person "
                omorstring="[WORD_ID=${lemma}][UPOS=NOUN][NUM=${number}][CASE=${case}][POSS=${person}]"
                printf "$omorstring" | bash src/bash/omorfi-generate.sh | \
                    grep WORD_ID=${lemma} | grep -v inf | cut -f 1,2 \
                    >> omorfi-inflected-${lemma}-${case}.txt
                # echo ""
                
            done
        done
        # echo "----------------------------------------------------------------"
    done
done
