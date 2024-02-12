#!/bin/bash

expt=$1
expt_dir="expts/${expt}"
config_file="${expt_dir}/config.sh"

. ${config_file}


# inflect lemmas with omorfi-generate.sh
cd omorfi
bash ../omorfi-inflect/permute-case-number-person.sh \
    ../${expt_dir}/lemmas.txt \
    ../${expt_dir}/cases.txt \
    ../${expt_dir}/numbers.txt \
    ../${expt_dir}/persons.txt \
    ../inflected

cd ..

# generate llm prompts from templates
template_file=${expt_dir}/prompts/templates/pt_short_2shot_english.sh

get_sample () {
    first_eg=$( cat inflected/*.txt | shuf -n 1 )

    word_form=$(echo $first_eg | awk '{print $2}')
    lemma=$(echo $first_eg | grep -o -P '(?<=WORD_ID=).*?(?=])')
    number=$(echo $first_eg | grep -o -P '(?<=NUM=).*?(?=])')
    gcase=$(echo $first_eg | grep -o -P '(?<=CASE=).*?(?=])')
    possessive=$(echo $first_eg | grep -o -P '(?<=POSS=).*?(?=])')
    
    answer="$lemma $number $gcase $possessive"
}

# parse tags
get_sample
word_form1=$word_form
answer1=$answer
get_sample
word_form2=$word_form
answer2=$answer
get_sample
word_form3=$word_form


bash $template_file \
    "$word_form1" "$answer1" \
    "$word_form2" "$answer2" \
    "$word_form3" "$lemma"

echo ""
echo "$answer"
