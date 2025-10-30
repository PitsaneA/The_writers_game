import pygame, random, time
from game_state import game_state, save_progress

WIDTH, HEIGHT = 900, 600
WHITE = (230, 230, 230)
YELLOW = (255, 255, 150)
BROWN = (150, 100, 60)

font = pygame.font.Font(None, 32)
big_font = pygame.font.Font(None, 48)

positive_words = [
    "hope", "love", "forgiveness", "a warm light",
    "my morning star", "harmony", "truth", "a new day"
]
negative_words = [
    "alone", "mistake", "guilt", "darkness", "silence",
    "fear", "cold night", "the end"
]

def show_instruction(screen, text):
    instr_font = pygame.font.Font(None, 36)
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.fill((0, 0, 0))
    overlay.set_alpha(200)
    screen.blit(overlay, (0, 0))
    label = instr_font.render(text, True, YELLOW)
    screen.blit(label, label.get_rect(center=(WIDTH // 2, HEIGHT // 2)))
    pygame.display.flip()
    pygame.time.wait(1800)


def run(screen):
    pygame.display.set_caption("The Writer's Game - Chapter I")

    show_instruction(screen, "Read the word")

    player = pygame.Rect(100, HEIGHT - 150, 50, 80)
    lamp = pygame.Rect(150, HEIGHT - 200, 50, 100)
    typewriter = pygame.Rect(700, HEIGHT - 120, 100, 60)

    clock = pygame.time.Clock()
    player_speed = 5

    light_on = False
    overlay_mode = False
    current_testament = None
    found_first = False
    chapter_done = False
    show_typewriter_hint = False
    used_words = set()

    def get_unique_word(pool):
        choices = [w for w in pool if w not in used_words]
        if not choices:
            choices = pool
        word = random.choice(choices)
        used_words.add(word)
        return word

    def gen_testament(word, positive, existing):
        while True:
            rect = pygame.Rect(
                random.randint(100, WIDTH - 160),
                random.randint(180, HEIGHT - 150),
                120, 50
            )
            if not any(rect.colliderect(o["rect"]) for o in existing) and \
               not rect.colliderect(lamp) and \
               not rect.colliderect(typewriter):
                return {"rect": rect, "text": word, "positive": positive, "collected": False}

    testaments = [gen_testament(get_unique_word(positive_words + negative_words),
                                random.random() > 0.5, [])]

    background = pygame.image.load("background.jpg").convert()
    background = pygame.transform.scale(background, (WIDTH, HEIGHT))

    running = True
    cooldown = 0

    while running:
        dt = clock.tick(60)
        cooldown = max(0, cooldown - dt)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if overlay_mode and event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                overlay_mode = False
                if current_testament:
                    current_testament["collected"] = True
                    current_testament = None
                    if not found_first:
                        for _ in range(3):
                            testaments.append(gen_testament(get_unique_word(positive_words), True, testaments))
                            testaments.append(gen_testament(get_unique_word(negative_words), False, testaments))
                        found_first = True

        keys = pygame.key.get_pressed()

        if not overlay_mode:
            if keys[pygame.K_a]:
                player.x -= player_speed
            if keys[pygame.K_d]:
                player.x += player_speed
            if keys[pygame.K_w]:
                player.y -= player_speed
            if keys[pygame.K_s]:
                player.y += player_speed
        player.clamp_ip(pygame.Rect(0, 0, WIDTH, HEIGHT))

        screen.blit(background, (0, 0))
        if not light_on:
            dark = pygame.Surface((WIDTH, HEIGHT))
            dark.fill((0, 0, 0))
            dark.set_alpha(150)
            screen.blit(dark, (0, 0))

        pygame.draw.rect(screen, (160, 110, 70), player)
        pygame.draw.rect(screen, YELLOW, lamp)
        pygame.draw.rect(screen, (200, 200, 200), typewriter)

        interaction_text = ""

        if not overlay_mode and player.colliderect(lamp):
            interaction_text = "Press E to toggle lamp"
            if keys[pygame.K_e] and cooldown == 0:
                light_on = not light_on
                cooldown = 300

        for t in testaments:
            if t["collected"]:
                continue
            visible = (light_on and t["positive"]) or (not light_on and not t["positive"]) or not found_first
            if visible:
                pygame.draw.rect(screen, BROWN, t["rect"], border_radius=6)
                lbl = font.render("Testament", True, WHITE)
                screen.blit(lbl, lbl.get_rect(center=t["rect"].center))

                if not overlay_mode and player.colliderect(t["rect"]):
                    interaction_text = "Press E to read"
                    if keys[pygame.K_e] and cooldown == 0:
                        cooldown = 300
                        overlay_mode = True
                        current_testament = t

        if found_first and all(t["collected"] for t in testaments) and not show_typewriter_hint:
            show_center_text(screen, ["Go to the typewriter"], 2.5)
            show_typewriter_hint = True

        if show_typewriter_hint and player.colliderect(typewriter) and not chapter_done:
            interaction_text = "Press E to finish Chapter I"
            if keys[pygame.K_e] and cooldown == 0:
                cooldown = 300
                show_center_text(screen, ["Chapter Complete"], 2.5)
                chapter_done = True

        if chapter_done and player.colliderect(typewriter):
            interaction_text = "Press E to continue"
            if keys[pygame.K_e] and cooldown == 0:
                show_center_text(screen, ["Chapter II - Autumn Thougts"], 2.5)
                game_state["progress"]["chapter1"] = True
                game_state["current_chapter"] = 2
                save_progress()
                running = False

        if overlay_mode and current_testament:
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.fill((0, 0, 0))
            overlay.set_alpha(220)
            screen.blit(overlay, (0, 0))

            wrapped = wrap_text(f"\"{current_testament['text']}\"", font, WIDTH - 200)
            draw_text_block(wrapped, font, WHITE, screen, HEIGHT // 2 - 60)
            hint = font.render("Press ENTER to close", True, YELLOW)
            screen.blit(hint, hint.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 70)))

        if interaction_text:
            txt = font.render(interaction_text, True, WHITE)
            screen.blit(txt, (50, 50))

        pygame.display.flip()


def show_center_text(screen, lines, seconds=2.0):
    clock = pygame.time.Clock()
    start = time.time()
    while time.time() - start < seconds:
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(200)
        screen.blit(overlay, (0, 0))
        for i, line in enumerate(lines):
            txt = big_font.render(line, True, WHITE)
            rect = txt.get_rect(center=(WIDTH // 2, HEIGHT // 2 + i * 50))
            screen.blit(txt, rect)
        pygame.display.flip()
        clock.tick(60)


def wrap_text(text, font, width):
    words = text.split(' ')
    lines, current = [], ""
    for w in words:
        if font.size(current + w)[0] < width:
            current += w + " "
        else:
            lines.append(current)
            current = w + " "
    if current:
        lines.append(current)
    return lines


def draw_text_block(lines, font, color, surface, y):
    for i, line in enumerate(lines):
        txt = font.render(line, True, color)
        rect = txt.get_rect(center=(WIDTH // 2, y + i * 30))
        surface.blit(txt, rect)
