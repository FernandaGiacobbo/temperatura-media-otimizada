#Junta os resultados de todos os mappers e produz a resposta final

#Recebe uma chave e os valores de todos os mappers, já combinados ou não
def reduce_fn(chave, valores):
    soma = 0.0
    contagem = 0

    #Mesma agregação do combiner: soma as somas e as contagens parciais
    for s, c in valores:
        soma += s
        contagem += c

    #A divisão acontece, uma única vez, com ostotais globais. garante o resultado exato: soma_total e contagem_total
    yield chave, soma / contagem
