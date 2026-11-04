"""Kyro-V version 1. Change CHOOSE at the bottom, then run."""
import math, random, re, time

class KyroError(Exception):
    pass

COLORS = {"black": "#000000", "white": "#ffffff", "red": "#e53935", "orange": "#ff9800", "yellow": "#ffeb3b",
          "gold": "#d4af37", "green": "#43a047", "blue": "#1e88e5", "purple": "#8e24aa", "pink": "#ff4fa3",
          "brown": "#8d5524", "gray": "#9e9e9e", "navy": "#0d1b4c"}
SHAPES = ["square", "rectangle", "door", "triangle", "circle", "star", "heart", "butterfly"]
GLOWS = {"none": 0, "soft": 2, "strong": 3}
PLACES = {"center": (0, 0), "top": (0, 150), "bottom": (0, -150), "left": (-170, 0), "right": (170, 0)}
DESIGN_MOTIONS = ["falling letters", "pulse", "spin", "flap", "fly"]
TEXT_MOTIONS = ["fade in", "rise", "blink", "typing"]
DETAILS = {"design": ["shape", "color", "glow", "text", "background", "motion"],
           "drawing": ["name", "background"], "shape": ["type", "color", "size", "place"],
           "platform": ["name", "theme"], "screen": ["name"], "section": ["name"],
           "video": ["name", "length", "background"], "text": ["content", "motion"]}
STRING = re.compile(r'"([^"]*)"')
PAIR = re.compile(r'([A-Za-z_]+)\s*:\s*((?:"[^"]*"\s*)*)')

class Node:
    def __init__(self, tag, line):
        self.tag, self.line, self.details, self.children = tag, line, {}, []

    def get(self, key, default=""): return self.details.get(key) or default

def add_details(node, text, line):
    text, pos = text.strip(), 0
    while pos < len(text):
        m = PAIR.match(text, pos)
        if not m:
            raise KyroError('Line %d: Cannot read "%s". Use name: "value".'
                            % (line, text[pos:pos + 25]))
        key = m.group(1).lower()
        if key not in DETAILS[node.tag]:
            raise KyroError("Line %d: @%s has no detail '%s'. It has: %s."
                            % (line, node.tag, key, ", ".join(DETAILS[node.tag])))
        node.details[key] = "".join(STRING.findall(m.group(2)))
        pos = m.end()

def parse(source):
    rows = [(n, r.replace("\t", "  ").rstrip()) for n, r in enumerate(source.splitlines(), 1) if r.strip()]
    if len(rows) < 2 or rows[0][1].strip().lower() != "*hey kyro-v*":
        raise KyroError("Start with *Hey kyro-V*.")
    if rows[-1][1].strip().lower() != "*bye kyro-v*":
        raise KyroError("Line %d: end with *bye kyro-V* (star on both sides)." % rows[-1][0])
    root, stack, commands = Node("program", 0), [], []
    for n, row in rows[1:-1]:
        indent, text = len(row) - len(row.lstrip()), row.strip()
        if text[0] == "@":
            m = re.match(r"@([A-Za-z_]+)(.*)$", text)
            tag = m.group(1).lower() if m else ""
            if tag not in DETAILS:
                raise KyroError("Line %d: Unknown @%s. Known: %s."
                                % (n, tag, ", ".join("@" + t for t in DETAILS)))
            if m.group(2).strip().startswith(":"):
                raise KyroError("Line %d: no colon after @%s." % (n, tag))
            node = Node(tag, n)
            add_details(node, m.group(2), n)
            while stack and stack[-1][0] >= indent:
                stack.pop()
            (stack[-1][1] if stack else root).children.append(node)
            stack.append((indent, node))
        elif text[0] == "$":
            m = re.match(r"\$\s*([A-Za-z_]+)\s*(.*)$", text)
            if not m:
                raise KyroError("Line %d: $ needs a command." % n)
            commands.append((n, m.group(1).lower(), "".join(STRING.findall(m.group(2)))))
        elif text[0] == "*":
            raise KyroError("Line %d: * is only for the start and end." % n)
        else:
            while stack and stack[-1][0] >= indent:
                stack.pop()
            if not stack:
                raise KyroError("Line %d: put details under an @ thing." % n)
            add_details(stack[-1][1], text, n)
    return root.children, commands

def color(name, line):
    found = COLORS.get(name.strip().lower())
    if found is None:
        raise KyroError("Line %d: Unknown color '%s'. Colors: %s." % (line, name, ", ".join(COLORS)))
    return found

def rgb(c):
    return [int(c[i:i + 2], 16) for i in (1, 3, 5)]

def blend(a, b, amount):
    x, y, k = rgb(a), rgb(b), max(0.0, min(1.0, amount))
    return "#%02x%02x%02x" % tuple(round(x[i] * (1 - k) + y[i] * k) for i in range(3))

def number(text, default, line):
    try:
        return float(text) if text else default
    except ValueError:
        raise KyroError('Line %d: "%s" must be a number.' % (line, text))

def motions(text, allowed, line):
    rest, found = (text or "").lower(), []
    for name in sorted(allowed, key=len, reverse=True):
        if name in rest:
            found.append(name)
            rest = rest.replace(name, " ")
    left = [w for w in rest.split() if w != "none"]
    if left:
        raise KyroError("Line %d: Unknown motion '%s'. Motions: %s."
                        % (line, " ".join(left), ", ".join(allowed)))
    return found

def span(pts):
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    return max(xs) - min(xs), max(ys) - min(ys), (max(xs) + min(xs)) / 2, (max(ys) + min(ys)) / 2

def fit(pts, size):
    w, h, mx, my = span(pts)
    return [((x - mx) * size / max(w, h), (y - my) * size / max(w, h)) for x, y in pts]

def points(kind, size, line):
    kind, h = kind.strip().lower(), size / 2.0
    if kind not in SHAPES:
        raise KyroError("Line %d: Unknown shape '%s'. Shapes: %s." % (line, kind, ", ".join(SHAPES)))
    if kind == "square":
        return [(-h, -h), (h, -h), (h, h), (-h, h)]
    if kind == "rectangle":
        return [(-h, -h * .6), (h, -h * .6), (h, h * .6), (-h, h * .6)]
    if kind == "door":
        return [(-h * .6, -h), (h * .6, -h), (h * .6, h), (-h * .6, h)]
    if kind == "triangle":
        return [(-h, -h * .7), (h, -h * .7), (0, h * .7)]
    if kind == "circle":
        return [(h * math.cos(math.pi * i / 20), h * math.sin(math.pi * i / 20)) for i in range(40)]
    if kind == "star":
        radii = [(h if i % 2 == 0 else h * .42, math.pi / 2 + i * math.pi / 5) for i in range(10)]
        return [(r * math.cos(a), r * math.sin(a)) for r, a in radii]
    pts = []
    for i in range(60 if kind == "heart" else 300):
        if kind == "heart":
            t = 2 * math.pi * i / 60
            pts.append((16 * math.sin(t) ** 3, 13 * math.cos(t) - 5 * math.cos(2 * t)
                        - 2 * math.cos(3 * t) - math.cos(4 * t)))
        else:
            t = 24 * math.pi * i / 300
            r = math.exp(math.sin(t)) - 2 * math.cos(4 * t) + math.sin((2 * t - math.pi) / 24) ** 5
            pts.append((r * math.sin(t), r * math.cos(t)))
    return fit(pts, size)

def move(pts, sx, sy, angle, dx, dy):
    c, s = math.cos(math.radians(angle)), math.sin(math.radians(angle))
    return [(x * sx * c - y * sy * s + dx, x * sx * s + y * sy * c + dy) for x, y in pts]

def place(text, line, prev, w, h):
    key = (text or "center").strip().lower()
    nums = re.findall(r"-?\d+(?:\.\d+)?", key)
    if key in PLACES:
        return PLACES[key]
    if key in ("on top", "below", "inside bottom"):
        if not prev:
            raise KyroError("Line %d: '%s' needs a shape before it." % (line, key))
        px, py, pw, ph = prev
        if key == "on top":
            return px, py + ph / 2 + h / 2
        return (px, py - ph / 2 - h / 2) if key == "below" else (px, py - ph / 2 + h / 2)
    if len(nums) == 2:
        return float(nums[0]), float(nums[1])
    raise KyroError("Line %d: Unknown place '%s'. Use %s, on top, below, inside bottom, or two numbers."
                    % (line, text, ", ".join(PLACES)))

class Screen:
    def __init__(self):
        import turtle
        self.module, self.screen, self.pen = turtle, turtle.Screen(), turtle.Turtle()
        self.screen.tracer(0)
        self.pen.hideturtle()
        self.pen.speed(0)
        self.pen.penup()
        self.bg, self.closed = COLORS["black"], False
        self.width, self.height = self.screen.window_width(), self.screen.window_height()
        try:
            self.ppp = 72.0 / float(self.screen.getcanvas().winfo_fpixels("1i"))
        except Exception:
            self.ppp = 0.75

    def background(self, c):
        self.bg = c
        self.screen.bgcolor(c)

    def clear(self): self.pen.clear()

    def polygon(self, pts, fill=None, outline=None, width=1):
        pen = self.pen
        pen.penup()
        pen.goto(pts[0][0], pts[0][1])
        pen.pensize(width)
        pen.pencolor(outline or fill)
        if fill:
            pen.fillcolor(fill)
            pen.begin_fill()
        pen.pendown()
        for x, y in pts[1:] + [pts[0]]:
            pen.goto(x, y)
        pen.penup()
        if fill:
            pen.end_fill()

    def text(self, words, x, y, c, size):
        self.pen.penup()
        self.pen.goto(x, y)
        self.pen.pencolor(c)
        self.pen.write(words, align="center", font=("Arial", max(1, int(round(size * self.ppp))), "bold"))

    def update(self): self.screen.update()

    def finish(self):
        self.screen.update()
        self.module.done()

def draw_drawing(screen, node):
    screen.background(color(node.get("background", "white"), node.line))
    screen.clear()
    prev = None
    for s in node.children:
        if s.tag != "shape":
            raise KyroError("Line %d: only @shape goes in @drawing." % s.line)
        pts = points(s.get("type"), number(s.get("size"), 100, s.line), s.line)
        w, h = span(pts)[:2]
        x, y = place(s.get("place"), s.line, prev, w, h)
        prev = (x, y, w, h)
        screen.polygon(move(pts, 1, 1, 0, x, y), fill=color(s.get("color", "black"), s.line))
    screen.update()

def make_design(node):
    glow = node.get("glow", "none").lower()
    if glow not in GLOWS:
        raise KyroError("Line %d: Unknown glow '%s'. Glows: %s." % (node.line, glow, ", ".join(GLOWS)))
    return {"pts": points(node.get("shape", "heart"), 170, node.line), "glow": GLOWS[glow],
            "color": color(node.get("color", "pink"), node.line), "text": node.get("text"),
            "bg": color(node.get("background", "black"), node.line),
            "motion": motions(node.get("motion"), DESIGN_MOTIONS, node.line)}

def paint_rain(screen, c, t):
    cols = max(4, min(8, int(screen.width // 80)))
    span_, chars = screen.height + 220, "01ABCDEFGHIJKLMNOPQRSTUVWXYZ$#@%*+"
    for i in range(cols):
        rng = random.Random(i * 97 + 11)
        speed, offset = 70 + rng.random() * 80, rng.random() * span_
        for r in range(5):
            y = screen.height / 2 + 40 - (t * speed + offset - r * 34) % span_
            screen.text(chars[(i * 7 + r * 3 + int(t * 3)) % len(chars)],
                        -screen.width / 2 + screen.width / (cols + 1.0) * (i + 1), y,
                        blend(screen.bg, c, 0.8 if r == 0 else max(0.15, 0.5 - r * 0.09)), 22)

def paint_shape(screen, d, t):
    m, sx, sy, angle, dx, dy = d["motion"], 1.0, 1.0, 0.0, 0.0, 0.0
    if "pulse" in m:
        sx = sy = 1 + 0.1 * math.sin(2 * math.pi * 1.1 * t)
    if "spin" in m:
        angle = 90 * t
    if "flap" in m or "fly" in m:
        sx *= 0.25 + 0.75 * abs(math.cos(2 * math.pi * 1.2 * t))
    if "fly" in m:
        dx, dy = 70 * math.sin(0.4 * math.pi * t), 22 * math.sin(math.pi * t)
    pts, g = move(d["pts"], sx, sy, angle, dx, 70 + dy), d["glow"]
    for k in range(g, 0, -1):
        screen.polygon(pts, width=k * 8, outline=blend(screen.bg, d["color"], 0.5 * (g - k + 1) / (g + 1.0)))
    screen.polygon(pts, fill=d["color"])

def paint_text(screen, words, m, t, y):
    amount = min(1.0, t / 2.0)
    if "typing" in m:
        words = words[:int(t * 8)]
    if "rise" in m:
        y -= 80 * (1 - amount)
    if "fade in" not in m and "rise" not in m:
        amount = 1.0
    if words and not ("blink" in m and int(t * 2) % 2 == 1):
        screen.text(words, 0, y, blend(screen.bg, COLORS["white"], amount), 34)

def paint_design(screen, d, t):
    if "falling letters" in d["motion"]:
        paint_rain(screen, d["color"], t)
    paint_shape(screen, d, t)
    if d["text"]:
        screen.text(d["text"], 0, -190, COLORS["white"], 34)

def make_video(node):
    designs = [make_design(c) for c in node.children if c.tag == "design"]
    texts = [c for c in node.children if c.tag == "text"]
    if not designs and not texts:
        raise KyroError("Line %d: a @video needs a @design or @text." % node.line)
    y = -20 if not designs else (-250 if any(d["text"] for d in designs) else -190)
    for c in texts:
        if not c.get("content"):
            raise KyroError("Line %d: this @text needs content." % c.line)
    m = re.search(r"\d+(?:\.\d+)?", node.get("length"))
    length = float(m.group()) if m else 10.0
    if not 0 < length <= 60:
        raise KyroError("Line %d: length must be 1 to 60 seconds." % node.line)
    return {"name": node.get("name", "video"), "designs": designs, "length": length,
            "bg": color(node.get("background", "black"), node.line),
            "texts": [(c.get("content"), motions(c.get("motion"), TEXT_MOTIONS, c.line), y - 60 * i)
                      for i, c in enumerate(texts)]}

def paint_video(screen, v, t):
    for d in v["designs"]:
        paint_design(screen, d, t)
    for words, m, y in v["texts"]:
        paint_text(screen, words, m, t, y)

def animate(screen, frame, length):
    start = time.time()
    try:
        while True:
            t, began = time.time() - start, time.time()
            if length is not None and t > length:
                break
            screen.clear()
            frame(t)
            screen.update()
            time.sleep(max(0, 1.0 / 15 - (time.time() - began)))
    except Exception as problem:
        if isinstance(problem, KyroError) or type(problem).__name__ not in ("Terminator", "TclError"):
            raise
        screen.closed = True

def draw_platform(screen, node):
    found = [COLORS[w] for w in re.findall(r"[a-z]+", node.get("theme").lower()) if w in COLORS]
    bg = found[0] if found else COLORS["black"]
    dark = bg != COLORS["white"]
    accent = found[1] if len(found) > 1 else (COLORS["gold"] if dark else COLORS["navy"])
    screen.background(bg)
    screen.clear()
    w, h, top = screen.width, screen.height, screen.height / 2 - 110
    screen.text(node.get("name", "Platform"), 0, h / 2 - 75, accent, 32)
    cols = 2 if len(node.children) > 1 else 1
    cw = min(300, (w - 40 - 24 * (cols - 1)) / cols)
    for start in range(0, len(node.children), cols):
        row = node.children[start:start + cols]
        hs = [84 + max(1, len(s.children)) * 56 for s in row]
        for i, s in enumerate(row):
            x = -(len(row) * cw + (len(row) - 1) * 24) / 2 + i * (cw + 24)
            box = lambda x0, y0, w0, h0: [(x0, y0), (x0 + w0, y0), (x0 + w0, y0 - h0), (x0, y0 - h0)]
            screen.polygon(box(x, top, cw, hs[i]), fill=blend(bg, accent, 0.12), outline=accent, width=2)
            screen.text(s.get("name", "Screen"), x + cw / 2, top - 42, accent, 22)
            for j, sec in enumerate(s.children):
                y = top - 60 - j * 56
                screen.polygon(box(x + 14, y, cw - 28, 44), outline=accent)
                screen.text(sec.get("name", "Section"), x + cw / 2, y - 30, "#ffffff" if dark else "#111111", 18)
        top -= max(hs) + 24
    screen.update()

def execute(nodes, commands):
    box = []

    def screen():
        if not box:
            box.append(Screen())
        return box[0]

    if not commands:
        print("Nothing to do. Add a command like $show before *bye kyro-V*.")
    for line, command, argument in commands:
        if box and box[0].closed:
            break
        if command == "show":
            for node in nodes:
                if node.tag == "drawing":
                    draw_drawing(screen(), node)
                elif node.tag == "platform":
                    draw_platform(screen(), node)
                elif node.tag == "design":
                    d = make_design(node)
                    screen().background(d["bg"])
                    if d["motion"]:
                        print("Moving design. Close the window to stop it.")
                        animate(box[0], lambda t: paint_design(box[0], d, t), None)
                    else:
                        box[0].clear()
                        paint_design(box[0], d, 0)
                        box[0].update()
        elif command == "play":
            for node in [n for n in nodes if n.tag == "video"]:
                v = make_video(node)
                screen().background(v["bg"])
                print('Playing "%s" (%g seconds)...' % (v["name"], v["length"]))
                animate(box[0], lambda t: paint_video(box[0], v, t), v["length"])
        elif command == "save":
            for node in [n for n in nodes if n.tag == "video"]:
                if "save_gif" in globals():
                    save_gif(make_video(node), argument)
                else:
                    print("Saving videos needs the saving add-on (not pasted).")
        else:
            raise KyroError("Line %d: Unknown command $%s." % (line, command))
    if box and not box[0].closed:
        box[0].finish()

def run(source):
    try:
        execute(*parse(source))
    except KyroError as problem:
        print("Kyro-V says: %s" % problem)

EXAMPLES = {
    "house": """
*Hey kyro-V*
@drawing name: "House"
  @shape type: "square" color: "brown" size: "120" place: "center"
  @shape type: "door" color: "gold" size: "60" place: "inside bottom"
  @shape type: "triangle" color: "red" size: "140" place: "on top"
$show
*bye kyro-V*
""",
    "heart": """
*Hey kyro-V*
@design
  shape: "heart"
  color: "pink"
  glow: "strong"
  text: "LOVE YOU"
  motion: "pulse falling letters"
$show
*bye kyro-V*
""",
    "butterfly": """
*Hey kyro-V*
@design
  shape: "butterfly"
  color: "orange"
  glow: "soft"
  text: "FLY"
  background: "navy"
  motion: "fly"
$show
*bye kyro-V*
""",
    "platform": """
*Hey kyro-V*
@platform name: "VIBE GRAM"
  theme: "black and gold"
  @screen name: "Home"
    @section name: "Feed"
    @section name: "Menu"
  @screen name: "Profile"
    @section name: "Photo"
    @section name: "Details"
$show
*bye kyro-V*
""",
    "video": """
*Hey kyro-V*
@video name: "Love"
  length: "6 seconds"
  @design
    shape: "heart"
    color: "pink"
    glow: "strong"
    motion: "pulse falling letters"
  @text
    content: "LOVE YOU"
    motion: "fade in"
$play
*bye kyro-V*
""",
    "mine": """
*Hey kyro-V*
@design
  shape: "star"
  color: "gold"
  glow: "soft"
  text: "MY FIRST KYRO-V"
  background: "navy"
  motion: "spin"
$show
*bye kyro-V*
""",
}

# ADD-ON GOES HERE (optional)
CHOOSE = "mine"    # house, heart, butterfly, platform, video or mine
print("Kyro-V is starting: " + CHOOSE)
run(EXAMPLES[CHOOSE])
print("Kyro-V finished.")
