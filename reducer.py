#Junta os resultados de todos os mappers e produz a correlação final de cada coluna
#soma as somas parciais de todos os mappers e aplica a fórmula de Pearson uma única vez por coluna

import math

#Recebe uma chave e as somas parciais de todos os mappers, já combinadas ou não
def reduce_fn(chave, valores):
    n, sx, sy, sxy, sxx, syy = 0, 0.0, 0.0, 0.0, 0.0, 0.0

    #Mesma agregação do combiner: soma as somas parciais
    for pn, psx, psy, psxy, psxx, psyy in valores:
        n += pn
        sx += psx
        sy += psy
        sxy += psxy
        sxx += psxx
        syy += psyy

    #Pearson: r = (nΣxy − ΣxΣy) / √[(nΣx² − (Σx)²) · (nΣy² − (Σy)²)]
    #A divisão acontece uma única vez, com os totais globais, o que garante o resultado exato
    cov = n * sxy - sx * sy
    var_x = n * sxx - sx * sx
    var_y = n * syy - sy * sy

    #Sem pelo menos 2 observações, ou com coluna constante (variância zero), a correlação não existe
    if n < 2 or var_x <= 0 or var_y <= 0:
        yield chave, (None, n)
        return

    r = cov / math.sqrt(var_x * var_y)
    r = max(-1.0, min(1.0, r))  #Evita 1.0000000002 por erro de arredondamento
    yield chave, (r, n)