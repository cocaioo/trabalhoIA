import pygame
import sys
import time
from collections import deque

N = 3
TILE_SIZE = 100
WIDTH = N * TILE_SIZE
HEIGHT = N * TILE_SIZE + 140  # espaço para métricas e botões
FPS = 2

class PuzzleState:
    def __init__(self, board, x, y, depth):
        self.board = board
        self.x = x
        self.y = y
        self.depth = depth

moves = [(0, -1), (0, 1), (-1, 0), (1, 0)]

def is_goal_state(board):
    return board == [[1, 2, 3], [4, 5, 6], [7, 8, 0]]

def is_valid(x, y):
    return 0 <= x < N and 0 <= y < N

def find_zero(board):
    for i in range(N):
        for j in range(N):
            if board[i][j] == 0:
                return i, j
    raise ValueError("Board must contain a 0")

# --- Pygame helpers ---
def draw_board(screen, board, font, metrics=None, buttons=None):
    screen.fill((30, 30, 30))
    for i in range(N):
        for j in range(N):
            value = board[i][j]
            rect = pygame.Rect(j * TILE_SIZE, i * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            if value == 0:
                pygame.draw.rect(screen, (50, 50, 50), rect)
            else:
                pygame.draw.rect(screen, (0, 150, 200), rect)
                text = font.render(str(value), True, (255, 255, 255))
                text_rect = text.get_rect(center=rect.center)
                screen.blit(text, text_rect)
            pygame.draw.rect(screen, (20, 20, 20), rect, 3)

    if metrics:
        small_font = pygame.font.SysFont("Arial", 24, bold=True)
        lines = [
            f"Nós gerados: {metrics['generated']}",
            f"Nós verificados: {metrics['expanded']}",
            f"Profundidade: {metrics['depth']}",
            f"Tempo: {metrics['time']:.2f}s"
        ]
        for idx, line in enumerate(lines):
            text = small_font.render(line, True, (255, 255, 255))
            screen.blit(text, (10, HEIGHT - 140 + idx * 25))

    if buttons:
        for text, rect in buttons:
            pygame.draw.rect(screen, (100, 100, 100), rect)
            pygame.draw.rect(screen, (255, 255, 255), rect, 2)
            btn_font = pygame.font.SysFont("Arial", 22, bold=True)
            label = btn_font.render(text, True, (255, 255, 255))
            label_rect = label.get_rect(center=rect.center)
            screen.blit(label, label_rect)

    pygame.display.flip()

def input_start_board():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Defina o estado inicial")
    font = pygame.font.SysFont("Arial", 40, bold=True)

    board = [[None for _ in range(N)] for _ in range(N)]
    current_num = 1
    chosen_algo = None

    bfs_btn = pygame.Rect(30, HEIGHT - 60, 140, 40)
    dfs_btn = pygame.Rect(200, HEIGHT - 60, 140, 40)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                row, col = y // TILE_SIZE, x // TILE_SIZE
                if row < N and col < N and current_num <= 8 and board[row][col] is None:
                    board[row][col] = current_num
                    current_num += 1
                elif bfs_btn.collidepoint(event.pos) and current_num > 8:
                    for i in range(N):
                        for j in range(N):
                            if board[i][j] is None:
                                board[i][j] = 0
                    chosen_algo = "BFS"
                elif dfs_btn.collidepoint(event.pos) and current_num > 8:
                    for i in range(N):
                        for j in range(N):
                            if board[i][j] is None:
                                board[i][j] = 0
                    chosen_algo = "DFS"

        if chosen_algo:
            return board, chosen_algo

        buttons = [("Resolver BFS", bfs_btn), ("Resolver DFS", dfs_btn)] if current_num > 8 else None
        draw_board(screen, [[c if c is not None else 0 for c in r] for r in board], font, buttons=buttons)

# --- BFS ---
def solve_puzzle_bfs(start):
    x, y = find_zero(start)
    q = deque()
    visited = set()
    parent = {}

    q.append(PuzzleState([r[:] for r in start], x, y, 0))
    visited.add(tuple(map(tuple, start)))
    parent[tuple(map(tuple, start))] = None

    generated = 1
    expanded = 0
    start_time = time.time()

    while q:
        curr = q.popleft()
        expanded += 1

        if is_goal_state(curr.board):
            path = []
            state_tuple = tuple(map(tuple, curr.board))
            while state_tuple is not None:
                path.append([list(r) for r in state_tuple])
                state_tuple = parent[state_tuple]
            elapsed = time.time() - start_time
            return path[::-1], {"generated": generated, "expanded": expanded, "depth": curr.depth, "time": elapsed}

        for dx, dy in moves:
            nx, ny = curr.x + dx, curr.y + dy
            if is_valid(nx, ny):
                new_board = [r[:] for r in curr.board]
                new_board[curr.x][curr.y], new_board[nx][ny] = new_board[nx][ny], new_board[curr.x][curr.y]
                t = tuple(map(tuple, new_board))
                if t not in visited:
                    visited.add(t)
                    parent[t] = tuple(map(tuple, curr.board))
                    q.append(PuzzleState(new_board, nx, ny, curr.depth + 1))
                    generated += 1
    return [], {"generated": generated, "expanded": expanded, "depth": 0, "time": time.time() - start_time}

# --- DFS ---
def solve_puzzle_dfs(start):
    x, y = find_zero(start)
    stack = [PuzzleState([r[:] for r in start], x, y, 0)]
    visited = set([tuple(map(tuple, start))])
    parent = {tuple(map(tuple, start)): None}

    generated = 1
    expanded = 0
    start_time = time.time()

    while stack:
        curr = stack.pop()
        expanded += 1

        if is_goal_state(curr.board):
            path = []
            state_tuple = tuple(map(tuple, curr.board))
            while state_tuple is not None:
                path.append([list(r) for r in state_tuple])
                state_tuple = parent[state_tuple]
            elapsed = time.time() - start_time
            return path[::-1], {"generated": generated, "expanded": expanded, "depth": curr.depth, "time": elapsed}

        for dx, dy in moves:
            nx, ny = curr.x + dx, curr.y + dy
            if is_valid(nx, ny):
                new_board = [r[:] for r in curr.board]
                new_board[curr.x][curr.y], new_board[nx][ny] = new_board[nx][ny], new_board[curr.x][curr.y]
                t = tuple(map(tuple, new_board))
                if t not in visited:
                    visited.add(t)
                    parent[t] = tuple(map(tuple, curr.board))
                    stack.append(PuzzleState(new_board, nx, ny, curr.depth + 1))
                    generated += 1
    return [], {"generated": generated, "expanded": expanded, "depth": 0, "time": time.time() - start_time}

# --- Animação ---
def animate_solution(states, metrics):
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("8 Puzzle Solver")
    font = pygame.font.SysFont("Arial", 40, bold=True)
    clock = pygame.time.Clock()

    for board in states:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        draw_board(screen, board, font)
        clock.tick(FPS)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        draw_board(screen, states[-1], font, metrics)

if __name__ == "__main__":
    start, algo = input_start_board()
    if algo == "BFS":
        path, metrics = solve_puzzle_bfs(start)
    else:
        path, metrics = solve_puzzle_dfs(start)

    if path:
        animate_solution(path, metrics)
    else:
        print("Nenhuma solução encontrada.")
