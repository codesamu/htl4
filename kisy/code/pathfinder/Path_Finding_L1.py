def initialize_queue_and_visited(start):
    """
    Initialisiert die Warteschlange (queue) mit dem Startpunkt und das Set der besuchten Knoten (visited).
    
    Args:
    start (tuple): Startkoordinate im Format (x, y)
    
    Returns:
    tuple: Ein Tupel bestehend aus der Warteschlange (queue) und dem Set der besuchten Knoten (visited).
    """
    queue = [(start[0], start[1]), []]
    visited = {start}
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
    nlist=[]

    if x!=4:
        if maze[y][x+1] == 0:
            if (y,x+1) not in visited:
                nlist.append((y,x+1))
        
    if x!=4:
        if maze[y][x-1] == 0:
            if (y,x-1) not in visited:
                nlist.append((y,x-1))

    if y!=0:
        if maze[y+1][x] == 0:
            if (y+1,x) not in visited:
                nlist.append((y+1,x))
        
    if y!=0:
        if maze[y-1][x] == 0:
            if (y-1,x) not in visited:  
                nlist.append((y-1,x))


    return nlist

    raise NotImplementedError("get_neighbors() is not implemented yet.")


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

    queue, visited = initialize_queue_and_visited(start)

    y = start[0]
    x = start[1]

    while True:
        if (x,y)== goal:
            print("nice")
            break

        queue.append(get_neighbors(x,y,maze,visited))
        visited.append((x,y))
        (x, y) = queue[0]    
    
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
