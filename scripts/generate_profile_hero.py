from PIL import Image, ImageDraw, ImageFont
import os, random

W, H = 900, 375
FPS, SECONDS = 6, 3
FRAMES = FPS * SECONDS

def font(size, bold=False):
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationMono-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation2/LiberationMono-Regular.ttf",
    ]
    for path in candidates:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()

f_small = font(10)
f_nav = font(9)
f_term = font(11)
f_term_b = font(11, True)
f_title = font(39, True)
f_sub = font(11)
f_brand = font(12, True)

GREEN = (22, 241, 106)
FG = (235, 248, 238)
DIM = (110, 135, 119)
TERM_DIM = (145, 160, 149)

chars = list("01#$%&*+-<>[]{}ABCDEFGHIJKLMNOPQRSTUVWXYZ")
random.seed(74)
columns = []
for x in range(8, W, 22):
    columns.append((
        x,
        random.uniform(55, 115),
        random.uniform(-H, 0),
        [random.choice(chars) for _ in range(random.randint(8, 16))]
    ))

palette_colors = [
    (2,5,3),(4,10,6),(6,16,9),(10,21,13),(13,48,25),(20,80,38),
    GREEN,(95,120,102),(130,180,142),TERM_DIM,(220,236,224),FG,
    (255,98,88),(255,189,46),(40,200,64),(255,45,95)
]
palette = Image.new("P", (1,1))
flat = []
for c in palette_colors:
    flat.extend(c)
flat += [0] * (768 - len(flat))
palette.putpalette(flat)

frames = []
for fi in range(FRAMES):
    t = fi / FPS
    im = Image.new("RGB", (W, H), (2,5,3))
    d = ImageDraw.Draw(im)

    # Dense Matrix rain.
    for x, speed, offset, seq in columns:
        y0 = (offset + speed * t) % (H + 180) - 160
        for j, ch in enumerate(seq):
            y = y0 + j * 17
            if -20 < y < H + 20:
                color = (20, 80 + min(140, j * 10), 60)
                if j == len(seq) - 1:
                    color = (130,255,165)
                d.text((x, y), ch, font=f_small, fill=color)

    # Header.
    d.line((0, 48, W, 48), fill=(13,48,25))
    d.text((44,20), "~/74Hamed", font=f_brand, fill=GREEN)
    if int(t * 2) % 2 == 0:
        d.rectangle((121,21,128,34), fill=GREEN)
    d.text((622,21), "./about  ./projects  ./skills  ./contact", font=f_nav, fill=(96,114,103))

    # Terminal card.
    tx, ty, tw, th = 195, 69, 510, 188
    d.rounded_rectangle((tx,ty,tx+tw,ty+th), radius=7, fill=(6,16,9), outline=(26,95,50))
    d.rounded_rectangle((tx,ty,tx+tw,ty+29), radius=7, fill=(10,21,13))
    d.line((tx,ty+29,tx+tw,ty+29), fill=(23,54,33))
    for cx, c in [(212,(255,98,88)),(226,(255,189,46)),(240,(40,200,64))]:
        d.ellipse((cx-4,80,cx+4,88), fill=c)
    d.text((255,79), "visitor@portfolio: ~", font=f_nav, fill=(111,131,116))

    y = 113
    entries = [
        ("whoami", "74Hamed - Creative Developer"),
        ("cat focus.txt", "web dev / desktop apps / ui/ux / ai tools"),
        ("./launch_portfolio.sh", "[ OK ] all systems online - scroll to explore v"),
    ]
    for i, (cmd, out) in enumerate(entries):
        d.text((212,y), "$", font=f_term_b, fill=GREEN)
        d.text((229,y), cmd, font=f_term_b, fill=FG)
        d.text((212,y+19), out, font=f_term, fill=(GREEN if i == 2 else TERM_DIM))
        y += 49

    # Hero title.
    d.text((W//2,291), "// hello world, i am", font=f_small, fill=DIM, anchor="mm")
    glitch = (1.15 < t < 1.55) or (2.45 < t < 2.80)
    if glitch:
        d.text((W//2+5,323), "74Hamed", font=f_title, fill=GREEN, anchor="mm")
        d.text((W//2-5,323), "74Hamed", font=f_title, fill=(255,45,95), anchor="mm")
    d.text((W//2,323), "74Hamed", font=f_title, fill=FG, anchor="mm")
    if glitch:
        for _ in range(2):
            yy = random.randint(306,335)
            x1 = random.randint(350,420)
            x2 = random.randint(500,570)
            d.rectangle((x1,yy,x2,yy+1), fill=GREEN)

    d.text(
        (W//2,350),
        "developer & designer crafting websites, desktop apps and UI/UX",
        font=f_sub, fill=(147,164,151), anchor="mm"
    )

    # Moving scanline.
    scan_y = int((t / SECONDS) * (H + 20)) - 10
    d.line((0, scan_y, W, scan_y), fill=(20,80,38))

    frames.append(im.quantize(palette=palette, dither=Image.Dither.NONE))

os.makedirs("assets", exist_ok=True)
frames[0].save(
    "assets/hero.gif",
    save_all=True,
    append_images=frames[1:],
    duration=int(1000 / FPS),
    loop=0,
    optimize=True,
    disposal=2,
)
print("Generated assets/hero.gif")
