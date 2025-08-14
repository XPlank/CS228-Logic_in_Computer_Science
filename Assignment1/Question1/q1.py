"""
sudoku_solver.py

Implement the function `solve_sudoku(grid: List[List[int]]) -> List[List[int]]` using a SAT solver from PySAT.
"""

from pysat.formula import CNF
from pysat.solvers import Solver
from typing import List

def conv(vars:List[int],cnf:CNF) :
    p=1
    ans:List[int] =[0,0,0,0,0,0,0,0,0]
    for i in range(2**9):
        if i==p :
            p*=2
        else :
            m=i
            for j in range(9):
                ans[j]=vars[j] if m%2==0 else -vars[j]
                m=int(m/2)
            cnf.append(ans)



def solve_sudoku(grid: List[List[int]]) -> List[List[int]]:
    """Solves a Sudoku puzzle using a SAT solver. Input is a 2D grid with 0s for blanks."""

    # TODO: implement encoding and solving using PySAT

    cnf=CNF()

    for row in range(9):
        for column in range(9):
            if grid[row][column] == 0 :
                continue
            else :
                # for num in range(1,10):
                #     cnf.append([((row+1)*100+(column+1)*10+num)*(1 if num == grid[row][column] else -1)])
                    cnf.append([(row+1)*100+(column+1)*10+grid[row][column]])

    Input:List[int] = [0,0,0,0,0,0,0,0,0]
    for row in range(1,10):
        for column in range(1,10):
            for num in range(1,10):
                Input[num-1]=(row*100+column*10+num)
            conv(Input,cnf)

    for row in range(1,10):
        for num in range(1,10):
            for column in range(1,10):
                Input[column-1]=(row*100+column*10+num)
            conv(Input,cnf)

    for column in range(1,10):
        for num in range(1,10):
            for row in range(1,10):
                Input[row-1]=(row*100+column*10+num)
            conv(Input,cnf)

    for i in range(0,7,3):
        for j in range(0,7,3):
            for num in range(1,10):
                Input=[]
                for row in range(1+i,4+i):
                    for column in range(1+j,4+j):
                        Input.append(row*100+column*10+num)
                conv(Input,cnf)

    with Solver(name='glucose3') as solver:
        solver.append_formula(cnf.clauses)
        if solver.solve():
            model = solver.get_model()
            # print("SAT solution:", model)
        else:
            print("UNSAT")

    for i in model :
        if i<0:
            continue
        else :
            grid[int(i/100)-1][(int(i/10)%10)-1]=(i%10)
        
    return grid