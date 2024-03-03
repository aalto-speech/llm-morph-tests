
def conllu_tags_to_dict(conllu_line):
    """Convert conllu tags separated by + to a dictionary."""
    splitted = conllu_line.split('+')
    tags = {}
    