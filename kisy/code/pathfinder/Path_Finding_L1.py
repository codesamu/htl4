def initialize_queue_and_visited(start):
    """
    Initialisiert die Warteschlange (queue) mit dem Startpunkt und das Set der besuchten Knoten (visited).
    
    Args:
    start (tuple): Startkoordinate im Format (x, y)
    
    Returns:
    tuple: Ein Tupel bestehend aus der Warteschlange (queue) und dem Set der besuchten Knoten (visited).
    """
    queue=[(start[0], start[1]), []]
    return queue



def get_neighbors(x, y, maze, visited):
    """
    Berechnet die gültigen Nachbarn (Nachbarzellen) für einen gegebenen Punkt im Labyrinth.
    
    Args:
    x (int): Die X-Koordinate des aktuellen Punktes.
    y (int): Die Y-Koordinate des aktuellen Punktes.
    maze (list of list of int): Die 2D-Matrix, die das Labyrinth darstellt.
    visited (set): Das Set der besuchten Knoten.
    
    Returns:
    list: Eine Liste der Nachbarknoten, die besucht werden können.
    """

    n_list = []
    if x != 4:
        if maze[y][x+1] == 0:
            if (x+1,y) not in visited:
                n_list.append((x+1,y))
    
    if x != 0:
        if maze[y][x-1] == 0:
            if (x-1,y) not in visited:
                n_list.append((x-1,y))
    
    if y != 4:
        if maze[y+1][x] == 0:
            if (x,y+1) not in visited:
                n_list.append((x,y+1))
    
    if y != 0:
        if maze[y-1][x] == 0:
            if (x,y-1) not in visited:
                n_list.append((x,y-1))

    visited.append((x,y))
    return n_list
            
                    

def bfs_maze_solver(maze, start, goal):
    """
    Führt den Breadth-First Search (BFS) durch, um den kürzesten Pfad im Labyrinth zu finden.
    
    Args:
    maze (list of list of int): Die 2D-Matrix, die das Labyrinth darstellt.
    start (tuple): Startkoordinate im Format (x, y)
    goal (tuple): Zielkoordinate im Format (x, y)
    
    Returns:
    list or None: Der kürzeste Pfad als Liste von Koordinaten oder None, wenn kein Pfad gefunden wird.
    """    
    # Initialisiere die Warteschlange und die besuchten Knoten
    queue = initialize_queue_and_visited(start)
    visited = []
    x = start[0]
    y = start[1]
    
    # Füge hier den Code für BFS hinzu. 

    while True:
        if goal == (x,y):       # Prüfe ob Ziel erreicht
            break
        print(y,x)
        n_list = get_neighbors(x, y, maze, visited)
        print("list = ", n_list)
        print("queue = ", queue)
        for i in n_list:
            queue.append(i)
        print("queue after = ",queue)
        print("visited", visited)
        print("queue 0 = ", queue[0])
        del queue[0]
        (x,y) = queue[1]
        print("\n")
        


    return visited

# Beispiel-Labyrinth
maze = [
    [0, 1, 0, 0, 0],
    [0, 1, 0, 1, 0],
    [0, 0, 0, 1, 0],
    [0, 1, 1, 1, 0],
    [0, 0, 0, 0, 0]
]

start = (0, 0)
goal = (4, 4)

# Finde den kürzesten Pfad mit BFS
path = bfs_maze_solver(maze, start, goal)

# Gib das Ergebnis aus
if path:
    print("Path found:", path)
else:
    print("No path found from start to goal.")


