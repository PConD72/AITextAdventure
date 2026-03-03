import textwrap
import sys
import os
import time


def supports_ansi():
    if os.getenv("NO_COLOR"):
        return False
    if sys.platform == "win32":
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            mode = ctypes.c_ulong()
            handle = kernel32.GetStdHandle(-11)
            if kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
                # Enable VIRTUAL_TERMINAL_PROCESSING
                kernel32.SetConsoleMode(handle, mode.value | 0x0004)
                return True
        except Exception:
            pass
        return os.getenv("TERM") is not None
    return hasattr(sys.stdout, "isatty") and sys.stdout.isatty()


_ANSI = supports_ansi()
WIDTH = 76


def bold(text):
    if _ANSI:
        return f"\033[1m{text}\033[0m"
    return text


def dim(text):
    if _ANSI:
        return f"\033[2m{text}\033[0m"
    return text


def italic(text):
    if _ANSI:
        return f"\033[3m{text}\033[0m"
    return text


def underline(text):
    if _ANSI:
        return f"\033[4m{text}\033[0m"
    return text


def wrap(text, width=WIDTH):
    paragraphs = text.split("\n")
    wrapped = []
    for para in paragraphs:
        para = para.strip()
        if not para:
            wrapped.append("")
        else:
            wrapped.extend(textwrap.wrap(para, width=width))
    return "\n".join(wrapped)


def print_wrapped(text, width=WIDTH):
    print(wrap(text, width))


def print_room_name(name):
    print()
    print(bold(f"--- {name} ---"))


def print_separator():
    print(dim("-" * WIDTH))


def print_slow(text, delay=0.02):
    """Typewriter effect for dramatic moments."""
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()


def get_input(prompt="> "):
    try:
        return input(bold(prompt)).strip()
    except (EOFError, KeyboardInterrupt):
        print()
        return "quit"


def clear_screen():
    os.system("cls" if sys.platform == "win32" else "clear")


def press_enter():
    get_input(dim("[Press Enter to continue] "))
