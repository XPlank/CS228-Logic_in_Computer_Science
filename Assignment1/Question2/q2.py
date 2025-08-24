    """
Sokoban Solver using SAT (Boilerplate)
--------------------------------------
Instructions:
- Implement encoding of Sokoban into CNF.
- Use PySAT to solve the CNF and extract moves.
- Ensure constraints for player movement, box pushes, and goal conditions.

Grid Encoding:
- 'P' = Player
- 'B' = Box
- 'G' = Goal
- '#' = Wall
- '.' = Empty space
"""

from pysat.formula import CNF
from pysat.solvers import Solver

# Directions for movement
DIRS = {'U': (-1, 0), 'D': (1, 0), 'L': (0, -1), 'R': (0, 1)}


class SokobanEncoder:
    def __init__(self, grid, T):
        """
        Initialize encoder with grid and time limit.

        Args:
            grid (list[list[str]]): Sokoban grid.
            T (int): Max number of steps allowed.
        """
        self.grid = grid
        self.T = T
        self.N = len(grid)
        self.M = len(grid[0])
        self.T_max = 20
        self.goals = []
        self.boxes = []
        self.player_start = None

        # TODO: Parse grid to fill self.goals, self.boxes, self.player_start
        self._parse_grid()

        self.num_boxes = len(self.boxes)
        self.cnf = CNF()

    def _parse_grid(self):
        """Parse grid to find player, boxes, and goals."""
        # TODO: Implement parsing logic
        for row in range(self.N):
            for col in range(self.M):
                if self.grid[row][col]=='P':
                    self.player_start = (row,col)
                if self.grid[row][col] == 'B':
                    self.boxes.append((row,col))
                if self.grid[row][col] == 'G':
                    self.goals.append((row,col))
                
        
    # ---------------- Variable Encoding ----------------
    def var_player(self, x, y, t):
        """
        Variable ID for player at (x, y) at time t.
        """
        # TODO: Implement encoding scheme
        return (t + (self.T_max)*y + (self.T_max)*(self.M)*x)
        

    def var_box(self, b, x, y, t):
        """
        Variable ID for box b at (x, y) at time t.
        """
        # TODO: Implement encoding scheme
        return (t + (self.T_max)*y + (self.T_max)*(self.M)*x + (self.T_max)*(self.M)*(self.N)*b)

    # ---------------- Encoding Logic ----------------
    def encode(self):
        """
        Build CNF constraints for Sokoban:
        - Initial state
        - Valid moves (player + box pushes)
        - Non-overlapping boxes
        - Goal condition at final timestep
        """
        # TODO: Add constraints for:
        # 1. Initial conditions
        # 2. Player movement
        # 3. Box movement (push rules)
        # 4. Non-overlap constraints
        # 5. Goal conditions
        # 6. Other conditions
    #set walls to false
        self._parse_grid()
        for row in range(self.N):
            for col in range(self.M):
                if self.grid[row][col] == '#':
                    for t in range(self.T_max):
                        self.cnf.append([-self.var_player(row, col, t)])
                        for b in range(1,self.num_boxes+1):
                            self.cnf.append([-self.var_box(b, row, col, t)])
        #set initial positions
        self.cnf.append([self.var_player(self.player_start[0],self.player_start[1],0)])
        b=1
        for (row,col) in self.boxes:
            self.cnf.append([self.var_box(b,row,col,0)])
            b+=1
        #atleast one pos for each box
        for t in range(self.T):
            for b in range(1, self.num_boxes + 1):
                clause = []
                for row in range(self.N):
                    for col in range(self.M):
                        if self.grid[row][col] != '#':
                            clause.append(self.var_box(b, row, col, t))
                self.cnf.append(clause)
        #atmost one position for each box 
        for t in range(self.T):
            for b in range(1, self.num_boxes + 1):
                positions = []
                for row in range(self.N):
                    for col in range(self.M):
                        if self.grid[row][col] != '#':
                            positions.append((row, col))
                for i in range(len(positions)):
                    for j in range(i + 1, len(positions)):
                        self.cnf.append([-self.var_box(b, positions[i][0], positions[i][1], t), -self.var_box(b, positions[j][0], positions[j][1], t)])
        #player movement
        for t in range(self.T):
            for row in range(self.N):
                for col in range(self.M):
                    clause =[]
                    for x,y in DIRS.values():
                        if 0<=row+x<self.N and 0<=col+y<self.M:
                            clause.append(self.var_player(row+x,col+y,t+1))
                    self.cnf.append([-self.var_player(row,col,t),self.var_player(row,col,t+1)]+clause)
                    for i in range(len(clause)):
                        for j in range(i+1,len(clause)+1):
                            self.cnf.append([-self.var_player(row, col, t), -clause[i], -clause[j]])
        #box movement 
        for t in range(self.T):
            for b in range(1,len(self.boxes)+1):
                for row in range(self.N):
                    for col in range(self.M):
                        for x,y in DIRS.values():
                            if 0<=row+2*x<self.N and 0<=col+2*y<self.M:
                                self.cnf.append([-self.var_player(row,col,t),-self.var_box(b,row+x,col+y,t),-self.var_player(row+x,col+y,t+1),self.var_box(b,row+2*x,col+2*y,t+1)]) 
                            if 0<=row+x<self.N and 0<=col+y<self.M:
                                self.cnf.append([-self.var_box(b,row+x,col+y,t),self.var_player(row+x,col+y,t+1),-self.var_player(row,col,t),self.var_box(b,row+x,col+y,t+1)])
                                self.cnf.append([self.var_player(row,col,t),-self.var_box(b,row+x,col+y,t),self.var_box(b,row+x,col+y,t+1)])
        #non overlap constraints
        for t in range(1,self.T+1):
            for row in range(self.N):
                for col in range(self.M):
                    for b1 in range(1,self.num_boxes+1):
                        for b2 in range(b1 + 1, self.num_boxes+1):
                            self.cnf.append([-self.var_box(b1, row, col, t),-self.var_box(b2, row, col, t)])
                    for b in range(1,self.num_boxes+1):
                        self.cnf.append([-self.var_box(b, row, col, t),-self.var_player(row, col, t)])
        #Goal conditions
        for b in range(1,len(self.boxes)+1):
            goal =[]
            for row, col in self.goals:
                goal.append(self.var_box(b,row,col,self.T))
            self.cnf.append(goal)
        return self.cnf   


def decode(model, encoder):
    """
    Decode SAT model into list of moves ('U', 'D', 'L', 'R').

    Args:
        model (list[int]): Satisfying assignment from SAT solver.
        encoder (SokobanEncoder): Encoder object with grid info.

    Returns:
        list[str]: Sequence of moves.
    """
    N, M, T = encoder.N, encoder.M, encoder.T

    # TODO: Map player positions at each timestep to movement directions
    player_pos = encoder.player_start
    moves =[]
    for t in range(1,encoder.T_max+1):
                if encoder.var_player(player_pos[0]+1,player_pos[1],t) in model:
                    moves.append('D')
                    player_pos=(player_pos[0]+1,player_pos[1])
                elif encoder.var_player(player_pos[0]-1,player_pos[1],t) in model:
                    moves.append('U')
                    player_pos=(player_pos[0]-1,player_pos[1])
                elif encoder.var_player(player_pos[0],player_pos[1]+1,t) in model:
                    moves.append('R')
                    player_pos=(player_pos[0],player_pos[1]+1)
                elif encoder.var_player(player_pos[0],player_pos[1]-1,t) in model:
                    moves.append('L')
                    player_pos=(player_pos[0],player_pos[1]-1)
                elif encoder.var_player(player_pos[0],player_pos[1],t) in model:
                    continue
    return moves

def solve_sokoban(grid, T):
    """
    DO NOT MODIFY THIS FUNCTION.

    Solve Sokoban using SAT encoding.

    Args:
        grid (list[list[str]]): Sokoban grid.
        T (int): Max number of steps allowed.

    Returns:
        list[str] or "unsat": Move sequence or unsatisfiable.
    """
    encoder = SokobanEncoder(grid, T)
    cnf = encoder.encode()

    with Solver(name='g3') as solver:
        solver.append_formula(cnf)
        if not solver.solve():
            return -1

        model = solver.get_model()
        if not model:
            return -1

        return decode(model, encoder)


