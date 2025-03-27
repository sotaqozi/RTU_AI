import tkinter as tk
import random
import math
import time

#%% Game Tree Structure

class GameNode:
    """Tree node to represent game states"""
    def __init__(self, number, player_score, ai_score, bank, is_player_turn):
        self.number = number
        self.player_score = player_score
        self.ai_score = ai_score
        self.bank = bank
        self.is_player_turn = is_player_turn
        self.children = []
        self.score = None
        self.best_move = None
    
    def add_child(self, child_node):
        """Add a child node to this node"""
        self.children.append(child_node)
        return child_node
    
    def is_terminal(self):
        """Check if this is a terminal state (game over)"""
        return self.number <= 10

#%% Side functions

def generate_initial_numbers():
    """Generate 5 initial numbers between 20000 and 30000"""
    numbers = []
    while len(numbers) < 5:
        num = random.randint(20000, 30000)
        numbers.append(num)
    return numbers

def process_turn(new_number, player_score, bank):
    """Process the turn according to game rules"""
    if new_number % 2 == 0:
        player_score -= 1
    else:
        player_score += 1
    if new_number % 10 == 0 or new_number % 10 == 5:
        bank += 1
        
    return new_number, player_score, bank

#%% Heuristic

def evaluate_state(node):
    """Evaluate the game state from the perspective of the maximizing player (AI)"""
    # If it's a terminal state (number ≤ 10), check if AI wins or loses
    if node.is_terminal():
        if not node.is_player_turn:  # Player must play but can't, AI wins
            return 10000
        else:  # AI must play but can't, AI loses
            return -10000
    
    # Initialize the score
    score = 0
    
    # Factor for the current number - smaller is better for the next player
    # With more importance as we approach 10
    number_factor = (100 - node.number)
    if node.number < 50:
        number_factor *= 3  # Give more importance to small numbers
    if node.number < 20:
        number_factor *= 5  # Even more important when approaching the end
    
    # Bonus for multiples of 5 and 10 (give +1 to the bank)
    bank_bonus = 100 if node.number % 5 == 0 else 0
    
    # Evaluate differently depending on whose turn it is
    if node.is_player_turn:
        score += number_factor * 0.5  # Less important for the player
        score -= node.player_score * 80  # Player's score is negative for AI
        score += node.ai_score * 100  # AI's score is positive
        score += bank_bonus * 0.5  # Bank is less important if it's the player's turn
    else:
        score += number_factor  # More important for AI
        score -= node.player_score * 100  # Player's score is very negative for AI
        score += node.ai_score * 120  # AI's score is very positive
        score += bank_bonus  # Bank is important if it's AI's turn
    
    # Controlling the bank adds value
    score += node.bank * 40
    
    # Analyze possible divisors for the current number
    # Prefer numbers with advantageous divisions
    for divisor in [2, 3, 4]:
        new_number = round(node.number / divisor)
        # Check if the division gives a number that advantages the next player
        if new_number <= 10:  # If it ends the game
            if node.is_player_turn:  # If it's the player's turn
                score -= 500  # Bad for AI
            else:  # If it's AI's turn
                score += 500  # Good for AI
        elif new_number % 2 == 0 and not node.is_player_turn:
            score += 30  # Good for AI if it can get an even number
        elif new_number % 2 == 1 and node.is_player_turn:
            score -= 60  # Bad for AI if the player can get an odd number
    
    return score

#%% Game Tree Generation

def generate_game_tree(node, depth, max_depth):
    """Generate a game tree to the specified depth"""
    if depth >= max_depth or node.is_terminal():
        node.score = evaluate_state(node)
        return node
    
    # Toujours utiliser les trois diviseurs, peu importe si le nombre est divisible
    possible_divisors = [2, 3, 4]
    
    for divisor in possible_divisors:
        # Arrondir au lieu de simplement diviser
        new_number = round(node.number / divisor)
        
        # Determine whose score to update
        if node.is_player_turn:
            player_score, ai_score = node.player_score, node.ai_score
            new_number, player_score, new_bank = process_turn(new_number, player_score, node.bank)
        else:
            player_score, ai_score = node.player_score, node.ai_score
            new_number, ai_score, new_bank = process_turn(new_number, ai_score, node.bank)
            
        # Create child node
        child = GameNode(new_number, player_score, ai_score, new_bank, not node.is_player_turn)
        node.add_child(child)
        
        # Recursively generate subtree
        generate_game_tree(child, depth + 1, max_depth)
    
    return node

#%% Minimax 

def minimax(node, depth, is_maximizing):
    """Minimax algorithm implementation"""
    if depth == 0 or node.is_terminal():
        node.score = evaluate_state(node)
        return node.score
    
    if is_maximizing:
        best_score = -math.inf
        for child in node.children:
            score = minimax(child, depth - 1, False)
            if score > best_score:
                best_score = score
                node.best_move = child
        node.score = best_score
        return best_score
    else:
        best_score = math.inf
        for child in node.children:
            score = minimax(child, depth - 1, True)
            if score < best_score:
                best_score = score
                node.best_move = child
        node.score = best_score
        return best_score

#%% Alpha-Beta

def alpha_beta(node, depth, alpha, beta, is_maximizing):
    """Alpha-Beta pruning algorithm implementation"""
    if depth == 0 or node.is_terminal():
        node.score = evaluate_state(node)
        return node.score
    
    if is_maximizing:
        best_score = -math.inf
        for child in node.children:
            score = alpha_beta(child, depth - 1, alpha, beta, False)
            if score > best_score:
                best_score = score
                node.best_move = child
            alpha = max(alpha, best_score)
            if beta <= alpha:
                break
        node.score = best_score
        return best_score
    else:
        best_score = math.inf
        for child in node.children:
            score = alpha_beta(child, depth - 1, alpha, beta, True)
            if score < best_score:
                best_score = score
                node.best_move = child
            beta = min(beta, best_score)
            if beta <= alpha:
                break
        node.score = best_score
        return best_score

#%% AI Decision Making

def ai_choose_move(current_number, player_score, ai_score, bank, use_alpha_beta=False, max_depth=4):
    """AI decision making function using either Minimax or Alpha-Beta"""
    # Create the root node for the current game state
    root = GameNode(current_number, player_score, ai_score, bank, False)  # False = AI's turn
    
    # Generate the game tree
    start_tree_time = time.time()
    generate_game_tree(root, 0, max_depth)
    tree_generation_time = time.time() - start_tree_time
    
    # Apply the selected algorithm
    start_algo_time = time.time()
    if use_alpha_beta:
        alpha_beta(root, max_depth, -math.inf, math.inf, True)
    else:
        minimax(root, max_depth, True)
    algo_time = time.time() - start_algo_time
    
    # Get the best move from the root node
    if root.best_move:
        return root.best_move, tree_generation_time + algo_time
    else:
        # Fallback si aucun meilleur mouvement n'est trouvé (ne devrait pas arriver en jeu normal)
        divisor = random.choice([2, 3, 4])
        new_number = round(current_number / divisor)
        child = GameNode(new_number, player_score, ai_score, bank, True)
        return child, 0.0

#%% Game GUI
class GameApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Number Division Game")
        self.root.geometry("500x600")
        
        # Game state variables
        self.player_score = 0
        self.ai_score = 0
        self.bank = 0
        self.current_number = 0
        self.player_turn = True
        self.use_alpha_beta = False
        self.numbers = []
        self.ai_last_move_time = 0
        self.first_player = "Player"  # Default first player
        self.game_over = False
        self.max_depth = 4  # Default search depth
        
        # Create menu bar
        self.create_menu_bar()
        
        # Main frame
        self.main_frame = tk.Frame(root, padx=20, pady=20)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Info frame for game stats
        self.info_frame = tk.Frame(self.main_frame)
        self.info_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Game control frame
        self.game_frame = tk.Frame(self.main_frame)
        self.game_frame.pack(fill=tk.BOTH, expand=True)
        
        # AI thinking time label
        self.ai_thinking_time_label = tk.Label(self.info_frame, text="AI Thinking Time: 0.00 seconds", font=("Arial", 12))
        self.ai_thinking_time_label.pack(pady=5, anchor=tk.W)
        
        # Algorithm label
        self.algorithm_label = tk.Label(self.info_frame, text="Algorithm: Minimax", font=("Arial", 12))
        self.algorithm_label.pack(pady=5, anchor=tk.W)
        
        # Status label
        self.status_label = tk.Label(self.info_frame, text="Game Status: Not Started", font=("Arial", 12))
        self.status_label.pack(pady=5, anchor=tk.W)
        
        # Start the game with the selection of the initial number
        self.setup_new_game()

    def create_menu_bar(self):
        """Create the application menu bar"""
        menu_bar = tk.Menu(self.root)
        self.root.config(menu=menu_bar)
        
        # Game menu
        game_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Game", menu=game_menu)
        game_menu.add_command(label="New Game", command=self.setup_new_game)
        game_menu.add_separator()
        game_menu.add_command(label="Exit", command=self.root.quit)
        
        # Settings menu
        settings_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Settings", menu=settings_menu)
        settings_menu.add_command(label="Choose Who Starts", command=self.choose_who_starts)
        settings_menu.add_command(label="Choose Algorithm", command=self.choose_algorithm)
        settings_menu.add_command(label="Set Search Depth", command=self.set_search_depth)

    def choose_who_starts(self):
        """Dialog for choosing who starts the game"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Choose First Player")
        dialog.geometry("300x150")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        
        tk.Label(dialog, text="Who should start the game?", font=("Arial", 12)).pack(pady=10)
        
        def set_first_player(choice):
            self.first_player = choice
            dialog.destroy()
            self.setup_new_game()
        
        button_frame = tk.Frame(dialog)
        button_frame.pack(pady=10)
        
        player_button = tk.Button(button_frame, text="Player", font=("Arial", 12), 
                                 width=10, command=lambda: set_first_player("Player"))
        player_button.pack(side=tk.LEFT, padx=10)
        
        ai_button = tk.Button(button_frame, text="AI", font=("Arial", 12),
                             width=10, command=lambda: set_first_player("AI"))
        ai_button.pack(side=tk.LEFT, padx=10)

    def choose_algorithm(self):
        """Dialog for choosing the AI algorithm"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Choose AI Algorithm")
        dialog.geometry("300x150")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        
        tk.Label(dialog, text="Choose the algorithm for AI:", font=("Arial", 12)).pack(pady=10)
        
        def set_algorithm(choice):
            self.use_alpha_beta = (choice == "Alpha-Beta")
            self.algorithm_label.config(text=f"Algorithm: {choice}")
            dialog.destroy()
        
        button_frame = tk.Frame(dialog)
        button_frame.pack(pady=10)
        
        minimax_button = tk.Button(button_frame, text="Minimax", font=("Arial", 12),
                                  width=10, command=lambda: set_algorithm("Minimax"))
        minimax_button.pack(side=tk.LEFT, padx=10)
        
        alpha_beta_button = tk.Button(button_frame, text="Alpha-Beta", font=("Arial", 12),
                                     width=10, command=lambda: set_algorithm("Alpha-Beta"))
        alpha_beta_button.pack(side=tk.LEFT, padx=10)

    def set_search_depth(self):
        """Dialog for setting the search depth"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Set Search Depth")
        dialog.geometry("300x150")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        
        tk.Label(dialog, text="Set AI search depth (2-6):", font=("Arial", 12)).pack(pady=10)
        
        depth_var = tk.IntVar(value=self.max_depth)
        depth_scale = tk.Scale(dialog, from_=2, to=6, orient=tk.HORIZONTAL, 
                              variable=depth_var, length=200, tickinterval=1)
        depth_scale.pack(pady=5)
        
        def set_depth():
            self.max_depth = depth_var.get()
            dialog.destroy()
        
        tk.Button(dialog, text="Apply", font=("Arial", 12), command=set_depth).pack(pady=10)

    def setup_new_game(self):
        """Set up a new game, clearing the previous game state"""
        # Reset game state
        self.player_score = 0
        self.ai_score = 0
        self.bank = 0
        self.game_over = False
        
        # Clear previous widgets
        for widget in self.game_frame.winfo_children():
            widget.destroy()
        
        # Update status
        self.status_label.config(text="Game Status: Selecting starting number")
        
        # Generate initial numbers
        self.numbers = generate_initial_numbers()
        self.select_initial_number()

    def select_initial_number(self):
        """Allow selection of the initial number to start the game"""
        # Framework for selecting the initial number
        selection_frame = tk.Frame(self.game_frame)
        selection_frame.pack(pady=20)
        
        tk.Label(selection_frame, text="Choose a number to start with:", font=("Arial", 14, "bold")).pack(pady=10)
        
        self.number_choice_var = tk.StringVar()
        
        # Create radio buttons for each number
        radio_frame = tk.Frame(selection_frame)
        radio_frame.pack(pady=10)
        
        for num in self.numbers:
            tk.Radiobutton(radio_frame, text=str(num), variable=self.number_choice_var, 
                          value=str(num), font=("Arial", 12)).pack(anchor=tk.W)
        
        # Start button
        start_button = tk.Button(selection_frame, text="Start Game", command=self.start_game, 
                               font=("Arial", 12), bg="#4CAF50", fg="white", padx=20, pady=5)
        start_button.pack(pady=20)

        # If AI starts, immediately choose a number and start
        if self.first_player == "AI":
            self.current_number = random.choice(self.numbers)
            self.player_turn = False
            self.start_game()

    def start_game(self):
        """Start the game after a number has been selected"""
        # If player selected number, get it from the choice variable
        if self.first_player == "Player":
            if not self.number_choice_var.get():
                tk.messagebox.showwarning("Warning", "Please select a number first!")
                return
            self.current_number = int(self.number_choice_var.get())
            self.player_turn = True
        # Si l'IA commence, on a déjà choisi un nombre aléatoire et défini player_turn à False
        
        # Clear the game frame
        for widget in self.game_frame.winfo_children():
            widget.destroy()
        
        # Update status
        self.status_label.config(text=f"Game Status: Active - {'Player' if self.player_turn else 'AI'}'s turn")
        
        # Update the game display and start the game loop
        self.update_game_display()

    def update_game_display(self):
        """Update the game display based on current state"""
        # Clear the game frame
        for widget in self.game_frame.winfo_children():
            widget.destroy()
            
        # Game info panel
        info_panel = tk.Frame(self.game_frame, bd=2, relief=tk.RIDGE, padx=15, pady=15)
        info_panel.pack(fill=tk.X, pady=10)
        
        # Current game state display
        game_info = [
            f"Current number: {self.current_number}",
            f"Player score: {self.player_score}",
            f"AI score: {self.ai_score}",
            f"Bank: {self.bank}"
        ]
        
        for info in game_info:
            tk.Label(info_panel, text=info, font=("Arial", 12), anchor=tk.W).pack(fill=tk.X, pady=2)
        
        # Game move panel
        move_panel = tk.Frame(self.game_frame, bd=2, relief=tk.RIDGE, padx=15, pady=15)
        move_panel.pack(fill=tk.X, pady=10, expand=True)
        
        # Check for game over
        if self.current_number <= 10:
            self.end_game()
            return
            
        # Handle turns
        if self.player_turn:
            self.handle_player_turn(move_panel)
        else:
            self.handle_ai_turn(move_panel)

    def handle_player_turn(self, parent_frame):
        """Handle the player's turn"""
        tk.Label(parent_frame, text="Player's Turn", font=("Arial", 14, "bold")).pack(pady=5)
        
        # Toujours offrir les trois diviseurs
        valid_divisors = [2, 3, 4]
        
        # Afficher des informations sur la division
        info_frame = tk.Frame(parent_frame)
        info_frame.pack(pady=5)
        
        for divisor in valid_divisors:
            result = self.current_number / divisor
            rounded = round(result)
            is_exact = self.current_number % divisor == 0
            
            info_text = f"Divide by {divisor}: {result:.2f} → {rounded}" + (" (exact)" if is_exact else " (rounded)")
            tk.Label(info_frame, text=info_text, font=("Arial", 11), anchor=tk.W).pack(anchor=tk.W, pady=2)
        
        # Make move selection
        move_frame = tk.Frame(parent_frame)
        move_frame.pack(pady=10)
        
        self.move_choice = tk.IntVar()
        
        for divisor in valid_divisors:
            tk.Radiobutton(move_frame, 
                          text=f"Divide by {divisor}",
                          variable=self.move_choice, 
                          value=divisor,
                          font=("Arial", 12)).pack(anchor=tk.W, pady=3)
        
        # Make move button
        tk.Button(parent_frame, 
                 text="Make Move", 
                 command=self.process_player_move,
                 font=("Arial", 12),
                 bg="#4CAF50", 
                 fg="white", 
                 padx=15, 
                 pady=5).pack(pady=10)

    def process_player_move(self):
        """Process the player's move"""
        if not hasattr(self, 'move_choice') or not self.move_choice.get():
            tk.messagebox.showwarning("Warning", "Please select a move first!")
            return
            
        divisor = self.move_choice.get()
        
        # Utiliser l'arrondi au lieu de la division entière
        self.current_number = round(self.current_number / divisor)
        
        # Apply game rules
        self.current_number, self.player_score, self.bank = process_turn(
            self.current_number, self.player_score, self.bank)
        
        # Switch to AI's turn
        self.player_turn = False
        
        # Update the display
        self.status_label.config(text="Game Status: Active - AI's turn")
        self.update_game_display()

    def handle_ai_turn(self, parent_frame):
        """Handle the AI's turn"""
        tk.Label(parent_frame, text="AI's Turn", font=("Arial", 14, "bold")).pack(pady=5)
        tk.Label(parent_frame, text="AI is thinking...", font=("Arial", 12)).pack(pady=5)
        
        # Update UI first then process AI move after a brief delay
        self.root.update()
        self.root.after(100, self.process_ai_move)

    def process_ai_move(self):
        """Process the AI's move using the selected algorithm"""
        # AI decision making
        result, thinking_time = ai_choose_move(
            self.current_number, 
            self.player_score,
            self.ai_score,
            self.bank,
            self.use_alpha_beta,
            self.max_depth
        )
        
        # Update the time display
        self.ai_thinking_time_label.config(text=f"AI Thinking Time: {thinking_time:.2f} seconds")
        
        if result:
            # Update game state
            self.current_number = result.number
            self.player_score = result.player_score
            self.ai_score = result.ai_score
            self.bank = result.bank
            
            # Switch to player's turn
            self.player_turn = True
            
            # Update status
            self.status_label.config(text="Game Status: Active - Player's turn")
            
            # Update the display
            self.update_game_display()
        else:
            # Error handling if no move found
            tk.messagebox.showerror("Error", "AI could not find a valid move!")
            self.end_game()

    def end_game(self):
        """Handle game over scenario"""
        for widget in self.game_frame.winfo_children():
            widget.destroy()

        if self.bank > 0:
            if self.player_turn == False :
                self.player_score += self.bank
            else:
                self.ai_score += self.bank
                
            self.bank = 0
            
        self.game_over = True
        
        # Create end game panel
        end_panel = tk.Frame(self.game_frame, bd=2, relief=tk.RIDGE, padx=20, pady=20)
        end_panel.pack(fill=tk.BOTH, expand=True, pady=20)
        
        # Show game over message
        tk.Label(end_panel, text="Game Over!", font=("Arial", 18, "bold")).pack(pady=10)
        
        # Display final scores
        scores_frame = tk.Frame(end_panel)
        scores_frame.pack(pady=10)
        
        
        
        tk.Label(scores_frame, text=f"Final Number: {self.current_number}", font=("Arial", 14)).pack(anchor=tk.W)
        tk.Label(scores_frame, text=f"Player Score: {self.player_score}", font=("Arial", 14)).pack(anchor=tk.W)
        tk.Label(scores_frame, text=f"AI Score: {self.ai_score}", font=("Arial", 14)).pack(anchor=tk.W)
        tk.Label(scores_frame, text=f"Bank: {self.bank}", font=("Arial", 14)).pack(anchor=tk.W)
        
        
        # Determine winner
        if self.player_score > self.ai_score:
            result_text = "Player Wins!"
            result_color = "#4CAF50"  # Green
        elif self.ai_score > self.player_score:
            result_text = "AI Wins!"
            result_color = "#F44336"  # Red
        else:
            result_text = "It's a Draw!"
            result_color = "#2196F3"  # Blue
            
        # Display winner
        tk.Label(end_panel, text=result_text, font=("Arial", 16, "bold"), fg=result_color).pack(pady=10)
        
        # Update status
        self.status_label.config(text=f"Game Status: Game Over - {result_text}")
        
        # New game button
        tk.Button(end_panel, 
                 text="New Game", 
                 command=self.setup_new_game,
                 font=("Arial", 14),
                 bg="#2196F3", 
                 fg="white",
                 padx=20,
                 pady=10).pack(pady=20)

#%% Run the game
if __name__ == "__main__":
    root = tk.Tk()
    app = GameApp(root)
    root.mainloop()
