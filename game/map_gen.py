import random
import time
from game import deebee as db

class Map:
    def __init__(self, width=db.GRID_WIDTH, height=db.GRID_HEIGHT, seed=None):
        self.width = width
        self.height = height
        self.grid = []
        if seed is None:
            self.seed = str(int(time.time()))
        else:
            self.seed = str(seed)
        self.rng = random.Random(self.seed)
        self.generate()

    def generate(self):
        # Step 1: Random Fill (Simulation Seed)
        # We fill the map with roughly 45% walls
        self.grid = [[1 if self.rng.random() < 0.45 else 0 
                      for _ in range(self.width)] 
                      for _ in range(self.height)]

        # Step 2: Smoothing (Simulation Steps)
        # Run the cellular automata rules 5 times to smooth the noise
        for _ in range(5):
            self.grid = self.smooth_step(self.grid)
        
        for x in range(self.width):
            self.grid[0][x] = 1; self.grid[self.height-1][x] = 1
        for y in range(self.height):
            self.grid[y][0] = 1; self.grid[y][self.width-1] = 1

    def smooth_step(self, input_grid):
        new_grid = [[0 for _ in range(self.width)] for _ in range(self.height)]
        
        for y in range(self.height):
            for x in range(self.width):
                neighbors = self.count_wall_neighbors(input_grid, x, y)
                
                # The Rules of the Simulation:
                # If a cell is surrounded by walls, it stays a wall.
                # If it's open but crowded, it becomes a wall.
                if neighbors > 4:
                    new_grid[y][x] = 1
                elif neighbors < 4:
                    new_grid[y][x] = 0
                else:
                    new_grid[y][x] = input_grid[y][x]
                    
        return new_grid

    def count_wall_neighbors(self, grid, x, y):
        count = 0
        for i in range(-1, 2):
            for j in range(-1, 2):
                neighbor_x = x + i
                neighbor_y = y + j
                
                # Check bounds: Borders are always walls
                if i == 0 and j == 0:
                    continue
                if neighbor_x < 0 or neighbor_y < 0 or neighbor_x >= self.width or neighbor_y >= self.height:
                    count += 1
                elif grid[neighbor_y][neighbor_x] == 1:
                    count += 1
        return count

    def is_blocked(self, x, y):
        """
        Returns True if the tile at (x,y) is a wall or out of bounds.
        """
        if x < 0 or y < 0 or x >= self.width or y >= self.height:
            return True
        if self.grid[y][x] == 1:
            return True
        return False
    
    def get_traversable_point(self, bias="top_left"):
        """
        Finds the nearest valid floor tile to the desired corner 
        using a Breadth-First Search (BFS).
        """
        # 1. Define Start Point based on Bias
        if bias == "top_left":
            start = (1, 1)
        elif bias == "bottom_right":
            start = (self.width - 2, self.height - 2)
        elif bias == "center":
            start = (self.width // 2, self.height // 2)
        else: # Random
            start = (random.randint(1, self.width-2), random.randint(1, self.height-2))

        # 2. BFS Init
        queue = [start]
        visited = set()
        visited.add(start)

        # 3. Search Loop
        while queue:
            current_x, current_y = queue.pop(0)

            # Check: Is this spot valid? (Within bounds + Is Floor)
            if (0 <= current_x < self.width and 
                0 <= current_y < self.height and 
                self.grid[current_y][current_x] == 0):
                
                return (current_x, current_y)

            # Add Neighbors to Queue (Shuffle for randomness so we don't always zigzag the same way)
            neighbors = [
                (current_x + 1, current_y), (current_x - 1, current_y),
                (current_x, current_y + 1), (current_x, current_y - 1)
            ]
            random.shuffle(neighbors)
            
            for nx, ny in neighbors:
                # Bounds check for queue addition
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    if (nx, ny) not in visited:
                        visited.add((nx, ny))
                        queue.append((nx, ny))

        # 4. Emergency Fallback (Map is 100% walls)
        print("CRITICAL: Map has no floor tiles!")
        return (1, 1)
    
    def find_open_space(self, radius=1, bias="top_left"):
        """
        Uses BFS to find the nearest open space of a specific size (radius).
        radius=1 means a 3x3 clear area.
        radius=0 means a 1x1 clear area.
        """
        # 1. Adjust Start Point & Bounds based on radius
        # We cannot pick a point too close to the edge, or the radius check fails.
        min_x, min_y = radius, radius
        max_x, max_y = self.width - 1 - radius, self.height - 1 - radius

        if bias == "top_left":
            start = (min_x + 1, min_y + 1)
        elif bias == "bottom_right":
            start = (max_x - 1, max_y - 1)
        elif bias == "center":
            start = (self.width // 2, self.height // 2)
        else: # Random
            start = (self.rng.randint(min_x, max_x), self.rng.randint(min_y, max_y))

        # 2. BFS Init
        queue = [start]
        visited = set()
        visited.add(start)

        # 3. Search Loop
        while queue:
            cx, cy = queue.pop(0)

            # --- CHECK AREA CLEARANCE ---
            is_clear = True
            # Scan the square area around the center point
            for dy in range(-radius, radius + 1):
                for dx in range(-radius, radius + 1):
                    # Check bounds and wall status
                    tx, ty = cx + dx, cy + dy
                    if not (0 <= tx < self.width and 0 <= ty < self.height) or self.grid[ty][tx] == 1:
                        is_clear = False
                        break
                if not is_clear: break
            
            if is_clear:
                return (cx, cy)
            # ---------------------------

            # 4. Add Neighbors (Respecting radius bounds)
            neighbors = [
                (cx + 1, cy), (cx - 1, cy),
                (cx, cy + 1), (cx, cy - 1)
            ]
            random.shuffle(neighbors)
            
            for nx, ny in neighbors:
                if min_x <= nx <= max_x and min_y <= ny <= max_y:
                    if (nx, ny) not in visited:
                        visited.add((nx, ny))
                        queue.append((nx, ny))

        # 5. Fallback: If no large space exists, try radius 0 (fit anywhere)
        if radius > 0:
            print(f"Warning: No empty space of radius {radius} found. Retrying with radius 0.")
            return self.find_open_space(radius=0, bias=bias)
            
        print("CRITICAL: Map is 100% walls.")
        return (1, 1)