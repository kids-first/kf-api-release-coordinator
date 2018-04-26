import random
import base32_crockford as b32


def kf_id_generator(prefix):
    """
    Returns a function to generator
    (Crockford)[http://www.crockford.com/wrmg/base32.html] base 32
    encoded number up to 8 characters left padded with 0 and prefixed with
    a two character value representing the entity type and delimited by
    an underscore
    Ex:
    'PT_0004PEDE'
    'SA_D167JSHP'
    'DM_ZZZZZZZZ'
    'ST_00000000'
    """
    assert len(prefix) == 2, 'Prefix must be two characters'
    prefix = prefix.upper()

    def generator():
        return '{0}_{1:0>8}'.format(prefix,
                                    b32.encode(random.randint(0, 32**8-1)))

    return generator
