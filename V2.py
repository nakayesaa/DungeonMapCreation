import heapq
import random
from collections import deque

import pygame

Wall = "#"
Floor = "."
Start = "P"
Goal = "G"
Monster = "M"


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


def distancetoPlayer(grid, start):
    widht, height = len(grid), len(grid[0])
    dist = []
    for _ in range(widht):
        row = []
        for _ in range(height):
            row.append(float("inf"))
        dist.append(row)
    queue = deque([start])
    dist[start[0]][start[1]] = 0

    while queue:
        x, y = queue.popleft()
        for addX, addY in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            newX, newY = x + addX, y + addY
            if 0 <= newX < widht and 0 <= newY < height and grid[newX][newY] != "#":
                if dist[newX][newY] > dist[x][y] + 1:
                    dist[newX][newY] = dist[x][y] + 1
                    queue.append((newX, newY))
    return dist


def monsterMove(monsterPosition, distanceMap):
    x, y = monsterPosition
    currentBest = (x, y)
    bestValue = distanceMap[x][y]

    for addX, addY in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
        newX, newY = x + addX, y + addY
        if distanceMap[newX][newY] < bestValue:
            currentBest = (newX, newY)
            bestValue = distanceMap[newX][newY]
    return currentBest


def monsterSpawn(grid):
    width, height = len(grid), len(grid[0])
    floorCells = [
        (x, y) for x in range(height) for y in range(width) if grid[x][y] == Floor
    ]
    randomSpawn = random.sample(floorCells, 7)
    for x, y in randomSpawn:
        grid[x][y] = Monster
    return randomSpawn


def isMonsterTrap(grid, monsterPosition, move=3):
    width, height = len(grid), len(grid[0])
    x, y = monsterPosition
    for _ in range(move):
        moves = []
        for addX, addY in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            newX = x + addX
            newY = y + addY
            if 0 <= newX < width and 0 <= newY < height:
                if grid[newX][newY] != "#":
                    moves.append((newX, newY))
        if not moves:
            return True
        nx, ny = moves[0]
        if nx == x and ny == y:
            return True
        x, y = nx, ny
    return False


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

pygame.init()
size = 6
height, width = len(mapInitialization), len(mapInitialization[0])
screen = pygame.display.set_mode((width * size, height * size))
pygame.display.set_caption("chase chase and chase")
clock = pygame.time.Clock()
playerPos = (0, 0)
monsterInitialPosition = monsterSpawn(mapInitialization)
running = True
caught = False
won = False
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and not caught and not won:
            x, y = 0, 0
            if event.key == pygame.K_UP:
                x = -1
            elif event.key == pygame.K_DOWN:
                x = 1
            elif event.key == pygame.K_LEFT:
                y = -1
            elif event.key == pygame.K_RIGHT:
                y = 1
            newX, newY = playerPos[0] + x, playerPos[1] + y
            if (
                0 <= newX < height
                and 0 <= newY < width
                and mapInitialization[newX][newY] != Wall
            ):
                playerPos = (newX, newY)
    if not caught and not won:
        distanceMap = distancetoPlayer(mapInitialization, playerPos)

        monsterPositionUpdate = []
        for mPosition in monsterInitialPosition:
            newPosition = monsterMove(mPosition, distanceMap)
            if (
                newPosition != mPosition
                and mapInitialization[newPosition[0]][newPosition[1]] != Wall
            ):
                monsterPositionUpdate.append(newPosition)
            else:
                monsterPositionUpdate.append(mPosition)
        monsterInitialPosition = monsterPositionUpdate

        if playerPos == (height - 1, width - 1):
            won = True
        if any(m == playerPos for m in monsterInitialPosition):
            caught = True
    color = {
        Wall: (30, 30, 30),
        Floor: (220, 220, 220),
        Start: (0, 255, 0),
        Goal: (255, 0, 0),
    }
    screen.fill((0, 0, 0))
    for x in range(height):
        for y in range(width):
            rect = pygame.Rect(y * size, x * size, size, size)
            pygame.draw.rect(
                screen, color.get(mapInitialization[x][y], (255, 255, 255)), rect
            )
    pygame.draw.circle(
        screen,
        (0, 0, 255),
        (playerPos[1] * size + size // 2, playerPos[0] * size + size // 2),
        size // 2,
    )
    for m in monsterInitialPosition:
        pygame.draw.circle(
            screen,
            (255, 0, 0),
            (m[1] * size + size // 2, m[0] * size + size // 2),
            size // 2,
        )
    font = pygame.font.SysFont(None, 36)
    if caught:
        text = font.render("CAUGHT!", True, (255, 0, 0))
    elif won:
        text = font.render("YOU WIN!", True, (0, 255, 0))
    else:
        text = font.render("Run", True, (255, 255, 255))
    screen.blit(text, (10, 10))

    pygame.display.flip()
    clock.tick(10)
pygame.quit()
