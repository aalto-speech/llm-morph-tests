
# data pre-processing

raw_data="data/omorfi_noun_lexemes_filtered_inflected_all.txt"

subset_size=1000

random_subset="data/omorfi_noun_lexemes_filtered_inflected_random${subset_size}.txt"

# take a random subset of subset_size samples
shuf -n $subset_size $raw_data > $random_subset

datadir="data/fairseq/random${subset_size}"

for clstype in  "person" "number" "case"
do
    python preprocess.py \
        --inflected-words $random_subset \
        --output-dir $datadir \
        --classtype $clstype

    fairseq-preprocess \
        --trainpref $datadir/train \
        --validpref $datadir/valid \
        --testpref $datadir/test \
        --source-lang input \
        --target-lang $clstype \
        --destdir $datadir/bin-${clstype} \
        --dataset-impl raw
done

# fairseq-train $datadir/bin-$clstype \
#     --task simple_classification \
#     --arch pytorch_tutorial_rnn \
#     --optimizer adam --lr 0.001 --lr-shrink 0.5 \
#     --max-tokens 1000 \
#     --target-lang $clstype \
#     --save-dir checkpoints/$clstype

for clstype in  "person" "number" "case"
do
    sbatch slrm-train-fairseq.sh \
        $datadir/bin-$clstype \
        $clstype \
        checkpoints/random${subset_size}/$clstype
done

subset_size=50000
clstype="person"
# clstype="number"
# clstype="case"
datadir="data/fairseq/random${subset_size}"

python eval_classifier.py \
    $datadir/bin-$clstype \
    --test-set $datadir/test \
    --target-lang $clstype \
    --path checkpoints/random${subset_size}/$clstype/checkpoint_best.pt \
    >> data/fairseq/rnn-results/results_random${subset_size}_${clstype}.txt





##### other test data set
#### preprocess json files
datadir=data/fairseq/random2000
test_set_datadir="expts/random2000/data"

for subset_size in 1000
do
    for clstype in  "person" "number" "case"
    do
        # python preprocess.py \
        #     --wordforms-json ${test_set_datadir}/samples.json \
        #     --omorstrings-json ${test_set_datadir}/omorstrings.json \
        #     --output-dir $datadir \
        #     --train-valid-test-split "0-0-100" \
        #     --classtype $clstype

        orig_datadir="data/fairseq/random${subset_size}"

        python eval_classifier.py \
            $orig_datadir/bin-$clstype \
            --target-lang $clstype \
            --path checkpoints/random${subset_size}/$clstype/checkpoint_best.pt \
            --test-set $datadir/test \
            > data/fairseq/rnn-results/results_random${subset_size}_${clstype}_random2000_new.txt
    done
done

####### visualise

resulttype=number
python visualise_results.py \
    --result-files data/fairseq/rnn-results/results_random*_${resulttype}_random2000_new.txt \
    --resulttype $resulttype \
    --output results_plot_rnn_${resulttype}.png \
    --rnn
