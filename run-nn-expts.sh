
# data pre-processing

raw_data="data/omorfi_noun_lexemes_filtered_inflected_all.txt"

subset_size=100000

random_subset="data/omorfi_noun_lexemes_filtered_inflected_random${subset_size}.txt"

# take a random subset of subset_size samples
shuf -n $subset_size $raw_data > $random_subset

datadir="data/fairseq/random${subset_size}"

# clstype="person"
# clstype="number"
clstype="case"

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

# fairseq-train $datadir/bin-$clstype \
#     --task simple_classification \
#     --arch pytorch_tutorial_rnn \
#     --optimizer adam --lr 0.001 --lr-shrink 0.5 \
#     --max-tokens 1000 \
#     --target-lang $clstype \
#     --save-dir checkpoints/$clstype

sbatch slrm-train-fairseq.sh \
    $datadir/bin-$clstype \
    $clstype \
    checkpoints/random${subset_size}/$clstype


subset_size=100000
# clstype="person"
# clstype="number"
clstype="case"
datadir="data/fairseq/random${subset_size}"

python eval_classifier.py \
    $datadir/bin-$clstype \
    --test-set $datadir/test \
    --target-lang $clstype \
    --path checkpoints/random${subset_size}/$clstype/checkpoint_best.pt \
    >> data/fairseq/rnn-results/results_random${subset_size}_${clstype}.txt





##### other test data set
#### preprocess json files
# clstype="person"
clstype="number"
clstype="case"
datadir=data/fairseq/random2000
subset_size=100000
# subset_size=10k

test_set_datadir="expts/random2000/data"

for clstype in "case" "number" "person"
do

    python preprocess.py \
        --wordforms-json ${test_set_datadir}/samples.json \
        --omorstrings-json ${test_set_datadir}/omorstrings.json \
        --output-dir $datadir \
        --train-valid-test-split "0-0-100" \
        --classtype $clstype

    orig_datadir="data/fairseq/random${subset_size}"

    python eval_classifier.py \
        $orig_datadir/bin-$clstype \
        --target-lang $clstype \
        --path checkpoints/random${subset_size}/$clstype/checkpoint_best.pt \
        --test-set $datadir/test \
        >> data/fairseq/rnn-results/results_random${subset_size}_${clstype}_random2000.txt
done