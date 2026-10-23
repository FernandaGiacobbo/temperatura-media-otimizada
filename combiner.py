#É um mini reducer que roda na saída de cada mapper, antes do shuffle. Agrega os dados localmente, então, ao invés de enviar milhares de pares pela rede, cada mapper envia um só por coluna.
#Cada mapper soma os próprios pares: 5170 pares viram 40

#Função que recebe uma chave e todos os valores que um mapper gerou pra ela
def combine_fn(chave, valores):
    #Acumuladores: n, Σx, Σy, Σxy, Σx², Σy²
    total = [0, 0.0, 0.0, 0.0, 0.0, 0.0]

    #Cada valor é uma tupla de 6 somas parciais vinda do mapper
    for v in valores:
        for i in range(6):
            total[i] += v[i]

    #Emite as somas e NÃO a correlação. Tem o mesmo formato da entrada, por isso o reducer funciona com ou sem combiner. (A correlação de dois pedaços não pode ser "média de correlações": só as somas podem ser combinadas.)
    yield chave, tuple(total)