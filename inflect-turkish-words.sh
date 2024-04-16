#/bin/bash



# output_dir=$1

for lemma in su
do
    for case in '<acc>' '<abl>' '<gen>' '<dat>' '<loc>' '<nom>' ''
    do
        for number in '<sg>' '<pl>' ''
        do
            for person in '<1s>' '<2s>' '<3s>' '<1p>' '<2p>' '<3p>' ''
            do
                output_file="${output_dir}/${lemma}-${case}.txt"
                feat_string="${lemma}<n>${number}${case}${person}"
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

# alternative for the same task
for lemma in su
do
    for case in nom acc abl gen dat loc
    do
        for number in sg pl
        do
            for person in 1s 2s 3s 1p 2p 3p
            do
                output_file="${output_dir}/${lemma}-${case}.txt"

                feat_string="${lemma}<n>"
                if [ $number != "sg" ]
                then
                    feat_string="${feat_string}<${number}>"
                fi
                if [ $case != "nom" ]
                then
                    feat_string="${feat_string}<${case}>"
                fi
                feat_string="${feat_string}<${person}>"
                # skip if omorstring in output file
                if [ ! -f $output_file ] || ! grep -qF "$feat_string" $output_file;
                then
                    # echo "$feat_string"
                    echo "$feat_string" | turkish-generate-words |grep -v ? >> $output_file
                fi
            done
        done
    done
done
