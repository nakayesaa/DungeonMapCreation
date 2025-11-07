import random, heapq, copy
from collections import deque
import pygame

Wall = '#'
Floor = '.'
Start = 'S'
Goal = 'G'

def manhattan(x, y):
    x1, x2 = x
    y1, y2 = y
    return abs(x1 - y1) + abs(x2 - y2)

def randomMap(width, height, bias=0.5):
    grid = []
    for y in range(height):
        row = []
        for x in range(width):
            if random.random() < bias : row.append(Wall)
            else : row.append(Floor)
        grid.append(row)
    grid[0][0] = Start
    grid[height - 1][width - 1] = Goal
    return grid

def printMap(grid):
    for row in grid:
        print("".join(row))
    print()

def solve(grid):
    StartPos = (0, 0)
    GoalPos = (len(grid) - 1, len(grid[0]) - 1)
    walk = []
    heapq.heappush(walk, (manhattan(StartPos, GoalPos), StartPos))
    backtracking = {}
    gScore = {StartPos: 0}

    while walk:
        _, current = heapq.heappop(walk)
        x, y = current
        if current == GoalPos:
            path = [current]
            while current in backtracking:
                current = backtracking[current]
                path.append(current)
            path.reverse()
            return path
        for addX, addY in [(1,0), (0,1), (-1,0), (0,-1)]:
            nx, ny = x + addX, y + addY
            if nx < 0 or ny < 0 or nx >= len(grid) or ny >= len(grid[0]): continue
            if grid[nx][ny] == Wall: continue
            nextNode = (nx, ny)
            newG = gScore[current] + 1
            if nextNode not in gScore or newG < gScore[nextNode]:
                backtracking[nextNode] = current
                gScore[nextNode] = newG
                fScore = newG + manhattan(nextNode, GoalPos)
                heapq.heappush(walk, (fScore, nextNode))
    return None

def booleanMap(height, width):
    return [[False for _ in range(width)] for _ in range(height)]

def connected(grid, start, visited):
    width, height = len(grid), len(grid[0])
    queue = deque([start])
    visited[start[0]][start[1]] = True
    connectedFloors = []
    connectedWalls = []
    while queue:
        x, y = queue.popleft()
        connectedFloors.append((x, y))
        for addX, addY in [(1,0), (0,1), (-1,0), (0,-1)]:
            newX, newY = x + addX, y + addY
            if 0 <= newY < height and 0 <= newX < width:
                if not visited[newX][newY] and grid[newX][newY] == Floor:
                    visited[newX][newY] = True
                    queue.append([newX, newY])
                elif grid[newX][newY] == Wall:
                    connectedWalls.append((newX, newY))
    return connectedFloors, connectedWalls

def findRegion(grid):
    height, width = len(grid), len(grid[0])
    visited = booleanMap(height, width)
    regions = []
    for x in range(height):
        for y in range(width):
            if grid[x][y] in (Floor, Start, Goal) and not visited[x][y]:
                floors, walls = connected(grid, (x, y), visited)
                regions.append({
                    "Floors": floors,   
                    "Walls": walls
                })
    return regions

def changeMap(grid):
    newGrid = copy.deepcopy(grid)
    regions = findRegion(newGrid)
    if len(regions) > 1:
        largest = max(regions, key=lambda r: len(r["Floors"]))
        for region in regions:
            if region is not largest:
                possible_links = [w for w in region["Walls"] if any(manhattan(w, f) == 1 for f in largest["Floors"])]
                if possible_links:
                    x, y = random.choice(possible_links)
                    newGrid[x][y] = Floor
    else:
        height, width = len(newGrid), len(newGrid[0])
        candidates = []
        for x in range(height):
            for y in range(width):
                if newGrid[x][y] == Wall:
                    for dx, dy in [(1,0),(-1,0),(0,1),(0,-1)]:
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < height and 0 <= ny < width:
                            if newGrid[nx][ny] == Floor:
                                candidates.append((x, y))
                                break
        if candidates:
            for x, y in random.sample(candidates, min(3, len(candidates))):
                newGrid[x][y] = Floor
    return newGrid

def displayMapsSideBySide(initial, final, path=None, title="Initial vs Final"):
    pygame.init()
    cell_size = 6
    height = len(initial)
    width = len(initial[0])
    gap = 5  # space between maps

    screen = pygame.display.set_mode(((width*2 + gap)*cell_size, height*cell_size))
    pygame.display.set_caption(title)

    color = {
        Wall: (30, 30, 30),
        Floor: (220, 220, 220),
        Start: (0, 255, 0),
        Goal: (255, 0, 0)
    }
    def drawMap(grid, offset_x):
        for y in range(height):
            for x in range(width):
                rect = pygame.Rect(
                    (x + offset_x)*cell_size,
                    y*cell_size,
                    cell_size,
                    cell_size
                )
                pygame.draw.rect(screen, color.get(grid[y][x], (255, 255, 255)), rect)

    screen.fill((0, 0, 0))
    drawMap(initial, 0)
    drawMap(final, width + gap)

    # ✅ Draw path correctly (fix x/y)
    if path:
        for (x, y) in path:
            rect = pygame.Rect(
                (y + width + gap) * cell_size,  # y controls horizontal position (columns)
                x * cell_size,                  # x controls vertical position (rows)
                cell_size,
                cell_size
            )
            pygame.draw.rect(screen, (255, 255, 0), rect)  # yellow path

    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                waiting = False
    pygame.quit()

initial_map = randomMap(100, 100)
print("Initial Map:")
printMap(initial_map)

mapInitialization = copy.deepcopy(initial_map)

path = None
iterations = 30
for i in range(iterations):
    path = solve(mapInitialization)
    if path:
        print(f"Solvable at iteration {i}")
        break
    mapInitialization = changeMap(mapInitialization)
    print(f"Iteration {i+1}")
else:
    print("Failed to make solvable within limit")

print("\nFinal Map:")
printMap(mapInitialization)
displayMapsSideBySide(initial_map, mapInitialization, path, "Initial vs Final Map")

