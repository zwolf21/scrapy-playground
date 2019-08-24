import re
from collections.abc import Iterable

def parse_csv(values, apply=str):
    '''문자열 인수를 배열화 시켜준다.
    '''
    if isinstance(values, str):
        values = re.sub('/s', '', values)
        if ',' in values:
            results = values.split(',')
        elif '-' in values:
            results = values.split('-')
            s, *_, e = results
            s, e = int(s), int(e)
            results = range(s, e+1)
        else:
            results = [values]
        return list(map(apply, results))
    elif isinstance(values, (Iterable)):
        return list(map(apply, values))

    raise ValueError('values like: 1-10, 1,2,3,4')
