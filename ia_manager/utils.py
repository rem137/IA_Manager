import os
import sys

try:
    from colorama import init, Fore, Style
    init(autoreset=True)
    COLOR_AVAILABLE = True
except Exception:
    COLOR_AVAILABLE = False
    class _Dummy:
        def __getattr__(self, name):
            return ''
    Fore = Style = _Dummy()

COLOR_ENABLED = COLOR_AVAILABLE and sys.stdout.isatty() and not os.environ.get('NO_COLOR')


def color(text: str, fore: str = '') -> str:
    """Return colored text if supported."""
    if COLOR_ENABLED and fore:
        return f"{fore}{text}{Style.RESET_ALL}"
    return text
