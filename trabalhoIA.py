import pygame
import sys
import time
from collections import deque
import heapq
import itertools

contador_guloso = itertools.count()

LARGURA_JANELA = 800
ALTURA_JANELA = 700
TAMANHO = 3
#TAMANHO_PECA = 180
TAMANHO_PECA = 90
ESPACO_METRICAS = int(TAMANHO_PECA * 1.4)
LARGURA = TAMANHO * TAMANHO_PECA
ALTURA = TAMANHO * TAMANHO_PECA + ESPACO_METRICAS
FPS = 2

OFFSET_X = (LARGURA_JANELA - LARGURA) // 2
OFFSET_Y = ((ALTURA_JANELA - ALTURA) // 2)

ESTADO_OBJETIVO = [[1, 2, 3], [4, 5, 6], [7, 8, 0]]

POSICOES_ALVO = {}
for l in range(3):
    for c in range(3):
        POSICOES_ALVO[ESTADO_OBJETIVO[l][c]] = (l, c)

class EstadoPuzzle:
    def __init__(self, tabuleiro, linha_zero, coluna_zero, profundidade):
        self.tabuleiro = tabuleiro
        self.linha_zero = linha_zero
        self.coluna_zero = coluna_zero
        self.profundidade = profundidade


MOVIMENTOS = [(0, -1), (0, 1), (-1, 0), (1, 0)]


def eh_estado_objetivo(tabuleiro):
    return tabuleiro == ESTADO_OBJETIVO


def eh_valido(x, y):
    return 0 <= x < TAMANHO and 0 <= y < TAMANHO


def encontra_zero(tabuleiro):
    for i in range(TAMANHO):
        for j in range(TAMANHO):
            if tabuleiro[i][j] == 0:
                return i, j
    raise ValueError("O tabuleiro deve conter um 0")

def calcular_INVERSOES(tabuleiro):
    inversoes = 0
    lista = [num for linha in tabuleiro for num in linha if num != 0]

    for i in range(len(lista)):
        for j in range(i+1, len(lista)):
            if lista[i] > lista[j]:
                inversoes += 1

    return inversoes

def tem_solucao(tabuleiro):
    inversoes = calcular_INVERSOES(tabuleiro)

    return (inversoes % 2) == 0 #para o tabuleiro 3x3 o numero de inversoes precisa ser par

def desenhar_tabuleiro(tela, tabuleiro, fonte, metricas=None, botoes=None):
    tela.fill((30, 30, 30))
    for i in range(TAMANHO):
        for j in range(TAMANHO):
            valor = tabuleiro[i][j]
            #rect = pygame.Rect(j * TAMANHO_PECA, i * TAMANHO_PECA, TAMANHO_PECA, TAMANHO_PECA)
            rect = pygame.Rect(OFFSET_X + j * TAMANHO_PECA, OFFSET_Y + i * TAMANHO_PECA, TAMANHO_PECA, TAMANHO_PECA)
            if valor == 0:
                pygame.draw.rect(tela, (50, 50, 50), rect)
            else:
                pygame.draw.rect(tela, (0, 150, 200), rect)
                texto = fonte.render(str(valor), True, (255, 255, 255))
                texto_rect = texto.get_rect(center=rect.center)
                tela.blit(texto, texto_rect)
            borda = max(2, TAMANHO_PECA // 33)
            pygame.draw.rect(tela, (20, 20, 20), rect, borda)

    if metricas:
        tamanho_fonte_pequena = max(14, int(TAMANHO_PECA * 0.24))
        fonte_pequena = pygame.font.SysFont("Arial", tamanho_fonte_pequena, bold=True)
        linhas = [
            f"N\u00f3s gerados: {metricas['generated']}",
            f"N\u00f3s verificados: {metricas['expanded']}",
            f"Profundidade: {metricas['depth']}",
            f"Tempo: {metricas['time']:.2f}s"
        ]
        for idx, linha in enumerate(linhas):
            texto = fonte_pequena.render(linha, True, (255, 255, 255))
            y_texto = ALTURA - ESPACO_METRICAS + 10 + idx * int(TAMANHO_PECA * 0.25)
            tela.blit(texto, (10, y_texto))

    if botoes:
        tamanho_fonte_btn = max(16, int(TAMANHO_PECA * 0.22))
        fonte_btn = pygame.font.SysFont("Arial", tamanho_fonte_btn, bold=True)
        for texto, rect in botoes:
            pygame.draw.rect(tela, (100, 100, 100), rect)
            pygame.draw.rect(tela, (255, 255, 255), rect, max(2, TAMANHO_PECA // 50))
            label = fonte_btn.render(texto, True, (255, 255, 255))
            label_rect = label.get_rect(center=rect.center)
            tela.blit(label, label_rect)

    pygame.display.flip()


def entrada_tabuleiro_inicial():
    pygame.init()
    tela = pygame.display.set_mode((LARGURA_JANELA, ALTURA_JANELA))
    pygame.display.set_caption("Defina o estado inicial")
    tamanho_fonte = max(24, int(TAMANHO_PECA * 0.44))
    fonte = pygame.font.SysFont("Arial", tamanho_fonte, bold=True)

    tabuleiro = [[None for _ in range(TAMANHO)] for _ in range(TAMANHO)]
    numero_atual = 1
    algoritmo_escolhido = None

    largura_btn = int(TAMANHO_PECA * 1.8)
    altura_btn = int(TAMANHO_PECA * 0.35)
    espaco_entre_btns = 30
    total_largura_btns = 3 * largura_btn + 2 * espaco_entre_btns
    esquerda_x = (LARGURA_JANELA - total_largura_btns) // 2

    btn_bfs = pygame.Rect(esquerda_x, ALTURA_JANELA - altura_btn - 20, largura_btn, altura_btn)
    btn_dfs = pygame.Rect(esquerda_x + largura_btn + espaco_entre_btns, ALTURA_JANELA - altura_btn - 20, largura_btn, altura_btn)
    btn_guloso = pygame.Rect(esquerda_x + 2 * (largura_btn + espaco_entre_btns), ALTURA_JANELA - altura_btn - 20, largura_btn, altura_btn)

    while True:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif evento.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                tab_x = x - OFFSET_X
                tab_y = y - OFFSET_Y
                linha, coluna = tab_y // TAMANHO_PECA, tab_x // TAMANHO_PECA
                if linha < TAMANHO and coluna < TAMANHO and numero_atual <= 8 and tabuleiro[linha][coluna] is None:
                    tabuleiro[linha][coluna] = numero_atual
                    numero_atual += 1
                elif btn_bfs.collidepoint(evento.pos) and numero_atual > 8:
                    for i in range(TAMANHO):
                        for j in range(TAMANHO):
                            if tabuleiro[i][j] is None:
                                tabuleiro[i][j] = 0
                    algoritmo_escolhido = "BFS"
                elif btn_dfs.collidepoint(evento.pos) and numero_atual > 8:
                    for i in range(TAMANHO):
                        for j in range(TAMANHO):
                            if tabuleiro[i][j] is None:
                                tabuleiro[i][j] = 0
                    algoritmo_escolhido = "DFS"
                elif btn_guloso.collidepoint(evento.pos) and numero_atual > 8:
                    for i in range(TAMANHO):
                        for j in range(TAMANHO):
                            if tabuleiro[i][j] is None:
                                tabuleiro[i][j] = 0
                    algoritmo_escolhido = "GULOSO"

        if algoritmo_escolhido:
            return tabuleiro, algoritmo_escolhido

        botoes = [("Resolver BFS", btn_bfs), ("Resolver DFS", btn_dfs), ("Resolver Guloso", btn_guloso)] if numero_atual > 8 else None
        desenhar_tabuleiro(tela, [[c if c is not None else 0 for c in r] for r in tabuleiro], fonte, botoes=botoes)


def resolver_puzzle_bfs(inicio_tabuleiro):
    linha_zero, coluna_zero = encontra_zero(inicio_tabuleiro)
    fila = deque()
    visitados = set()
    pai = {}

    fila.append(EstadoPuzzle([r[:] for r in inicio_tabuleiro], linha_zero, coluna_zero, 0))
    visitados.add(tuple(map(tuple, inicio_tabuleiro)))
    pai[tuple(map(tuple, inicio_tabuleiro))] = None

    gerados = 1
    expandidos = 0
    tempo_inicio = time.time()

    while fila:
        atual = fila.popleft()
        expandidos += 1

        if eh_estado_objetivo(atual.tabuleiro):
            caminho = []
            tupla_estado = tuple(map(tuple, atual.tabuleiro))
            while tupla_estado is not None:
                caminho.append([list(r) for r in tupla_estado])
                tupla_estado = pai[tupla_estado]
            tempo_passado = time.time() - tempo_inicio
            return caminho[::-1], {"generated": gerados, "expanded": expandidos, "depth": atual.profundidade, "time": tempo_passado}

        for dx, dy in MOVIMENTOS:
            nlinha, ncoluna = atual.linha_zero + dx, atual.coluna_zero + dy
            if eh_valido(nlinha, ncoluna):
                novo_tabuleiro = [r[:] for r in atual.tabuleiro]
                novo_tabuleiro[atual.linha_zero][atual.coluna_zero], novo_tabuleiro[nlinha][ncoluna] = novo_tabuleiro[nlinha][ncoluna], novo_tabuleiro[atual.linha_zero][atual.coluna_zero]
                t = tuple(map(tuple, novo_tabuleiro))
                if t not in visitados:
                    visitados.add(t)
                    pai[t] = tuple(map(tuple, atual.tabuleiro))
                    fila.append(EstadoPuzzle(novo_tabuleiro, nlinha, ncoluna, atual.profundidade + 1))
                    gerados += 1
    return [], {"generated": gerados, "expanded": expandidos, "depth": 0, "time": time.time() - tempo_inicio}


def resolver_puzzle_dfs(inicio_tabuleiro):
    limite_maximo = 50
    total_gerados = 0
    total_expandidos = 0
    tempo_inicio = time.time()

    tupla_inicio = tuple(map(tuple, inicio_tabuleiro))

    def dfs_limitado(limite):
        linha_zero, coluna_zero = encontra_zero(inicio_tabuleiro)
        pilha = [EstadoPuzzle([r[:] for r in inicio_tabuleiro], linha_zero, coluna_zero, 0)]
        visitados = set([tupla_inicio])
        pai = {tupla_inicio: None}

        gerados = 1
        expandidos = 0

        while pilha:
            atual = pilha.pop()
            expandidos += 1

            if eh_estado_objetivo(atual.tabuleiro):
                caminho = []
                tupla_estado = tuple(map(tuple, atual.tabuleiro))
                while tupla_estado is not None:
                    caminho.append([list(r) for r in tupla_estado])
                    tupla_estado = pai[tupla_estado]
                return caminho[::-1], {"generated": gerados, "expanded": expandidos, "depth": atual.profundidade}

            if atual.profundidade < limite:
                for dx, dy in MOVIMENTOS:
                    nlinha, ncoluna = atual.linha_zero + dx, atual.coluna_zero + dy
                    if eh_valido(nlinha, ncoluna):
                        novo_tabuleiro = [r[:] for r in atual.tabuleiro]
                        novo_tabuleiro[atual.linha_zero][atual.coluna_zero], novo_tabuleiro[nlinha][ncoluna] = novo_tabuleiro[nlinha][ncoluna], novo_tabuleiro[atual.linha_zero][atual.coluna_zero]
                        t = tuple(map(tuple, novo_tabuleiro))
                        if t not in visitados:
                            visitados.add(t)
                            pai[t] = tuple(map(tuple, atual.tabuleiro))
                            pilha.append(EstadoPuzzle(novo_tabuleiro, nlinha, ncoluna, atual.profundidade + 1))
                            gerados += 1

        return None, {"generated": gerados, "expanded": expandidos, "depth": None}

    for limite in range(0, limite_maximo + 1):
        resultado, estatisticas = dfs_limitado(limite)
        total_gerados += estatisticas["generated"]
        total_expandidos += estatisticas["expanded"]
        if resultado:
            tempo_passado = time.time() - tempo_inicio
            return resultado, {"generated": total_gerados, "expanded": total_expandidos, "depth": len(resultado) - 1, "time": tempo_passado}

    tempo_passado = time.time() - tempo_inicio
    return [], {"generated": total_gerados, "expanded": total_expandidos, "depth": 0, "time": tempo_passado}

def calcula_heuristica(tabuleiro):
    #Distância Manhattan: é a soma das distancias verticais e horizontais de cada peça até a sua posição correta
    soma_total_dist = 0
    for linha in range(TAMANHO):
        for coluna in range(TAMANHO):
            peca = tabuleiro[linha][coluna]
            if peca != 0: #zero nao conta:
                linha_correta, coluna_correta = POSICOES_ALVO[peca]
                #calculo da distancia (cumulativo) = modulo dist linha + modulo dist coluna
                soma_total_dist += abs(linha - linha_correta) + abs(coluna - coluna_correta)
    return soma_total_dist



def resolver_puzzle_guloso(inicio_tabuleiro):
    linha_zero, coluna_zero = encontra_zero(inicio_tabuleiro)
    soma_inicial = calcula_heuristica(inicio_tabuleiro)

    estado_inicial = EstadoPuzzle([r[:] for r in inicio_tabuleiro], linha_zero, coluna_zero, profundidade=0)

    # fila de prioridade
    fila_prioridade = [(soma_inicial, estado_inicial.profundidade, next(contador_guloso), estado_inicial)]

    tupla_inicial = tuple(map(tuple, inicio_tabuleiro))
    visitados = {tupla_inicial}

    pai = {tupla_inicial: None}

    gerados = 1
    expandidos = 0
    tempo_inicio = time.time()

    while fila_prioridade:
        # estado de menor valor de heurística
        _, _, _, atual = heapq.heappop(fila_prioridade)
        expandidos += 1

        tupla_atual = tuple(map(tuple, atual.tabuleiro))

        if eh_estado_objetivo(atual.tabuleiro):
            caminho = []
            tupla_estado = tupla_atual
            while tupla_estado is not None:
                caminho.append([list(r) for r in tupla_estado])
                tupla_estado = pai.get(tupla_estado)
            
            tempo_passado = time.time() - tempo_inicio

            return caminho[::-1], {
                "generated": gerados, 
                "expanded": expandidos, 
                "depth": atual.profundidade, 
                "time": tempo_passado}
        
        # gera e avalia os sucessores
        for dx, dy in MOVIMENTOS:
            nlinha, ncoluna = atual.linha_zero + dx, atual.coluna_zero + dy 

            if eh_valido(nlinha, ncoluna):
                novo_tabuleiro = [r[:] for r in atual.tabuleiro]
                novo_tabuleiro[atual.linha_zero][atual.coluna_zero], novo_tabuleiro[nlinha][ncoluna] = \
                    novo_tabuleiro[nlinha][ncoluna], novo_tabuleiro[atual.linha_zero][atual.coluna_zero]
                
                t = tuple(map(tuple, novo_tabuleiro))
                
                if t not in visitados:
                    # cálculo guloso: a heurística é o fator decisivo
                    soma_nova = calcula_heuristica(novo_tabuleiro)
                    
                    novo_estado = EstadoPuzzle(
                        tabuleiro=novo_tabuleiro, 
                        linha_zero=nlinha, 
                        coluna_zero=ncoluna, 
                        profundidade=atual.profundidade + 1
                    )
                    
                    # insere na fila de prioridade, com um contador para evitar comparações diretas de estados com mesmo valor de soma
                    heapq.heappush(fila_prioridade, (soma_nova, novo_estado.profundidade, next(contador_guloso), novo_estado))
                    
                    # Atualiza os conjuntos de controle
                    visitados.add(t)
                    pai[t] = tupla_atual
                    gerados += 1

    # Se a fila esvaziar e o objetivo não for encontrado
    tempo_passado = time.time() - tempo_inicio
    return [], {"generated": gerados, "expanded": expandidos, "depth": 0, "time": tempo_passado}

def resolver_puzzle_a_estrela(inicio_tabuleiro):
    pass

def animar_solucao(estados, metricas):
    pygame.init()
    tela = pygame.display.set_mode((LARGURA_JANELA, ALTURA_JANELA))
    pygame.display.set_caption("Jogo dos 8")
    tamanho_fonte = max(24, int(TAMANHO_PECA * 0.44))
    fonte = pygame.font.SysFont("Arial", tamanho_fonte, bold=True)
    relogio = pygame.time.Clock()

    for tabuleiro in estados:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        desenhar_tabuleiro(tela, tabuleiro, fonte)
        relogio.tick(FPS)

    while True:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        desenhar_tabuleiro(tela, estados[-1], fonte, metricas)


if __name__ == "__main__":
    inicio, algoritmo = entrada_tabuleiro_inicial()

    if not tem_solucao(inicio):
        print("\n🚫 Esse estado inicial não possui soluçao, pois possui uma quantidade impar de inversoes.")
        pygame.quit()
        sys.exit()

    if algoritmo == "BFS":
        caminho, metricas = resolver_puzzle_bfs(inicio)
    elif algoritmo == "DFS":
        caminho, metricas = resolver_puzzle_dfs(inicio)
    else:
        caminho, metricas = resolver_puzzle_guloso(inicio)

    if caminho:
        animar_solucao(caminho, metricas)
    else:
        print("Nenhuma solução encontrada devido ao limite de profundidade.")
