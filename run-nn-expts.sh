
# data pre-processing

raw_data="data/omorfi_noun_lexemes_filtered_inflected_all.txt"

python preprocess.py \
    --data $raw_data \
    --output_dir "data" \
    --n_samples 1000

# run rnn
python rnn.py \
    --data_dir "data" \
    --output_dir "expts/rnn" \
    --n_samples 1000 \
    --n_shot 0 \
    --word_class "noun" \
    --n_epochs 100

