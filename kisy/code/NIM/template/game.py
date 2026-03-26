import pygame
import sys
import time
import warnings
import os

# Initialize Pygame
pygame.init()
try:
    # In some environments pygame's font module can be broken due to an internal
    # circular import. We treat fonts as optional so the game can still run.
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        pygame.font.init()
    FONT = pygame.font.Font(None, 36)
except Exception:
    FONT = None

# Constants
WIDTH, HEIGHT = 700, 500
FPS = 30
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
LIGHT_GREY = (200, 200, 200)
DARK_GREY = (50, 50, 50)

# Create screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Nim Game')

# Define piles (number of coins in each pile)
piles = [4, 4, 4, 4]  # 4 piles with 4 coins each
selected_stones = []  # To store selected stones for removal
selected_pile = None  # Tracks the pile from which coins are selected

# Players
player_turn = 1  # Player 1 starts (alternates between 1 and 2)

# Game State
game_over = False
winner = None

def draw_piles():
    """Draws the piles of coins as circles with padding."""
    x_pos = 130  # Start from left with padding
    y_start = 250
    padding = 150  # Increased space between piles for better symmetry
    radius = 20
    for idx, pile in enumerate(piles):
        y_pos = y_start
        for stone in range(pile):
            color = RED
            if (idx, stone) in selected_stones:
                color = GREEN  # Show selected stones as green
            pygame.draw.circle(screen, color, (x_pos, y_pos), radius)
            y_pos -= 2 * radius + 10  # Space between circles
        if FONT is not None:
            text = FONT.render(f'Pile {idx + 1}', True, BLACK)
            screen.blit(text, (x_pos - 30, 320))
        x_pos += padding  # Increase x position and add padding

def check_game_over():
    """Check if the game is over (all piles empty)."""
    global winner, game_over
    if all(pile == 0 for pile in piles):
        winner = 2 if player_turn == 1 else 1  # The other player wins
        game_over = True

def draw_game_state():
    """Draws the current game state including piles and turn."""
    screen.fill(LIGHT_GREY)  # Background color
    draw_piles()

    if game_over:
        if player_turn == 1:
            if FONT is not None:
                text = FONT.render(f'You win, hooray!', True, GREEN)
                screen.blit(text, (WIDTH // 2 - text.get_width() // 2, 30))  # Adjusted y-position for spacing
        else:
            if FONT is not None:
                text = FONT.render(f'AI wins!', True, GREEN)
                screen.blit(text, (WIDTH // 2 - text.get_width() // 2, 30))  # Adjusted y-position for spacing
       
        # Draw the Restart button
        pygame.draw.rect(screen, DARK_GREY, (WIDTH // 2 - 60, HEIGHT - 60, 120, 40))
        if FONT is not None:
            restart_text = FONT.render("Restart", True, WHITE)
            screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT - 50))
    else:
        if player_turn == 1:
            if FONT is not None:
                text = FONT.render(f'Your turn!', True, BLACK)
                screen.blit(text, (WIDTH // 2 - text.get_width() // 2, 30))  # Centered player label
        else:
            if FONT is not None:
                text = FONT.render(f'Computer thinking... ', True, BLACK)
                screen.blit(text, (WIDTH // 2 - text.get_width() // 2, 30))  # Centered player labe


    # Draw the "Remove" button at the bottom
    pygame.draw.rect(screen, BLACK, (WIDTH // 2 - 60, HEIGHT - 120, 120, 40))
    if FONT is not None:
        remove_text = FONT.render("Remove", True, WHITE)
        screen.blit(remove_text, (WIDTH // 2 - remove_text.get_width() // 2, HEIGHT - 110))

def remove_stones():
    """Removes the selected stones from the selected pile."""
    global player_turn, selected_pile
    for pile_index, stone_index in selected_stones:
        piles[pile_index] -= 1
    selected_stones.clear()
    selected_pile = None  # Reset selected pile after removal
    player_turn = 2 if player_turn == 1 else 1  # Switch turns
    check_game_over()

def handle_selection(pile_index, stone_index):
    """Handles selecting or deselecting stones, ensuring only one pile can be selected."""
    global selected_pile
    if selected_pile is None or selected_pile == pile_index:
        selected_pile = pile_index  # Lock the selection to the current pile
        if (pile_index, stone_index) in selected_stones:
            selected_stones.remove((pile_index, stone_index))  # Deselect
        else:
            selected_stones.append((pile_index, stone_index))  # Select

def restart_game():
    """Restarts the game."""
    global piles, player_turn, selected_stones, selected_pile, game_over, winner
    piles = [4, 4, 4, 4]  # Reset piles
    selected_stones.clear()
    selected_pile = None
    player_turn = 1
    game_over = False
    winner = None

def start_game(ai):
    """Starts the game and integrates AI for playing against the computer."""
    global player_turn, game_over

    # Main game loop
    clock = pygame.time.Clock()
    while True:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and not game_over and player_turn == 1:
                mouse_x, mouse_y = event.pos
                # Check for pile selection (clicking on a coin)
                x_pos = 130
                y_start = 250
                padding = 150
                radius = 20
                for pile_index, pile in enumerate(piles):
                    y_pos = y_start
                    for stone_index in range(pile):
                        dist = ((mouse_x - x_pos)**2 + (mouse_y - y_pos)**2)**0.5
                        if dist <= radius:
                            handle_selection(pile_index, stone_index)
                        y_pos -= 2 * radius + 10
                    x_pos += padding
                # Check for "Remove" button click
                if WIDTH // 2 - 60 <= mouse_x <= WIDTH // 2 + 60 and HEIGHT - 120 <= mouse_y <= HEIGHT - 80:
                    remove_stones()

            # If game over, check for "Restart" button click
            elif event.type == pygame.MOUSEBUTTONDOWN and game_over:
                mouse_x, mouse_y = event.pos
                if WIDTH // 2 - 60 <= mouse_x <= WIDTH // 2 + 60 and HEIGHT - 60 <= mouse_y <= HEIGHT - 20:
                    restart_game()

        # If it's the AI's turn and the game is not over
        if player_turn == 2 and not game_over:
            draw_game_state()
            pygame.display.flip()
            # Simulate thinking
            time.sleep(2)
            # AI makes its move
            action = ai.choose_action(piles, epsilon=False)
            remove_stones_from_ai(action)

        draw_game_state()
        pygame.display.flip()

def remove_stones_from_ai(action):
    """Handles AI stone removal."""
    pile, count = action
    for i in range(count):
        piles[pile] -= 1
    global player_turn
    player_turn = 1  # Switch back to human player
    check_game_over()


if __name__ == "__main__":
    # Allow controlling training duration from the outside (so `python game.py`
    # is usable without waiting forever).
    # Example: `NIM_TRAIN_GAMES=0 python game.py` to skip training.
    train_games = int(os.getenv("NIM_TRAIN_GAMES", "1000"))

    from nim import train, NimAI

    ai = train(train_games) if train_games > 0 else NimAI()
    start_game(ai)
