#!/bin/sh

# define parameters which are passed in.
first_eg_word=$1
first_eg_word_answer=$2
second_eg_word=$3
second_eg_word_answer=$4
test_word=$5
test_word_answer=$6

# define the template. remove last newline with perl
cat  << EOF | perl -pe 'chomp if eof'
Luokittele suomenkieliset sanat seuraaviin morfologisiin kategorioihin:
A. yksikkö tai monikko,
B. sijamuoto,
C. omistusliite.

Sana: ${first_eg_word}
Luokittelu: ${first_eg_word_answer}

Sana: ${second_eg_word}
Luokittelu: ${second_eg_word_answer}

Sana: ${test_word}
Luokittelu: ${test_word_answer},
EOF
