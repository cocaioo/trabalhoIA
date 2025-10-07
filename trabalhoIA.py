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

    return (inversoes % 2) == 0

def desenhar_tabuleiro(tela, tabuleiro, fonte, metricas=None, botoes=None):
    tela.fill((30, 30, 30))
    for i in range(TAMANHO):
        for j in range(TAMANHO):
            valor = tabuleiro[i][j]
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
            f"Tempo: {metricas['time']*1000:.2f}ms"
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

    largura_btn = int(TAMANHO_PECA * 1.5)
    altura_btn = int(TAMANHO_PECA * 0.5)
    espaco_entre_btns = 20
    total_largura_btns = 4 * largura_btn + 3 * espaco_entre_btns
    esquerda_x = (LARGURA_JANELA - total_largura_btns) // 2

    btn_bfs = pygame.Rect(esquerda_x, ALTURA_JANELA - altura_btn - 180, largura_btn, altura_btn)
    btn_dfs = pygame.Rect(esquerda_x + largura_btn + espaco_entre_btns, ALTURA_JANELA - altura_btn - 180, largura_btn, altura_btn)
    btn_guloso = pygame.Rect(esquerda_x + 2 * (largura_btn + espaco_entre_btns), ALTURA_JANELA - altura_btn - 180, largura_btn, altura_btn)
    btn_a_estrela = pygame.Rect(esquerda_x + 3 * (largura_btn + espaco_entre_btns), ALTURA_JANELA - altura_btn - 180, largura_btn, altura_btn)

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
                elif btn_a_estrela.collidepoint(evento.pos) and numero_atual > 8:
                    for i in range(TAMANHO):
                        for j in range(TAMANHO):
                            if tabuleiro[i][j] is None:
                                tabuleiro[i][j] = 0
                    algoritmo_escolhido = "A_ESTRELA"

        if algoritmo_escolhido:
            return tabuleiro, algoritmo_escolhido

        botoes = [("BFS", btn_bfs), ("DFS", btn_dfs), ("Guloso", btn_guloso), ("A*", btn_a_estrela)] if numero_atual > 8 else None
        
        desenhar_tabuleiro(tela, [[c if c is not None else 0 for c in r] for r in tabuleiro], fonte, botoes=botoes)


def resolver_puzzle_bfs(inicio_tabuleiro):
    linha_zero, coluna_zero = encontra_zero(inicio_tabuleiro)
    fila = deque()
    visitados = set()
    pai = {}
    passos = []

    fila.append(EstadoPuzzle([r[:] for r in inicio_tabuleiro], linha_zero, coluna_zero, 0))
    visitados.add(tuple(map(tuple, inicio_tabuleiro)))
    pai[tuple(map(tuple, inicio_tabuleiro))] = None

    gerados = 1
    expandidos = 0
    tempo_inicio = time.time()

    while fila:
        atual = fila.popleft()
        expandidos += 1

        passos.append({
            "atual": [r[:] for r in atual.tabuleiro],
            "fronteira": [],
            "visitados": len(visitados),
            "gerados": gerados,
            "expandidos": expandidos
        })

        if eh_estado_objetivo(atual.tabuleiro):
            caminho = []
            tupla_estado = tuple(map(tuple, atual.tabuleiro))
            while tupla_estado is not None:
                caminho.append([list(r) for r in tupla_estado])
                tupla_estado = pai[tupla_estado]
            tempo_passado = time.time() - tempo_inicio
            return caminho[::-1], {"generated": gerados, "expanded": expandidos, "depth": atual.profundidade, "time": tempo_passado}, passos

        sucessores_gerados = []
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
                    sucessores_gerados.append([r[:] for r in novo_tabuleiro])
        
        passos.append({
            "atual": [r[:] for r in atual.tabuleiro],
            "fronteira": sucessores_gerados,
            "visitados": len(visitados),
            "gerados": gerados,
            "expandidos": expandidos
        })
    return [], {"generated": gerados, "expanded": expandidos, "depth": 0, "time": time.time() - tempo_inicio}, passos


def resolver_puzzle_dfs(inicio_tabuleiro):
    limite_maximo = 50
    total_gerados = 0
    total_expandidos = 0
    tempo_inicio = time.time()
    todos_passos = []

    tupla_inicio = tuple(map(tuple, inicio_tabuleiro))

    def dfs_classico(limite):
        linha_zero, coluna_zero = encontra_zero(inicio_tabuleiro)
        pilha = [EstadoPuzzle([r[:] for r in inicio_tabuleiro], linha_zero, coluna_zero, 0)]
        pai = {tupla_inicio: None}
        
        gerados = 1
        expandidos = 0
        passos = []
        profundidade_anterior = -1
        
        while pilha:
            atual = pilha.pop()
            expandidos += 1
            
            backtracking = atual.profundidade < profundidade_anterior
            profundidade_anterior = atual.profundidade
            
            passos.append({
                "atual": [r[:] for r in atual.tabuleiro],
                "fronteira": [],
                "visitados": expandidos,
                "gerados": gerados,
                "expandidos": expandidos,
                "limite": limite,
                "profundidade_atual": atual.profundidade,
                "backtracking": backtracking
            })
            
            if eh_estado_objetivo(atual.tabuleiro):
                caminho = []
                tupla_estado = tuple(map(tuple, atual.tabuleiro))
                while tupla_estado is not None:
                    caminho.append([list(r) for r in tupla_estado])
                    tupla_estado = pai[tupla_estado]
                return caminho[::-1], {"generated": gerados, "expanded": expandidos, "depth": atual.profundidade}, passos
            
            sucessores_gerados = [] 
            if atual.profundidade < limite:
                sucessores = []
                for dx, dy in MOVIMENTOS:
                    nlinha, ncoluna = atual.linha_zero + dx, atual.coluna_zero + dy
                    if eh_valido(nlinha, ncoluna):
                        novo_tabuleiro = [r[:] for r in atual.tabuleiro]
                        novo_tabuleiro[atual.linha_zero][atual.coluna_zero], novo_tabuleiro[nlinha][ncoluna] = \
                            novo_tabuleiro[nlinha][ncoluna], novo_tabuleiro[atual.linha_zero][atual.coluna_zero]
                        
                        tupla_novo = tuple(map(tuple, novo_tabuleiro))
                        tupla_atual = tuple(map(tuple, atual.tabuleiro))
                        if pai.get(tupla_atual) != tupla_novo:
                            sucessores.append(EstadoPuzzle(novo_tabuleiro, nlinha, ncoluna, atual.profundidade + 1))
                            pai[tupla_novo] = tupla_atual
                            gerados += 1
                
                for sucessor in sucessores:
                    pilha.append(sucessor)
                
                sucessores_gerados = [[list(r) for r in s.tabuleiro] for s in sucessores]

            passos.append({
                "atual": [r[:] for r in atual.tabuleiro],
                "fronteira": sucessores_gerados, 
                "visitados": expandidos,
                "gerados": gerados,
                "expandidos": expandidos,
                "limite": limite,
                "profundidade_atual": atual.profundidade,
                "backtracking": backtracking
            })
        
        return None, {"generated": gerados, "expanded": expandidos, "depth": None}, passos

    for limite in range(30, limite_maximo + 1):
        resultado, estatisticas, passos = dfs_classico(limite)
        total_gerados += estatisticas["generated"]
        total_expandidos += estatisticas["expanded"]
        
        for passo in passos:
            if not todos_passos or passo["atual"] != todos_passos[-1]["atual"]:
                todos_passos.append(passo)
            elif passo["atual"] == todos_passos[-1]["atual"]:
                todos_passos[-1].update({
                    "gerados": passo["gerados"],
                    "expandidos": passo["expandidos"],
                    "visitados": passo["visitados"],
                    "limite": passo["limite"]
                })
        
        if resultado:
            tempo_passado = time.time() - tempo_inicio
            return resultado, {"generated": total_gerados, "expanded": total_expandidos, "depth": len(resultado) - 1, "time": tempo_passado}, todos_passos

    tempo_passado = time.time() - tempo_inicio
    return [], {"generated": total_gerados, "expanded": total_expandidos, "depth": 0, "time": tempo_passado}, todos_passos

def calcula_heuristica(tabuleiro):
    soma_total_dist = 0
    for linha in range(TAMANHO):
        for coluna in range(TAMANHO):
            peca = tabuleiro[linha][coluna]
            if peca != 0:
                linha_correta, coluna_correta = POSICOES_ALVO[peca]
                soma_total_dist += abs(linha - linha_correta) + abs(coluna - coluna_correta)
    return soma_total_dist


def resolver_puzzle_guloso(inicio_tabuleiro):
    linha_zero, coluna_zero = encontra_zero(inicio_tabuleiro)
    soma_inicial = calcula_heuristica(inicio_tabuleiro)

    estado_inicial = EstadoPuzzle([r[:] for r in inicio_tabuleiro], linha_zero, coluna_zero, profundidade=0)

    fila_prioridade = [(soma_inicial, estado_inicial.profundidade, next(contador_guloso), estado_inicial)]

    tupla_inicial = tuple(map(tuple, inicio_tabuleiro))
    visitados = {tupla_inicial}

    pai = {tupla_inicial: None}

    gerados = 1
    expandidos = 0
    tempo_inicio = time.time()
    passos = []

    while fila_prioridade:
        _, _, _, atual = heapq.heappop(fila_prioridade)
        expandidos += 1

        tupla_atual = tuple(map(tuple, atual.tabuleiro))

        passos.append({
            "atual": [r[:] for r in atual.tabuleiro],
            "fronteira": [],
            "visitados": len(visitados),
            "gerados": gerados,
            "expandidos": expandidos,
            "heuristica": calcula_heuristica(atual.tabuleiro)
        })

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
                "time": tempo_passado}, passos
        
        sucessores_gerados = []
        for dx, dy in MOVIMENTOS:
            nlinha, ncoluna = atual.linha_zero + dx, atual.coluna_zero + dy 

            if eh_valido(nlinha, ncoluna):
                novo_tabuleiro = [r[:] for r in atual.tabuleiro]
                novo_tabuleiro[atual.linha_zero][atual.coluna_zero], novo_tabuleiro[nlinha][ncoluna] = novo_tabuleiro[nlinha][ncoluna], novo_tabuleiro[atual.linha_zero][atual.coluna_zero]
                
                t = tuple(map(tuple, novo_tabuleiro))
                
                if t not in visitados:
                    soma_nova = calcula_heuristica(novo_tabuleiro)
                    novo_estado = EstadoPuzzle(
                        tabuleiro=novo_tabuleiro, 
                        linha_zero=nlinha, 
                        coluna_zero=ncoluna, 
                        profundidade=atual.profundidade + 1
                    )
                    heapq.heappush(fila_prioridade, (soma_nova, novo_estado.profundidade, next(contador_guloso), novo_estado))
                    visitados.add(t)
                    pai[t] = tupla_atual
                    gerados += 1
                    sucessores_gerados.append((novo_tabuleiro, soma_nova))
        
        fronteira_estados = [s[0] for s in sucessores_gerados]
        fronteira_h = [s[1] for s in sucessores_gerados]
        passos.append({
            "atual": [r[:] for r in atual.tabuleiro],
            "fronteira": fronteira_estados,
            "fronteira_heuristicas": fronteira_h,
            "visitados": len(visitados),
            "gerados": gerados,
            "expandidos": expandidos,
            "heuristica": calcula_heuristica(atual.tabuleiro)
        })

    tempo_passado = time.time() - tempo_inicio
    return [], {"generated": gerados, "expanded": expandidos, "depth": 0, "time": tempo_passado}, passos

def resolver_puzzle_a_estrela(inicio_tabuleiro):
    linha_zero, coluna_zero = encontra_zero(inicio_tabuleiro)
    heuristica_inicial = calcula_heuristica(inicio_tabuleiro)
    
    estado_inicial = EstadoPuzzle([r[:] for r in inicio_tabuleiro], linha_zero, coluna_zero, profundidade=0)
    
    fila_prioridade = [(heuristica_inicial, heuristica_inicial, next(contador_guloso), estado_inicial)]
    
    tupla_inicial = tuple(map(tuple, inicio_tabuleiro))
    visitados = {tupla_inicial}
    pai = {tupla_inicial: None}
    
    gerados = 1
    expandidos = 0
    tempo_inicio = time.time()
    passos = []
    
    while fila_prioridade:
        f_atual, h_atual, _, atual = heapq.heappop(fila_prioridade)
        expandidos += 1
        
        tupla_atual = tuple(map(tuple, atual.tabuleiro))
        
        passos.append({
            "atual": [r[:] for r in atual.tabuleiro],
            "fronteira": [],
            "visitados": len(visitados),
            "gerados": gerados,
            "expandidos": expandidos,
            "heuristica": h_atual,
            "custo_g": atual.profundidade,
            "custo_f": f_atual
        })
        
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
                "time": tempo_passado
            }, passos
        
        sucessores_gerados = []
        for dx, dy in MOVIMENTOS:
            nlinha, ncoluna = atual.linha_zero + dx, atual.coluna_zero + dy
            
            if eh_valido(nlinha, ncoluna):
                novo_tabuleiro = [r[:] for r in atual.tabuleiro]
                novo_tabuleiro[atual.linha_zero][atual.coluna_zero], novo_tabuleiro[nlinha][ncoluna] = \
                    novo_tabuleiro[nlinha][ncoluna], novo_tabuleiro[atual.linha_zero][atual.coluna_zero]
                
                t = tuple(map(tuple, novo_tabuleiro))
                
                if t not in visitados:
                    g_novo = atual.profundidade + 1
                    h_novo = calcula_heuristica(novo_tabuleiro)
                    f_novo = g_novo + h_novo
                    
                    novo_estado = EstadoPuzzle(
                        tabuleiro=novo_tabuleiro,
                        linha_zero=nlinha,
                        coluna_zero=ncoluna,
                        profundidade=g_novo
                    )
                    
                    heapq.heappush(fila_prioridade, (f_novo, h_novo, next(contador_guloso), novo_estado))
                    
                    visitados.add(t)
                    pai[t] = tupla_atual
                    gerados += 1
                    sucessores_gerados.append((novo_tabuleiro, h_novo, g_novo, f_novo))
        
        fronteira_estados = [s[0] for s in sucessores_gerados]
        fronteira_h = [s[1] for s in sucessores_gerados]
        fronteira_g = [s[2] for s in sucessores_gerados]
        fronteira_f = [s[3] for s in sucessores_gerados]
        passos.append({
            "atual": [r[:] for r in atual.tabuleiro],
            "fronteira": fronteira_estados,
            "fronteira_heuristicas": fronteira_h,
            "fronteira_g": fronteira_g,
            "fronteira_f": fronteira_f,
            "visitados": len(visitados),
            "gerados": gerados,
            "expandidos": expandidos,
            "heuristica": h_atual,
            "custo_g": atual.profundidade,
            "custo_f": f_atual
        })
    
    tempo_passado = time.time() - tempo_inicio
    return [], {"generated": gerados, "expanded": expandidos, "depth": 0, "time": tempo_passado}, passos

def visualizar_passo_a_passo(passos, algoritmo):
    pygame.init()
    largura_viz = 1200
    altura_viz = 700
    tela = pygame.display.set_mode((largura_viz, altura_viz))
    pygame.display.set_caption(f"Passo a Passo - {algoritmo}")
    
    tamanho_fonte = max(20, int(TAMANHO_PECA * 0.35))
    fonte = pygame.font.SysFont("Arial", tamanho_fonte, bold=True)
    fonte_pequena = pygame.font.SysFont("Arial", 16, bold=False)
    fonte_titulo = pygame.font.SysFont("Arial", 18, bold=True)
    
    relogio = pygame.time.Clock()
    passo_atual = 0
    pausado = True
    velocidade = 1
    tempo_ultimo_passo = 0
    
    tam_peca_pequeno = 50
    margem_esquerda = 50
    margem_topo = 80
    
    btn_largura = 100
    btn_altura = 35
    btn_y = altura_viz - 60
    btn_anterior = pygame.Rect(margem_esquerda, btn_y, btn_largura, btn_altura)
    btn_proximo = pygame.Rect(margem_esquerda + btn_largura + 20, btn_y, btn_largura, btn_altura)
    btn_play_pause = pygame.Rect(margem_esquerda + 2 * (btn_largura + 20), btn_y, btn_largura, btn_altura)
    btn_velocidade = pygame.Rect(margem_esquerda + 3 * (btn_largura + 20), btn_y, btn_largura, btn_altura)
    btn_pular = pygame.Rect(margem_esquerda + 4 * (btn_largura + 20), btn_y, btn_largura + 50, btn_altura)
    
    def desenhar_tabuleiro_pequeno(tela, tabuleiro, x, y, tam_peca, cor_fundo=(0, 150, 200), destacar=False):
        for i in range(TAMANHO):
            for j in range(TAMANHO):
                valor = tabuleiro[i][j]
                rect = pygame.Rect(x + j * tam_peca, y + i * tam_peca, tam_peca, tam_peca)
                if valor == 0:
                    pygame.draw.rect(tela, (50, 50, 50), rect)
                else:
                    pygame.draw.rect(tela, cor_fundo, rect)
                    texto = fonte_pequena.render(str(valor), True, (255, 255, 255))
                    texto_rect = texto.get_rect(center=rect.center)
                    tela.blit(texto, texto_rect)
                borda_largura = 3 if destacar else 1
                cor_borda = (255, 255, 0) if destacar else (20, 20, 20)
                pygame.draw.rect(tela, cor_borda, rect, borda_largura)
    
    def desenhar_botao(tela, rect, texto, cor=(100, 100, 100)):
        pygame.draw.rect(tela, cor, rect)
        pygame.draw.rect(tela, (255, 255, 255), rect, 2)
        label = fonte_pequena.render(texto, True, (255, 255, 255))
        label_rect = label.get_rect(center=rect.center)
        tela.blit(label, label_rect)
    
    while True:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return
            elif evento.type == pygame.MOUSEBUTTONDOWN:
                if btn_anterior.collidepoint(evento.pos):
                    passo_atual = max(0, passo_atual - 1)
                    pausado = True
                elif btn_proximo.collidepoint(evento.pos):
                    passo_atual = min(len(passos) - 1, passo_atual + 1)
                    pausado = True
                elif btn_play_pause.collidepoint(evento.pos):
                    pausado = not pausado
                elif btn_velocidade.collidepoint(evento.pos):
                    velocidade = 3 if velocidade == 1 else 1
                elif btn_pular.collidepoint(evento.pos):
                    return
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_SPACE:
                    pausado = not pausado
                elif evento.key == pygame.K_LEFT:
                    passo_atual = max(0, passo_atual - 1)
                    pausado = True
                elif evento.key == pygame.K_RIGHT:
                    passo_atual = min(len(passos) - 1, passo_atual + 1)
                    pausado = True
                elif evento.key == pygame.K_ESCAPE:
                    return
        
        if not pausado:
            tempo_atual = pygame.time.get_ticks()
            intervalo = 1000 / velocidade
            if tempo_atual - tempo_ultimo_passo >= intervalo:
                passo_atual += 1
                tempo_ultimo_passo = tempo_atual
                if passo_atual >= len(passos):
                    pausado = True
                    passo_atual = len(passos) - 1
        
        passo = passos[passo_atual]
        
        tela.fill((30, 30, 30))
        
        titulo = fonte_titulo.render(f"Algoritmo: {algoritmo} - Passo {passo_atual + 1} de {len(passos)}", True, (255, 255, 255))
        tela.blit(titulo, (margem_esquerda, 20))
        
        label_atual = fonte_titulo.render("Nó Atual (Expandindo):", True, (255, 200, 100))
        tela.blit(label_atual, (margem_esquerda, margem_topo - 30))
        
        if passo.get("backtracking", False):
            fonte_backtrack = pygame.font.SysFont("Arial", 26, bold=True)
            msg_backtrack = fonte_backtrack.render("⚠️ BACKTRACKING ⚠️", True, (255, 255, 255))
            
            largura_banner = 350
            altura_banner = 80
            margem_direita = 20
            margem_inferior = 100
            
            x_banner = largura_viz - largura_banner - margem_direita
            y_banner = altura_viz - altura_banner - margem_inferior
            
            rect_backtrack = pygame.Rect(x_banner, y_banner, largura_banner, altura_banner)
            
            sombra = pygame.Rect(x_banner + 3, y_banner + 3, largura_banner, altura_banner)
            pygame.draw.rect(tela, (40, 10, 10), sombra, border_radius=10)
            
            pygame.draw.rect(tela, (150, 20, 20), rect_backtrack, border_radius=10)
            pygame.draw.rect(tela, (255, 100, 100), rect_backtrack, 5, border_radius=10)
            
            texto_rect = msg_backtrack.get_rect(center=(rect_backtrack.centerx, rect_backtrack.centery - 12))
            tela.blit(msg_backtrack, texto_rect)
            
            fonte_explicacao = pygame.font.SysFont("Arial", 13, bold=False)
            explicacao = fonte_explicacao.render("Voltando para explorar", True, (255, 220, 220))
            explicacao2 = fonte_explicacao.render("outro caminho", True, (255, 220, 220))
            
            exp_rect = explicacao.get_rect(center=(rect_backtrack.centerx, rect_backtrack.centery + 15))
            exp2_rect = explicacao2.get_rect(center=(rect_backtrack.centerx, rect_backtrack.centery + 30))
            
            tela.blit(explicacao, exp_rect)
            tela.blit(explicacao2, exp2_rect)
        
        desenhar_tabuleiro_pequeno(tela, passo["atual"], margem_esquerda, margem_topo, tam_peca_pequeno, cor_fundo=(200, 100, 50), destacar=True)
        
        stats_x = margem_esquerda + TAMANHO * tam_peca_pequeno + 30
        stats_y = margem_topo
        stats = [
            f"Nós Gerados: {passo['gerados']}",
            f"Nós Expandidos: {passo['expandidos']}",
            f"Visitados: {passo['visitados']}"
        ]
        
        if 'heuristica' in passo:
            stats.append(f"Heurística h(n): {passo['heuristica']}")
        if 'custo_g' in passo:
            stats.append(f"Custo g(n): {passo['custo_g']}")
        if 'custo_f' in passo:
            stats.append(f"Custo f(n): {passo['custo_f']}")
        if 'limite' in passo:
            stats.append(f"Limite DFS: {passo['limite']}")
        if 'profundidade_atual' in passo:
            stats.append(f"Profundidade: {passo['profundidade_atual']}")
        
        for idx, stat in enumerate(stats):
            texto_stat = fonte_pequena.render(stat, True, (255, 255, 255))
            tela.blit(texto_stat, (stats_x, stats_y + idx * 25))
        
        label_fronteira = fonte_titulo.render("Fronteira (próximos candidatos):", True, (100, 200, 255))
        fronteira_y = margem_topo + TAMANHO * tam_peca_pequeno + 50
        tela.blit(label_fronteira, (margem_esquerda, fronteira_y - 30))
        
        max_mostrar = min(8, len(passo["fronteira"]))
        for idx, tabuleiro_front in enumerate(passo["fronteira"][:max_mostrar]):
            col = idx % 4
            row = idx // 4
            x = margem_esquerda + col * (TAMANHO * tam_peca_pequeno + 20)
            y = fronteira_y + row * (TAMANHO * tam_peca_pequeno + 10)
            desenhar_tabuleiro_pequeno(tela, tabuleiro_front, x, y, tam_peca_pequeno, cor_fundo=(50, 150, 200))
        
        if len(passo["fronteira"]) > max_mostrar:
            texto_mais = fonte_pequena.render(f"... e mais {len(passo['fronteira']) - max_mostrar} estados na fronteira", True, (180, 180, 180))
            tela.blit(texto_mais, (margem_esquerda, fronteira_y + 2 * (TAMANHO * tam_peca_pequeno + 10) + 10))
        
        desenhar_botao(tela, btn_anterior, "← Anterior")
        desenhar_botao(tela, btn_proximo, "Próximo →")
        desenhar_botao(tela, btn_play_pause, "⏸ Pausar" if not pausado else "▶ Play")
        desenhar_botao(tela, btn_velocidade, f"Velocidade: {velocidade}x")
        desenhar_botao(tela, btn_pular, "Pular para Final", cor=(150, 50, 50))
        
        instrucoes = fonte_pequena.render("Controles: Setas ←/→, Espaço (pausar), ESC (sair)", True, (150, 150, 150))
        tela.blit(instrucoes, (margem_esquerda, btn_y - 30))
        
        pygame.display.flip()
        relogio.tick(60)

def animar_solucao(estados, metricas):
    pygame.init()
    tela = pygame.display.set_mode((LARGURA_JANELA, ALTURA_JANELA))
    pygame.display.set_caption("Jogo dos 8")
    tamanho_fonte = max(24, int(TAMANHO_PECA * 0.44))
    fonte = pygame.font.SysFont("Arial", tamanho_fonte, bold=True)
    relogio = pygame.time.Clock()

    for i, tabuleiro in enumerate(estados):
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
        caminho, metricas, passos = resolver_puzzle_bfs(inicio)
    elif algoritmo == "DFS":
        caminho, metricas, passos = resolver_puzzle_dfs(inicio)
    elif algoritmo == "GULOSO":
        caminho, metricas, passos = resolver_puzzle_guloso(inicio)
    elif algoritmo == "A_ESTRELA":
        caminho, metricas, passos = resolver_puzzle_a_estrela(inicio)
    else:
        print("Algoritmo não reconhecido.")
        pygame.quit()
        sys.exit()

    if caminho:
        visualizar_passo_a_passo(passos, algoritmo)
        animar_solucao(caminho, metricas)
    else:
        print("Nenhuma solução encontrada devido ao limite de profundidade.")