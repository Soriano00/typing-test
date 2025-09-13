import curses
from curses import wrapper
import time
import random
import textwrap
import re  # <<< para normalizar espacios

def start_screen(stdscr):
    stdscr.clear()
    stdscr.addstr("Welcome to the Speed Typing Test!")
    stdscr.addstr("\nPress any key to begin...")
    stdscr.refresh()
    stdscr.getkey()

def display_text(stdscr, target, current, wpm=0, precision=0):
    stdscr.clear()
    height, width = stdscr.getmaxyx()

    wrapped_target = textwrap.wrap(target, width - 1)

    for i, line in enumerate(wrapped_target):
        stdscr.addstr(i, 0, line, curses.color_pair(3))

    current_str = "".join(current)
    wrapped_current = textwrap.wrap(current_str, width - 1)

    for row, line in enumerate(wrapped_current):
        for col, typed_char in enumerate(line):
            target_char = ''
            if row < len(wrapped_target) and col < len(wrapped_target[row]):
                target_char = wrapped_target[row][col]
            color = 2 if typed_char != target_char else 1
            stdscr.addstr(row, col, typed_char, curses.color_pair(color))

    stdscr.addstr(len(wrapped_target) + 1, 0, f"WPM: {wpm}  Precision: {precision}%")

def load_text():
    with open("text.txt", "r", encoding="utf-8") as f:
        content = f.read().strip()
        paragraphs = [p.strip() for p in content.split("\n") if p.strip()]
        if not paragraphs:
            raise ValueError("El archivo text.txt no contiene párrafos válidos.")
        chosen = random.choice(paragraphs)
        text = chosen.replace("\n", " ").replace("\r", " ")
        # Normalizar espacios múltiples a uno solo
        text = re.sub(r"\s+", " ", text).strip()
        return text


def wpm_test(stdscr):
    target_text = load_text()
    current_text = []
    wpm = 0
    precision = 0
    total_typed = 0
    correct_typed = 0
    start_time = time.time()
    stdscr.nodelay(True)

    while True:
        elapsed_time = max(time.time() - start_time, 1)
        wpm = round((len(current_text) / (elapsed_time / 60)) / 5)
        precision = round((correct_typed / total_typed) * 100) if total_typed else 0

        display_text(stdscr, target_text, current_text, wpm, precision)
        stdscr.refresh()
        curses.napms(50)

        # Normalizamos ambas cadenas
        current_clean = re.sub(r"\s+", " ", "".join(current_text)).strip()
        target_clean = re.sub(r"\s+", " ", target_text).strip()

        if current_clean == target_clean:
            stdscr.nodelay(False)
            stdscr.addstr(len(textwrap.wrap(target_text, stdscr.getmaxyx()[1] - 1)) + 3, 0,
                          f"Test completed! Final WPM: {wpm}, Precision: {precision}%. Press any key to continue...")
            stdscr.getkey()
            break

        try:
            key = stdscr.getch()
        except:
            continue

        if key == 27:  # ESC
            break
        elif key in (curses.KEY_BACKSPACE, 127, 8):
            if len(current_text) > 0:
                current_text.pop()
        elif 32 <= key <= 126:
            if len(current_text) < len(target_text):
                typed_char = chr(key)
                current_text.append(typed_char)
                total_typed += 1
                if typed_char == target_text[len(current_text)-1]:
                    correct_typed += 1
                    
def main(stdscr):
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_BLACK)

    start_screen(stdscr)
    while True:
        wpm_test(stdscr)
        stdscr.clear()
        stdscr.addstr(0, 0, "Test complete! Press any key to restart or ESC to exit.")
        key = stdscr.getkey()
        if key == '\x1b':
            break

wrapper(main)
