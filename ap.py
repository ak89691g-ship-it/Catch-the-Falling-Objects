"""
PS 63 - Catch the Falling Objects (Python 3 + Pygame)

Run:  python catch_falling_objects.py
  1. First all 4 test cases run in the terminal (one run, PASS/FAIL shown).
  2. Then the game window opens.  Move the basket with LEFT / RIGHT arrows.

Run only the test cases (no game window):
      python catch_falling_objects.py --tests-only
"""
import random
import sys

try:
    import pygame
    HAS_PYGAME = True
    Rect = pygame.Rect
    K_LEFT, K_RIGHT, K_UP = pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP
except ImportError:
    # Pygame is not installed: the test cases still run with a simple Rect.
    pygame = None
    HAS_PYGAME = False
    K_LEFT, K_RIGHT, K_UP = 1073741904, 1073741903, 1073741906

    class Rect:
        def __init__(self, x, y, w, h):
            self.x, self.y, self.w, self.h = x, y, w, h

        @property
        def top(self):
            return self.y

        def colliderect(self, o):
            return (self.x < o.x + o.w and o.x < self.x + self.w and
                    self.y < o.y + o.h and o.y < self.y + self.h)

# ---------------- Settings (from the problem statement) ----------------
WIDTH, HEIGHT = 500, 600
BASKET_W, BASKET_H, BASKET_Y = 80, 20, 560
BASKET_SPEED = 10            # px per key press
OBJ_SIZE = 20                # object is 20 x 20
FALL_SPEED = 5               # px per frame
START_LIVES = 3
MAX_BASKET_X = WIDTH - BASKET_W      # 420
FPS = 60


# ---------------- Core functions ----------------
def new_state(basket_x=210, lives=START_LIVES, score=0, obj_pos=None):
    """Create the game state. obj_pos=(x, y) gives a fixed object (used in tests)."""
    state = {"basket_x": basket_x, "lives": lives, "score": score,
             "game_over": False}
    state["obj"] = Rect(obj_pos[0], obj_pos[1], OBJ_SIZE, OBJ_SIZE) \
        if obj_pos else spawn_object()
    return state


def spawn_object():
    """New object at the top of the screen with a random x (0 to 480)."""
    return Rect(random.randint(0, WIDTH - OBJ_SIZE), 0, OBJ_SIZE, OBJ_SIZE)


def move_basket(x, key):
    """LEFT / RIGHT move the basket 10 px and keep it inside the window.
    Any other key is ignored (x stays the same)."""
    if key == K_LEFT:
        return max(0, x - BASKET_SPEED)
    if key == K_RIGHT:
        return min(MAX_BASKET_X, x + BASKET_SPEED)
    return x


def update_object(obj):
    """Object falls 5 px every frame."""
    obj.y += FALL_SPEED


def check_catch(basket_rect, obj_rect):
    """Rect collision between basket and object."""
    return basket_rect.colliderect(obj_rect)


def update_score_lives(state, caught):
    """Caught: score + 1.  Missed: lives - 1 (game over at 0)."""
    if caught:
        state["score"] += 1
        return "Object caught | Score: %d | Lives: %d" % (state["score"], state["lives"])
    state["lives"] -= 1
    if state["lives"] <= 0:
        state["lives"] = 0
        state["game_over"] = True
        return "Object missed | Lives: 0 | Game Over | Final Score: %d" % state["score"]
    return "Object missed | Lives: %d" % state["lives"]


def game_step(state):
    """One frame: object falls, then catch / miss is checked.
    Returns a message when an object is caught or missed, otherwise None."""
    obj = state["obj"]
    update_object(obj)
    basket_rect = Rect(state["basket_x"], BASKET_Y, BASKET_W, BASKET_H)
    if check_catch(basket_rect, obj):
        message = update_score_lives(state, True)
        state["obj"] = spawn_object()
        return message
    if obj.top > HEIGHT:                         # fell past the bottom
        message = update_score_lives(state, False)
        state["obj"] = spawn_object()
        return message
    return None


def run_until_event(state):
    """Keep stepping frames until an object is caught or missed (for tests)."""
    while True:
        message = game_step(state)
        if message:
            return message


def draw_screen(screen, font, state):
    screen.fill((247, 245, 239))
    pygame.draw.rect(screen, (217, 162, 27),
                     (state["basket_x"], BASKET_Y, BASKET_W, BASKET_H))
    pygame.draw.rect(screen, (192, 57, 43), state["obj"])
    hud = font.render("Score: %d   Lives: %d" % (state["score"], state["lives"]),
                      True, (18, 38, 74))
    screen.blit(hud, (10, 10))


def game_over_screen(screen, font, big_font, score):
    screen.fill((18, 38, 74))
    text = big_font.render("GAME OVER", True, (255, 255, 255))
    final = font.render("Final Score: %d" % score, True, (255, 255, 255))
    screen.blit(text, text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 20)))
    screen.blit(final, final.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 30)))


# ---------------- All test cases in one run ----------------
def _show(label, expected, got):
    ok = (got == expected)
    print("   %s" % label)
    print("      Expected : %s" % expected)
    print("      Got      : %s   -> %s" % (got, "PASS" if ok else "FAIL"))
    return ok


def run_test_cases():
    results = []
    print("=" * 66)
    print("PS 63 - CATCH THE FALLING OBJECTS : TEST CASES")
    print("=" * 66)

    print("\nTest Case 1: Normal Input (Basket x = 210, Object at (230, 545))")
    s = new_state(basket_x=210, obj_pos=(230, 545))
    results.append(_show("Object reaches the basket",
                         "Object caught | Score: 1 | Lives: 3", run_until_event(s)))

    print("\nTest Case 2: Boundary / Minimum Input")
    x = move_basket(0, K_LEFT)
    results.append(_show("(a) Basket x = 0, key: LEFT arrow",
                         "Basket x = 0 (no movement, stays inside window)",
                         "Basket x = %d (no movement, stays inside window)" % x))
    x = move_basket(420, K_RIGHT)
    results.append(_show("(b) Basket x = 420, key: RIGHT arrow",
                         "Basket x = 420 (no movement, stays inside window)",
                         "Basket x = %d (no movement, stays inside window)" % x))

    print("\nTest Case 3: Invalid Input (Basket x = 210, UP arrow)")
    x = move_basket(210, K_UP)
    results.append(_show("UP arrow is not a control key",
                         "Key ignored. Basket x = 210",
                         "Key ignored. Basket x = %d" % x))

    print("\nTest Case 4: Different Valid Scenario")
    s = new_state(basket_x=210, lives=3, obj_pos=(400, 0))
    results.append(_show("(a) Basket x = 210, object falls past y = 600 at x = 400, lives before: 3",
                         "Object missed | Lives: 2", run_until_event(s)))
    s = new_state(basket_x=210, lives=1, score=7, obj_pos=(400, 0))
    results.append(_show("(b) Same miss with lives before: 1, score: 7",
                         "Object missed | Lives: 0 | Game Over | Final Score: 7",
                         run_until_event(s)))

    print("\n" + "=" * 66)
    print("RESULT: %d / %d TEST CASES PASSED" % (sum(results), len(results)))
    print("=" * 66)
    return all(results)


# ---------------- Game loop ----------------
def main():
    run_test_cases()
    if "--tests-only" in sys.argv:
        return
    if not HAS_PYGAME:
        print("\nPygame is not installed, so the game window cannot open.")
        print("Install it with:  python -m pip install pygame")
        print("(If that fails on a very new Python version, install Python 3.12 or 3.13.)")
        return

    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Catch the Falling Objects")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 30)
    big_font = pygame.font.SysFont(None, 64)
    pygame.key.set_repeat(150, 30)       # holding an arrow key keeps moving

    state = new_state()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and not state["game_over"]:
                state["basket_x"] = move_basket(state["basket_x"], event.key)

        if not state["game_over"]:
            message = game_step(state)
            if message:
                print(message)           # same messages as the test cases
            draw_screen(screen, font, state)
        else:
            game_over_screen(screen, font, big_font, state["score"])

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()