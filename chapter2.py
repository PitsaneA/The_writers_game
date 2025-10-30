import sys
import pygame, random, time
from game_state import game_state, save_progress

WIDTH, HEIGHT = 900, 600
WHITE = (230, 230, 230)
YELLOW = (255, 255, 150)
BROWN = (150, 100, 60)

pygame.font.init()
font = pygame.font.Font(None, 32)
big_font = pygame.font.Font(None, 48)

positive_words = [
    "everything I want", "hope", "another chance", "God",
    "your eyes", "your smile", "gentler fire", "my morning star"
]
negative_words = [
    "move on", "alone", "mistakes", "cruel world", "not in our story",
    "we don't talk", "kills me", "fool", "message", "I've changed so much"
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
    pygame.display.set_caption("Autumn Thoughts")

    show_instruction(screen, "Type the word")

    player = pygame.Rect(100, HEIGHT - 150, 50, 80)
    lamp = pygame.Rect(150, HEIGHT - 200, 50, 100)
    typewriter = pygame.Rect(700, HEIGHT - 120, 100, 60)
    clock = pygame.time.Clock()
    player_speed = 5

    light_on = False
    first_spawned = True
    first_collected = False
    first_written = False
    can_write = False
    typing_mode = False
    current_testament = None
    last_read_word = ""
    typed_word = ""
    waiting_to_continue = False
    chapter_done = False

    used_words = set()

    def get_unique(pool):
        choices = [w for w in pool if w not in used_words]
        if not choices:
            choices = pool[:]
        w = random.choice(choices)
        used_words.add(w)
        return w

    def gen_testament(text, positive, existing):
        tries = 0
        while True:
            tries += 1
            rect = pygame.Rect(random.randint(80, WIDTH - 160), random.randint(180, HEIGHT - 160), 140, 48)
            collide = False
            for o in existing:
                if rect.colliderect(o["rect"].inflate(8, 8)):
                    collide = True
                    break
            if rect.colliderect(lamp) or rect.colliderect(typewriter):
                collide = True
            if not collide or tries > 400:
                return {"rect": rect, "text": text, "positive": positive, "collected": False, "written": False}

    first_text = get_unique(positive_words + negative_words)
    first_positive = random.random() > 0.5
    testaments = [gen_testament(first_text, first_positive, [])]

    try:
        background = pygame.image.load("background.jpg").convert()
        background = pygame.transform.scale(background, (WIDTH, HEIGHT))
    except Exception:
        background = pygame.Surface((WIDTH, HEIGHT))
        background.fill((20, 20, 20))

    running = True
    while running:
        dt = clock.tick(60)
        events = pygame.event.get()
        for ev in events:
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            if typing_mode and ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    typing_mode = False
                    typed_word = ""
                elif ev.key == pygame.K_RETURN:
                    if typed_word.strip().lower() == last_read_word.strip().lower():
                        for t in testaments:
                            if t["text"] == last_read_word:
                                t["written"] = True
                        typed_word = ""
                        typing_mode = False
                        first_written = True if first_collected and not first_written else first_written
                        if first_collected and first_written and len(testaments) == 1:
                            pos_sel, neg_sel = [], []
                            for _ in range(3):
                                if len([x for x in positive_words if x not in used_words]) > 0:
                                    pos_sel.append(get_unique(positive_words))
                            for _ in range(3):
                                if len([x for x in negative_words if x not in used_words]) > 0:
                                    neg_sel.append(get_unique(negative_words))
                            for w in pos_sel:
                                testaments.append(gen_testament(w, True, testaments))
                            for w in neg_sel:
                                testaments.append(gen_testament(w, False, testaments))
                        can_write = False
                    else:
                        typed_word = ""
                elif ev.key == pygame.K_BACKSPACE:
                    typed_word = typed_word[:-1]
                else:
                    if ev.unicode:
                        typed_word += ev.unicode

        keys = pygame.key.get_pressed()

        can_move = (current_testament is None) and (not typing_mode)
        if can_move:
            if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                player.x -= player_speed
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                player.x += player_speed
            if keys[pygame.K_w] or keys[pygame.K_UP]:
                player.y -= player_speed
            if keys[pygame.K_s] or keys[pygame.K_DOWN]:
                player.y += player_speed
        player.clamp_ip(pygame.Rect(0, 0, WIDTH, HEIGHT))

        screen.blit(background, (0, 0))
        if not light_on:
            dark = pygame.Surface((WIDTH, HEIGHT))
            dark.fill((0,0,0))
            dark.set_alpha(150)
            screen.blit(dark,(0,0))

        pygame.draw.rect(screen, (160,110,70), player)
        pygame.draw.rect(screen, YELLOW, lamp)
        pygame.draw.rect(screen, (200,200,200), typewriter)

        interaction_text = ""

        if current_testament is None and not typing_mode and player.colliderect(lamp):
            interaction_text = "Press E to toggle lamp"
            for ev in events:
                if ev.type == pygame.KEYDOWN and ev.key == pygame.K_e:
                    light_on = not light_on

        if last_read_word and (current_testament is None) and not typing_mode:
            r_hint = font.render("Press R to reread last fragment", True, WHITE)
            screen.blit(r_hint, (WIDTH - 360, 36))
            if keys[pygame.K_r]:
                show_overlay(screen, last_read_word)

        for t in testaments:
            if t["collected"]:
                continue
            visible = (light_on and t["positive"]) or (not light_on and not t["positive"]) or (not first_spawned)
            if visible:
                pygame.draw.rect(screen, BROWN, t["rect"], border_radius=6)
                label = font.render("Testament", True, WHITE)
                screen.blit(label, label.get_rect(center=t["rect"].center))
                unfinished = any(tt["collected"] and not tt["written"] for tt in testaments)
                if current_testament is None and not typing_mode and not unfinished and player.colliderect(t["rect"]):
                    interaction_text = "Press E to read"
                    if keys[pygame.K_e]:
                        current_testament = t
                        time.sleep(0.12)

        if current_testament is not None:
            if keys[pygame.K_RETURN]:
                current_testament["collected"] = True
                last_read_word = current_testament["text"]
                current_testament = None
                first_collected = True
                can_write = True
                time.sleep(0.12)

        if player.colliderect(typewriter) and can_write and not typing_mode and current_testament is None:
            interaction_text = "Press E to write"
            if keys[pygame.K_e]:
                typing_mode = True
                typed_word = ""
                time.sleep(0.12)

        if typing_mode:
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.fill((0,0,0))
            overlay.set_alpha(230)
            screen.blit(overlay,(0,0))
            p = font.render("Type the last fragment you read (ENTER submit, ESC cancel):", True, WHITE)
            screen.blit(p, (WIDTH//2 - 340, HEIGHT//2 - 80))
            typed_surf = font.render(typed_word, True, YELLOW)
            screen.blit(typed_surf, (WIDTH//2 - 340, HEIGHT//2 - 30))

        all_done = False
        if first_collected and first_written:
            all_done = all((t.get("collected", False) and t.get("written", False)) for t in testaments)
        if all_done and not waiting_to_continue:
            show_center_text(screen, ["Chapter Complete"], 2.0)
            waiting_to_continue = True
            chapter_done = True

        if waiting_to_continue and player.colliderect(typewriter):
            interaction_text = "Press E to continue to Chapter III"
            if keys[pygame.K_e]:
                show_center_text(screen, ["Chapter III", "Endless Love"], 2.2)
                game_state["progress"]["chapter2"] = True
                game_state["current_chapter"] = 3
                save_progress()
                running = False

        if interaction_text:
            t = font.render(interaction_text, True, WHITE)
            screen.blit(t, (40, 40))

        if current_testament is not None:
            show_overlay(screen, current_testament["text"])

        pygame.display.flip()

def show_overlay(screen, text):
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.fill((0,0,0))
    overlay.set_alpha(220)
    screen.blit(overlay,(0,0))
    wrapped = wrap_text(f"\"{text}\"", font, WIDTH - 200)
    draw_text_block(wrapped, font, WHITE, screen, HEIGHT//2 - 60)
    hint = font.render("Press ENTER to close", True, YELLOW)
    screen.blit(hint, hint.get_rect(center=(WIDTH//2, HEIGHT//2 + 70)))

def show_center_text(screen, lines, seconds=2.0):
    start = time.time()
    local_clock = pygame.time.Clock()
    while time.time() - start < seconds:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
        try:
            bg = pygame.image.load("background.jpg").convert()
            bg = pygame.transform.scale(bg, (WIDTH, HEIGHT))
            screen.blit(bg, (0,0))
        except Exception:
            screen.fill((20,20,20))
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.fill((0,0,0))
        overlay.set_alpha(200)
        screen.blit(overlay,(0,0))
        for i, line in enumerate(lines):
            txt = big_font.render(line, True, WHITE)
            screen.blit(txt, txt.get_rect(center=(WIDTH//2, HEIGHT//2 + i*50)))
        pygame.display.flip()
        local_clock.tick(30)

def wrap_text(text, fontobj, width):
    words = text.split(' ')
    lines, cur = [], ""
    for w in words:
        if fontobj.size(cur + w)[0] < width:
            cur += w + " "
        else:
            lines.append(cur)
            cur = w + " "
    if cur:
        lines.append(cur)
    return lines

def draw_text_block(lines, fontobj, color, surf, y):
    for i, line in enumerate(lines):
        txt = fontobj.render(line, True, color)
        rect = txt.get_rect(center=(WIDTH//2, y + i*30))
        surf.blit(txt, rect)
