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
Classify Finnish words in the following morphological categories:
A. singular or plural
B. grammatical case;
C. possessive suffix;

Word: ${first_eg_word}
Classification: ${first_eg_word_answer}

Word: ${second_eg_word}
Classification: ${second_eg_word_answer}

Word: ${test_word}
Classification: ${test_word_answer}, 
EOF
