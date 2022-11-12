import random
import string


def get_random_code():
    return (''.join((random.choice(string.ascii_letters)
                    + random.choice(string.digits) for x in range(5)))
            )
