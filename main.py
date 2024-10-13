import pygame
import random
import sys
import speech_recognition as sr  # For speech-to-text functionality
from nlp_utils import normalize_command, COLOR_KEYWORDS  # Import the updated NLP function and color map

# Initialize pygame
pygame.init()

# Set up the display
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
GROUND_HEIGHT = 100
PLAYER_SIZE = 50
COIN_SIZE = 50

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Kid-Friendly Game")

# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
PINK = (255, 182, 193)
GRAY = (200, 200, 200)
CLICK_COLOR = (0, 200, 0)  # Green effect when clicked
NORMAL_COLOR = (0, 0, 0)  # Default black
COLORS = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0)]
current_color = BLACK


# Load images
def load_and_scale_images():
    sky_image = pygame.image.load('Sky.png')
    ground_image = pygame.image.load('ground.png')
    coin_image = pygame.image.load('coin.png')
    microphone_image = pygame.image.load('microphone.png')  # Load microphone icon

    sky_image = pygame.transform.scale(sky_image, (SCREEN_WIDTH, SCREEN_HEIGHT - GROUND_HEIGHT))
    ground_image = pygame.transform.scale(ground_image, (SCREEN_WIDTH, GROUND_HEIGHT))
    coin_image = pygame.transform.scale(coin_image, (COIN_SIZE, COIN_SIZE))
    microphone_image = pygame.transform.scale(microphone_image, (50, 50))  # Scale the microphone icon

    return sky_image, ground_image, coin_image, microphone_image


sky_image, ground_image, coin_image, microphone_image = load_and_scale_images()

# Define player and coin properties
player_x = SCREEN_WIDTH // 2 - PLAYER_SIZE // 2
player_y = SCREEN_HEIGHT - GROUND_HEIGHT - PLAYER_SIZE
player_speed = 50
player_jump_power = -20
player_gravity = 1.5
player_dy = 0
player_grounded = True

coin_x = random.randint(0, SCREEN_WIDTH - COIN_SIZE)
coin_y = SCREEN_HEIGHT - GROUND_HEIGHT - COIN_SIZE
coin_collected = False

# Set up fonts
font_large = pygame.font.SysFont(None, 48)
font_medium = pygame.font.SysFont(None, 36)
font_small = pygame.font.SysFont(None, 28)


# Draw microphone icon with click effect
def draw_microphone_icon(is_clicked):
    """
    Draws the microphone icon. If is_clicked is True, it will display the icon with a highlight effect
    to simulate a 'click' action by changing the background color.
    """
    microphone_rect = pygame.Rect(730, 30, 50, 50)

    if is_clicked:
        pygame.draw.rect(screen, CLICK_COLOR, microphone_rect)  # Draw green background when clicked
    else:
        pygame.draw.rect(screen, NORMAL_COLOR, microphone_rect)  # Normal background

    screen.blit(microphone_image, (730, 30))  # Draw the microphone image on top


# Draw sky and ground
def draw_environment():
    screen.blit(sky_image, (0, 0))
    screen.blit(ground_image, (0, SCREEN_HEIGHT - GROUND_HEIGHT))


# Draw player
def draw_player():
    pygame.draw.rect(screen, current_color, (player_x, player_y, PLAYER_SIZE, PLAYER_SIZE))


# Draw coin
def draw_coin():
    screen.blit(coin_image, (coin_x, coin_y))


# Handle input commands
def handle_input(command):
    global score, player_x, player_dy, player_grounded, current_color, coin_collected, coin_x, coin_y

    command = normalize_command(command)  # Normalize command using NLP with typo correction

    if command == "error: unrecognized command":
        return False  # Indicate that the command was not valid

    if "move left" in command:
        player_x = max(0, player_x - player_speed)
    elif "move right" in command:
        player_x = min(SCREEN_WIDTH - PLAYER_SIZE, player_x + player_speed)
    elif "jump" in command and player_grounded:
        player_dy = player_jump_power
        player_grounded = False
    elif command.startswith("change color"):
        # Extract color from the command or randomly change the color
        color_name = command.split()[-1]
        if color_name == "random":
            current_color = random.choice(list(COLOR_KEYWORDS.values()))
        elif color_name in COLOR_KEYWORDS:
            current_color = COLOR_KEYWORDS[color_name]
        else:
            return False  # Invalid color

    if player_collides_with_coin():
        coin_collected = True
        score += 1
        relocate_coin()


    return True  # Indicate that the command was successfully processed


# Speech-to-text recognition
def speech_to_text():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        try:
            print("Listening...")
            audio = r.listen(source, timeout=3)

            # First, try to recognize as Danish
            try:
                command = r.recognize_google(audio, language="da-DK")
                print(command, "danish")
                return command.lower()
            except sr.UnknownValueError:
                # If Danish fails, try English
                try:
                    command = r.recognize_google(audio, language="en-US")
                    print(command, "engl")
                    return command.lower()
                except sr.UnknownValueError:
                    return "error: could not understand", None
        except sr.RequestError:
            return "error: speech recognition service unavailable", None

# Check collision with coin
def player_collides_with_coin():
    return (player_x < coin_x + COIN_SIZE and
            player_x + PLAYER_SIZE > coin_x and
            player_y < coin_y + COIN_SIZE and
            player_y + PLAYER_SIZE > coin_y)


# Relocate coin
def relocate_coin():
    global coin_x, coin_y
    coin_placed = False
    while not coin_placed:
        coin_x = random.randint(0, SCREEN_WIDTH - COIN_SIZE)
        coin_y = SCREEN_HEIGHT - GROUND_HEIGHT - COIN_SIZE

        if not (coin_x < player_x + PLAYER_SIZE and
                coin_x + COIN_SIZE > player_x and
                coin_y < player_y + PLAYER_SIZE and
                coin_y + COIN_SIZE > player_y):
            coin_placed = True


# Draw input box and handle text
def draw_input_box(input_text, input_active, cursor_visible, error_message):
    input_box = pygame.Rect(10, 30, 700, 60)
    pygame.draw.rect(screen, PINK, input_box)

    # Placeholder or input text
    if input_text == "" and not input_active:
        placeholder_surface = font_large.render("Enter command here", True, BLUE)
        screen.blit(placeholder_surface, (input_box.x + 10, input_box.y + 10))
    else:
        input_surface = font_large.render(input_text, True, BLACK)
        screen.blit(input_surface, (input_box.x + 10, input_box.y + 10))
        if input_active and cursor_visible:
            cursor_surface = font_large.render("|", True, BLUE)
            screen.blit(cursor_surface, (input_box.x + 10 + input_surface.get_width() + 2, input_box.y + 10))

    # Calculate the x-coordinate to center the button
    enter_button_width = 200
    enter_button_height = 50
    enter_button_x = (SCREEN_WIDTH - enter_button_width) // 2  # Centered horizontally
    enter_button_y = 100  # Below the pink box

    # Draw the Enter button
    enter_button = pygame.Rect(enter_button_x, enter_button_y, enter_button_width, enter_button_height)
    pygame.draw.rect(screen, (0, 255, 0), enter_button)  # Green color for the button
    enter_button_text = font_large.render("Enter", True, BLACK)
    screen.blit(enter_button_text, (enter_button_x + 50, enter_button_y + 5))

    if error_message:
        error_surface = font_medium.render(error_message, True, (255, 0, 0))
        screen.blit(error_surface, (10, 160))

    return enter_button

# Main game loop
def main():
    global player_y, player_dy, player_grounded, coin_collected, score
    score = 0

    clock = pygame.time.Clock()
    input_text = ""

    cursor_visible = True
    cursor_timer = 0
    cursor_blink_rate = 500
    input_active = False
    error_message = ""  # To hold any error message
    instructions = "Commands: move left, jump, move right, change color"
    microphone_clicked = False

    while True:
        screen.fill(WHITE)

        if not player_grounded:
            player_y += player_dy
            player_dy += player_gravity
            if player_y >= SCREEN_HEIGHT - GROUND_HEIGHT - PLAYER_SIZE:
                player_y = SCREEN_HEIGHT - GROUND_HEIGHT - PLAYER_SIZE
                player_dy = 0
                player_grounded = True

        draw_environment()
        draw_player()
        draw_coin()

        # Draw microphone icon with color change effect when clicked
        draw_microphone_icon(microphone_clicked)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Check if the microphone icon is clicked
                if pygame.Rect(730, 30, 50, 50).collidepoint(event.pos):
                    microphone_clicked = True
                    recognized_speech = speech_to_text()  # Get the recognized speech text
                    if recognized_speech == "error: could not understand":
                        error_message = "Could not understand speech. Please try again."
                    elif recognized_speech == "error: speech recognition service unavailable":
                        error_message = "Speech recognition service unavailable."
                    else:
                        input_text = recognized_speech  # Paste the recognized speech into the input field
                        error_message = ""
                input_active = pygame.Rect(10, 30, 700, 60).collidepoint(event.pos)

                # Check if the Enter button is clicked
                enter_button = draw_input_box(input_text, input_active, cursor_visible, error_message)
                if enter_button.collidepoint(event.pos):
                    success = handle_input(input_text)  # Process the input when the button is clicked
                    if not success:
                        error_message = "Unrecognized command or invalid color. Please try again."
                    else:
                        error_message = ""
                    input_text = ""

            elif event.type == pygame.MOUSEBUTTONUP:
                # Reset the microphone button appearance after click
                microphone_clicked = False
            elif event.type == pygame.KEYDOWN and input_active:
                if event.key == pygame.K_RETURN:
                    success = handle_input(input_text)  # Process the input when Enter is pressed
                    if not success:
                        error_message = "Unrecognized command or invalid color. Please try again."
                    else:
                        error_message = ""
                    input_text = ""
                elif event.key == pygame.K_BACKSPACE:
                    input_text = input_text[:-1]
                else:
                    input_text += event.unicode

        cursor_timer += clock.get_time()
        if cursor_timer >= cursor_blink_rate:
            cursor_visible = not cursor_visible
            cursor_timer = 0

        # Call draw_input_box to render the text and the Enter button
        enter_button = draw_input_box(input_text, input_active, cursor_visible, error_message)

        score_surface = font_medium.render(f"Score: {score}", True, BLACK)
        screen.blit(score_surface, (10, 140))

        instructions_surface = font_small.render(instructions, True, BLACK)
        screen.blit(instructions_surface, (10, 180))

        pygame.display.update()
        clock.tick(30)


if __name__ == "__main__":
    main()
