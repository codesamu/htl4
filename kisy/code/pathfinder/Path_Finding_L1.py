def initialize_queue_and_visited(start):
    queue=[((start[0], start[1]), [])]
    return queue

def get_neighbors(x, y, maze, visited, path):

    new_path = []
    n_list = []
    for i in path:
        new_path.append(i)

    new_path.append((x,y))

    if x != (len(maze[y])-1):
        if maze[y][x+1] == 0:
            if (x+1,y) not in visited:
                visited.append((x+1,y))
                n_list.append(((x+1,y),new_path))
    
    if x != 0:
        if maze[y][x-1] == 0:
            if (x-1,y) not in visited:
                visited.append((x-1,y))
                n_list.append(((x-1,y),new_path))
    
    if y != (len(maze)-1):
        if maze[y+1][x] == 0:
            if (x,y+1) not in visited:
                visited.append((x,y+1))
                n_list.append(((x,y+1),new_path))
    
    if y != 0:
        if maze[y-1][x] == 0:
            if (x,y-1) not in visited:
                visited.append((x,y-1))
                n_list.append(((x,y-1),new_path))

    return n_list

def bfs_maze_solver(maze, start, goal):
    queue = initialize_queue_and_visited(start)
    visited = [(start[0],start[0])]
    x = start[0]
    y = start[1]
    path = queue[0][1]
    
    for point in queue:
        ((x,y),path) = point
        if goal == (x,y):       
            return path
        #print("y = ", y,"x = ", x)
        n_list = get_neighbors(x, y, maze, visited, path)
        # print("list = ", n_list)
        # print("queue = ", queue)
        for i in n_list:
            queue.append(i)
        #print("queue after = ", queue)
        # print("visited", visited)
        #print("queue 0 = ", queue[0])
                #print("point= ",point)
        #print("\n")
        
    return None

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

def start_solving(maze, start, goal):

    # Finde den kürzesten Pfad mit BFS
    path = bfs_maze_solver(maze, start, goal)

    # Gib das Ergebnis aus
    if path:
        print("Path found:", path)
    else:
        print("No path found from start to goal.")

