"""
Game Manager for Z.E.U.S. Virtual Assistant
Handles game selection, initialization, and state management
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Dict, Any, Callable
from dataclasses import dataclass
from enum import Enum
import json
import os
from datetime import datetime
from .tic_tac_toe import TicTacToeGame
from .connect_4 import Connect4Game
from .battleship import BattleshipGame


class GameType(Enum):
    """Available game types"""
    TIC_TAC_TOE = "tic_tac_toe"
    CONNECT_4 = "connect_4"
    BATTLESHIP = "battleship"


@dataclass
class GameResult:
    """Game result data model"""
    game_type: str
    winner: Optional[str]
    player_score: int
    ai_score: int
    game_duration: float
    moves_count: int
    timestamp: datetime
    
@dataclass
class GameState:
    """Game state data model"""
    game_type: str
    board_state: Any
    current_player: str
    game_status: str  # 'active', 'ended', 'paused'
    move_history: list
    ai_difficulty: str
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None


class GameManager:
    """Main game manager class for handling game selection and state"""
    
    def __init__(self, parent_frame: ttk.Frame):
        self.parent_frame = parent_frame
        self.current_game = None
        self.current_game_type = None
        self.game_state = None
        self.status_callback = None
        self.game_callback = None
        
        # Game instances will be created on demand
        self.game_instances = {}
        
        # Game statistics and persistence
        self.game_results_file = "data/game_results.json"
        self.saved_game_file = "data/saved_game.json"
        self.game_results = self.load_game_results()
        
        # Ensure data directory exists
        os.makedirs("data", exist_ok=True)
        
        # Initialize the game selection interface
        self.setup_game_selection_ui()
    
    def setup_game_selection_ui(self):
        """Create the game selection interface"""
        # Clear any existing content
        for widget in self.parent_frame.winfo_children():
            widget.destroy()
        
        # Main container
        main_container = ttk.Frame(self.parent_frame)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Title section
        title_frame = ttk.Frame(main_container)
        title_frame.pack(fill=tk.X, pady=(20, 30))
        
        title_label = ttk.Label(
            title_frame,
            text="🎮 Interactive Games",
            font=("Arial", 24, "bold"),
            foreground="#0078d4"
        )
        title_label.pack()
        
        subtitle_label = ttk.Label(
            title_frame,
            text="Choose a game to play against the AI",
            font=("Arial", 12),
            foreground="#666666"
        )
        subtitle_label.pack(pady=(5, 0))
        
        # Games grid
        games_frame = ttk.Frame(main_container)
        games_frame.pack(expand=True, pady=20)
        
        # Configure grid weights for centering
        games_frame.grid_columnconfigure(0, weight=1)
        games_frame.grid_columnconfigure(1, weight=1)
        games_frame.grid_columnconfigure(2, weight=1)
        
        # Tic-Tac-Toe game card
        self._create_game_card(
            games_frame,
            row=0, column=0,
            title="Tic-Tac-Toe",
            emoji="⭕",
            description="Classic 3x3 grid game\nFirst to get 3 in a row wins!",
            game_type=GameType.TIC_TAC_TOE,
            difficulty="Easy"
        )
        
        # Connect 4 game card
        self._create_game_card(
            games_frame,
            row=0, column=1,
            title="Connect 4",
            emoji="🔴",
            description="Drop pieces to connect 4\nVertical, horizontal, or diagonal!",
            game_type=GameType.CONNECT_4,
            difficulty="Medium"
        )
        
        # Battleship game card
        self._create_game_card(
            games_frame,
            row=0, column=2,
            title="Battleship",
            emoji="🚢",
            description="Naval strategy game\nSink all enemy ships to win!",
            game_type=GameType.BATTLESHIP,
            difficulty="Hard"
        )
        
        # Resume game section (if saved game exists)
        if self.has_saved_game():
            resume_frame = ttk.Frame(main_container)
            resume_frame.pack(pady=20)
            
            resume_label = ttk.Label(
                resume_frame,
                text="📁 Saved Game Available",
                font=("Arial", 12, "bold"),
                foreground="#0078d4"
            )
            resume_label.pack()
            
            ttk.Button(
                resume_frame,
                text="▶️ Resume Game",
                command=self.load_saved_game,
                style='Nav.TButton'
            ).pack(pady=5)
        
        # Statistics and info section
        back_frame = ttk.Frame(main_container)
        back_frame.pack(side=tk.BOTTOM, pady=20)
        
        # Show game statistics if available
        stats = self.get_game_statistics()
        if stats["total_games"] > 0:
            stats_text = f"Games Played: {stats['total_games']} | Win Rate: {stats['win_rate']:.1f}% | Favorite: {stats['favorite_game']}"
            stats_label = ttk.Label(
                back_frame,
                text=stats_text,
                font=("Arial", 9),
                foreground="#666666"
            )
            stats_label.pack(pady=(0, 5))
        
        # Game info
        info_label = ttk.Label(
            back_frame,
            text="All games feature intelligent AI opponents with varying difficulty levels",
            font=("Arial", 10),
            foreground="#666666"
        )
        info_label.pack()
    
    def _create_game_card(self, parent, row: int, column: int, title: str, 
                         emoji: str, description: str, game_type: GameType, difficulty: str):
        """Create a game selection card"""
        # Card frame with border
        card_frame = ttk.Frame(parent, relief=tk.RAISED, borderwidth=2)
        card_frame.grid(row=row, column=column, padx=15, pady=10, sticky="nsew")
        
        # Configure card internal layout
        card_frame.grid_columnconfigure(0, weight=1)
        
        # Game emoji/icon
        emoji_label = ttk.Label(
            card_frame,
            text=emoji,
            font=("Arial", 48)
        )
        emoji_label.grid(row=0, column=0, pady=(20, 10))
        
        # Game title
        title_label = ttk.Label(
            card_frame,
            text=title,
            font=("Arial", 16, "bold"),
            foreground="#0078d4"
        )
        title_label.grid(row=1, column=0, pady=(0, 5))
        
        # Difficulty indicator
        difficulty_label = ttk.Label(
            card_frame,
            text=f"Difficulty: {difficulty}",
            font=("Arial", 10),
            foreground="#666666"
        )
        difficulty_label.grid(row=2, column=0, pady=(0, 10))
        
        # Game description
        desc_label = ttk.Label(
            card_frame,
            text=description,
            font=("Arial", 10),
            justify=tk.CENTER,
            wraplength=180
        )
        desc_label.grid(row=3, column=0, pady=(0, 15), padx=10)
        
        # Play button
        play_button = ttk.Button(
            card_frame,
            text="Play Game",
            command=lambda: self.start_game(game_type),
            style='Nav.TButton'
        )
        play_button.grid(row=4, column=0, pady=(0, 20), padx=20, sticky="ew")
        
        # Store reference for potential styling updates
        setattr(self, f"{game_type.value}_card", card_frame)
    
    def start_game(self, game_type: GameType):
        """Initialize and start a specific game"""
        try:
            self.current_game_type = game_type
            
            # Update status
            if self.status_callback:
                self.status_callback(f"Starting {game_type.value.replace('_', ' ').title()}...")
            
            # Clear the selection interface
            for widget in self.parent_frame.winfo_children():
                widget.destroy()
            
            # Create game-specific interface based on type
            if game_type == GameType.TIC_TAC_TOE:
                self._start_tic_tac_toe()
            elif game_type == GameType.CONNECT_4:
                self._start_connect_4()
            elif game_type == GameType.BATTLESHIP:
                self._start_battleship()
            
            # Initialize game state
            self.game_state = GameState(
                game_type=game_type.value,
                board_state=None,  # Will be set by specific game
                current_player="human",
                game_status="active",
                move_history=[],
                ai_difficulty="normal",
                start_time=datetime.now()
            )
            
            if self.status_callback:
                self.status_callback(f"{game_type.value.replace('_', ' ').title()} started - Your turn!")
                
        except Exception as e:
            if self.status_callback:
                self.status_callback(f"Error starting game: {str(e)}")
            # Fall back to selection screen
            self.show_game_selection()
    
    def _start_tic_tac_toe(self):
        """Start Tic-Tac-Toe game"""
        # Create and initialize the Tic-Tac-Toe game
        self.current_game = TicTacToeGame(
            parent_frame=self.parent_frame,
            status_callback=self.status_callback,
            back_callback=self.show_game_selection,
            end_game_callback=self.end_game
        )
        
        # Store game instance for potential future reference
        self.game_instances[GameType.TIC_TAC_TOE] = self.current_game
    
    def _start_connect_4(self):
        """Start Connect 4 game"""
        # Create and initialize the Connect 4 game
        self.current_game = Connect4Game(
            parent_frame=self.parent_frame,
            status_callback=self.status_callback,
            back_callback=self.show_game_selection,
            end_game_callback=self.end_game
        )
        
        # Store game instance for potential future reference
        self.game_instances[GameType.CONNECT_4] = self.current_game
    
    def _start_battleship(self):
        """Start Battleship game"""
        # Create and initialize the Battleship game
        self.current_game = BattleshipGame(
            parent_frame=self.parent_frame,
            status_callback=self.status_callback,
            back_callback=self.show_game_selection,
            end_game_callback=self.end_game
        )
        
        # Store game instance for potential future reference
        self.game_instances[GameType.BATTLESHIP] = self.current_game
    
    def show_game_selection(self):
        """Return to the game selection interface"""
        self.current_game = None
        self.current_game_type = None
        self.game_state = None
        self.setup_game_selection_ui()
        
        if self.status_callback:
            self.status_callback("Games mode - Choose a game to play")
    
    def handle_player_move(self, move: Any) -> bool:
        """Handle a player move (to be implemented by specific games)"""
        if not self.current_game:
            return False
        
        # This will be implemented by specific game classes
        # For now, return False as placeholder
        return False
    
    def get_ai_move(self) -> Any:
        """Get AI move for current game (to be implemented by specific games)"""
        if not self.current_game:
            return None
        
        # This will be implemented by specific game classes
        # For now, return None as placeholder
        return None
    
    def check_game_end(self) -> bool:
        """Check if current game has ended (to be implemented by specific games)"""
        if not self.current_game:
            return False
        
        # This will be implemented by specific game classes
        # For now, return False as placeholder
        return False
    
    def get_game_state(self) -> Optional[GameState]:
        """Get current game state"""
        return self.game_state
    
    def set_status_callback(self, callback: Callable[[str], None]):
        """Set callback function for status updates"""
        self.status_callback = callback
    
    def set_game_callback(self, callback: Callable[[str, Any], None]):
        """Set callback function for game events"""
        self.game_callback = callback
    
    def pause_game(self):
        """Pause the current game"""
        if self.game_state and self.game_state.game_status == "active":
            self.game_state.game_status = "paused"
            self.save_game_state()
            if self.status_callback:
                self.status_callback("Game paused")
    
    def resume_game(self):
        """Resume the current game"""
        if self.game_state and self.game_state.game_status == "paused":
            self.game_state.game_status = "active"
            if self.status_callback:
                self.status_callback("Game resumed")
    
    def save_game_state(self):
        """Save current game state to file"""
        if not self.game_state:
            return False
        
        try:
            # Get detailed state from current game if available
            detailed_state = None
            if self.current_game and hasattr(self.current_game, 'get_game_state'):
                detailed_state = self.current_game.get_game_state()
            
            save_data = {
                "game_type": self.game_state.game_type,
                "board_state": self.game_state.board_state,
                "current_player": self.game_state.current_player,
                "game_status": self.game_state.game_status,
                "move_history": self.game_state.move_history,
                "ai_difficulty": self.game_state.ai_difficulty,
                "start_time": self.game_state.start_time.isoformat() if self.game_state.start_time else None,
                "end_time": self.game_state.end_time.isoformat() if self.game_state.end_time else None,
                "detailed_state": detailed_state.__dict__ if detailed_state else None
            }
            
            with open(self.saved_game_file, 'w') as f:
                json.dump(save_data, f, indent=2, default=str)
            return True
        except Exception as e:
            print(f"Error saving game state: {e}")
            return False
    
    def load_saved_game(self) -> bool:
        """Load saved game state from file"""
        try:
            if not os.path.exists(self.saved_game_file):
                return False
            
            with open(self.saved_game_file, 'r') as f:
                save_data = json.load(f)
            
            # Restore game state
            self.game_state = GameState(
                game_type=save_data["game_type"],
                board_state=save_data["board_state"],
                current_player=save_data["current_player"],
                game_status=save_data["game_status"],
                move_history=save_data["move_history"],
                ai_difficulty=save_data["ai_difficulty"],
                start_time=datetime.fromisoformat(save_data["start_time"]) if save_data.get("start_time") else None,
                end_time=datetime.fromisoformat(save_data["end_time"]) if save_data.get("end_time") else None
            )
            
            # Restore the specific game
            game_type = GameType(save_data["game_type"])
            self.current_game_type = game_type
            
            # Start the game and restore its state
            if game_type == GameType.TIC_TAC_TOE:
                self._start_tic_tac_toe()
            elif game_type == GameType.CONNECT_4:
                self._start_connect_4()
            elif game_type == GameType.BATTLESHIP:
                self._start_battleship()
            
            # Restore detailed game state if available
            if save_data.get("detailed_state") and hasattr(self.current_game, 'restore_game_state'):
                self.current_game.restore_game_state(save_data["detailed_state"])
            
            if self.status_callback:
                self.status_callback(f"Resumed {game_type.value.replace('_', ' ').title()}")
            
            return True
        except Exception as e:
            print(f"Error loading saved game: {e}")
            return False
    
    def clear_saved_game(self):
        """Clear saved game state file"""
        try:
            if os.path.exists(self.saved_game_file):
                os.remove(self.saved_game_file)
        except Exception as e:
            print(f"Error clearing saved game: {e}")
    
    def has_saved_game(self) -> bool:
        """Check if there's a saved game available"""
        return os.path.exists(self.saved_game_file)
    
    def save_game_result(self, result: GameResult):
        """Save game result to results file"""
        try:
            self.game_results.append(result)
            
            # Convert results to serializable format
            results_data = []
            for r in self.game_results:
                results_data.append({
                    "game_type": r.game_type,
                    "winner": r.winner,
                    "player_score": r.player_score,
                    "ai_score": r.ai_score,
                    "game_duration": r.game_duration,
                    "moves_count": r.moves_count,
                    "timestamp": r.timestamp.isoformat()
                })
            
            with open(self.game_results_file, 'w') as f:
                json.dump(results_data, f, indent=2)
        except Exception as e:
            print(f"Error saving game result: {e}")
    
    def load_game_results(self) -> list:
        """Load game results from file"""
        try:
            if not os.path.exists(self.game_results_file):
                return []
            
            with open(self.game_results_file, 'r') as f:
                results_data = json.load(f)
            
            results = []
            for r_data in results_data:
                result = GameResult(
                    game_type=r_data["game_type"],
                    winner=r_data["winner"],
                    player_score=r_data["player_score"],
                    ai_score=r_data["ai_score"],
                    game_duration=r_data["game_duration"],
                    moves_count=r_data["moves_count"],
                    timestamp=datetime.fromisoformat(r_data["timestamp"])
                )
                results.append(result)
            return results
        except Exception as e:
            print(f"Error loading game results: {e}")
            return []
    
    def get_game_statistics(self) -> Dict[str, Any]:
        """Get game statistics summary"""
        if not self.game_results:
            return {
                "total_games": 0,
                "wins": 0,
                "losses": 0,
                "draws": 0,
                "win_rate": 0.0,
                "average_duration": 0.0,
                "favorite_game": "None"
            }
        
        total_games = len(self.game_results)
        wins = sum(1 for r in self.game_results if r.winner == "player")
        losses = sum(1 for r in self.game_results if r.winner == "ai")
        draws = sum(1 for r in self.game_results if r.winner is None)
        
        win_rate = (wins / total_games * 100) if total_games > 0 else 0.0
        average_duration = sum(r.game_duration for r in self.game_results) / total_games if total_games > 0 else 0.0
        
        # Find most played game
        game_counts = {}
        for r in self.game_results:
            game_counts[r.game_type] = game_counts.get(r.game_type, 0) + 1
        favorite_game = max(game_counts, key=game_counts.get) if game_counts else "None"
        
        return {
            "total_games": total_games,
            "wins": wins,
            "losses": losses,
            "draws": draws,
            "win_rate": win_rate,
            "average_duration": average_duration,
            "favorite_game": favorite_game.replace('_', ' ').title()
        }
    
    def show_game_result_dialog(self, result: GameResult):
        """Show game result dialog with options"""
        # Create result dialog
        result_window = tk.Toplevel(self.parent_frame)
        result_window.title("Game Over")
        result_window.geometry("400x300")
        result_window.resizable(False, False)
        
        # Center the window
        result_window.transient(self.parent_frame.winfo_toplevel())
        result_window.grab_set()
        
        # Main frame
        main_frame = ttk.Frame(result_window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Result title
        if result.winner == "player":
            title_text = "🎉 Victory!"
            title_color = "#0078d4"
        elif result.winner == "ai":
            title_text = "💻 AI Wins!"
            title_color = "#d13438"
        else:
            title_text = "🤝 Draw!"
            title_color = "#666666"
        
        title_label = ttk.Label(
            main_frame,
            text=title_text,
            font=("Arial", 18, "bold"),
            foreground=title_color
        )
        title_label.pack(pady=(0, 20))
        
        # Game details
        details_frame = ttk.Frame(main_frame)
        details_frame.pack(fill=tk.X, pady=10)
        
        details = [
            ("Game:", result.game_type.replace('_', ' ').title()),
            ("Duration:", f"{result.game_duration:.1f} seconds"),
            ("Moves:", str(result.moves_count))
        ]
        
        for label, value in details:
            row_frame = ttk.Frame(details_frame)
            row_frame.pack(fill=tk.X, pady=2)
            
            ttk.Label(row_frame, text=label, font=("Arial", 10, "bold")).pack(side=tk.LEFT)
            ttk.Label(row_frame, text=value, font=("Arial", 10)).pack(side=tk.RIGHT)
        
        # Statistics
        stats = self.get_game_statistics()
        stats_frame = ttk.LabelFrame(main_frame, text="Your Statistics", padding=10)
        stats_frame.pack(fill=tk.X, pady=10)
        
        stats_text = f"Total Games: {stats['total_games']}\n"
        stats_text += f"Win Rate: {stats['win_rate']:.1f}%\n"
        stats_text += f"Favorite Game: {stats['favorite_game']}"
        
        ttk.Label(stats_frame, text=stats_text, font=("Arial", 9)).pack()
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(side=tk.BOTTOM, pady=20)
        
        # Play again button
        ttk.Button(
            button_frame,
            text="🔄 Play Again",
            command=lambda: self._play_again(result_window)
        ).pack(side=tk.LEFT, padx=5)
        
        # Different game button
        ttk.Button(
            button_frame,
            text="🎮 Choose Game",
            command=lambda: self._choose_different_game(result_window)
        ).pack(side=tk.LEFT, padx=5)
        
        # Close button
        ttk.Button(
            button_frame,
            text="Close",
            command=result_window.destroy
        ).pack(side=tk.LEFT, padx=5)
    
    def _play_again(self, dialog_window):
        """Start the same game again"""
        dialog_window.destroy()
        if self.current_game_type:
            self.start_game(self.current_game_type)
    
    def _choose_different_game(self, dialog_window):
        """Return to game selection"""
        dialog_window.destroy()
        self.show_game_selection()
    
    def end_game(self, winner: str = None):
        """End the current game and save results"""
        if self.game_state:
            self.game_state.game_status = "ended"
            self.game_state.end_time = datetime.now()
            
            # Calculate game statistics
            game_duration = 0
            if self.game_state.start_time and self.game_state.end_time:
                game_duration = (self.game_state.end_time - self.game_state.start_time).total_seconds()
            
            # Create game result
            result = GameResult(
                game_type=self.game_state.game_type,
                winner=winner,
                player_score=1 if winner == "player" else 0,
                ai_score=1 if winner == "ai" else 0,
                game_duration=game_duration,
                moves_count=len(self.game_state.move_history),
                timestamp=self.game_state.end_time or datetime.now()
            )
            
            # Save result
            self.save_game_result(result)
            
            # Clear saved game state
            self.clear_saved_game()
            
            # Show result dialog
            self.show_game_result_dialog(result)
            
            if winner and self.status_callback:
                self.status_callback(f"Game ended - {winner} wins!")
            elif self.status_callback:
                self.status_callback("Game ended")