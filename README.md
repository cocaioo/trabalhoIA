# Jogo dos 8 - Algoritmos de Busca

## Descrição
Este projeto implementa o clássico problema do Jogo dos 8 (8-puzzle) utilizando diferentes algoritmos de busca:
- **BFS** (Busca em Largura)
- **DFS** (Busca em Profundidade com aprofundamento iterativo)
- **Busca Gulosa** (Heurística de distância Manhattan)
- **A*** (A-estrela: combina custo do caminho + heurística)

## Novas Funcionalidades

### 🎯 Visualização Passo a Passo
O programa agora oferece **duas interfaces complementares**:

1. **Interface de Visualização Passo a Passo** (Nova!)
   - Mostra o processo de busca em tempo real
   - Exibe o nó atual sendo expandido
   - Mostra a fronteira (próximos estados candidatos)
   - Apresenta estatísticas em tempo real (nós gerados, expandidos, visitados)
   - Para algoritmos heurísticos, mostra os valores de h(n), g(n) e f(n)

2. **Interface da Solução Final**
   - Exibe o caminho completo encontrado
   - Anima a sequência de movimentos
   - Mostra métricas finais da execução

### 🎮 Controles da Visualização Passo a Passo

**Botões:**
- **← Anterior**: Volta um passo
- **Próximo →**: Avança um passo
- **▶ Play / ⏸ Pausar**: Inicia/pausa a reprodução automática
- **Velocidade**: Alterna entre 1x e 3x
- **Pular para Final**: Vai direto para a solução final

**Teclas de Atalho:**
- **Seta Esquerda (←)**: Passo anterior
- **Seta Direita (→)**: Próximo passo
- **Espaço**: Pausar/continuar
- **ESC**: Sair da visualização

### 📊 Informações Exibidas

Durante a visualização passo a passo, você verá:
- **Nó Atual**: O estado sendo expandido (destacado em laranja)
- **Fronteira**: Até 8 próximos estados candidatos
- **Estatísticas**:
  - Nós gerados
  - Nós expandidos
  - Estados visitados
  - Valores heurísticos (quando aplicável)

### 🚀 Como Usar

1. Execute o programa
2. Clique nos quadrados para definir o estado inicial (números de 1 a 8)
3. Escolha um algoritmo (BFS, DFS, Guloso ou A*)
4. Aguarde a execução
5. **Primeiro**: Visualize o passo a passo do algoritmo
6. **Depois**: Veja a solução final animada

## Algoritmos Implementados

### BFS (Busca em Largura)
- Garante encontrar o caminho mais curto
- Usa uma fila (FIFO)
- Explora nível por nível

### DFS (Busca em Profundidade)
- Implementado com aprofundamento iterativo
- Usa uma pilha (LIFO)
- Explora em profundidade antes de retornar

### Busca Gulosa
- Usa heurística de distância Manhattan
- Sempre expande o nó mais promissor
- Não garante caminho ótimo

### A* (A-estrela)
- Combina custo do caminho (g) + heurística (h)
- f(n) = g(n) + h(n)
- Garante caminho ótimo com heurística admissível
- Mais eficiente que BFS

## Requisitos
- Python 3.x
- Pygame

## Instalação
```bash
pip install -r requirements.txt
```

## Execução
```bash
python trabalhoIA.py
```

## Entendendo o Processo de Busca

A visualização passo a passo permite compreender como cada algoritmo toma decisões:

- **BFS**: Observe como explora todos os estados de um nível antes de ir para o próximo
- **DFS**: Veja como vai fundo em uma ramificação antes de retornar
- **Guloso**: Perceba como sempre escolhe o estado com menor distância Manhattan
- **A***: Note como balanceia entre o custo do caminho e a estimativa para o objetivo

Isso torna o aprendizado dos algoritmos muito mais intuitivo e visual!
