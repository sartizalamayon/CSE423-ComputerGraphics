"""
### **Maze Runner Game Design (2D)**

#### **Game Flow**
1. **Start Screen**:
   - Title: "Maze Runner" (GL_POINTS).
   - Options: Start Game, Instructions, Exit.
   - Navigation: Keyboard inputs / Mouse clicks.

2. **Game Start**:
   - Display a 2D maze.
   - Runner: A minimal shape of a 2d man, more like mincraft like human.
   - Maze walls: Drawn using the midpoint line algorithm.
   - Exit: Marked by a flashing color.

3. **Objective**:
   - Complete all 3 levels of increasing difficulty.
   - Fall into traps or circles

4. **Gameplay Loop**:
   - **Movement**: Arrow keys; restricted by maze walls.
   - **Obstacles**: 
     - Static traps (colored points).
     - Moving circles (timing-based avoidance).
   - **Collectibles**: Keys or glowing points to unlock paths that means open a blocked path.
   - **Levels**:
     - Each level increases in maze complexity and number of obstacles.
     - Timer for each level decreases as difficulty increases.

5. **End Game**:
   - **Win**: Successfully complete all levels.
   - **Lose**: 
     1. Fail to complete a level within the time limit.
     2. Fall into a trap and lose all lives.
   - Display a victory/defeat screen.


6. **Post-Game Options**:
   - Replay or exit to the main menu.

"""