#Simula o que o hadoop faria: divide a entrada, executa o mapper, combiner e shuffle, chama o reducer e roda as verificações

import sys
from collections import defaultdict

from mapper import map_fn
from combiner import combine_fn
from reducer import reduce_fn


def dividir_em_splits(linhas, n):
    #Divide a entrada em n splits (cada um seria processado por um mapper). Cada split contém linhas inteiras, então nenhum registro é cortado ao meio.
    tam = max(1, -(-len(linhas) // n))  #Divisão com arredondamento para cima (teto)
    return [linhas[i:i + tam] for i in range(0, len(linhas), tam)]


def agrupar(pares):
    #Agrupa os valores por chave. Equivale ao shuffle do Hadoop, que entrega ao reducer todos os valores de uma mesma chave juntos. O Shuffle junta tudo que tem a mesma chave
    grupos = defaultdict(list)
    for chave, valor in pares:
        grupos[chave].append(valor)
    return grupos


def executar(linhas, n_mappers=4, usar_combiner=True):

    #Roda o pipeline completo e devolve (resultado, pares emitidos, pares enviados)
    saida_para_reducer = []  #Tudo o que passa pela rede até o reducer
    emitidos_pelos_mappers = 0  #Contador só pra comparar o ganho do combiner

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


def conferir(resultado, linhas):
    #Verificação independente: recalcula tudo de uma vez, sem MapReduce, com statistics.correlation (Python 3.10+), e devolve a maior diferença encontrada
    from statistics import correlation
    from mapper import linha_valida, COLUNAS_Y

    registros = [r for r in (linha_valida(l) for l in linhas) if r is not None]
    xs = [x for x, _ in registros]
    maior = 0.0
    for i, nome in enumerate(COLUNAS_Y):
        ys = [ys_[i] for _, ys_ in registros]
        try:
            esperado = correlation(xs, ys)
        except Exception:  #coluna constante
            continue
        obtido = resultado[f"temperatura x {nome}"][0]
        if obtido is not None:
            maior = max(maior, abs(obtido - esperado))
    return maior


if __name__ == "__main__":

    #Pega o caminho do CSV pela linha de comando, ou usa o padrão
    caminho = sys.argv[1] if len(sys.argv) > 1 else "forestfireinput.csv"
    with open(caminho, encoding="utf-8") as f:
        linhas = f.readlines()

    #Executa duas vezes, com e sem combiner, para comparar
    resultados = {}
    for usar in (False, True):
        res, emitidos, enviados = executar(linhas, n_mappers=4, usar_combiner=usar)
        resultados[usar] = res
        rotulo = "COM combiner" if usar else "SEM combiner"
        print(f"{rotulo}: pares emitidos pelos mappers = {emitidos} | "
              f"pares enviados ao reducer = {enviados}")

    print(f"\nLinhas lidas: {len(linhas)}")
    print(f"\n{'Correlação':<24}{'r':>10}{'n':>6}")
    for chave, (r, n) in resultados[True].items():
        texto = f"{r:+.4f}" if r is not None else "indefinida"
        print(f"{chave:<24}{texto:>10}{n:>6}")

    #Prova 1: o combiner não pode alterar o resultado
    iguais = all(
        resultados[True][k][0] is not None and abs(resultados[True][k][0] - resultados[False][k][0]) < 1e-9
        for k in resultados[True] if resultados[True][k][0] is not None
    )
    print(f"\nResultado igual com e sem combiner: {'sim' if iguais else 'NÃO'}")

    #Prova 2: bate com o cálculo direto, sem MapReduce
    try:
        print(f"Maior diferença para o cálculo direto: {conferir(resultados[True], linhas):.2e}")
    except ImportError:
        print("statistics.correlation indisponível (Python < 3.10): pulei a conferência")