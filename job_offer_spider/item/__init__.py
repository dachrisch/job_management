import re


def remove_non_letters(string: str):
    return re.sub(r'[^A-Za-z0-9 ]+', '', string)
