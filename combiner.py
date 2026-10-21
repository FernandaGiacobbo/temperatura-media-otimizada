#É um mini reducer que roda na saída de cada mapper, antes do shuffle. Agrega os dados localmente, então, ao invés de enciar milhares de pares pela rede, cada mapper envia um só.

#Função que recebe uma chave e todos os valores que um mapper gerou pra ela
def combine_fn(chave, valores):
    soma = 0.0 #acumulador de temperaturas
    contagem = 0 #acumulador de quantos registros foram somados

    #Cada valor é uma tupla vinda do mapper
    for s, c in valores:
        soma += s
        contagem += c

    #Emite (soma, contagem) e não a média. Tem o mesmo formato da entrada e por isso o reducer funciona com ou sem combiner
    yield chave, (soma, contagem)
