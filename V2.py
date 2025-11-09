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


def monsterMove(monsterPosition, distanceMap, randomness=0.2):
    x, y = monsterPosition
    height, width = len(distanceMap), len(distanceMap[0])

    # Get all possible moves
    moves = []
    for addX, addY in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
        newX, newY = x + addX, y + addY
        if 0 <= newX < height and 0 <= newY < width:
            moves.append((newX, newY, distanceMap[newX][newY]))

    # Random chance for suboptimal move
    if random.random() < randomness and moves:
        return random.choice([(m[0], m[1]) for m in moves])

    # Otherwise, take best move
    if moves:
        best = min(moves, key=lambda m: m[2])
        return (best[0], best[1])
    return monsterPosition


def monsterMoveSmart(grid, monsterPosition, distanceMap, vision=10, randomness=0.1):
    x, y = monsterPosition
    if distanceMap[x][y] > vision:
        # Monster can't see player - patrol randomly
        moves = [(x+dx, y+dy) for dx, dy in [(1,0),(-1,0),(0,1),(0,-1)]
                 if 0 <= x+dx < len(grid) and 0 <= y+dy < len(grid[0]) and grid[x+dx][y+dy] != Wall]
        return random.choice(moves) if moves else monsterPosition
    else:
        # Monster can see player - chase with some randomness
        return monsterMove(monsterPosition, distanceMap, randomness)


def monsterBehavior(grid, monsterPosition, distanceMap, role="hunter"):
    if role == "hunter":
        return monsterMoveSmart(grid, monsterPosition, distanceMap, vision=20, randomness=0.05)
    elif role == "stalker":
        if distanceMap[monsterPosition[0]][monsterPosition[1]] < 8:
            return monsterMoveSmart(grid, monsterPosition, distanceMap, vision=18, randomness=0.2)
        else:
            # Move closer instead of waiting
            return monsterMoveSmart(grid, monsterPosition, distanceMap, vision=18, randomness=0.3)
    elif role == "wanderer":
        return monsterMoveSmart(grid, monsterPosition, distanceMap, vision=6, randomness=0.8)


def monsterSpawn(grid):
    width, height = len(grid), len(grid[0])
    playerPos = (0, 0)
    floorCells = [
        (x, y) for x in range(height) for y in range(width)
        if grid[x][y] == Floor and manhattan((x, y), playerPos) >= 10
    ]
    if len(floorCells) < 7:
        # If not enough safe cells, allow closer spawns but still avoid immediate vicinity
        floorCells = [
            (x, y) for x in range(height) for y in range(width)
            if grid[x][y] == Floor and manhattan((x, y), playerPos) >= 5
        ]
    randomSpawn = random.sample(floorCells, min(7, len(floorCells)))
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


initialMap = randomMap(50, 50)
# print("Initial Map:")
# printMap(initialMap)
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
# print("\nFinal Map:")
# printMap(mapInitialization)
# displayMapsSideBySide(initialMap, mapInitialization, path, "Initial vs Final Map")

pygame.init()
size = 15
height, width = len(mapInitialization), len(mapInitialization[0])
screen = pygame.display.set_mode((width * size, height * size))
pygame.display.set_caption("Dungeon Map Game")
clock = pygame.time.Clock()

# Button properties
button_width = 200
button_height = 50
button_color = (100, 100, 100)
button_hover_color = (150, 150, 150)
button_text_color = (255, 255, 255)
font = pygame.font.SysFont(None, 36)

def draw_button(screen, text, x, y, width, height, color, hover_color, mouse_pos):
    rect = pygame.Rect(x, y, width, height)
    if rect.collidepoint(mouse_pos):
        pygame.draw.rect(screen, hover_color, rect)
    else:
        pygame.draw.rect(screen, color, rect)
    pygame.draw.rect(screen, (255, 255, 255), rect, 2)  # border
    text_surf = font.render(text, True, button_text_color)
    text_rect = text_surf.get_rect(center=(x + width // 2, y + height // 2))
    screen.blit(text_surf, text_rect)
    return rect

def reset_game():
    global playerPos, monsterInitialPosition, monsterRoles, monsterCooldowns, caught, won
    playerPos = (0, 0)
    monsterInitialPosition = monsterSpawn(mapInitialization)
    # Assign random roles to monsters
    monsterRoles = [random.choice(["hunter", "stalker", "wanderer"]) for _ in monsterInitialPosition]
    monsterCooldowns = [0] * len(monsterInitialPosition)
    caught = False
    won = False

reset_game()
running = True
main_menu = True
game_started = False
info_screen = False
keys_pressed = set()
mouse_pos = (0, 0)

while running:
    mouse_pos = pygame.mouse.get_pos()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                if main_menu:
                    start_rect = draw_button(screen, "Start Game", (width * size - button_width) // 2, (height * size - button_height) // 2 - 100, button_width, button_height, button_color, button_hover_color, mouse_pos)
                    quit_rect = draw_button(screen, "Quit", (width * size - button_width) // 2, (height * size - button_height) // 2 + 100, button_width, button_height, button_color, button_hover_color, mouse_pos)
                    if start_rect.collidepoint(mouse_pos):
                        main_menu = False
                        info_screen = True
                        info_from_menu = True
                    elif quit_rect.collidepoint(mouse_pos):
                        running = False
                elif not game_started and not info_screen:
                    button_rect = draw_button(screen, "Start Game", (width * size - button_width) // 2, (height * size - button_height) // 2, button_width, button_height, button_color, button_hover_color, mouse_pos)
                    if button_rect.collidepoint(mouse_pos):
                        info_screen = True
                elif info_screen:
                    # Info screen buttons
                    continue_rect = draw_button(screen, "Continue", (width * size - button_width) // 2 - 120, height * size - 100, button_width, button_height, button_color, button_hover_color, mouse_pos)
                    close_rect = draw_button(screen, "Close", (width * size - button_width) // 2 + 120, height * size - 100, button_width, button_height, button_color, button_hover_color, mouse_pos)
                    if continue_rect.collidepoint(mouse_pos) or close_rect.collidepoint(mouse_pos):
                        info_screen = False
                        game_started = True
                elif caught:
                    button_rect = draw_button(screen, "Retry", (width * size - button_width) // 2, (height * size - button_height) // 2, button_width, button_height, button_color, button_hover_color, mouse_pos)
                    if button_rect.collidepoint(mouse_pos):
                        reset_game()
                        game_started = True
                elif won:
                    button_rect = draw_button(screen, "Play Again", (width * size - button_width) // 2, (height * size - button_height) // 2, button_width, button_height, button_color, button_hover_color, mouse_pos)
                    if button_rect.collidepoint(mouse_pos):
                        reset_game()
                        game_started = True
        elif event.type == pygame.KEYDOWN:
            keys_pressed.add(event.key)
            if not game_started and event.key == pygame.K_SPACE:
                game_started = True
            elif caught and event.key == pygame.K_r:
                reset_game()
                game_started = True
        elif event.type == pygame.KEYUP:
            keys_pressed.discard(event.key)

    if game_started and not caught and not won:
        x, y = 0, 0
        if pygame.K_w in keys_pressed:
            x = -1
        elif pygame.K_s in keys_pressed:
            x = 1
        if pygame.K_a in keys_pressed:
            y = -1
        elif pygame.K_d in keys_pressed:
            y = 1
        if x != 0 or y != 0:
            newX, newY = playerPos[0] + x, playerPos[1] + y
            can_move = (
                0 <= newX < height
                and 0 <= newY < width
                and mapInitialization[newX][newY] != Wall
            )
            # Prevent diagonal movement through walls
            if x != 0 and y != 0:
                can_move = can_move and (
                    mapInitialization[playerPos[0] + x][playerPos[1]] != Wall and
                    mapInitialization[playerPos[0]][playerPos[1] + y] != Wall
                )
            if can_move:
                playerPos = (newX, newY)

        distanceMap = distancetoPlayer(mapInitialization, playerPos)

        monsterPositionUpdate = []
        for i, mPosition in enumerate(monsterInitialPosition):
            if monsterCooldowns[i] > 0:
                monsterCooldowns[i] -= 1
                monsterPositionUpdate.append(mPosition)
                continue
            role = monsterRoles[i]
            newPosition = monsterBehavior(mapInitialization, mPosition, distanceMap, role)
            if (
                newPosition != mPosition
                and mapInitialization[newPosition[0]][newPosition[1]] != Wall
            ):
                monsterPositionUpdate.append(newPosition)
                monsterCooldowns[i] = random.randint(2, 4)  # Cooldown after moving
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
            # Add grid lines
            pygame.draw.rect(screen, (0, 0, 0), rect, 1)
    if game_started:
        pygame.draw.circle(
            screen,
            (0, 0, 255),
            (playerPos[1] * size + size // 2, playerPos[0] * size + size // 2),
            size // 2,
        )
        monster_colors = {
            "hunter": (255, 0, 0),      # Red
            "stalker": (255, 165, 0),   # Orange
            "wanderer": (128, 0, 128),  # Purple
        }
        for i, m in enumerate(monsterInitialPosition):
            role = monsterRoles[i]
            pygame.draw.circle(
                screen,
                monster_colors.get(role, (255, 0, 0)),
                (m[1] * size + size // 2, m[0] * size + size // 2),
                size // 2,
            )
    font = pygame.font.SysFont(None, 36)
    if main_menu:
        # Draw main menu
        title_font = pygame.font.SysFont(None, 72)
        title_text = title_font.render("Dungeon Map Game", True, (255, 255, 255))
        screen.blit(title_text, ((width * size - title_text.get_width()) // 2, 100))
        draw_button(screen, "Start Game", (width * size - button_width) // 2, (height * size - button_height) // 2 - 100, button_width, button_height, button_color, button_hover_color, mouse_pos)
        draw_button(screen, "Quit", (width * size - button_width) // 2, (height * size - button_height) // 2 + 100, button_width, button_height, button_color, button_hover_color, mouse_pos)
    elif not game_started and not info_screen:
        draw_button(screen, "Start Game", (width * size - button_width) // 2, (height * size - button_height) // 2, button_width, button_height, button_color, button_hover_color, mouse_pos)
    elif info_screen:
        # Draw info screen background
        pygame.draw.rect(screen, (0, 0, 0), (0, 0, width * size, height * size))
        # Draw info text
        info_lines = [
            "Dungeon Map Game",
            "",
            "Controls:",
            "WASD - Move",
            "",
            "Monster Types:",
            "Red (Hunter): Aggressive, chases player",
            "Orange (Stalker): Waits, then chases",
            "Purple (Wanderer): Random movement",
            "",
            "Goal: Reach the red goal without getting caught!"
        ]
        for i, line in enumerate(info_lines):
            text = font.render(line, True, (255, 255, 255))
            screen.blit(text, (50, 50 + i * 40))
        # Draw buttons
        draw_button(screen, "Continue", (width * size - button_width) // 2 - 120, height * size - 100, button_width, button_height, button_color, button_hover_color, mouse_pos)
        draw_button(screen, "Close", (width * size - button_width) // 2 + 120, height * size - 100, button_width, button_height, button_color, button_hover_color, mouse_pos)
    elif caught:
        draw_button(screen, "Retry", (width * size - button_width) // 2, (height * size - button_height) // 2, button_width, button_height, button_color, button_hover_color, mouse_pos)
    elif won:
        draw_button(screen, "Play Again", (width * size - button_width) // 2, (height * size - button_height) // 2, button_width, button_height, button_color, button_hover_color, mouse_pos)
    else:
        text = font.render("Run", True, (255, 255, 255))
        screen.blit(text, (10, 10))

    pygame.display.flip()
    clock.tick(10)
pygame.quit()
