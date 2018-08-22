def plural(palavra):
    if palavra.endswith('r'):
        return palavra+'es'
    else:
        return palavra+'s'
    
def singular(palavra):
    if palavra.endswith('es'):
        return palavra[:-2]
    elif palavra.endswith('s'):
        return palavra[:-1]
    else:
        return palavra