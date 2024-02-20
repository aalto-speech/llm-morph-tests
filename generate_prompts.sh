#!/bin/bash

expt=$1
template_name=$2

expt_dir="expts/${expt}"
template_file=${expt_dir}/prompts/templates/${template_name}.sh

get_sample () {
    first_eg=$( cat inflected/*.txt | shuf -n 1 )

    word_form=$(echo $first_eg | awk '{print $2}')
    lemma=$(echo $first_eg | grep -o -P '(?<=WORD_ID=).*?(?=])')
    number=$(echo $first_eg | grep -o -P '(?<=NUM=).*?(?=])')
    gcase=$(echo $first_eg | grep -o -P '(?<=CASE=).*?(?=])')
    possessive=$(echo $first_eg | grep -o -P '(?<=POSS=).*?(?=])')
    
    # answer="$lemma $number $gcase $possessive"
    conv_number=$(python convert_label.py $number finnish-numbers.txt)
    conv_gcase=$(python convert_label.py $gcase finnish-cases.txt)
    conv_possessive=$(python convert_label.py $possessive finnish-persons.txt)
    answer="$lemma, $conv_number, $conv_gcase, $conv_possessive"
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

mkdir -p ${expt_dir}/prompts/generated/${template_name}
bash $template_file \
    "$word_form1" "$answer1" \
    "$word_form2" "$answer2" \
    "$word_form3" "$lemma" >> \
    ${expt_dir}/prompts/generated/${template_name}/${word_form3}.input

echo "$conv_number, $conv_gcase, $conv_possessive" \
    >> ${expt_dir}/prompts/generated/${template_name}/${word_form3}.ref
