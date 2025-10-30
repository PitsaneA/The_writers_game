import pygame, sys
pygame.init()
from game_state import game_state, load_progress, save_progress, reset_progress
from chapters import chapter1, chapter2, chapter3

WIDTH, HEIGHT = 900, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Echoes of the Unwritten Letter")

WHITE = (230, 230, 230)
GRAY = (40, 40, 40)
YELLOW = (255, 240, 150)

font = pygame.font.Font(None, 36)
big_font = pygame.font.Font(None, 64)

clock = pygame.time.Clock()

background = pygame.image.load("background.jpg").convert()
background = pygame.transform.scale(background, (WIDTH, HEIGHT))

game_running = True
paused = False
in_menu = True


def draw_text_center(text, font, color, surface, y):
    text_surface = font.render(text, True, color)
    rect = text_surface.get_rect(center=(WIDTH // 2, y))
    surface.blit(text_surface, rect)


def main_menu():
    selected = 0
    options = ["Continue", "New Game", "Quit"]

    while True:
        screen.blit(background, (0, 0))
        draw_text_center("Echoes of the Unwritten Letter", big_font, WHITE, screen, 180)
        for i, option in enumerate(options):
            color = YELLOW if i == selected else WHITE
            draw_text_center(option, font, color, screen, 300 + i * 60)

        prog = game_state["progress"]
        progress_text = f"Progress: Chapter1 {'✓' if prog['chapter1'] else '✗'} | Chapter2 {'✓' if prog['chapter2'] else '✗'} | Chapter3 {'✓' if prog['chapter3'] else '✗'}"
        draw_text_center(progress_text, font, WHITE, screen, 500)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected = (selected - 1) % len(options)
                elif event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(options)
                elif event.key == pygame.K_RETURN:
                    if options[selected] == "Continue":
                        return "continue"
                    elif options[selected] == "New Game":
                        reset_progress()
                        return "new"
                    elif options[selected] == "Quit":
                        pygame.quit(); sys.exit()

        clock.tick(60)


def pause_menu():
    selected = 0
    options = ["Resume", "Main Menu", "Quit"]

    while True:
        screen.blit(background, (0, 0))
        draw_text_center("Paused", big_font, WHITE, screen, 200)
        for i, option in enumerate(options):
            color = YELLOW if i == selected else WHITE
            draw_text_center(option, font, color, screen, 320 + i * 60)

        prog = game_state["progress"]
        progress_text = f"Progress: Ch1 {'✓' if prog['chapter1'] else '✗'} | Ch2 {'✓' if prog['chapter2'] else '✗'} | Ch3 {'✓' if prog['chapter3'] else '✗'}"
        draw_text_center(progress_text, font, WHITE, screen, 520)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected = (selected - 1) % len(options)
                elif event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(options)
                elif event.key == pygame.K_RETURN:
                    if options[selected] == "Resume":
                        return "resume"
                    elif options[selected] == "Main Menu":
                        return "menu"
                    elif options[selected] == "Quit":
                        pygame.quit(); sys.exit()

        clock.tick(60)


load_progress()
choice = main_menu()

if choice == "continue" or choice == "new":
    current = game_state["current_chapter"]

while True:
    current = game_state["current_chapter"]

    if current == 1:
        chapter1.run(screen)
    elif current == 2:
        chapter2.run(screen)
    elif current == 3:
        chapter3.run(screen)
    else:
        break  

    if not game_state["progress"].get(f"chapter{current}", False):
        break
