#Transforma cada linha bruta do CSV em pares chave-valor. Cada par carrega as somas parciais necessárias para calcular a correlação de Pearson entre a temperatura (X) e outra coluna (Y).
#Confere se cada linha é válida. Se for, emite 1 par por coluna com os 6 números

import math

INDICE_TEMPERATURA = 8  #Posição da temperatura (coluna 9) em cada linha
TOTAL_CAMPOS = 13       #Número de campos esperado em cada linha completa

#Colunas numéricas que serão correlacionadas com a temperatura (nome -> posição).
#As colunas 2 e 3 (mês e dia da semana) ficam de fora porque são texto ("mar", "fri"): correlação de Pearson só faz sentido entre números.
COLUNAS_Y = {
    "X": 0, "Y": 1,
    "FFMC": 4, "DMC": 5, "DC": 6, "ISI": 7,
    "RH": 9, "wind": 10, "rain": 11, "area": 12,
}


def linha_valida(linha):
    #Garante a integridade do registro ANTES de qualquer cálculo. Devolve (x, [y1, y2, ...]) ou None se a linha tiver qualquer problema.
    #A linha é aceita ou descartada INTEIRA. Se cada correlação descartasse linhas por conta própria, cada uma usaria um n diferente e os resultados não seriam comparáveis.

    campos = linha.strip().split(",")
    if len(campos) != TOTAL_CAMPOS:  #Linha incompleta, vazia ou cabeçalho mal formado
        return None

    try:
        x = float(campos[INDICE_TEMPERATURA])
        ys = [float(campos[i]) for i in COLUNAS_Y.values()]
    except ValueError:  #Algum campo não é número (texto, vazio, cabeçalho)
        return None

    #float() aceita "nan" e "inf" sem dar erro, mas eles contaminariam todas as somas
    if not all(math.isfinite(v) for v in [x] + ys):
        return None

    return x, ys


#Recebe uma linha do CSV e emite um par para cada coluna Y: (chave, (n, Σx, Σy, Σxy, Σx², Σy²)).
def map_fn(linha):

    registro = linha_valida(linha)
    if registro is None:
        return  #Linha descartada por inteiro: nenhum par é emitido

    x, ys = registro
    for nome, y in zip(COLUNAS_Y, ys):
        #Como este registro é uma única observação, cada soma parcial é o próprio valor (n = 1)
        yield f"temperatura x {nome}", (1, x, y, x * y, x * x, y * y)