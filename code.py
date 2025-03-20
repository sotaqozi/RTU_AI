#%% Library import
import random

#%% Side functions

# Function that generates the first number
def generate_initial_numbers():
    numbers = []
    while len(numbers) < 5:
        num = random.randint(20000, 30000)
        if num % 2 == 0 and num % 3 == 0 and num % 4 == 0:
            numbers.append(num)
    return numbers

# Function that follows the game's rules
def process_turn(new_number, player_score, bank):
    if new_number % 2 == 0:
        player_score -= 1
    else:
        player_score += 1
    if new_number % 10 == 0 or new_number % 10 == 5:
        bank += 1
        
    return new_number, player_score, bank

#%%
# Principal function to run the game
def play():
    numbers = generate_initial_numbers()
    print(f"You can choose one number between {numbers}")
    chosen_number = int(input("What's your choice ?"))
    while chosen_number not in numbers:
        print("Invalid choice! Please choose one of the generated numbers.")
        chosen_number = int(input("What's your choice ?"))
    
    # Initial values
    player_1_score = 0
    player_2_score = 0
    bank = 0
    current_number = chosen_number
    player_turn = 1  
    
    while current_number > 10:
        print(f"Current number: {current_number}")
        # The divisors 2, 3, and 4 are available for both players
        dividers = [2, 3, 4]
        
        if player_turn == 1:
            print(f"Player 1's turn. Current score: {player_1_score}")
            chosen_divider = int(input("With which number do you want to divide? (Choose 2, 3, or 4) "))
            while chosen_divider not in dividers:
                print("Invalid choice! Please choose one of 2, 3, or 4.")
                chosen_divider = int(input("With which number do you want to divide? (Choose 2, 3, or 4) "))
            
                
            current_number = round(current_number / chosen_divider)
            current_number, player_1_score, bank = process_turn(current_number, player_1_score, bank)
            player_turn = 2  # Switch turn to Player 2
        
        else:
            print(f"Player 2's turn. Current score: {player_2_score}")
            chosen_divider = int(input("With which number do you want to divide? (Choose 2, 3, or 4) "))
            while chosen_divider not in dividers:
                print("Invalid choice! Please choose one of 2, 3, or 4.")
                chosen_divider = int(input("With which number do you want to divide? (Choose 2, 3, or 4) "))
                
            current_number = round(current_number / chosen_divider)
            current_number, player_2_score, bank = process_turn(current_number, player_2_score, bank)
            player_turn = 1  # Switch turn to Player 1
    
    # End of the game: Add the bank points to the player who ended the game
    if player_turn == 1:  # Player 1's turn ended the game
        player_1_score += bank
    else:  # Player 2's turn ended the game
        player_2_score += bank
    
    # Determine the winner
    print(f"Game over! Player 1 score: {player_1_score}, Player 2 score: {player_2_score}")
    
    if player_1_score > player_2_score:
        print("Player 1 wins!")
    elif player_2_score > player_1_score:
        print("Player 2 wins!")
    else:
        print("It's a draw!")

#%% Run the game
play()

       


       
       
       
       
       
       
       
       
       
       
       
       
       
       
       
       
       
       
