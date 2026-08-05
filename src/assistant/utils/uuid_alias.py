import random
import string

def generate_unique_alias_id(length: int = 6) -> str:
    """
    Generate a short, random alias string like 'lyafce'.
    You can later replace this with something smarter if you want.
    """
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for _ in range(length))
