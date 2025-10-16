import math
import copy

X = "X"
O = "O"
EMPTY = None

def initial_state():
    """
    Returns starting state of the board.
    """    
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]

def player(board):
    """
    Returns player who has the next turn on a board.
    """
    nx = sum(row.count("X") for row in board)
    ny = sum(row.count("O") for row in board)

    if nx == ny:
        return "X"
    else:
        return "O"

def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    possible = []

    for i in range(len(board)):
        for j in range(len(board[i])):
            if board[i][j] == EMPTY:
                possible.append((i,j))

    return set(possible)



def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    result_board = copy.deepcopy(board)

    if action not in actions(board):
        raise Exception(f"{action} not valid, possible actions are: {actions(board)}")
    else:
        result_board[action[0]][action[1]] = player(board)

    return result_board

def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    full = sum(row.count(EMPTY) for row in board)
     


    for row in board:
        if row[0] == row[1] == row[2] != None:
            return row[0]

    for col in range(3):
        if board[0][col] == board[1][col] == board[2][col] != None:
            return board[0][col]

    if board[0][0] == board[1][1] == board[2][2] != None:
        return board[0][0]
    if board[0][2] == board[1][1] == board[2][0] != None:
        return board[0][2]


    if full ==0:
        return False
    else:
        return None

def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    if winner(board) == None:
        return False

    elif winner(board) == "X" or winner(board)=="O":
        return True

    elif winner(board) == False:
        return True
    
    else:
        return False

def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    if winner(board) == "X":
        return 1

    elif winner(board) == "O":
        return -1

    elif winner(board) == None or winner(board) == False:
        return 0

def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """

    if player(board) == "X":
        value, action = max_value(board)
        # print only the chosen action to avoid confusion
        print("max action:", action, "value:", value)
        return action
    else:
        value, action = min_value(board)
        print("min action:", action, "value:", value)
        return action


def min_value(board, alpha=-math.inf, beta=math.inf):
    """
    Returns the minimum utility value and the corresponding action for the MIN player.
    """
    if terminal(board):
        return utility(board), None
    
    v = math.inf
    best_action = None
    
    for action in actions(board):
        value, _ = max_value(result(board, action), alpha, beta)
        # print(value)
        if value < v:
            v = value
            best_action = action

        beta = max(beta, v)
        if beta <= alpha:
            break
    
    return v, best_action

def max_value(board, alpha=-math.inf, beta=math.inf):
    """
    Returns the maximum utility value and the corresponding action for the MAX player.
    """
    if terminal(board):
        return utility(board), None
    
    v = -math.inf
    best_action = None
    
    for action in actions(board):
        value, _ = min_value(result(board, action), alpha, beta)
        if value > v:
            v = value
            best_action = action

        alpha = max(alpha, v)
        if beta <= alpha:
            break
    
    return v, best_action

# board = initial_state()
# print("Actions: ",actions(board))
# print("Winner: ",winner(board))
# print("Terminal: ",terminal(board))
# print("Utility:",utility(board))
# minimax(board)
