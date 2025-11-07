import heapq
import random
from collections import deque

import pygame

Wall = "#"
Floor = "."
Start = "S"
Goal = "G"


def manhattan(x, y):
    x1, x2 = x
    y1, y2 = y
    return abs(x1 - y1) + abs(x2 - y2)


def randomMap(width, height, bias=0.5):
    grid = []
    for x in range(width):
        row = []
        for y in range(height):
            if random.random() < bias:
                row.append(Wall)
            else:
                row.append(Floor)
        grid.append(row)
    grid[0][0] = Start
    grid[height - 1][width - 1] = Goal
    return grid


def printMap(grid):
    for row in grid:
        print("".join(row))
    print()


def solve(grid):
    start = (0, 0)
    widht, height = len(grid), len(grid[0])
    goal = (widht - 1, height - 1)
    walk = []
    heapq.heappush(walk, (manhattan(start, goal), start))
    backtracking = {}
    gScore = {start: 0}

    while walk:
        _, current = heapq.heappop(walk)
        x, y = current
        if current == goal:
            path = [current]
            while current in backtracking:
                current = backtracking[current]
                path.append(current)
            path.reverse()
            return path
        for addX, addY in [(1, 0), (0, 1), (-1, 0), (0, -1)]:
            newX, newY = x + addX, y + addY
            if newX < 0 or newY < 0 or newX >= len(grid) or newY >= len(grid[0]):
                continue
            if grid[newX][newY] == Wall:
                continue
            nextNode = (newX, newY)
            newG = gScore[current] + 1
            if nextNode not in gScore or newG < gScore[nextNode]:
                backtracking[nextNode] = current
                gScore[nextNode] = newG
                fScore = newG + manhattan(nextNode, goal)
                heapq.heappush(walk, (fScore, nextNode))
    return None


def booleanMap(height, width):
    boolMap = []
    for x in range(width):
        row = []
        for y in range(height):
            row.append(False)
        boolMap.append(row)
    return boolMap


def connected(grid, start, visited):
    width, height = len(grid), len(grid[0])
    queue = deque([start])
    visited[start[0]][start[1]] = True
    connectedFloors = []
    connectedWalls = []
    while queue:
        x, y = queue.popleft()
        connectedFloors.append((x, y))
        for addX, addY in [(1, 0), (0, 1), (-1, 0), (0, -1)]:
            newX, newY = x + addX, y + addY
            if newX < 0 or newY < 0 or newX >= width or newY >= height:
                continue
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
                regions.append({"Floors": floors, "Walls": walls})
    return regions


def copyMap(grid):
    newMap = []
    for x in range(len(grid)):
        row = []
        for y in range(len(grid[0])):
            row.append(grid[x][y])
        newMap.append(row)
    return newMap


def impasse(grid):
    widht, height = len(grid), len(grid[0])
    floorCount = 0
    impasse = 0
    branch = 0

    for x in range(widht):
        for y in range(height):
            if grid[x][y] in (Start, Goal, Floor):
                floorCount += 1
                neighbors = 0
                for addX, addY in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                    newX, newY = x + addX, y + addY
                    if newX < 0 or newX >= widht or newY < 0 or newY >= height:
                        continue
                    if grid[newX][newY] == Wall:
                        continue
                    neighbors += 1
                if neighbors == 1:
                    impasse += 1
                branch += neighbors
    if floorCount > 0:
        averageBranch = branch / floorCount
    else:
        averageBranch = 0
    return impasse, averageBranch


def changeMap(grid):
    newGrid = copyMap(grid)
    regions = findRegion(newGrid)
    if len(regions) > 1:
        largest = max(regions, key=lambda r: len(r["Floors"]))
        for region in regions:
            if region is not largest:
                links = []
                for w in region["Walls"]:
                    connected = False
                    for f in largest["Floors"]:
                        if manhattan(w, f) == 1:
                            connected = True
                            break
                    if connected:
                        links.append(w)
                if links:
                    x, y = random.choice(links)
                    newGrid[x][y] = Floor
    else:
        height, width = len(newGrid), len(newGrid[0])
        candidates = []
        for x in range(height):
            for y in range(width):
                if newGrid[x][y] == Wall:
                    for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                        newX, newY = x + dx, y + dy
                        if newX < 0 or newY < 0 or newX >= width or newY >= height:
                            continue
                        if newGrid[newX][newY] == Floor:
                            candidates.append((x, y))
                            break
        if candidates:
            for x, y in random.sample(candidates, min(3, len(candidates))):
                newGrid[x][y] = Floor
    return newGrid


def displayMapsSideBySide(initial, final, path=None, title="InitialMap vs FinalMap"):
    pygame.init()
    size = 6
    height = len(initial)
    width = len(initial[0])
    gap = 5
    screen = pygame.display.set_mode(((width * 2 + gap) * size, height * size))
    pygame.display.set_caption(title)
    color = {
        Wall: (30, 30, 30),
        Floor: (220, 220, 220),
        Start: (0, 255, 0),
        Goal: (255, 0, 0),
    }

    def drawMap(grid, XOffset):
        for y in range(height):
            for x in range(width):
                rect = pygame.Rect((x + XOffset) * size, y * size, size, size)
                pygame.draw.rect(screen, color.get(grid[y][x], (255, 255, 255)), rect)

    screen.fill((0, 0, 0))
    drawMap(initial, 0)
    drawMap(final, width + gap)
    if path:
        for x, y in path:
            rect = pygame.Rect((y + width + gap) * size, x * size, size, size)
            pygame.draw.rect(screen, (255, 255, 0), rect)  # yellow path
    pygame.display.flip()
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                waiting = False
    pygame.quit()


def fitness(grid):
    regions = findRegion(grid)
    totalRegions = len(regions)
    connectivityPen = -100 * (totalRegions - 1)

    path = solve(grid)
    if path:
        solvabilityScore = 1000
        pathScore = len(path)
    else:
        solvabilityScore = -1000
        pathScore = 0

    widht, height = len(grid), len(grid[0])
    totalCells = widht * height
    totalFloors = 0
    for row in grid:
        for cell in row:
            if cell != Wall:
                totalFloors += 1
    if totalCells > 0:
        density = totalFloors / totalCells
    else:
        density = 0
    density_score = -abs(density - 0.5) * 200

    impasses, avgBranching = impasse(grid)
    impassesPen = -impasses * 2
    branchingScore = avgBranching * 10

    return (
        solvabilityScore
        + pathScore
        + connectivityPen
        + density_score
        + impassesPen
        + branchingScore
    )


initialMap = randomMap(100, 100)
print("Initial Map:")
printMap(initialMap)
mapInitialization = copyMap(initialMap)
path = None
iterations = 30
currentFitness = fitness(mapInitialization)
for i in range(iterations):
    path = solve(mapInitialization)
    if path:
        print(f"the map is already solvable at iteration {i}")
        break
    candidates = [changeMap(mapInitialization) for _ in range(3)]
    candidateFitness = [fitness(cand) for cand in candidates]
    best = candidateFitness.index(max(candidateFitness))
    bestCandidates = candidates[best]
    bestFitness = candidateFitness[best]
    if bestFitness > currentFitness:
        mapInitialization = bestCandidates
        currentFitness = bestFitness
        print(f"Improved fitness to {currentFitness} at iteration {i + 1}")
    else:
        print(f"No improvement at iteration {i + 1}")
else:
    print(f"Failed to make the map solvable in {i} iteration")
print("\nFinal Map:")
printMap(mapInitialization)
displayMapsSideBySide(initialMap, mapInitialization, path, "Initial vs Final Map")
