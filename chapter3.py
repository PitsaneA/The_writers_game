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
    "you mattered to someone", "new lovers", "simple", "change my entire destiny",
    "younger", "wanted to be loved"
]
negative_words = [
    "broken soul", "without hope", "lifeless", "something bad to say",
    "our story had ended", "dying", "abyss", "eternity was too short"
]

endings = {
    "very_bad": {"title": "Ashes of Love", "text": ["Everything you wrote burned away."] , "light": (10,10,10)},
    "very_good": {"title": "Endless Love", "text": ["You sent it, and someone read it."], "light": (255,240,210)}
}

def run(screen):
    pygame.display.set_caption("Endless Love")

    player = pygame.Rect(100, HEIGHT - 150, 50, 80)
    player_speed = 5
    lamp = pygame.Rect(150, HEIGHT - 200, 50, 100)
    typewriter = pygame.Rect(700, HEIGHT - 120, 100, 60)

    clock = pygame.time.Clock()
    try:
        background = pygame.image.load("background.jpg").convert()
        background = pygame.transform.scale(background, (WIDTH, HEIGHT))
    except Exception:
        background = pygame.Surface((WIDTH, HEIGHT)); background.fill((20,20,20))

    light_on = False
    testaments = []
    used_words = set()           
    collected = []
    first_found = False
    reading_fragment = False
    guessing = False
    current_word = ""           
    current_testament = None    
    guess_word = ""
    guesses = 0
    initial_hint = None         
    hint_indexes = []           

    def get_unique(pool):
        """Returnează un element din pool care nu a fost folosit. Dacă nu mai sunt, returnează None."""
        avail = [w for w in pool if w not in used_words]
        if not avail:
            return None
        w = random.choice(avail)
        used_words.add(w)
        return w

    def gen_testament(text, positive, existing):
        tries = 0
        while True:
            tries += 1
            r = pygame.Rect(random.randint(80, WIDTH-160), random.randint(180, HEIGHT-150), 140, 48)
            collide = False
            if r.colliderect(lamp) or r.colliderect(typewriter):
                collide = True
            for o in existing:
                if r.colliderect(o["rect"].inflate(8,8)):
                    collide = True
                    break
            if not collide or tries > 400:
                return {"rect": r, "text": text, "positive": positive, "collected": False}

    pool_all = positive_words + negative_words
    first_text = get_unique(pool_all)
    if not first_text:
        first_text = random.choice(pool_all)
    first_positive = random.random() > 0.5
    testaments.append(gen_testament(first_text, first_positive, []))

    running = True
    while running:
        dt = clock.tick(60)
        events = pygame.event.get()
        for ev in events:
            if ev.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()

        allow_move = not reading_fragment and not guessing
        if allow_move:
            if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                player.x -= player_speed
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                player.x += player_speed
            if keys[pygame.K_w] or keys[pygame.K_UP]:
                player.y -= player_speed
            if keys[pygame.K_s] or keys[pygame.K_DOWN]:
                player.y += player_speed
        player.clamp_ip(pygame.Rect(0,0,WIDTH,HEIGHT))

        screen.blit(background,(0,0))
        if not light_on:
            dark = pygame.Surface((WIDTH,HEIGHT)); dark.fill((0,0,0)); dark.set_alpha(150); screen.blit(dark,(0,0))

        pygame.draw.rect(screen, (160,110,70), player)
        pygame.draw.rect(screen, YELLOW, lamp)
        pygame.draw.rect(screen, (200,200,200), typewriter)

        interaction_text = ""

        if not reading_fragment and not guessing and player.colliderect(lamp):
            interaction_text = "Press E to toggle lamp"
            for ev in events:
                if ev.type==pygame.KEYDOWN and ev.key==pygame.K_e:
                    light_on = not light_on
                    time.sleep(0.12)

        if collected and not reading_fragment and not guessing:
            r_hint = font.render("Press R to reread last fragment", True, WHITE)
            screen.blit(r_hint, (WIDTH-360, 36))
            if keys[pygame.K_r]:
                show_overlay(screen, collected[-1])

        for t in testaments:
            if t.get("collected", False):
                continue
            visible = (light_on and t["positive"]) or (not light_on and not t["positive"]) or (not first_found)
            if visible:
                pygame.draw.rect(screen, BROWN, t["rect"], border_radius=6)
                label = font.render("Testament", True, WHITE)
                screen.blit(label, label.get_rect(center=t["rect"].center))

                unfinished = any(tt.get("collected", False) and tt["text"] not in collected for tt in testaments)
                if not reading_fragment and not guessing and current_testament is None and not unfinished and player.colliderect(t["rect"]):
                    interaction_text = "Press E to read"
                    if keys[pygame.K_e]:
                        current_testament = t
                        current_word = t["text"]
                        reading_fragment = True
                        initial_hint = generate_hint_static(current_word, reveal_letters=2)
                        hint_indexes = []      
                        guesses = 0
                        time.sleep(0.12)

        if reading_fragment and current_testament:
            for ev in events:
                if ev.type==pygame.KEYDOWN and ev.key==pygame.K_RETURN:
                    reading_fragment = False
                    guessing = True
                    guess_word = ""
                    guesses = 0
                    time.sleep(0.12)

        if guessing:
            for ev in events:
                if ev.type==pygame.KEYDOWN:
                    if ev.key==pygame.K_ESCAPE:
                        guessing = False
                        current_testament = None
                        initial_hint = None
                        guess_word = ""
                    elif ev.key==pygame.K_RETURN:
                        guesses += 1
                        if guess_word.strip().lower() == current_word.strip().lower():
                            current_testament["collected"] = True
                            collected.append(current_word)
                            guessing = False
                            current_testament = None
                            initial_hint = None
                            guess_word = ""
                            first_found = True
                            if first_found and len(testaments) == 1:
                                pos_sel = []
                                neg_sel = []
                                for _ in range(3):
                                    w = get_unique_from_lists(positive_words, used_words)
                                    if w: pos_sel.append(w)
                                for _ in range(3):
                                    w = get_unique_from_lists(negative_words, used_words)
                                    if w: neg_sel.append(w)
                                for w in pos_sel:
                                    testaments.append(gen_testament(w, True, testaments))
                                for w in neg_sel:
                                    testaments.append(gen_testament(w, False, testaments))
                        else:
                            guess_word = ""
                            if guesses >= 2:
                                initial_hint = reveal_one_more_letter(initial_hint, current_word)
                    elif ev.key==pygame.K_BACKSPACE:
                        guess_word = guess_word[:-1]
                    else:
                        if ev.unicode:
                            guess_word += ev.unicode

        if first_found and all(t.get("collected", False) for t in testaments):
            show_center_text(screen, ["Chapter Complete"], 2.0)
            if player.colliderect(typewriter):
                interaction_text = "Press E to choose final action"
                if keys[pygame.K_e]:
                    sel = show_final_menu(screen)
                    if sel == "send":
                        ending = endings["very_good"]
                    else:
                        ending = endings["very_bad"]
                    show_ending(screen, ending)
                    game_state["progress"]["chapter3"] = True
                    game_state["current_chapter"] = None
                    save_progress()
                    running = False

        if interaction_text:
            txt = font.render(interaction_text, True, WHITE)
            screen.blit(txt, (40,40))

        if reading_fragment and current_testament:
            show_overlay(screen, current_testament["text"], prompt="Press ENTER to start guessing")

        if guessing and (initial_hint is not None):
            overlay = pygame.Surface((WIDTH,HEIGHT)); overlay.fill((0,0,0)); overlay.set_alpha(220); screen.blit(overlay,(0,0))
            title = font.render("Type the full fragment exactly and press ENTER", True, WHITE)
            screen.blit(title, (WIDTH//2 - 300, HEIGHT//2 - 120))
            hint_txt = font.render(f"Hint: {initial_hint}", True, (200,200,200))
            screen.blit(hint_txt, (WIDTH//2 - 300, HEIGHT//2 - 40))
            typed_surface = font.render(guess_word, True, YELLOW)
            screen.blit(typed_surface, (WIDTH//2 - 300, HEIGHT//2 + 10))

        pygame.display.flip()

    def get_unique_from_lists(pool, used_set):
        choices = [w for w in pool if w not in used_set]
        if not choices:
            return None
        w = random.choice(choices)
        used_set.add(w)
        return w

    def generate_hint_static(word, reveal_letters=2):
        """
        Returnează o versiune a frazei în care doar reveal_letters litere (în total,
        nu pe fiecare cuvânt) sunt dezvăluite; restul sunt underscore.
        Păstrăm spațiile și semnele.
        """
        letters = [i for i,ch in enumerate(word) if ch.isalpha()]
        if not letters:
            return ''.join('_' if c.isalpha() else c for c in word)
        k = min(reveal_letters, len(letters))
        reveal_pos = set(random.sample(letters, k))
        out = []
        for i,ch in enumerate(word):
            if not ch.isalpha():
                out.append(ch)
            elif i in reveal_pos:
                out.append(ch)
            else:
                out.append('_')
        return ''.join(out)

    def reveal_one_more_letter(current_hint, word):
        """Dezvăluie o literă suplimentară în current_hint — păstrează constanța pozițiilor."""
        if not current_hint:
            return generate_hint_static(word, reveal_letters=1)
        idxs = [i for i,(h,ch) in enumerate(zip(current_hint, word)) if h=='_' and ch.isalpha()]
        if not idxs:
            return current_hint
        pick = random.choice(idxs)
        new_hint = list(current_hint)
        new_hint[pick] = word[pick]
        return ''.join(new_hint)

    def show_overlay(screen, text, prompt="Press ENTER to close"):
        overlay = pygame.Surface((WIDTH,HEIGHT)); overlay.fill((0,0,0)); overlay.set_alpha(220); screen.blit(overlay,(0,0))
        wrapped = wrap_text(f"\"{text}\"", font, WIDTH-200)
        draw_text_block(wrapped, font, WHITE, screen, HEIGHT//2 - 60)
        hint = font.render(prompt, True, YELLOW)
        screen.blit(hint, hint.get_rect(center=(WIDTH//2, HEIGHT//2 + 70)))

    def show_center_text(screen, lines, seconds=2.0):
        start = time.time()
        lc = pygame.time.Clock()
        while time.time()-start < seconds:
            for e in pygame.event.get():
                if e.type==pygame.QUIT:
                    pygame.quit(); return
            try:
                bg = pygame.image.load("background.jpg").convert()
                bg = pygame.transform.scale(bg, (WIDTH, HEIGHT))
                screen.blit(bg,(0,0))
            except Exception:
                screen.fill((20,20,20))
            over = pygame.Surface((WIDTH,HEIGHT)); over.fill((0,0,0)); over.set_alpha(200); screen.blit(over,(0,0))
            for i,line in enumerate(lines):
                t = big_font.render(line, True, WHITE)
                screen.blit(t, t.get_rect(center=(WIDTH//2, HEIGHT//2 + i*50)))
            pygame.display.flip()
            lc.tick(30)

    def show_final_menu(screen):
        selected = 0
        opts = ["Send it", "Burn it"]
        lc = pygame.time.Clock()
        while True:
            for e in pygame.event.get():
                if e.type==pygame.QUIT:
                    return "burn"
                if e.type==pygame.KEYDOWN:
                    if e.key in (pygame.K_UP, pygame.K_w):
                        selected = (selected-1)%2
                    if e.key in (pygame.K_DOWN, pygame.K_s):
                        selected = (selected+1)%2
                    if e.key==pygame.K_RETURN:
                        return "send" if selected==0 else "burn"
            screen.fill((0,0,0))
            title = big_font.render("Final Choice", True, WHITE)
            screen.blit(title, title.get_rect(center=(WIDTH//2, HEIGHT//3)))
            for i,opt in enumerate(opts):
                col = YELLOW if i==selected else WHITE
                t = font.render(opt, True, col)
                screen.blit(t, t.get_rect(center=(WIDTH//2, HEIGHT//2 + i*50)))
            pygame.display.flip()
            lc.tick(30)

    def show_ending(screen, ending):
        target = ending["light"]
        cur = [0,0,0]
        lc = pygame.time.Clock()
        for _ in range(60):
            cur = [cur[i] + (target[i]-cur[i])*0.05 for i in range(3)]
            screen.fill(tuple(int(x) for x in cur))
            title = big_font.render(ending["title"], True, WHITE)
            screen.blit(title, title.get_rect(center=(WIDTH//2, HEIGHT//4)))
            pygame.display.flip()
            lc.tick(30)
        show_center_text(screen, ending["text"], 4.0)

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
        for i,line in enumerate(lines):
            t = fontobj.render(line, True, color)
            r = t.get_rect(center=(WIDTH//2, y + i*30))
            surf.blit(t, r)


