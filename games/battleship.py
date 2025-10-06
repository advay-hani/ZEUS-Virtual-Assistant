"""
Battleship Game Implementation for Z.E.U.S. Virtual Assistant
Features dual 10x10 grids with ship placement and intelligent AI opponent
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import List, Tuple, Optional, Dict, Set
from dataclasses import dataclass
from enum import Enum
import copy
import random


class CellState(Enum):
    """States for battleship grid cells"""
    EMPTY = "empty"
    SHIP = "ship"
    HIT = "hit"
    MISS = "miss"


class ShipType(Enum):
    """Types of ships with their sizes"""
    CARRIER = 5
    BATTLESHIP = 4
    CRUISER = 3
    SUBMARINE = 3
    DESTROYER = 2


@dataclass
class Ship:
    """Represents a ship on the battleship grid"""
    ship_type: ShipType
    positions: List[Tuple[int, int]]
    hits: Set[Tuple[int, int]] = None
    
    def __post_init__(self):
        if self.hits is None:
            self.hits = set()
    
    @property
    def is_sunk(self) -> bool:
        """Check if the ship is completely sunk"""
        return len(self.hits) == len(self.positions)
    
    @property
    def size(self) -> int:
        """Get the size of the ship"""
        return self.ship_type.value


@dataclass
class BattleshipState:
    """Represents the state of a Battleship game"""
    player_grid: List[List[CellState]]
    ai_grid: List[List[CellState]]
    player_ships: List[Ship]
    ai_ships: List[Ship]
    current_player: str
    winner: Optional[str]
    game_over: bool
    move_count: int
    game_phase: str  # 'placement' or 'battle'


class BattleshipGame:
    """Battleship game with AI opponent and intelligent strategies"""
    
    def __init__(self, parent_frame: ttk.Frame, status_callback=None, back_callback=None, end_game_callback=None):
        self.parent_frame = parent_frame
        self.status_callback = status_callback
        self.back_callback = back_callback
        self.end_game_callback = end_game_callback
        
        # Game constants
        self.GRID_SIZE = 10
        self.SHIPS = [
            ShipType.CARRIER,
            ShipType.BATTLESHIP,
            ShipType.CRUISER,
            ShipType.SUBMARINE,
            ShipType.DESTROYER
        ]
        
        # Game state
        self.player_grid = [[CellState.EMPTY for _ in range(self.GRID_SIZE)] for _ in range(self.GRID_SIZE)]
        self.ai_grid = [[CellState.EMPTY for _ in range(self.GRID_SIZE)] for _ in range(self.GRID_SIZE)]
        self.player_ships = []
        self.ai_ships = []
        self.current_player = 'player'
        self.game_over = False
        self.winner = None
        self.move_count = 0
        self.game_phase = 'placement'
        
        # Ship placement state
        self.current_ship_index = 0
        self.placement_orientation = 'horizontal'  # 'horizontal' or 'vertical'
        self.preview_positions = []
        
        # AI strategy state
        self.ai_target_mode = False
        self.ai_target_stack = []
        self.ai_last_hit = None
        self.ai_hit_direction = None
        self.ai_tried_positions = set()
        
        # UI elements
        self.player_grid_buttons = []
        self.ai_grid_buttons = []
        self.game_frame = None
        self.info_frame = None
        self.current_phase_label = None
        self.ship_info_label = None
        
        # Initialize the game UI
        self.setup_game_ui()
        self.place_ai_ships()
        self.update_status("Place your ships! Click to place, right-click to rotate.")
    
    def setup_game_ui(self):
        """Create the Battleship game interface"""
        # Clear any existing content
        for widget in self.parent_frame.winfo_children():
            widget.destroy()
        
        # Main container
        main_container = ttk.Frame(self.parent_frame)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Header section
        header_frame = ttk.Frame(main_container)
        header_frame.pack(fill=tk.X, pady=(10, 5))
        
        # Title
        title_label = ttk.Label(
            header_frame,
            text="🚢 Battleship",
            font=("Arial", 20, "bold"),
            foreground="#0078d4"
        )
        title_label.pack()
        
        # Game info section
        self.info_frame = ttk.Frame(main_container)
        self.info_frame.pack(pady=5)
        
        # Current phase indicator
        self.current_phase_label = ttk.Label(
            self.info_frame,
            text="Ship Placement Phase",
            font=("Arial", 12, "bold"),
            foreground="#0078d4"
        )
        self.current_phase_label.pack()
        
        # Ship placement info
        self.ship_info_label = ttk.Label(
            self.info_frame,
            text=f"Place {self.SHIPS[0].name} (Size: {self.SHIPS[0].value})",
            font=("Arial", 10),
            foreground="#666666"
        )
        self.ship_info_label.pack()
        
        # Grids container
        grids_container = ttk.Frame(main_container)
        grids_container.pack(expand=True, pady=10)
        
        # Player grid section
        player_section = ttk.Frame(grids_container)
        player_section.pack(side=tk.LEFT, padx=20)
        
        player_title = ttk.Label(
            player_section,
            text="Your Fleet",
            font=("Arial", 12, "bold"),
            foreground="#0078d4"
        )
        player_title.pack(pady=(0, 5))
        
        # Player grid
        player_grid_frame = ttk.Frame(player_section)
        player_grid_frame.pack()
        
        self.create_grid(player_grid_frame, "player")
        
        # AI grid section
        ai_section = ttk.Frame(grids_container)
        ai_section.pack(side=tk.LEFT, padx=20)
        
        ai_title = ttk.Label(
            ai_section,
            text="Enemy Waters",
            font=("Arial", 12, "bold"),
            foreground="#d13438"
        )
        ai_title.pack(pady=(0, 5))
        
        # AI grid
        ai_grid_frame = ttk.Frame(ai_section)
        ai_grid_frame.pack()
        
        self.create_grid(ai_grid_frame, "ai")
        
        # Control buttons section
        controls_frame = ttk.Frame(main_container)
        controls_frame.pack(side=tk.BOTTOM, pady=10)
        
        # Rotate button (for ship placement)
        self.rotate_button = ttk.Button(
            controls_frame,
            text="🔄 Rotate Ship",
            command=self.rotate_ship
        )
        self.rotate_button.pack(side=tk.LEFT, padx=5)
        
        # Auto-place button
        self.auto_place_button = ttk.Button(
            controls_frame,
            text="🎲 Auto-Place Ships",
            command=self.auto_place_player_ships
        )
        self.auto_place_button.pack(side=tk.LEFT, padx=5)
        
        # New game button
        new_game_button = ttk.Button(
            controls_frame,
            text="🔄 New Game",
            command=self.reset_game
        )
        new_game_button.pack(side=tk.LEFT, padx=5)
        
        # Back to selection button
        back_button = ttk.Button(
            controls_frame,
            text="← Back to Games",
            command=self.back_to_selection
        )
        back_button.pack(side=tk.LEFT, padx=5)
    
    def create_grid(self, parent_frame: ttk.Frame, grid_type: str):
        """Create a 10x10 grid for player or AI"""
        # Add column headers (A-J)
        for col in range(self.GRID_SIZE + 1):
            if col == 0:
                # Empty corner cell
                label = ttk.Label(parent_frame, text="", width=3)
            else:
                label = ttk.Label(parent_frame, text=chr(ord('A') + col - 1), width=3, font=("Arial", 8, "bold"))
            label.grid(row=0, column=col, padx=1, pady=1)
        
        # Create grid with row headers (1-10)
        grid_buttons = []
        for row in range(self.GRID_SIZE):
            # Row header
            row_label = ttk.Label(parent_frame, text=str(row + 1), width=3, font=("Arial", 8, "bold"))
            row_label.grid(row=row + 1, column=0, padx=1, pady=1)
            
            button_row = []
            for col in range(self.GRID_SIZE):
                if grid_type == "player":
                    button = tk.Button(
                        parent_frame,
                        text='',
                        font=("Arial", 8),
                        width=3,
                        height=1,
                        command=lambda r=row, c=col: self.handle_player_grid_click(r, c),
                        bg="#87CEEB",  # Light blue for water
                        relief=tk.RAISED,
                        borderwidth=1
                    )
                    # Bind right-click for rotation during placement
                    button.bind("<Button-3>", lambda e, r=row, c=col: self.handle_right_click(r, c))
                    # Bind mouse enter/leave for ship placement preview
                    button.bind("<Enter>", lambda e, r=row, c=col: self.show_ship_preview(r, c))
                    button.bind("<Leave>", lambda e: self.clear_ship_preview())
                else:  # AI grid
                    button = tk.Button(
                        parent_frame,
                        text='',
                        font=("Arial", 8),
                        width=3,
                        height=1,
                        command=lambda r=row, c=col: self.handle_ai_grid_click(r, c),
                        bg="#87CEEB",  # Light blue for water
                        relief=tk.RAISED,
                        borderwidth=1,
                        state='disabled'  # Disabled during ship placement
                    )
                
                button.grid(row=row + 1, column=col + 1, padx=1, pady=1)
                button_row.append(button)
            
            grid_buttons.append(button_row)
        
        if grid_type == "player":
            self.player_grid_buttons = grid_buttons
        else:
            self.ai_grid_buttons = grid_buttons
    
    def handle_player_grid_click(self, row: int, col: int):
        """Handle clicks on the player grid"""
        if self.game_phase == 'placement':
            self.place_ship(row, col)
        # During battle phase, player grid is not clickable for attacks
    
    def handle_ai_grid_click(self, row: int, col: int):
        """Handle clicks on the AI grid (attacks during battle phase)"""
        if self.game_phase == 'battle' and self.current_player == 'player' and not self.game_over:
            self.make_attack(row, col, 'player')
    
    def handle_right_click(self, row: int, col: int):
        """Handle right-click to rotate ship during placement"""
        if self.game_phase == 'placement':
            self.rotate_ship()
    
    def show_ship_preview(self, row: int, col: int):
        """Show preview of ship placement"""
        if self.game_phase != 'placement' or self.current_ship_index >= len(self.SHIPS):
            return
        
        # Clear previous preview
        self.clear_ship_preview()
        
        # Calculate ship positions
        ship_size = self.SHIPS[self.current_ship_index].value
        positions = self.get_ship_positions(row, col, ship_size, self.placement_orientation)
        
        # Check if placement is valid
        if self.is_valid_ship_placement(positions):
            # Show valid preview in light green
            for r, c in positions:
                self.player_grid_buttons[r][c].config(bg="#90EE90")
            self.preview_positions = positions
        else:
            # Show invalid preview in light red
            for r, c in positions:
                if 0 <= r < self.GRID_SIZE and 0 <= c < self.GRID_SIZE:
                    self.player_grid_buttons[r][c].config(bg="#FFB6C1")
            self.preview_positions = positions
    
    def clear_ship_preview(self):
        """Clear ship placement preview"""
        for r, c in self.preview_positions:
            if 0 <= r < self.GRID_SIZE and 0 <= c < self.GRID_SIZE:
                if self.player_grid[r][c] == CellState.EMPTY:
                    self.player_grid_buttons[r][c].config(bg="#87CEEB")
                elif self.player_grid[r][c] == CellState.SHIP:
                    self.player_grid_buttons[r][c].config(bg="#808080")
        self.preview_positions = []
    
    def place_ship(self, row: int, col: int):
        """Place a ship on the player grid"""
        if self.current_ship_index >= len(self.SHIPS):
            return
        
        ship_type = self.SHIPS[self.current_ship_index]
        ship_size = ship_type.value
        positions = self.get_ship_positions(row, col, ship_size, self.placement_orientation)
        
        if self.is_valid_ship_placement(positions):
            # Place the ship
            ship = Ship(ship_type, positions)
            self.player_ships.append(ship)
            
            # Update grid state and UI
            for r, c in positions:
                self.player_grid[r][c] = CellState.SHIP
                self.player_grid_buttons[r][c].config(bg="#808080", text="■")
            
            # Move to next ship
            self.current_ship_index += 1
            
            if self.current_ship_index >= len(self.SHIPS):
                # All ships placed, start battle phase
                self.start_battle_phase()
            else:
                # Update info for next ship
                next_ship = self.SHIPS[self.current_ship_index]
                self.ship_info_label.config(
                    text=f"Place {next_ship.name} (Size: {next_ship.value})"
                )
            
            self.clear_ship_preview()
    
    def get_ship_positions(self, start_row: int, start_col: int, size: int, orientation: str) -> List[Tuple[int, int]]:
        """Get positions for a ship given start position, size, and orientation"""
        positions = []
        
        if orientation == 'horizontal':
            for i in range(size):
                positions.append((start_row, start_col + i))
        else:  # vertical
            for i in range(size):
                positions.append((start_row + i, start_col))
        
        return positions
    
    def is_valid_ship_placement(self, positions: List[Tuple[int, int]]) -> bool:
        """Check if ship placement is valid"""
        for row, col in positions:
            # Check bounds
            if row < 0 or row >= self.GRID_SIZE or col < 0 or col >= self.GRID_SIZE:
                return False
            
            # Check if cell is already occupied
            if self.player_grid[row][col] != CellState.EMPTY:
                return False
            
            # Check adjacent cells (ships can't touch)
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    adj_row, adj_col = row + dr, col + dc
                    if (0 <= adj_row < self.GRID_SIZE and 0 <= adj_col < self.GRID_SIZE and
                        self.player_grid[adj_row][adj_col] == CellState.SHIP and
                        (adj_row, adj_col) not in positions):
                        return False
        
        return True
    
    def rotate_ship(self):
        """Rotate ship orientation during placement"""
        if self.game_phase == 'placement':
            self.placement_orientation = 'vertical' if self.placement_orientation == 'horizontal' else 'horizontal'
            self.update_status(f"Ship orientation: {self.placement_orientation}")
    
    def auto_place_player_ships(self):
        """Automatically place all remaining player ships"""
        while self.current_ship_index < len(self.SHIPS):
            ship_type = self.SHIPS[self.current_ship_index]
            ship_size = ship_type.value
            
            # Try random placements until one works
            placed = False
            attempts = 0
            while not placed and attempts < 1000:
                row = random.randint(0, self.GRID_SIZE - 1)
                col = random.randint(0, self.GRID_SIZE - 1)
                orientation = random.choice(['horizontal', 'vertical'])
                
                positions = self.get_ship_positions(row, col, ship_size, orientation)
                
                if self.is_valid_ship_placement(positions):
                    # Place the ship
                    ship = Ship(ship_type, positions)
                    self.player_ships.append(ship)
                    
                    # Update grid state and UI
                    for r, c in positions:
                        self.player_grid[r][c] = CellState.SHIP
                        self.player_grid_buttons[r][c].config(bg="#808080", text="■")
                    
                    placed = True
                
                attempts += 1
            
            if not placed:
                self.update_status("Failed to auto-place ships. Try manual placement.")
                return
            
            self.current_ship_index += 1
        
        # All ships placed, start battle phase
        self.start_battle_phase()
    
    def place_ai_ships(self):
        """Automatically place AI ships using intelligent placement"""
        self.ai_ships = []
        
        for ship_type in self.SHIPS:
            ship_size = ship_type.value
            placed = False
            attempts = 0
            
            while not placed and attempts < 1000:
                row = random.randint(0, self.GRID_SIZE - 1)
                col = random.randint(0, self.GRID_SIZE - 1)
                orientation = random.choice(['horizontal', 'vertical'])
                
                positions = self.get_ship_positions(row, col, ship_size, orientation)
                
                if self.is_valid_ai_ship_placement(positions):
                    # Place the ship
                    ship = Ship(ship_type, positions)
                    self.ai_ships.append(ship)
                    
                    # Update AI grid state (but not UI - ships are hidden)
                    for r, c in positions:
                        self.ai_grid[r][c] = CellState.SHIP
                    
                    placed = True
                
                attempts += 1
    
    def is_valid_ai_ship_placement(self, positions: List[Tuple[int, int]]) -> bool:
        """Check if AI ship placement is valid"""
        for row, col in positions:
            # Check bounds
            if row < 0 or row >= self.GRID_SIZE or col < 0 or col >= self.GRID_SIZE:
                return False
            
            # Check if cell is already occupied
            if self.ai_grid[row][col] != CellState.EMPTY:
                return False
            
            # Check adjacent cells (ships can't touch)
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    adj_row, adj_col = row + dr, col + dc
                    if (0 <= adj_row < self.GRID_SIZE and 0 <= adj_col < self.GRID_SIZE and
                        self.ai_grid[adj_row][adj_col] == CellState.SHIP and
                        (adj_row, adj_col) not in positions):
                        return False
        
        return True
    
    def start_battle_phase(self):
        """Start the battle phase after ship placement"""
        self.game_phase = 'battle'
        self.current_phase_label.config(text="Battle Phase - Sink the Enemy Fleet!")
        self.ship_info_label.config(text="Click on enemy grid to attack")
        
        # Enable AI grid for attacks
        for row in self.ai_grid_buttons:
            for button in row:
                button.config(state='normal')
        
        # Hide placement controls
        self.rotate_button.config(state='disabled')
        self.auto_place_button.config(state='disabled')
        
        self.update_status("Battle begins! Click on enemy waters to attack.")
    
    def make_attack(self, row: int, col: int, attacker: str) -> bool:
        """Make an attack on the specified grid position"""
        if attacker == 'player':
            # Player attacking AI grid
            if self.ai_grid[row][col] in [CellState.HIT, CellState.MISS]:
                self.update_status("You already attacked that position!")
                return False
            
            # Check if it's a hit or miss
            if self.ai_grid[row][col] == CellState.SHIP:
                # Hit!
                self.ai_grid[row][col] = CellState.HIT
                self.ai_grid_buttons[row][col].config(bg="#FF0000", text="X", fg="white")
                
                # Check if ship is sunk
                sunk_ship = self.check_ship_sunk(row, col, self.ai_ships)
                if sunk_ship:
                    self.update_status(f"Hit! You sunk the enemy {sunk_ship.ship_type.name}!")
                    self.mark_sunk_ship(sunk_ship, 'ai')
                else:
                    self.update_status("Hit! Keep firing!")
                
                # Check for victory
                if self.check_victory('player'):
                    self.end_game('player')
                    return True
                
            else:
                # Miss
                self.ai_grid[row][col] = CellState.MISS
                self.ai_grid_buttons[row][col].config(bg="#0000FF", text="•", fg="white")
                self.update_status("Miss! AI's turn.")
                
                # Switch to AI turn
                self.current_player = 'ai'
                self.parent_frame.after(1000, self.make_ai_attack)
        
        else:  # AI attacking player grid
            # AI attacking player grid
            if self.player_grid[row][col] in [CellState.HIT, CellState.MISS]:
                return False  # AI shouldn't attack same position twice
            
            # Check if it's a hit or miss
            if self.player_grid[row][col] == CellState.SHIP:
                # Hit!
                self.player_grid[row][col] = CellState.HIT
                self.player_grid_buttons[row][col].config(bg="#FF0000", text="X", fg="white")
                
                # Update AI strategy
                self.ai_last_hit = (row, col)
                self.ai_target_mode = True
                if (row, col) not in self.ai_target_stack:
                    self.ai_target_stack.append((row, col))
                
                # Check if ship is sunk
                sunk_ship = self.check_ship_sunk(row, col, self.player_ships)
                if sunk_ship:
                    self.update_status(f"AI hit and sunk your {sunk_ship.ship_type.name}!")
                    self.mark_sunk_ship(sunk_ship, 'player')
                    self.ai_target_mode = False
                    self.ai_target_stack = []
                    self.ai_last_hit = None
                    self.ai_hit_direction = None
                else:
                    self.update_status("AI hit your ship!")
                
                # Check for AI victory
                if self.check_victory('ai'):
                    self.end_game('ai')
                    return True
                
                # AI gets another turn after a hit
                self.parent_frame.after(1000, self.make_ai_attack)
                
            else:
                # Miss
                self.player_grid[row][col] = CellState.MISS
                self.player_grid_buttons[row][col].config(bg="#0000FF", text="•", fg="white")
                self.update_status("AI missed! Your turn.")
                
                # Switch back to player turn
                self.current_player = 'player'
        
        self.move_count += 1
        return True
    
    def make_ai_attack(self):
        """Make AI attack using intelligent strategy"""
        if self.game_over or self.current_player != 'ai':
            return
        
        target_row, target_col = self.get_ai_attack_position()
        
        if target_row is not None and target_col is not None:
            self.make_attack(target_row, target_col, 'ai')
    
    def get_ai_attack_position(self) -> Tuple[Optional[int], Optional[int]]:
        """Get AI attack position using intelligent strategy"""
        # If in target mode (after a hit), use targeted strategy
        if self.ai_target_mode and self.ai_last_hit:
            return self.get_targeted_attack()
        
        # Otherwise, use hunting strategy
        return self.get_hunting_attack()
    
    def get_targeted_attack(self) -> Tuple[Optional[int], Optional[int]]:
        """Get targeted attack position after hitting a ship"""
        if not self.ai_last_hit:
            return self.get_hunting_attack()
        
        last_row, last_col = self.ai_last_hit
        
        # If we have a direction, continue in that direction
        if self.ai_hit_direction:
            dr, dc = self.ai_hit_direction
            next_row, next_col = last_row + dr, last_col + dc
            
            # Check if we can continue in this direction
            if (0 <= next_row < self.GRID_SIZE and 0 <= next_col < self.GRID_SIZE and
                self.player_grid[next_row][next_col] not in [CellState.HIT, CellState.MISS]):
                return next_row, next_col
            else:
                # Can't continue, try opposite direction
                opposite_dr, opposite_dc = -dr, -dc
                # Find the other end of the ship
                current_row, current_col = last_row, last_col
                while (0 <= current_row - opposite_dr < self.GRID_SIZE and 
                       0 <= current_col - opposite_dc < self.GRID_SIZE and
                       self.player_grid[current_row - opposite_dr][current_col - opposite_dc] == CellState.HIT):
                    current_row -= opposite_dr
                    current_col -= opposite_dc
                
                next_row, next_col = current_row + opposite_dr, current_col + opposite_dc
                if (0 <= next_row < self.GRID_SIZE and 0 <= next_col < self.GRID_SIZE and
                    self.player_grid[next_row][next_col] not in [CellState.HIT, CellState.MISS]):
                    return next_row, next_col
        
        # Try adjacent positions to the last hit
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]  # right, down, left, up
        
        for dr, dc in directions:
            next_row, next_col = last_row + dr, last_col + dc
            
            if (0 <= next_row < self.GRID_SIZE and 0 <= next_col < self.GRID_SIZE and
                self.player_grid[next_row][next_col] not in [CellState.HIT, CellState.MISS]):
                
                # If this would be a second hit, establish direction
                if self.player_grid[next_row][next_col] == CellState.SHIP:
                    self.ai_hit_direction = (dr, dc)
                
                return next_row, next_col
        
        # No valid adjacent positions, switch to hunting mode
        self.ai_target_mode = False
        self.ai_last_hit = None
        self.ai_hit_direction = None
        return self.get_hunting_attack()
    
    def get_hunting_attack(self) -> Tuple[Optional[int], Optional[int]]:
        """Get hunting attack position using checkerboard pattern"""
        # Use checkerboard pattern for efficient hunting
        available_positions = []
        
        for row in range(self.GRID_SIZE):
            for col in range(self.GRID_SIZE):
                if self.player_grid[row][col] not in [CellState.HIT, CellState.MISS]:
                    # Prefer checkerboard pattern (every other cell)
                    if (row + col) % 2 == 0:
                        available_positions.append((row, col))
        
        # If no checkerboard positions available, try all positions
        if not available_positions:
            for row in range(self.GRID_SIZE):
                for col in range(self.GRID_SIZE):
                    if self.player_grid[row][col] not in [CellState.HIT, CellState.MISS]:
                        available_positions.append((row, col))
        
        if available_positions:
            return random.choice(available_positions)
        
        return None, None
    
    def check_ship_sunk(self, row: int, col: int, ships: List[Ship]) -> Optional[Ship]:
        """Check if a ship is sunk after a hit"""
        for ship in ships:
            if (row, col) in ship.positions:
                ship.hits.add((row, col))
                if ship.is_sunk:
                    return ship
                break
        return None
    
    def mark_sunk_ship(self, ship: Ship, grid_type: str):
        """Mark a sunk ship on the grid"""
        if grid_type == 'ai':
            buttons = self.ai_grid_buttons
        else:
            buttons = self.player_grid_buttons
        
        # Mark all positions of the sunk ship
        for row, col in ship.positions:
            buttons[row][col].config(bg="#800000", text="☠", fg="white")
    
    def check_victory(self, player: str) -> bool:
        """Check if a player has won by sinking all enemy ships"""
        if player == 'player':
            # Check if all AI ships are sunk
            return all(ship.is_sunk for ship in self.ai_ships)
        else:
            # Check if all player ships are sunk
            return all(ship.is_sunk for ship in self.player_ships)
    
    def end_game(self, winner: str):
        """End the game and show result"""
        self.game_over = True
        self.winner = winner
        
        # Disable all grids
        for row in self.ai_grid_buttons:
            for button in row:
                button.config(state='disabled')
        
        # Show result
        if winner == 'player':
            result_text = "🎉 Victory! You sunk the entire enemy fleet!"
            self.update_status("Congratulations! You won the naval battle!")
        else:
            result_text = "💥 Defeat! The AI sunk your entire fleet!"
            self.update_status("AI won this battle. Better luck next time!")
        
        # Update phase display to show result
        self.current_phase_label.config(
            text=result_text,
            foreground="#0078d4" if winner == 'player' else "#d13438"
        )
        
        # Notify game manager of game end
        if self.end_game_callback:
            self.end_game_callback(winner)
        else:
            # Show popup with result if no callback
            messagebox.showinfo("Game Over", result_text)
    
    def reset_game(self):
        """Reset the game to initial state"""
        # Reset game state
        self.player_grid = [[CellState.EMPTY for _ in range(self.GRID_SIZE)] for _ in range(self.GRID_SIZE)]
        self.ai_grid = [[CellState.EMPTY for _ in range(self.GRID_SIZE)] for _ in range(self.GRID_SIZE)]
        self.player_ships = []
        self.ai_ships = []
        self.current_player = 'player'
        self.game_over = False
        self.winner = None
        self.move_count = 0
        self.game_phase = 'placement'
        self.current_ship_index = 0
        self.placement_orientation = 'horizontal'
        self.preview_positions = []
        
        # Reset AI strategy
        self.ai_target_mode = False
        self.ai_target_stack = []
        self.ai_last_hit = None
        self.ai_hit_direction = None
        self.ai_tried_positions = set()
        
        # Reset UI
        for row in self.player_grid_buttons:
            for button in row:
                button.config(text='', bg='#87CEEB', state='normal')
        
        for row in self.ai_grid_buttons:
            for button in row:
                button.config(text='', bg='#87CEEB', state='disabled')
        
        # Reset controls
        self.rotate_button.config(state='normal')
        self.auto_place_button.config(state='normal')
        
        # Reset labels
        self.current_phase_label.config(text="Ship Placement Phase", foreground="#0078d4")
        self.ship_info_label.config(text=f"Place {self.SHIPS[0].name} (Size: {self.SHIPS[0].value})")
        
        # Place AI ships
        self.place_ai_ships()
        
        self.update_status("New game started! Place your ships.")
    
    def update_status(self, message: str):
        """Update status message"""
        if self.status_callback:
            self.status_callback(message)
    
    def back_to_selection(self):
        """Return to game selection"""
        if self.back_callback:
            self.back_callback()
    
    def get_game_state(self) -> BattleshipState:
        """Get current game state"""
        return BattleshipState(
            player_grid=copy.deepcopy(self.player_grid),
            ai_grid=copy.deepcopy(self.ai_grid),
            player_ships=copy.deepcopy(self.player_ships),
            ai_ships=copy.deepcopy(self.ai_ships),
            current_player=self.current_player,
            winner=self.winner,
            game_over=self.game_over,
            move_count=self.move_count,
            game_phase=self.game_phase
        )