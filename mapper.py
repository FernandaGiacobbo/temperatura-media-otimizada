#Transforma cada linha bruta do CSV em um par chave-valor que o resto do pipeline sabe processar

INDICE_TEMPERATURA = 8  #Posição da temperatura em cada linha
CHAVE = "temperatura"

#Recebe uma linha do CSV e emite pares (chave, (temperatura, 1)).
def map_fn(linha):

    campos = linha.strip().split(",") #Quebra a linha nas vírgulas, virando uma lista de strings
    if len(campos) <= INDICE_TEMPERATURA: #Se a linha não tiver o número esperado de campos, ignora
        return  
    try:
        temperatura = float(campos[INDICE_TEMPERATURA]) #Converte tudo para número pq o CSV guarda tudo como texto.
    except ValueError:
        return 
    #Emite o resultado sem encerrar a função. O valor é uma tupla (soma, contagem) - como esse registro é uma única temperatura, a soma parcial é a própria temperatura e a contagem é 1. 
    yield CHAVE, (temperatura, 1)
