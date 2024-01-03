def gen_slug(*args):
    fields = ['d1id', 'dirId', 'docId', 'answerNo', 'commentNo']
    tkns = [f"{f}-{v}" for f, v in zip(fields, args)]
    return '-'.join(tkns)