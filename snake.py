#!/usr/bin/env python3
import curses
import random
import json
import os
import time

HIGHSCORE_FILE = os.path.join(os.path.dirname(__file__), ".highscore")

SNAKE_COLORS = [
    (curses.COLOR_GREEN, curses.COLOR_BLACK),
    (curses.COLOR_CYAN, curses.COLOR_BLACK),
    (curses.COLOR_YELLOW, curses.COLOR_BLACK),
    (curses.COLOR_MAGENTA, curses.COLOR_BLACK),
]


def load_highscore():
    try:
        with open(HIGHSCORE_FILE) as f:
            return json.load(f).get("score", 0)
    except (FileNotFoundError, json.JSONDecodeError):
        return 0


def save_highscore(score):
    with open(HIGHSCORE_FILE, "w") as f:
        json.dump({"score": score}, f)


def draw_border(win, h, w):
    win.attron(curses.color_pair(6))
    win.border("│", "│", "─", "─", "╭", "╮", "╰", "╯")
    win.attroff(curses.color_pair(6))


def game(stdscr):
    curses.curs_set(0)
    curses.start_color()
    curses.use_default_colors()

    curses.init_pair(1, curses.COLOR_GREEN, -1)
    curses.init_pair(2, curses.COLOR_CYAN, -1)
    curses.init_pair(3, curses.COLOR_YELLOW, -1)
    curses.init_pair(4, curses.COLOR_MAGENTA, -1)
    curses.init_pair(5, curses.COLOR_RED, -1)
    curses.init_pair(6, curses.COLOR_WHITE, -1)
    curses.init_pair(7, curses.COLOR_WHITE, -1)

    highscore = load_highscore()

    while True:
        stdscr.clear()
        h, w = stdscr.getmaxyx()

        if h < 20 or w < 40:
            stdscr.addstr(0, 0, "Terminal zu klein! Bitte vergrößern (min 40x20).")
            stdscr.refresh()
            stdscr.getch()
            return

        # Start screen
        title = "🐍  TERMINAL SNAKE"
        stdscr.attron(curses.color_pair(1) | curses.A_BOLD)
        stdscr.addstr(h // 2 - 4, (w - len(title)) // 2, title)
        stdscr.attroff(curses.color_pair(1) | curses.A_BOLD)

        lines = [
            f"Highscore: {highscore}",
            "",
            "Steuerung: Pfeiltasten / WASD",
            "Beenden:   Q",
            "",
            "[ ENTER zum Starten ]",
        ]
        for i, line in enumerate(lines):
            stdscr.addstr(h // 2 - 2 + i, (w - len(line)) // 2, line)

        stdscr.refresh()

        key = stdscr.getch()
        if key in (ord("q"), ord("Q")):
            return
        if key not in (10, 13, curses.KEY_ENTER):
            continue

        # Game setup
        play_h = h - 4  # leave room for header/footer
        play_w = w - 2
        start_y, start_x = 2, 1  # top-left of play area

        snake = [(play_h // 2, play_w // 4 + i) for i in range(4, -1, -1)]
        direction = curses.KEY_RIGHT
        score = 0
        speed = 0.12

        def place_food():
            while True:
                fy = random.randint(start_y + 1, start_y + play_h - 2)
                fx = random.randint(start_x + 1, start_x + play_w - 2)
                if (fy, fx) not in snake:
                    return (fy, fx)

        food = place_food()
        stdscr.nodelay(True)
        stdscr.timeout(int(speed * 1000))

        last_time = time.time()

        while True:
            stdscr.clear()
            h, w = stdscr.getmaxyx()
            play_w = w - 2

            # Header
            header = f" Score: {score}   Highscore: {highscore}   [Q] Beenden "
            stdscr.attron(curses.color_pair(1) | curses.A_BOLD)
            stdscr.addstr(0, (w - len(header)) // 2, header)
            stdscr.attroff(curses.color_pair(1) | curses.A_BOLD)

            # Border
            for col in range(start_x, start_x + play_w):
                stdscr.attron(curses.color_pair(6))
                if col < w:
                    stdscr.addch(start_y, col, "─")
                    if start_y + play_h - 1 < h and col < w:
                        stdscr.addch(start_y + play_h - 1, col, "─")
                stdscr.attroff(curses.color_pair(6))
            for row in range(start_y, start_y + play_h):
                stdscr.attron(curses.color_pair(6))
                if row < h:
                    stdscr.addch(row, start_x, "│")
                    if start_x + play_w - 1 < w:
                        stdscr.addch(row, start_x + play_w - 1, "│")
                stdscr.attroff(curses.color_pair(6))

            # Corners
            stdscr.attron(curses.color_pair(6))
            stdscr.addch(start_y, start_x, "╭")
            stdscr.addch(start_y, start_x + play_w - 1, "╮")
            if start_y + play_h - 1 < h:
                stdscr.addch(start_y + play_h - 1, start_x, "╰")
                if start_x + play_w - 1 < w:
                    stdscr.addch(start_y + play_h - 1, start_x + play_w - 1, "╯")
            stdscr.attroff(curses.color_pair(6))

            # Food
            if food[0] < h and food[1] < w:
                stdscr.attron(curses.color_pair(5) | curses.A_BOLD)
                stdscr.addch(food[0], food[1], "●")
                stdscr.attroff(curses.color_pair(5) | curses.A_BOLD)

            # Snake with gradient colors
            for idx, (sy, sx) in enumerate(snake):
                if sy < h and sx < w:
                    color_idx = (idx // 3) % 4 + 1
                    char = "█" if idx == 0 else "▓" if idx < 3 else "░"
                    attr = curses.color_pair(color_idx)
                    if idx == 0:
                        attr |= curses.A_BOLD
                    stdscr.attron(attr)
                    stdscr.addch(sy, sx, char)
                    stdscr.attroff(attr)

            # Footer hint
            hint = " ← ↑ ↓ → oder W A S D "
            if h - 1 >= 0 and len(hint) < w:
                stdscr.attron(curses.color_pair(6))
                stdscr.addstr(h - 1, (w - len(hint)) // 2, hint)
                stdscr.attroff(curses.color_pair(6))

            stdscr.refresh()

            # Input
            key = stdscr.getch()
            if key in (ord("q"), ord("Q")):
                return

            key_map = {
                ord("w"): curses.KEY_UP, ord("W"): curses.KEY_UP,
                ord("s"): curses.KEY_DOWN, ord("S"): curses.KEY_DOWN,
                ord("a"): curses.KEY_LEFT, ord("A"): curses.KEY_LEFT,
                ord("d"): curses.KEY_RIGHT, ord("D"): curses.KEY_RIGHT,
            }
            key = key_map.get(key, key)

            opposites = {
                curses.KEY_UP: curses.KEY_DOWN,
                curses.KEY_DOWN: curses.KEY_UP,
                curses.KEY_LEFT: curses.KEY_RIGHT,
                curses.KEY_RIGHT: curses.KEY_LEFT,
            }
            if key in opposites and key != opposites.get(direction):
                direction = key

            # Move
            now = time.time()
            if now - last_time < speed:
                continue
            last_time = now

            head_y, head_x = snake[0]
            if direction == curses.KEY_UP:
                head_y -= 1
            elif direction == curses.KEY_DOWN:
                head_y += 1
            elif direction == curses.KEY_LEFT:
                head_x -= 1
            elif direction == curses.KEY_RIGHT:
                head_x += 1

            # Collision: walls
            if (head_y <= start_y or head_y >= start_y + play_h - 1 or
                    head_x <= start_x or head_x >= start_x + play_w - 1):
                break

            # Collision: self
            if (head_y, head_x) in snake[1:]:
                break

            snake.insert(0, (head_y, head_x))

            if (head_y, head_x) == food:
                score += 10
                if score > highscore:
                    highscore = score
                    save_highscore(highscore)
                # Speed up
                speed = max(0.04, speed - 0.003)
                stdscr.timeout(int(speed * 1000))
                food = place_food()
            else:
                snake.pop()

        # Game over screen
        stdscr.nodelay(False)
        stdscr.clear()
        msgs = [
            "╔══════════════════╗",
            "║   GAME  OVER!    ║",
            "╚══════════════════╝",
            "",
            f"  Score:      {score}",
            f"  Highscore:  {highscore}",
            "",
            "[ ENTER = Nochmal   Q = Beenden ]",
        ]
        for i, msg in enumerate(msgs):
            y = h // 2 - len(msgs) // 2 + i
            x = (w - len(msg)) // 2
            if i == 0 or i == 2:
                stdscr.attron(curses.color_pair(5) | curses.A_BOLD)
            elif i == 1:
                stdscr.attron(curses.color_pair(5) | curses.A_BOLD)
            else:
                stdscr.attron(curses.color_pair(7))
            if 0 <= y < h and x >= 0:
                stdscr.addstr(y, max(0, x), msg)
            stdscr.attroff(curses.color_pair(5) | curses.A_BOLD)
            stdscr.attroff(curses.color_pair(7))

        stdscr.refresh()

        while True:
            k = stdscr.getch()
            if k in (ord("q"), ord("Q")):
                return
            if k in (10, 13, curses.KEY_ENTER):
                break


def main():
    curses.wrapper(game)


if __name__ == "__main__":
    main()
