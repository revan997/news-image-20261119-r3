"""Draw the front page of THE GLOBAL HERALD for Thursday 19 November 2026.

Pure Python standard library: renders a 1024x1024 newspaper front page into
a PNG (zlib + struct only, no third-party imaging) and writes it to the path
given on the command line (default: entry.png next to this script).

Deterministic: same input always produces the same bytes (fixed layout, fixed
zlib level, no timestamps, no randomness).
"""

import math
import os
import struct
import sys
import zlib

WIDTH = 1024
HEIGHT = 1024

PAPER = (253, 251, 244)
INK = (17, 17, 17)
RED = (178, 34, 34)
GREY = (110, 110, 110)

# ---------------------------------------------------------------- 5x7 font
# Each glyph is 7 rows; each row is a 5-bit int, bit 4 = leftmost column.
FONT = {
    "A": (0b01110, 0b10001, 0b10001, 0b11111, 0b10001, 0b10001, 0b10001),
    "B": (0b11110, 0b10001, 0b10001, 0b11110, 0b10001, 0b10001, 0b11110),
    "C": (0b01110, 0b10001, 0b10000, 0b10000, 0b10000, 0b10001, 0b01110),
    "D": (0b11110, 0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b11110),
    "E": (0b11111, 0b10000, 0b10000, 0b11110, 0b10000, 0b10000, 0b11111),
    "F": (0b11111, 0b10000, 0b10000, 0b11110, 0b10000, 0b10000, 0b10000),
    "G": (0b01110, 0b10001, 0b10000, 0b10111, 0b10001, 0b10001, 0b01111),
    "H": (0b10001, 0b10001, 0b10001, 0b11111, 0b10001, 0b10001, 0b10001),
    "I": (0b01110, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0b01110),
    "J": (0b00111, 0b00010, 0b00010, 0b00010, 0b00010, 0b10010, 0b01100),
    "K": (0b10001, 0b10010, 0b10100, 0b11000, 0b10100, 0b10010, 0b10001),
    "L": (0b10000, 0b10000, 0b10000, 0b10000, 0b10000, 0b10000, 0b11111),
    "M": (0b10001, 0b11011, 0b10101, 0b10101, 0b10001, 0b10001, 0b10001),
    "N": (0b10001, 0b11001, 0b10101, 0b10011, 0b10001, 0b10001, 0b10001),
    "O": (0b01110, 0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b01110),
    "P": (0b11110, 0b10001, 0b10001, 0b11110, 0b10000, 0b10000, 0b10000),
    "Q": (0b01110, 0b10001, 0b10001, 0b10001, 0b10101, 0b10010, 0b01101),
    "R": (0b11110, 0b10001, 0b10001, 0b11110, 0b10100, 0b10010, 0b10001),
    "S": (0b01111, 0b10000, 0b10000, 0b01110, 0b00001, 0b00001, 0b11110),
    "T": (0b11111, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100),
    "U": (0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b01110),
    "V": (0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b01010, 0b00100),
    "W": (0b10001, 0b10001, 0b10001, 0b10101, 0b10101, 0b11011, 0b10001),
    "X": (0b10001, 0b10001, 0b01010, 0b00100, 0b01010, 0b10001, 0b10001),
    "Y": (0b10001, 0b10001, 0b01010, 0b00100, 0b00100, 0b00100, 0b00100),
    "Z": (0b11111, 0b00001, 0b00010, 0b00100, 0b01000, 0b10000, 0b11111),
    "a": (0b00000, 0b00000, 0b01110, 0b00001, 0b01111, 0b10001, 0b01111),
    "b": (0b10000, 0b10000, 0b10110, 0b11001, 0b10001, 0b10001, 0b11110),
    "c": (0b00000, 0b00000, 0b01110, 0b10001, 0b10000, 0b10001, 0b01110),
    "d": (0b00001, 0b00001, 0b01101, 0b10011, 0b10001, 0b10001, 0b01111),
    "e": (0b00000, 0b00000, 0b01110, 0b10001, 0b11111, 0b10000, 0b01110),
    "f": (0b00110, 0b01001, 0b01000, 0b11110, 0b01000, 0b01000, 0b01000),
    "g": (0b00000, 0b01111, 0b10001, 0b10001, 0b01111, 0b00001, 0b01110),
    "h": (0b10000, 0b10000, 0b10110, 0b11001, 0b10001, 0b10001, 0b10001),
    "i": (0b00100, 0b00000, 0b01100, 0b00100, 0b00100, 0b00100, 0b01110),
    "j": (0b00010, 0b00000, 0b00110, 0b00010, 0b00010, 0b10010, 0b01100),
    "k": (0b10000, 0b10000, 0b10010, 0b10100, 0b11000, 0b10100, 0b10010),
    "l": (0b01100, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0b01110),
    "m": (0b00000, 0b00000, 0b11010, 0b10101, 0b10101, 0b10101, 0b10101),
    "n": (0b00000, 0b00000, 0b10110, 0b11001, 0b10001, 0b10001, 0b10001),
    "o": (0b00000, 0b00000, 0b01110, 0b10001, 0b10001, 0b10001, 0b01110),
    "p": (0b00000, 0b00000, 0b10110, 0b11001, 0b10001, 0b11110, 0b10000),
    "q": (0b00000, 0b00000, 0b01101, 0b10011, 0b10001, 0b01111, 0b00001),
    "r": (0b00000, 0b00000, 0b10110, 0b11001, 0b10000, 0b10000, 0b10000),
    "s": (0b00000, 0b00000, 0b01111, 0b10000, 0b01110, 0b00001, 0b11110),
    "t": (0b01000, 0b01000, 0b11100, 0b01000, 0b01000, 0b01001, 0b00110),
    "u": (0b00000, 0b00000, 0b10001, 0b10001, 0b10001, 0b10011, 0b01101),
    "v": (0b00000, 0b00000, 0b10001, 0b10001, 0b10001, 0b01010, 0b00100),
    "w": (0b00000, 0b00000, 0b10001, 0b10101, 0b10101, 0b10101, 0b01010),
    "x": (0b00000, 0b00000, 0b10001, 0b01010, 0b00100, 0b01010, 0b10001),
    "y": (0b00000, 0b00000, 0b10001, 0b10001, 0b01111, 0b00001, 0b01110),
    "z": (0b00000, 0b00000, 0b11111, 0b00010, 0b00100, 0b01000, 0b11111),
    "0": (0b01110, 0b10001, 0b10011, 0b10101, 0b11001, 0b10001, 0b01110),
    "1": (0b00100, 0b01100, 0b00100, 0b00100, 0b00100, 0b00100, 0b01110),
    "2": (0b01110, 0b10001, 0b00001, 0b00110, 0b01000, 0b10000, 0b11111),
    "3": (0b11111, 0b00010, 0b00100, 0b00010, 0b00001, 0b10001, 0b01110),
    "4": (0b00010, 0b00110, 0b01010, 0b10010, 0b11111, 0b00010, 0b00010),
    "5": (0b11111, 0b10000, 0b11110, 0b00001, 0b00001, 0b10001, 0b01110),
    "6": (0b00110, 0b01000, 0b10000, 0b11110, 0b10001, 0b10001, 0b01110),
    "7": (0b11111, 0b00001, 0b00010, 0b00100, 0b01000, 0b01000, 0b01000),
    "8": (0b01110, 0b10001, 0b10001, 0b01110, 0b10001, 0b10001, 0b01110),
    "9": (0b01110, 0b10001, 0b10001, 0b01111, 0b00001, 0b00010, 0b01100),
    " ": (0, 0, 0, 0, 0, 0, 0),
    ".": (0b00000, 0b00000, 0b00000, 0b00000, 0b00000, 0b01100, 0b01100),
    ",": (0b00000, 0b00000, 0b00000, 0b00000, 0b01100, 0b00100, 0b01000),
    ":": (0b00000, 0b01100, 0b01100, 0b00000, 0b01100, 0b01100, 0b00000),
    ";": (0b00000, 0b01100, 0b01100, 0b00000, 0b01100, 0b00100, 0b01000),
    "!": (0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0b00000, 0b00100),
    "?": (0b01110, 0b10001, 0b00001, 0b00010, 0b00100, 0b00000, 0b00100),
    "-": (0b00000, 0b00000, 0b00000, 0b01110, 0b00000, 0b00000, 0b00000),
    "'": (0b00100, 0b00100, 0b01000, 0b00000, 0b00000, 0b00000, 0b00000),
    '"': (0b01010, 0b01010, 0b01010, 0b00000, 0b00000, 0b00000, 0b00000),
    "(": (0b00010, 0b00100, 0b01000, 0b01000, 0b01000, 0b00100, 0b00010),
    ")": (0b01000, 0b00100, 0b00010, 0b00010, 0b00010, 0b00100, 0b01000),
    "/": (0b00001, 0b00010, 0b00010, 0b00100, 0b01000, 0b01000, 0b10000),
    "%": (0b11001, 0b11010, 0b00010, 0b00100, 0b01000, 0b01011, 0b10011),
    "$": (0b00100, 0b01111, 0b10100, 0b01110, 0b00101, 0b11110, 0b00100),
    "&": (0b01100, 0b10010, 0b10100, 0b01000, 0b10101, 0b10010, 0b01101),
    "+": (0b00000, 0b00100, 0b00100, 0b11111, 0b00100, 0b00100, 0b00000),
    "=": (0b00000, 0b00000, 0b11111, 0b00000, 0b11111, 0b00000, 0b00000),
    "|": (0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100),
    "•": (0b00000, 0b00000, 0b01100, 0b01100, 0b01100, 0b00000, 0b00000),
}


class Canvas:
    def __init__(self, width, height, paper):
        self.width = width
        self.height = height
        self.buf = bytearray(paper * (width * height))

    def fill_rect(self, x, y, w, h, color):
        if w <= 0 or h <= 0:
            return
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.width, x + w)
        y1 = min(self.height, y + h)
        if x1 <= x0 or y1 <= y0:
            return
        row = bytes(color) * (x1 - x0)
        stride = self.width * 3
        for yy in range(y0, y1):
            base = yy * stride + x0 * 3
            self.buf[base:base + len(row)] = row

    def hline(self, x, y, w, color, thickness=1):
        self.fill_rect(x, y, w, thickness, color)

    def vline(self, x, y, h, color, thickness=1):
        self.fill_rect(x, y, thickness, h, color)

    def text_width(self, text, scale):
        if not text:
            return 0
        return len(text) * 6 * scale - scale

    def draw_text(self, x, y, text, scale, color):
        cx = x
        for ch in text:
            glyph = FONT.get(ch)
            if glyph is None:
                glyph = FONT["?"]
            for row in range(7):
                bits = glyph[row]
                if bits == 0:
                    continue
                for col in range(5):
                    if bits & (1 << (4 - col)):
                        self.fill_rect(cx + col * scale, y + row * scale,
                                       scale, scale, color)
            cx += 6 * scale

    def draw_centered(self, cx, y, text, scale, color):
        self.draw_text(cx - self.text_width(text, scale) // 2, y, text,
                       scale, color)


def wrap_text(canvas, text, max_width, scale):
    """Greedy word wrap; returns a list of lines fitting max_width px."""
    char_w = 6 * scale
    max_chars = max(1, max_width // char_w)
    lines = []
    for paragraph in text.split("\n"):
        words = paragraph.split(" ")
        line = ""
        for word in words:
            trial = word if not line else line + " " + word
            if len(trial) <= max_chars:
                line = trial
            else:
                if line:
                    lines.append(line)
                # hard-split an over-long single word
                while len(word) > max_chars:
                    lines.append(word[:max_chars])
                    word = word[max_chars:]
                line = word
        if line:
            lines.append(line)
    return lines


def draw_globe(canvas, cx, cy, r, color):
    """Simple wireframe globe: outline, meridians, latitude chords."""
    steps = 360
    for deg in range(steps):
        a = math.radians(deg)
        px = int(round(cx + r * math.cos(a)))
        py = int(round(cy + r * math.sin(a)))
        canvas.fill_rect(px - 1, py - 1, 3, 3, color)
    # meridians (vertical ellipses)
    for rx in (int(r * 0.45), int(r * 0.85)):
        for deg in range(steps):
            a = math.radians(deg)
            px = int(round(cx + rx * math.cos(a)))
            py = int(round(cy + r * math.sin(a)))
            canvas.fill_rect(px, py, 2, 2, color)
    # latitude chords
    for dy in (-r // 2, 0, r // 2):
        half = int(math.sqrt(max(0, r * r - dy * dy)))
        canvas.hline(cx - half, cy + dy, half * 2, color, 2)


# ---------------------------------------------------------------- layout
def render(path):
    c = Canvas(WIDTH, HEIGHT, PAPER)
    left, right = 36, 988
    full_w = right - left

    # Masthead
    c.draw_centered(WIDTH // 2, 26, "THE GLOBAL HERALD", 7, INK)
    c.fill_rect(left, 84, full_w, 4, RED)
    c.hline(left, 92, full_w, INK, 1)

    # Dateline
    c.draw_text(left, 104, "No. 323", 2, GREY)
    c.draw_centered(WIDTH // 2, 104, "THURSDAY, 19 NOVEMBER 2026", 3, INK)
    c.draw_text(right - c.text_width("ONE PAGE", 2), 104, "ONE PAGE", 2, GREY)
    c.hline(left, 134, full_w, INK, 1)

    # ---- Lead story: ICJ Rohingya ruling, with globe art on the right
    lead_x, lead_w = left, 700
    globe_x0, globe_x1 = 776, right
    c.draw_text(lead_x, 150, "THE HAGUE - WORLD COURT", 2, RED)
    y = 176
    for line in wrap_text(c, "WORLD COURT RULES MYANMAR COMMITTED GENOCIDE",
                          lead_w, 4):
        c.draw_text(lead_x, y, line, 4, INK)
        y += 34
    y += 8
    for line in wrap_text(
            c,
            "The International Court of Justice finds Myanmar responsible "
            "for genocide against the Rohingya in its 2017 clearance "
            "operations, and orders restitution.",
            lead_w, 2):
        c.draw_text(lead_x, y, line, 2, INK)
        y += 18
    # Globe box
    c.fill_rect(globe_x0, 150, globe_x1 - globe_x0, 2, INK)
    c.fill_rect(globe_x0, 318, globe_x1 - globe_x0, 2, INK)
    c.fill_rect(globe_x0, 150, 2, 170, INK)
    c.fill_rect(globe_x1 - 2, 150, 2, 170, INK)
    draw_globe(c, (globe_x0 + globe_x1) // 2, 226, 58, INK)
    c.draw_centered((globe_x0 + globe_x1) // 2, 296, "THE WORLD TODAY",
                    2, INK)

    # Divider under the lead
    c.fill_rect(left, 336, full_w, 2, INK)
    c.hline(left, 342, full_w, INK, 1)

    # ---- Middle: two columns, two stories each
    col_w = 464
    mid_x = 512
    c.vline(mid_x, 358, 306, GREY, 1)

    def story(x, y, kicker, headline, deck):
        c.draw_text(x, y, kicker, 2, RED)
        y += 26
        for line in wrap_text(c, headline, col_w, 3):
            c.draw_text(x, y, line, 3, INK)
            y += 26
        y += 4
        for line in wrap_text(c, deck, col_w, 2):
            c.draw_text(x, y, line, 2, INK)
            y += 18
        return y

    story(left, 358, "SHENZHEN - SUMMIT",
          "TRUMP, XI AND PUTIN ISSUE JOINT PEACE DECLARATION",
          "The three leaders meet for the first trilateral summit, but "
          "mention neither Ukraine nor Iran.")
    story(left, 522, "BRUSSELS - EUROPE",
          "EU PROPOSES 45 BILLION EURO LOAN TO UKRAINE",
          "The Commission plan would fund Kyiv as Zelenskyy says a "
          "90 billion euro loan is close.")
    story(mid_x + 12, 358, "NEW YORK - MARKETS",
          "ANTHROPIC IN RECORD 100 BILLION DOLLAR IPO",
          "Shares debut on Nasdaq at about 83 dollars, valuing the AI "
          "developer near 2 trillion dollars.")
    story(mid_x + 12, 522, "STRAIT OF HORMUZ - CONFLICT",
          "TANKER ATTACKS WIDEN AS IRAN STRIKES GULF ALLIES",
          "An ADNOC vessel is hit, leaving 11 crew hurt and one missing, "
          "as Iran strikes Kuwait and Bahrain.")

    # Divider under the middle section
    c.fill_rect(left, 682, full_w, 2, INK)
    c.hline(left, 688, full_w, INK, 1)

    # ---- Also today: three columns, then a second row of briefs
    c.draw_text(left, 704, "ALSO TODAY", 2, RED)
    col3_w = 304
    col3_x = [left, left + 324, left + 648]

    def brief(x, y, head, deck):
        c.draw_text(x, y, head, 2, RED)
        y += 20
        for line in wrap_text(c, deck, col3_w, 2):
            c.draw_text(x, y, line, 2, INK)
            y += 18
        return y

    brief(col3_x[0], 730, "GAZA",
          "Israeli forces cross the ceasefire line as the IDF ends its "
          "Nuseirat operation.")
    brief(col3_x[1], 730, "BANGLADESH",
          "Violence spreads to 28 districts and the Yunus family home "
          "is set on fire.")
    brief(col3_x[2], 730, "ART RECORD",
          "A Van Gogh sells for 190.4 million dollars, a record price "
          "for the artist.")
    y = 832
    for item in (
            "CLIMATE: COP31 ministers race to unblock talks in Antalya.",
            "SCIENCE: Voyager 1 passes one light-day from Earth.",
            "QUAKE: A magnitude 6.0 earthquake strikes Papua New Guinea."):
        c.draw_text(left, y, "• " + item, 2, INK)
        y += 20

    # ---- Markets bar
    c.fill_rect(left, 912, full_w, 30, INK)
    c.draw_centered(WIDTH // 2, 920,
                    "MARKETS: S&P 500 -0.23% | NASDAQ +0.42% | "
                    "BRENT -2.57% | GOLD -0.06%", 2, PAPER)

    # ---- Footer
    c.hline(left, 962, full_w, INK, 1)
    c.draw_centered(WIDTH // 2, 974,
                    "THE GLOBAL HERALD - THURSDAY 19 NOVEMBER 2026 - "
                    "WORLD NEWS IN ONE PAGE", 2, INK)

    write_png(c, path)


def write_png(canvas, path):
    raw = bytearray()
    stride = canvas.width * 3
    for yy in range(canvas.height):
        raw.append(0)  # filter: none
        base = yy * stride
        raw += canvas.buf[base:base + stride]
    comp = zlib.compress(bytes(raw), 9)

    def chunk(kind, data):
        out = struct.pack(">I", len(data)) + kind + data
        out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
        return out

    ihdr = struct.pack(">IIBBBBB", canvas.width, canvas.height, 8, 2, 0, 0, 0)
    png = (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
           + chunk(b"IDAT", comp) + chunk(b"IEND", b""))
    with open(path, "wb") as fh:
        fh.write(png)


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "entry.png")
    render(target)
    print("wrote", target)
