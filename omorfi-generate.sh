echo kauppa > kauppa.wordlist
bash src/bash/generate-wordlist.sh kauppa.wordlist kauppa.wordforms
hfst-lookup src/generated/omorfi.describe.hfst -q < kauppa.wordforms |\
	sed -e 's/\[WORD_ID=kauppa\]\[UPOS=//' |\
	tr '][' '  ' | tr -s '\n' | sed -e 's/[0-9, ]*$//' |\
	fgrep -v DRV | fgrep -v COMPOUND | fgrep -v WORD_ID=kaupata
