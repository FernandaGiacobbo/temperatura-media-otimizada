#No Hadoop, o framework cuida de dividir a entrada, distribuir os mappers e fazer um shuffle. O main simula essas etapas para enxergar o fluxo completo.

import sys
from collections import defaultdict

from mapper import map_fn
from combiner import combine_fn
from reducer import reduce_fn


def dividir_em_splits(linhas, n):
    #Divide a entrada em n splits (cada um seria processado por um mapper). No Hadoop, cada split seria processado por um mapper diferente
    tam = -(-len(linhas) // n)  #Divisão com arredondamento para cima (teto)
    return [linhas[i:i + tam] for i in range(0, len(linhas), tam)]


def agrupar(pares):
    #Agrupa os valores por chave. Equivale ao shuffle do Hadoop, que entrega ao reduver todos os valores de uma mesma chave juntos
    grupos = defaultdict(list)
    for chave, valor in pares:
        grupos[chave].append(valor)
    return grupos


def executar(linhas, n_mappers=4, usar_combiner=True):

    #Roda o pipeline completo e devolve (resultado, pares emitidos, pares enviados)
    saida_para_reducer = [] #Tudo o que passa pela rede até o reducer
    emitidos_pelos_mappers = 0 #Contador só pra comparar o ganho do combiner

    #Cada iteração representa um mapper trabalhando no seu split.
    for split in dividir_em_splits(linhas, n_mappers):

        #MAP - aplica map_fn em cada linha do split e junta tudo numa lista
        saida_map = [par for linha in split for par in map_fn(linha)]
        emitidos_pelos_mappers += len(saida_map)

        #Combine: roda localmente, só sobre a saída desse mapper
        if usar_combiner:
            for chave, valores in agrupar(saida_map).items():
                saida_para_reducer.extend(combine_fn(chave, valores))
        else:
            #Sem combiner, todos os pares crus seguem direto para o reducer
            saida_para_reducer.extend(saida_map)

    #Shuffle + reduce: agrupa por chave e aplica o reducer sobre cada grupo
    resultado = {}
    for chave, valores in agrupar(saida_para_reducer).items():
        for k, v in reduce_fn(chave, valores):
            resultado[k] = v

    return resultado, emitidos_pelos_mappers, len(saida_para_reducer)


if __name__ == "__main__":

    #Pega o caminho do CSV pela linha de comando, ou usa o padrão
    caminho = sys.argv[1] if len(sys.argv) > 1 else "forestfireinput.csv"
    with open(caminho, encoding="utf-8") as f:
        linhas = f.readlines()

    #Executa duas vezes, com e sem combiner, para comparar
    for usar in (False, True):
        res, emitidos, enviados = executar(linhas, n_mappers=4, usar_combiner=usar)
        rotulo = "COM combiner" if usar else "SEM combiner"
        print(f"{rotulo}: média = {res['temperatura']:.4f} | "
              f"pares emitidos pelos mappers = {emitidos} | "
              f"pares enviados ao reducer = {enviados}")
