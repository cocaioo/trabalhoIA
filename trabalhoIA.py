import pygame
import sys
import time
from collections import deque

#variaveis para interface do tabuleiro
TAMANHO = 3 #tabuleiro 3x3
TAMANHO_PECA = 180 #tamanho da peça no tabuleiro
ESPACO_METRICAS = int(TAMANHO_PECA * 1.4)
LARGURA = TAMANHO * TAMANHO_PECA
ALTURA = TAMANHO * TAMANHO_PECA + ESPACO_METRICAS
FPS = 2
#variaveis para interface do tabuleiro

class EstadoPuzzle:
    def __init__(self, tabuleiro, linha_zero, coluna_zero, profundidade):
        self.tabuleiro = tabuleiro
        self.linha_zero = linha_zero
        self.coluna_zero = coluna_zero
        self.profundidade = profundidade


MOVIMENTOS = [(0, -1), (0, 1), (-1, 0), (1, 0)]


def eh_estado_objetivo(tabuleiro):
    return tabuleiro == [[1, 2, 3], [4, 5, 6], [7, 8, 0]]


def eh_valido(x, y):
    return 0 <= x < TAMANHO and 0 <= y < TAMANHO


def encontra_zero(tabuleiro):
    for i in range(TAMANHO):
        for j in range(TAMANHO):
            if tabuleiro[i][j] == 0:
                return i, j
    raise ValueError("O tabuleiro deve conter um 0")


def desenhar_tabuleiro(tela, tabuleiro, fonte, metricas=None, botoes=None):
    tela.fill((30, 30, 30))
    for i in range(TAMANHO):
        for j in range(TAMANHO):
            valor = tabuleiro[i][j]
            rect = pygame.Rect(j * TAMANHO_PECA, i * TAMANHO_PECA, TAMANHO_PECA, TAMANHO_PECA)
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
    tela = pygame.display.set_mode((LARGURA, ALTURA))
    pygame.display.set_caption("Defina o estado inicial")
    tamanho_fonte = max(24, int(TAMANHO_PECA * 0.44))
    fonte = pygame.font.SysFont("Arial", tamanho_fonte, bold=True)

    tabuleiro = [[None for _ in range(TAMANHO)] for _ in range(TAMANHO)]
    numero_atual = 1
    algoritmo_escolhido = None

    largura_btn = int(TAMANHO_PECA * 1.4)
    altura_btn = int(TAMANHO_PECA * 0.35)
    esquerda_x = 30
    btn_bfs = pygame.Rect(esquerda_x, ALTURA - altura_btn - 20, largura_btn, altura_btn)
    btn_dfs = pygame.Rect(esquerda_x + largura_btn + 30, ALTURA - altura_btn - 20, largura_btn, altura_btn)

    while True:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif evento.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                linha, coluna = y // TAMANHO_PECA, x // TAMANHO_PECA
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

        if algoritmo_escolhido:
            return tabuleiro, algoritmo_escolhido

        botoes = [("Resolver BFS", btn_bfs), ("Resolver DFS", btn_dfs)] if numero_atual > 8 else None
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


def animar_solucao(estados, metricas):
    pygame.init()
    tela = pygame.display.set_mode((LARGURA, ALTURA))
    pygame.display.set_caption("8 Puzzle Solver")
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
    if algoritmo == "BFS":
        caminho, metricas = resolver_puzzle_bfs(inicio)
    else:
        caminho, metricas = resolver_puzzle_dfs(inicio)

    if caminho:
        animar_solucao(caminho, metricas)
    else:
        print("Nenhuma solução encontrada.")
