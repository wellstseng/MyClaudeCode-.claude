"""Capture a screenshot of a specific window (by title) or full screen.

Usage:
    python screenshot.py [--window "Unity"] [--output path.png]
"""
import argparse
import sys

def find_window_rect(title_substring):
    """Find window rect by title substring using win32gui."""
    try:
        import win32gui
        import win32con
    except ImportError:
        print(f"[WARN] pywin32 not available, falling back to full screen", file=sys.stderr)
        return None

    result = []

    def enum_cb(hwnd, _):
        if not win32gui.IsWindowVisible(hwnd):
            return
        text = win32gui.GetWindowText(hwnd)
        if title_substring.lower() in text.lower():
            result.append((hwnd, text, win32gui.GetWindowRect(hwnd)))

    win32gui.EnumWindows(enum_cb, None)

    if not result:
        print(f"[WARN] No window matching '{title_substring}' found, falling back to full screen", file=sys.stderr)
        return None

    hwnd, text, rect = result[0]
    print(f"[INFO] Found window: '{text}' at {rect}", file=sys.stderr)

    # Try to bring window to foreground
    try:
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        win32gui.SetForegroundWindow(hwnd)
        import time; time.sleep(0.3)
        rect = win32gui.GetWindowRect(hwnd)
    except Exception as e:
        print(f"[WARN] Could not foreground window: {e}", file=sys.stderr)

    left, top, right, bottom = rect
    return (left, top, right - left, bottom - top)


def main():
    parser = argparse.ArgumentParser(description="Capture screenshot")
    parser.add_argument("--window", "-w", type=str, default=None,
                        help="Window title substring to capture (e.g. 'Unity')")
    parser.add_argument("--output", "-o", type=str, default="c:/tmp/unity_screenshot.png",
                        help="Output file path")
    args = parser.parse_args()

    import pyautogui
    import os
    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)

    region = None
    if args.window:
        region = find_window_rect(args.window)

    if region:
        img = pyautogui.screenshot(region=region)
    else:
        img = pyautogui.screenshot()

    img.save(args.output)
    print(f"[OK] Screenshot saved to {args.output} ({img.size[0]}x{img.size[1]})")


if __name__ == "__main__":
    main()
