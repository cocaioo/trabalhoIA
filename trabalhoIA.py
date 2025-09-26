import tkinter as tk

def toMatrix():
    pass

#busca em largura
def BFS():
    currently_state = (1,2,3,4,5,6,7,8,0)
    final_state = (1,2,3,4,5,6,7,0,8)

    steps = 0
    queue = []

    while currently_state != final_state:
        i = currently_state.index(0)
        row, column = divmod(i, 3)

        Upper = None
        Lower = None
        Left = None
        Right = None
        
        
#busca em profundidade
def DFS():
    steps = 0
    pass

