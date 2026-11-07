"""One illustration per verse of the Hanuman Chalisa, composed from the verse's
bhāva (reflection) and meaning. Each entry: id -> (caption, draw function)."""
import math
from lib import *

GOLD = "#ebb84c"
SAFFRON = "#e0601e"
SCENES = {}


def scene(vid, caption):
    def deco(fn):
        SCENES[vid] = (caption, fn)
        return fn
    return deco


def dawn(S):
    sky(S, [(0, "#2a1740"), (0.35, "#7d3460"), (0.62, "#e7774a"), (0.82, "#f8b65a"), (1, "#ffe6aa")])


def golden(S):
    sky(S, [(0, "#f3a24a"), (0.45, "#f9cf79"), (1, "#fff1cf")])


def night(S):
    sky(S, [(0, "#070a1f"), (0.5, "#172452"), (1, "#3a3a76")])


def dusk(S):
    sky(S, [(0, "#1f1436"), (0.4, "#5b2652"), (0.7, "#c2492e"), (1, "#f39a3d")])


def celestial(S):
    sky(S, [(0, "#140d33"), (0.4, "#3f2a74"), (0.75, "#b07ac9"), (1, "#ffdcb8")])


def fire_sky(S):
    sky(S, [(0, "#1a0505"), (0.45, "#5e1208"), (0.75, "#c53b12"), (1, "#ffad3b")])


# ───────────── Opening dohas ─────────────

@scene("d1", "The mind made a mirror, cleansed by the dust of the Guru's lotus feet")
def d1(S):
    sky(S, [(0, "#3b1d4f"), (0.45, "#c25b6b"), (0.75, "#f6b26b"), (1, "#fde8c0")])
    mandala(S, 300, 300, 230, "#ffe3a8", 0.35, 20)
    sun(S, 300, 300, 46, rays=True, ray_a=0.3)
    # mirror
    S.add(f'<ellipse cx="300" cy="470" rx="98" ry="128" fill="{S.lin([(0, "#fff7e2"), (0.5, "#f6c98a"), (1, "#e48a5c")])}"/>')
    # reflection inside the mirror: a dawn and a lotus
    clip = S.uid("c")
    S.defs.append(f'<clipPath id="{clip}"><ellipse cx="300" cy="470" rx="92" ry="122"/></clipPath>')
    S.add(f'<g clip-path="url(#{clip})">')
    glow(S, 300, 470, 120, "#ffffff", 0.9)
    lotus(S, 300, 540, 1.25, "#fbd3dc", "#e87d98", "#6aa07a")
    S.add("</g>")
    S.add(f'<ellipse cx="300" cy="470" rx="98" ry="128" fill="none" stroke="{GOLD}" stroke-width="9"/>',
          f'<ellipse cx="300" cy="470" rx="108" ry="138" fill="none" stroke="{GOLD}" stroke-width="1.5" opacity=".7"/>',
          f'<path d="M290,598 L310,598 L316,680 L284,680 Z" fill="{GOLD}"/>')
    # the Guru's feet on a lotus
    lotus_seat(S, 300, 790, 1.5, "#f8c9a0", "#c86a3a")
    footprints(S, 300, 762, 1.25, "#f3d2b8")
    # pollen drifting up to the mirror
    for i in range(70):
        t = S.r.random()
        x = 300 + S.r.uniform(-60, 60) * (1 - t) + S.r.uniform(-90, 90) * t
        y = 760 - t * 240
        S.add(f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(S.r.uniform(0.8, 2.6))}" fill="#ffe89e" opacity="{f(0.3 + 0.6 * S.r.random())}"/>')
    vignette(S, 0.35)


@scene("d2", "A humble seeker calls on the Son of the Wind for strength, wisdom and knowledge")
def d2(S):
    dusk(S)
    stars(S, 50, 0, 300)
    for y, a in ((180, 0.45), (250, 0.35), (330, 0.3)):
        wind(S, y, "#ffd9a0", a, 2)
    figure(S, "fly", 360, 300, 2.1, 1, fill="#2a0f1c", glowc="#ffcf88")
    gada(S, (360 + 2.1 * 48, 300 - 2.1 * 50), -0.3, 2.1)
    ridge(S, 760, 600, "#4a1d2b", 6, seed=3)
    ridge(S, 900, 700, "#2a0f18", 5, seed=8)
    figure(S, "kneel", 210, 760, 1.3, 1, "person", fill="#170811", accent=None)
    for i, x in enumerate((270, 300, 330)):
        diya(S, x, 772, 0.55, glow_r=3)
    vignette(S, 0.4)


# ───────────── Chaupais ─────────────

@scene("c1", "Ocean of wisdom and virtue, lighting all three worlds")
def c1(S):
    sky(S, [(0, "#0e1340"), (0.3, "#3a3a8a"), (0.55, "#f19a5b"), (0.62, "#ffd28a"), (1, "#0d3554")])
    stars(S, 60, 0, 230)
    beams(S, 300, 520, 18, 700, "#ffe7b0", 0.09)
    ocean(S, 540, "#1b5b7a", "#082236", "#bfe6ff", 0.4)
    glow(S, 300, 520, 300, "#ffd690", 0.6)
    S.add(f'<path d="M200,640 Q300,600 400,640 L420,700 L180,700 Z" fill="#0c1a26"/>')
    figure(S, "stand", 300, 640, 2.4, 1, fill="#120a12", halo="#ffe0a0")
    gada(S, (300 + 2.4 * 12, 640 - 2.4 * 49), -1.9, 2.4)
    mandala(S, 300, 640 - 2.4 * 90, 70, "#ffe6b0", 0.5, 12)
    vignette(S, 0.4)


@scene("c2", "Rāma's messenger, home of matchless strength, son of Añjanī and the Wind")
def c2(S):
    sky(S, [(0, "#5a3c7a"), (0.5, "#e7a26a"), (1, "#ffe6b5")])
    sun(S, 300, 330, 60, ray_a=0.25)
    for y in (220, 280, 420):
        wind(S, y, "#fff2d4", 0.4)
    ridge(S, 720, 560, "#a2566a", 7, seed=11, a=0.7)
    ridge(S, 900, 700, "#3d1a2c", 6, seed=12)
    figure(S, "bless", 390, 760, 2.3, -1, "rama", fill="#1d2a52", accent=SAFFRON)
    bow(S, (390 + 2.3 * 9, 760 - 2.3 * 50), 2.3, GOLD, face=-1)
    figure(S, "kneel_offer", 200, 760, 2.0, 1, fill="#2a0f18")
    ring(S, 200 + 2.0 * 22, 760 - 2.0 * 62, 5)
    vignette(S, 0.35)


@scene("c3", "The thunderbolt-bodied hero scatters the clouds of bad thinking")
def c3(S):
    sky(S, [(0, "#0d0b1e"), (0.5, "#32244a"), (0.8, "#e88a3f"), (1, "#ffe0a0")])
    glow(S, 300, 640, 360, "#ffd38a", 0.75)
    beams(S, 300, 640, 22, 760, "#ffe9b8", 0.08)
    cloudbank(S, 120, "#1a1428", 1, 1.8, 6, seed=5)
    cloudbank(S, 210, "#2a2140", 0.95, 1.5, 6, seed=6)
    lightning(S, 120, 60, 200, seed=2)
    lightning(S, 470, 40, 170, seed=9)
    ridge(S, 900, 760, "#1d0d10", 5, seed=4)
    figure(S, "giant", 300, 790, 3.2, 1, fill="#1d0b0f")
    gada(S, (300 + 3.2 * 17, 790 - 3.2 * 104), -1.35, 3.2)
    vignette(S, 0.35)


@scene("c4", "His golden form, earrings swaying, curls framing his face")
def c4(S):
    sky(S, [(0, "#5a1d1d"), (0.45, "#b2402a"), (1, "#f1a24a")])
    mandala(S, 300, 420, 260, "#ffe2a0", 0.4, 24)
    mandala(S, 300, 420, 180, "#ffd780", 0.5, 16)
    glow(S, 300, 420, 260, "#ffd68a", 0.7)
    gold_fill = S.lin([(0, "#fff1b8"), (0.4, "#f2b53c"), (1, "#a8601a")], 0, 150, 0, 820, user=True)
    figure(S, "namaste", 300, 800, 5.0, 1, fill=gold_fill, gold="#fff3c8", accent="#b5281b")
    # curls around the crown
    for i in range(9):
        a = math.radians(200 + i * 18)
        cx, cy = 300 + 5.0 + 58 * math.cos(a), 800 - 5.0 * 90 + 50 * math.sin(a)
        swirl(S, cx, cy, 9, "#7a3a0e", 0.7, 2.2, 1.2)
    lotus_seat(S, 300, 820, 2.4, "#f7c27a", "#9a4a1a")
    particles(S, 60, color="#fff0b8")
    vignette(S, 0.35)


@scene("c5", "Thunderbolt and banner in his hands; the sacred thread across his shoulder")
def c5(S):
    sky(S, [(0, "#a0361c"), (0.5, "#ef8a3a"), (1, "#ffe0a0")])
    sun(S, 300, 520, 140, rays=True, ray_a=0.22, n=48)
    ridge(S, 900, 780, "#5a1d10", 5, seed=21)
    figure(S, "guard", 270, 800, 4.6, 1, fill="#2a0e0a")
    gada(S, (270 + 4.6 * 17, 800 - 4.6 * 50), -1.57, 4.6)
    banner(S, (270 - 4.6 * 7, 800 - 4.6 * 50), 4.6, "#ff7a22", GOLD, flip=-1, L=78)
    vignette(S, 0.3)


@scene("c6", "Born of Śiva's essence, beloved son of Kesarī")
def c6(S):
    night(S)
    stars(S, 120, 0, 520)
    moon(S, 430, 150, 46)
    peak(S, 300, 640, 560, 420, "#2d3a6a", "#e8ecff")
    S.add(f'<g stroke="#cfd6ff" stroke-width="5" opacity=".35" fill="none" stroke-linecap="round"><path d="M300,220 L300,320"/><path d="M280,230 Q280,256 300,262 Q320,256 320,230"/></g>')
    ridge(S, 900, 640, "#141a36", 6, seed=31)
    figure(S, "dhyana", 300, 840, 3.2, 1, fill="#0a0d1e", glowc="#8fa0ff")
    vignette(S, 0.4)


@scene("c7", "Learned and wise, he studied at the Sun's own feet")
def c7(S):
    golden(S)
    sun(S, 360, 340, 120, rays=True, ray_a=0.35, n=48)
    cloudbank(S, 700, "#fff4dc", 0.85, 1.6, 6, hi="#f0c27a", seed=7)
    cloudbank(S, 800, "#ffe8c0", 0.9, 1.9, 6, hi="#e9b46a", seed=8)
    figure(S, "fly_back", 170, 640, 2.4, 1, fill="#5a2510")
    palm_leaf(S, 170 + 2.4 * 40, 640 - 2.4 * 62, 42, 12, ang=-20)
    vignette(S, 0.2)


@scene("c8", "Delighting in Rāma's story; Rāma, Lakṣmaṇa and Sītā dwell in his heart")
def c8(S):
    sky(S, [(0, "#120b20"), (0.6, "#3a1b3a"), (1, "#8a3a2a")])
    stars(S, 40, 0, 200)
    cloud(S, 300, 300, 3.0, "#f8e4c2", 0.18)
    glow(S, 300, 290, 220, "#ffd690", 0.6)
    figure(S, "bless", 300, 380, 1.5, 1, "rama", fill="#2a3f7a", accent=SAFFRON)
    figure(S, "stand", 340, 380, 1.35, -1, "sita", fill="#8a2236")
    figure(S, "stand", 255, 380, 1.45, 1, "lakshmana", fill="#3a3a5a", accent=SAFFRON)
    bow(S, (255 + 1.45 * 12, 380 - 1.45 * 49), 1.45)
    S.add('<path d="M120,830 L480,830 L470,850 L130,850 Z" fill="#2a1410"/>')
    figure(S, "seated", 300, 820, 3.0, 1, fill="#1a0b0d")
    for x in (150, 450):
        diya(S, x, 830, 0.8, glow_r=4)
    particles(S, 40, 100, 150, 500, 450, "#ffe6a8")
    vignette(S, 0.4)


@scene("c9", "Tiny before Mother Sītā; vast and fearsome before burning Laṅkā")
def c9(S):
    fire_sky(S)
    figure(S, "giant", 410, 600, 4.6, -1, fill="#1a0505", tail_fire=True)
    city(S, 640, -10, 610, "#200606", burning=True, seed=9, hmin=50, hmax=180)
    S.add(f'<rect x="0" y="640" width="600" height="260" fill="{S.lin([(0, "#2a0a06"), (1, "#0d0303")])}"/>')
    glow(S, 170, 760, 170, "#ffcf7a", 0.35)
    tree(S, 170, 880, 1.6, "#140806", kind="ashoka", flowers="#e8552e", seed=4)
    figure(S, "sit_bless", 200, 870, 0.9, -1, "sita", fill="#3a0e18", halo="#ffd380")
    figure(S, "namaste", 150, 700, 0.42, 1, fill="#120505")
    vignette(S, 0.35)


@scene("c10", "In mighty form he struck down the demons, and completed Rāma's work")
def c10(S):
    sky(S, [(0, "#14060e"), (0.5, "#5a1420"), (0.85, "#d6491c"), (1, "#f3a03a")])
    glow(S, 300, 520, 360, "#ff9a3a", 0.55)
    ridge(S, 900, 700, "#22080c", 7, seed=10)
    figure(S, "giant", 300, 760, 4.0, 1, fill="#1a050a")
    gada(S, (300 + 4.0 * 17, 760 - 4.0 * 104), -1.0, 4.0)
    for (x, s, fc) in ((80, 1.1, 1), (140, 0.9, 1), (500, 1.0, -1), (560, 0.8, -1), (40, 0.7, 1)):
        figure(S, "run", x, 850, s, -fc, "rakshasa", fill="#0d0306")
    particles(S, 50, color="#ffb35a", rmax=2)
    vignette(S, 0.4)


@scene("c11", "He brought the whole mountain of Sañjīvanī, and Rāma held him to his heart")
def c11(S):
    night(S)
    stars(S, 110, 0, 600)
    full_moon(S, 470, 140, 44)
    ridge(S, 900, 760, "#0b1026", 7, seed=22)
    # the mountain, aglow with healing herbs
    fx, fy, s = 230, 600, 2.4
    J = figure(S, "fly_carry", fx, fy, s, 1, fill="#0b0d1c")
    mx, my = J["hr"]
    glow(S, mx, my - 70, 190, "#9cffc0", 0.5)
    S.add(f'<path d="M{f(mx - 110)},{f(my + 4)} L{f(mx - 60)},{f(my - 90)} L{f(mx - 20)},{f(my - 60)} L{f(mx + 10)},{f(my - 140)} L{f(mx + 60)},{f(my - 70)} L{f(mx + 110)},{f(my + 4)} Q{f(mx)},{f(my + 30)} {f(mx - 110)},{f(my + 4)} Z" fill="#1d3a3a"/>')
    for _ in range(60):
        x = mx + S.r.uniform(-90, 90)
        y = my - S.r.uniform(0, 110) * (1 - abs(x - mx) / 120)
        S.add(f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(S.r.uniform(1.2, 3.6))}" fill="#c9ffb0" opacity="{f(S.r.uniform(0.5, 1))}"/>')
    hut(S, 470, 850, 0.8, "#060812", glow_c="#ffbf55")
    vignette(S, 0.4)


@scene("c12", "'As dear to me as my brother Bharata' — the Lord embraces his devotee")
def c12(S):
    sky(S, [(0, "#4a2350"), (0.5, "#d47b5a"), (1, "#ffe0b0")])
    mandala(S, 300, 420, 240, "#fff0c8", 0.4, 20)
    glow(S, 300, 460, 280, "#ffe4a8", 0.75)
    figure(S, "embrace", 260, 790, 3.4, 1, "rama", fill="#22356a", accent=SAFFRON)
    figure(S, "namaste", 345, 790, 3.0, -1, fill="#3a1414")
    lotus_seat(S, 300, 805, 2.8, "#f6c58a", "#a8582a")
    # Bharata's devotion: the Lord's sandals placed on the throne
    paduka(S, 110, 820, 0.9)
    glow(S, 110, 815, 60, "#ffd88a", 0.6)
    particles(S, 50, color="#fff3c8")
    vignette(S, 0.3)


@scene("c13", "'May the thousand-mouthed Śeṣa sing your glory!'")
def c13(S):
    celestial(S)
    stars(S, 80, 0, 400)
    # Śeṣa's hood of many heads
    cx, cy = 300, 420
    glow(S, cx, cy - 60, 320, "#d8c0ff", 0.4)
    hood = []
    n = 13
    for i in range(n):
        a = math.radians(-165 + i * (150 / (n - 1)))
        hx, hy = cx + 200 * math.cos(a), cy + 200 * math.sin(a) + 40
        hood.append((hx, hy))
        S.add(f'<path d="M{f(cx)},{f(cy + 120)} Q{f((cx + hx) / 2)},{f((cy + hy) / 2 + 40)} {f(hx)},{f(hy)}" stroke="#2c6a5a" stroke-width="26" fill="none" stroke-linecap="round"/>')
    for (hx, hy) in hood:
        S.add(f'<ellipse cx="{f(hx)}" cy="{f(hy)}" rx="22" ry="17" fill="#3a8a6e"/>',
              f'<circle cx="{f(hx - 7)}" cy="{f(hy - 3)}" r="2.6" fill="#ffe08a"/><circle cx="{f(hx + 7)}" cy="{f(hy - 3)}" r="2.6" fill="#ffe08a"/>',
              f'<path d="M{f(hx - 4)},{f(hy + 10)} l-3,10 M{f(hx + 4)},{f(hy + 10)} l3,10" stroke="#ff6a5a" stroke-width="1.4"/>')
    ocean(S, 700, "#e9d7ff", "#a68ed6", "#ffffff", 0.6)
    figure(S, "embrace", 260, 780, 2.8, 1, "rama", fill="#1c2452", accent=SAFFRON)
    figure(S, "namaste", 330, 780, 2.5, -1, fill="#2a1430")
    # music notes rising (the hymn of praise)
    for i in range(14):
        x, y = S.r.uniform(80, 520), S.r.uniform(120, 520)
        S.add(f'<circle cx="{f(x)}" cy="{f(y)}" r="2.2" fill="#fff4d6" opacity=".8"/><path d="M{f(x + 2)},{f(y)} l0,-12 l6,3" stroke="#fff4d6" stroke-width="1.2" fill="none" opacity=".8"/>')
    vignette(S, 0.35)


@scene("c14", "Sages, Brahmā, Nārada and Sarasvatī gather in song")
def c14(S):
    celestial(S)
    stars(S, 60, 0, 300)
    glow(S, 300, 300, 220, "#fff0d0", 0.8)
    figure(S, "namaste", 300, 360, 1.9, 1, fill="#ffdc8a", gold="#fff7d8", accent="#c0392b", halo="#fff4cc")
    cloudbank(S, 520, "#f6e6ff", 0.9, 1.6, 6, hi="#c9a8ff", seed=14)
    # an arc of haloed figures on clouds
    who = [("sage", "dhyana"), ("sage", "teach"), ("person", "play"), ("sage", "seated"), ("sage", "teach"), ("sage", "dhyana")]
    for i, (k, ps) in enumerate(who):
        x = 70 + i * 92
        y = 640 + abs(i - 2.5) * -22
        figure(S, ps, x, y, 1.2, 1 if x < 300 else -1, k, fill="#3a2460", halo="#ffe6a8")
    veena(S, 70 + 2 * 92 + 18, 600, 0.9)
    lotus(S, 300, 760, 1.6, "#ffd8e8", "#e88ab0", "#5d4a8a")
    cloudbank(S, 820, "#e8d6ff", 0.95, 2.0, 6, hi="#b893f0", seed=15)
    vignette(S, 0.3)


@scene("c15", "Yama, Kubera and the guardians of the directions — even they cannot fully tell his glory")
def c15(S):
    sky(S, [(0, "#0b0a24"), (0.5, "#2a2050"), (1, "#5a3a6a")])
    stars(S, 120, 0, 900)
    cx, cy = 300, 400
    mandala(S, cx, cy, 220, "#ffe2a8", 0.45, 32)
    glow(S, cx, cy, 160, "#fff0c0", 0.85)
    sun(S, cx, cy, 34, rays=True, ray_a=0.4)
    for i in range(8):
        a = -math.pi / 2 + i * math.pi / 4
        x, y = cx + 190 * math.cos(a), cy + 190 * math.sin(a) + 20
        figure(S, "namaste", x, y, 0.62, 1 if math.cos(a) <= 0 else -1, "sage", fill="#1a1236", halo="#ffd890")
    # the poet below, pen raised, words falling short
    figure(S, "write", 300, 840, 2.3, 1, "poet", fill="#120a1e")
    palm_leaf(S, 300 + 2.3 * 14, 840 - 2.3 * 34, 60, 14, ang=-12)
    for i in range(12):
        x = 330 + i * 9 + S.r.uniform(-4, 4)
        y = 700 - i * 22
        S.add(f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(2.6 - i * 0.18)}" fill="#ffe7b0" opacity="{f(0.9 - i * 0.07)}"/>')
    vignette(S, 0.4)


@scene("c16", "He brought Sugrīva to Rāma, and a kingdom was restored")
def c16(S):
    sky(S, [(0, "#3a2a5a"), (0.5, "#e08a5a"), (1, "#ffd59a")])
    sun(S, 300, 380, 70, ray_a=0.2)
    ridge(S, 760, 520, "#8a4a4a", 6, seed=16, sharp=True)
    ridge(S, 900, 720, "#3a1a1a", 5, seed=17)
    sacred_fire(S, 300, 790, 1.2)
    figure(S, "embrace", 190, 790, 2.4, 1, "rama", fill="#1c2452", accent=SAFFRON)
    figure(S, "embrace", 410, 790, 2.3, -1, "sugriva", fill="#3a1610")
    figure(S, "namaste", 300, 640, 1.2, 1, fill="#2a0e0a")
    vignette(S, 0.35)


@scene("c17", "In Laṅkā, a house marked with Rāma's name: Vibhīṣaṇa heeds his counsel")
def c17(S):
    night(S)
    stars(S, 90, 0, 420)
    moon(S, 120, 130, 36)
    city(S, 700, -10, 610, "#0a0d22", win="#ff9a4a", seed=17, hmin=120, hmax=330)
    # Vibhīṣaṇa's house, with Rāma's name and a tulsi plant
    glow(S, 330, 760, 220, "#ffd27a", 0.5)
    S.add('<rect x="250" y="680" width="160" height="120" fill="#2a1a2e"/><path d="M236,686 L330,620 L424,686 Z" fill="#2a1a2e"/>')
    S.add('<rect x="280" y="700" width="100" height="48" rx="6" fill="#ffe1a0"/>')
    deva_text(S, 330, 738, 34, "राम", "#b3261e")
    S.add('<path d="M305,800 L305,770 Q330,752 355,770 L355,800 Z" fill="#ffbf55"/>')
    tulsi(S, 450, 810, 1.1)
    S.add(f'<rect x="0" y="800" width="600" height="100" fill="#06070f"/>')
    figure(S, "stand", 460, 805, 1.7, -1, "lakshmana", fill="#160a1a", gold="#c99a3a", accent="#7a2a3a")
    figure(S, "kneel", 120, 690, 1.3, 1, fill="#05060e")
    vignette(S, 0.45)


@scene("c18", "The child who leapt for the rising sun, thinking it a ripe fruit")
def c18(S):
    sky(S, [(0, "#3a1f5a"), (0.35, "#d0567a"), (0.65, "#ffb35a"), (1, "#ffeab8")])
    sun(S, 410, 260, 110, core="#fff8d8", rim="#ff8a2a", halo="#ffc45a", ray_a=0.4, n=40)
    cloudbank(S, 720, "#ffd6c0", 0.85, 1.6, 6, hi="#ff9a7a", seed=18)
    cloudbank(S, 820, "#ffe6d0", 0.95, 2.0, 6, hi="#ffb08a", seed=19)
    figure(S, "leap", 170, 640, 2.6, 1, "baby", fill="#5a1e2a")
    # an innocent open mouth reaching for the fruit
    particles(S, 40, 150, 120, 520, 520, "#fff3c0", 2.2)
    vignette(S, 0.25)


@scene("c19", "With the Lord's ring in his mouth, he leapt across the ocean")
def c19(S):
    sky(S, [(0, "#22325a"), (0.5, "#e88a5a"), (0.7, "#ffd28a"), (1, "#ffefcc")])
    sun(S, 470, 520, 46, ray_a=0.25)
    ocean(S, 540, "#e9935a", "#123049", "#ffe0b0", 0.45)
    city(S, 545, 400, 620, "#5a2a3a", win="#ffd28a", scale=0.35, seed=19, hmin=40, hmax=130)
    S.add('<path d="M-20,900 L-20,700 Q60,620 150,700 Q200,760 240,900 Z" fill="#1a1420"/>')
    # arc of the leap
    S.add('<path d="M120,690 Q300,170 500,540" fill="none" stroke="#fff3d0" stroke-width="2" stroke-dasharray="3 9" opacity=".7"/>')
    J = figure(S, "fly", 270, 360, 2.2, 1, fill="#1d0f1e")
    hx, hy = J["h"]
    ring(S, hx + 13, hy + 6, 4.5)
    vignette(S, 0.35)


@scene("c20", "By his grace the hardest tasks become easy: stones that float with Rāma's name")
def c20(S):
    sky(S, [(0, "#1f3a6a"), (0.5, "#7fb0d0"), (0.75, "#ffd9a0"), (1, "#fff0d0")])
    sun(S, 300, 520, 50, ray_a=0.2)
    ocean(S, 540, "#4a8ab0", "#0d2a44", "#e6f6ff", 0.45)
    # the bridge of floating stones, receding to the horizon
    for i in range(16):
        t = i / 15
        y = 880 - t * 330
        s = 1.6 - t * 1.35
        x = 300 + math.sin(t * 2.5) * 30 * (1 - t)
        S.add(f'<ellipse cx="{f(x)}" cy="{f(y)}" rx="{f(60 * s)}" ry="{f(20 * s)}" fill="#a8a29a"/><ellipse cx="{f(x)}" cy="{f(y - 4 * s)}" rx="{f(54 * s)}" ry="{f(15 * s)}" fill="#cfc8bc"/>')
        if s > 0.45:
            deva_text(S, x, y + 2 * s, 18 * s, "राम", "#b3261e", 0.9)
    figure(S, "carry_stone", 120, 840, 1.5, 1, "vanara", fill="#2a1a12")
    S.add('<ellipse cx="120" cy="680" rx="28" ry="15" fill="#a8a29a"/>')
    figure(S, "run", 470, 820, 1.3, -1, "vanara", fill="#2a1a12")
    vignette(S, 0.3)


@scene("c21", "The guardian at Rāma's door")
def c21(S):
    sky(S, [(0, "#1a0b14"), (0.6, "#4a1a24"), (1, "#7a2a20")])
    stars(S, 30, 0, 160)
    # temple gate
    shikhara(S, 300, 330, 260, 260, "#3a1418", flag=SAFFRON)
    S.add('<rect x="150" y="320" width="300" height="520" fill="#3a1418"/>')
    S.add(f'<path d="M210,840 L210,520 Q300,400 390,520 L390,840 Z" fill="{S.lin([(0, "#fff8dc"), (0.5, "#ffd27a"), (1, "#e88a2a")])}"/>')
    glow(S, 300, 640, 260, "#ffd890", 0.55)
    figure(S, "bless", 300, 820, 1.4, 1, "rama", fill="#c27a2a", gold="#fff3c0", halo="#fff8e0", accent="#c0392b")
    for x in (170, 430):
        S.add(f'<rect x="{x - 10}" y="420" width="20" height="420" fill="#2a0c10"/>')
    S.add('<rect x="0" y="840" width="600" height="60" fill="#1a0808"/>')
    figure(S, "guard", 480, 860, 2.5, -1, fill="#12060a")
    gada(S, (480 - 2.5 * 17, 860 - 2.5 * 50), -1.57, 2.5)
    vignette(S, 0.4)


@scene("c22", "Take refuge in him, and what is there to fear?")
def c22(S):
    sky(S, [(0, "#06080f"), (0.6, "#1a2236"), (1, "#2a3448")])
    cloudbank(S, 90, "#0c0f1a", 1, 2.0, 6, seed=22)
    lightning(S, 470, 120, 260, seed=22)
    rain(S, 260, "#b8c8e8", 0.35)
    glow(S, 300, 650, 260, "#ffcf7a", 0.75)
    S.add(f'<ellipse cx="300" cy="840" rx="300" ry="90" fill="#0c0f16"/>')
    figure(S, "giant", 300, 830, 3.6, 1, fill="#140c10")
    gada(S, (300 + 3.6 * 17, 830 - 3.6 * 104), -1.3, 3.6)
    figure(S, "namaste", 220, 830, 1.0, 1, "child", fill="#1a0f12")
    figure(S, "namaste", 190, 830, 1.35, 1, "person", fill="#1a0f12")
    vignette(S, 0.45)


@scene("c23", "Only he can hold his own blazing power; at his roar the three worlds tremble")
def c23(S):
    sky(S, [(0, "#0a0420"), (0.33, "#3a1048"), (0.34, "#4a1a3a"), (0.66, "#c0402a"), (0.67, "#d35a2a"), (1, "#ffb04a")])
    peak(S, 300, 900, 700, 330, "#1a0810")
    J = figure(S, "roar", 300, 580, 3.2, 1, fill="#1a0810")
    hx, hy = J["h"]
    for i in range(7):
        r = 60 + i * 55
        S.add(f'<path d="M{f(hx + r * 0.35)},{f(hy - r * 0.95)} A{f(r)},{f(r)} 0 0 1 {f(hx + r * 0.95)},{f(hy + r * 0.25)}" fill="none" stroke="#ffe6b0" stroke-width="{f(3 - i * 0.3)}" opacity="{f(0.8 - i * 0.1)}"/>',
              f'<path d="M{f(hx - r * 0.2)},{f(hy - r * 0.98)} A{f(r)},{f(r)} 0 0 0 {f(hx - r * 0.9)},{f(hy - r * 0.2)}" fill="none" stroke="#ffe6b0" stroke-width="{f(2.4 - i * 0.25)}" opacity="{f(0.6 - i * 0.08)}"/>')
    stars(S, 40, 0, 280)
    vignette(S, 0.4)


@scene("c24", "Spirits of fear flee when the hero's name is spoken")
def c24(S):
    sky(S, [(0, "#04050c"), (0.7, "#101826"), (1, "#1a2430")])
    stars(S, 70, 0, 420)
    # a vast protective presence in the sky
    figure(S, "guard", 300, 760, 6.4, 1, fill="#2a3a5a", gold="#6a7aa8", accent="#4a5a88", sash=False)
    S.add(f'<rect width="600" height="900" fill="#04050c" opacity=".45"/>')
    for (x, y, s, fl) in ((60, 300, 1.1, -1), (520, 260, 1.0, 1), (40, 560, 0.8, -1), (560, 520, 0.9, 1)):
        ghost(S, x, y, s, "#3a4658", 0.55, fl)
    tree(S, 520, 900, 2.0, "#05060a", seed=3)
    tree(S, 60, 900, 1.7, "#05060a", seed=5)
    glow(S, 300, 780, 230, "#ffc25a", 0.7)
    figure(S, "stand", 300, 860, 1.8, 1, "child", fill="#120a08")
    diya(S, 300 + 1.8 * 14, 860 - 1.8 * 52, 0.6, glow_r=3)
    deva_text(S, 300, 650, 46, "राम", "#ffe6a8", 0.75)
    vignette(S, 0.45)


@scene("c25", "Healing flows from his name, remembered without a gap")
def c25(S):
    sky(S, [(0, "#0b2a2a"), (0.5, "#2f6f5a"), (1, "#d8efb0")])
    glow(S, 300, 470, 320, "#e9ffcf", 0.6)
    mala(S, 300, 470, 220, 108, "#e8c27a", "#e05a3a")
    for i in range(30):
        a = S.r.uniform(0, 2 * math.pi)
        rr = S.r.uniform(40, 200)
        x, y = 300 + rr * math.cos(a), 470 + rr * math.sin(a)
        S.add(f'<ellipse cx="{f(x)}" cy="{f(y)}" rx="3" ry="7" fill="#b8f0a0" opacity=".55" transform="rotate({f(S.r.uniform(0, 180))} {f(x)} {f(y)})"/>')
    figure(S, "dhyana", 300, 600, 2.8, 1, fill="#0d2a22", glowc="#f6ffd8")
    lotus(S, 300, 640, 2.0, "#f4ffe0", "#a8d88a", "#1e4a3a")
    ridge(S, 900, 780, "#0b2a22", 5, seed=25)
    particles(S, 60, color="#efffd0")
    vignette(S, 0.3)


@scene("c26", "Mind, deed and word united in him: the remover of distress")
def c26(S):
    sky(S, [(0, "#1a0f2a"), (0.5, "#5a2a4a"), (1, "#e08a4a")])
    mandala(S, 300, 300, 140, "#ffe0a8", 0.5)
    sun(S, 300, 300, 52, rays=True, ray_a=0.3)
    figure(S, "namaste", 300, 395, 1.1, 1, fill="#4a1a24", halo="#ffe0a8")
    # three flames rising and merging into one light
    for (x0, c) in ((150, "#8fb8ff"), (300, "#ffb35a"), (450, "#ff8a8a")):
        S.add(f'<path d="M{x0},700 C{x0},560 {f((x0 + 300) / 2)},480 300,380" fill="none" stroke="{c}" stroke-width="3" opacity=".75"/>')
        diya(S, x0, 720, 0.8, glow_r=3)
    ridge(S, 900, 790, "#1a0c18", 5, seed=26)
    figure(S, "dhyana", 300, 860, 2.2, 1, "person", fill="#120814")
    vignette(S, 0.35)


@scene("c27", "Rāma, the ascetic king, rules over all; Hanumān carries out his every work")
def c27(S):
    sky(S, [(0, "#203a2a"), (0.5, "#7a9a5a"), (1, "#f6deaa")])
    glow(S, 300, 480, 280, "#fff2c8", 0.6)
    tree(S, 300, 640, 3.0, "#1a2a18", seed=27)
    S.add('<path d="M190,640 Q300,600 410,640 L420,700 L180,700 Z" fill="#3a3020"/>')
    # royal umbrella over the forest-dweller king
    S.add(f'<path d="M230,380 Q300,320 370,380 Z" fill="{SAFFRON}"/><path d="M300,380 L300,470" stroke="{GOLD}" stroke-width="3"/><circle cx="300" cy="346" r="5" fill="{GOLD}"/>')
    S.add(''.join(f'<circle cx="{f(232 + i * 10)}" cy="383" r="3" fill="{GOLD}"/>' for i in range(15)))
    figure(S, "sit_bless", 300, 640, 2.0, 1, "rama", fill="#1c2a4a", accent="#c8902a")
    ridge(S, 900, 760, "#1f2f1a", 5, seed=28)
    figure(S, "kneel", 200, 820, 1.9, 1, fill="#1a1410")
    vignette(S, 0.3)


@scene("c28", "The chariot of the mind, brought to him, arrives at boundless fulfilment")
def c28(S):
    sky(S, [(0, "#1a1440"), (0.5, "#6a3a8a"), (0.8, "#f08a6a"), (1, "#ffe2b0")])
    stars(S, 50, 0, 300)
    sun(S, 420, 250, 70, rays=True, ray_a=0.35)
    cloudbank(S, 780, "#f8d4e0", 0.8, 1.8, 6, hi="#e89ab8", seed=28)
    # flying chariot
    cx, cy = 230, 560
    S.add(f'<path d="M{cx - 90},{cy} L{cx + 90},{cy} L{cx + 70},{cy - 40} L{cx - 70},{cy - 40} Z" fill="#7a2a2a"/>',
          f'<path d="M{cx - 60},{cy - 40} L{cx - 60},{cy - 100} M{cx + 60},{cy - 40} L{cx + 60},{cy - 100}" stroke="{GOLD}" stroke-width="4"/>')
    shikhara(S, cx, cy - 98, 150, 90, "#a83a2a")
    banner(S, (cx, cy - 190), 1.0, SAFFRON, GOLD, L=40)
    wheel(S, cx - 50, cy + 10, 34, GOLD, 1, 12, 2)
    wheel(S, cx + 50, cy + 10, 34, GOLD, 1, 12, 2)
    for i in range(6):
        S.add(f'<path d="M{cx - 120 - i * 20},{cy - 10 + i * 12} L{cx - 220 - i * 30},{cy + 20 + i * 18}" stroke="#fff0d0" stroke-width="2" opacity="{f(0.6 - i * 0.08)}"/>')
    figure(S, "namaste", 420, 330, 1.2, -1, fill="#5a2a2a", halo="#fff0c0")
    particles(S, 40, color="#fff0c8")
    vignette(S, 0.3)


@scene("c29", "His glory shines through all four ages: the light of the world")
def c29(S):
    sky(S, [(0, "#04061a"), (0.5, "#1a1a4a"), (1, "#4a3a7a")])
    stars(S, 160, 0, 900)
    # four ages as four arcs of light
    for i, c in enumerate(("#ffffff", "#ffd27a", "#ff9a5a", "#8a6ad0")):
        r = 360 - i * 52
        S.add(f'<path d="M{f(300 - r)},{f(820)} A{f(r)},{f(r)} 0 0 1 {f(300 + r)},{f(820)}" fill="none" stroke="{c}" stroke-width="{f(10 - i * 2)}" opacity=".55"/>')
    S.add(f'<ellipse cx="300" cy="980" rx="520" ry="200" fill="#0c0e22"/>')
    glow(S, 300, 760, 220, "#ffe0a0", 0.6)
    figure(S, "dhyana", 300, 800, 2.4, 1, fill="#080918", halo="#ffe6a8")
    vignette(S, 0.35)


@scene("c30", "Protector of saints, uprooter of evil, Rāma's darling")
def c30(S):
    sky(S, [(0, "#2a1a3a"), (0.5, "#b55a4a"), (1, "#f8c88a")])
    sun(S, 150, 400, 50, ray_a=0.2)
    ridge(S, 900, 700, "#4a2028", 6, seed=30)
    J = figure(S, "uproot", 360, 760, 3.0, 1, fill="#1d0c10")
    # the uprooted thorn tree, roots exposed, lifted overhead
    hx, hy = J["hr"]
    S.add(f'<path d="M{f(hx - 10)},{f(hy)} L{f(hx + 90)},{f(hy - 140)}" stroke="#2a1416" stroke-width="10" stroke-linecap="round"/>')
    for i in range(8):
        a = math.radians(200 + i * 18)
        S.add(f'<path d="M{f(hx - 6)},{f(hy + 2)} q{f(20 * math.cos(a))},{f(30)} {f(46 * math.cos(a))},{f(50 + i * 4)}" fill="none" stroke="#2a1416" stroke-width="3"/>')
    for i in range(10):
        bx, by = hx + 40 + i * 6, hy - 60 - i * 10
        S.add(f'<path d="M{f(bx)},{f(by)} l{f(S.r.uniform(-40, 40))},{f(S.r.uniform(-30, 10))}" stroke="#2a1416" stroke-width="3" stroke-linecap="round"/>')
    hut(S, 120, 860, 1.4, "#2a1414", glow_c="#ffbf55")
    figure(S, "dhyana", 200, 870, 1.2, -1, "sage", fill="#1a0a0c")
    vignette(S, 0.35)


@scene("c31", "Mother Jānakī's boon: giver of the eight powers and nine treasures")
def c31(S):
    sky(S, [(0, "#2a1440"), (0.5, "#8a3a5a"), (1, "#f0a46a")])
    tree(S, 140, 900, 3.0, "#24101a", kind="ashoka", flowers="#ff6a3a", seed=31)
    figure(S, "sit_bless", 190, 860, 2.2, 1, "sita", fill="#7a1a2a", halo="#ffe0a0")
    figure(S, "kneel", 420, 860, 2.4, -1, fill="#1a0a10")
    # eight jewels and nine pots of treasure arching overhead
    for i in range(8):
        a = math.radians(-160 + i * (140 / 7))
        x, y = 330 + 200 * math.cos(a), 470 + 200 * math.sin(a)
        glow(S, x, y, 30, "#fff0c0", 0.6)
        S.add(f'<path d="M{f(x)},{f(y - 12)} L{f(x + 9)},{f(y)} L{f(x)},{f(y + 12)} L{f(x - 9)},{f(y)} Z" fill="{["#ff5a5a", "#5ab0ff", "#7aff9a", "#ffe05a"][i % 4]}"/>')
    for i in range(9):
        x = 250 + i * 34
        kalash(S, x, 560 + abs(i - 4) * 8, 0.42)
    particles(S, 50, 200, 200, 580, 600, "#fff0c0")
    vignette(S, 0.35)


@scene("c32", "He holds the elixir of Rāma's name, forever the Lord's servant")
def c32(S):
    sky(S, [(0, "#1a0b24"), (0.6, "#5a1a3a"), (1, "#c0502a")])
    mandala(S, 300, 470, 220, "#ffe2a8", 0.45, 24)
    glow(S, 300, 520, 240, "#ffd890", 0.7)
    figure(S, "seated", 300, 760, 3.4, 1, fill="#1a0a10")
    kalash(S, 300 + 3.4 * 4, 760 - 3.4 * 40 + 4, 1.1)
    deva_text(S, 316, 650, 34, "राम", "#ffe9b0", 0.95)
    beams(S, 316, 600, 16, 420, "#ffe9b8", 0.08, -math.pi * 0.95, -math.pi * 0.05)
    vignette(S, 0.35)


@scene("c33", "Through bhajan, the jolting wheel of life runs true again")
def c33(S):
    dusk(S)
    stars(S, 40, 0, 250)
    glow(S, 300, 330, 260, "#ffd27a", 0.5)
    wheel(S, 300, 330, 160, "#ffd27a", 0.85, 24, 3)
    ridge(S, 900, 700, "#2a0f1c", 5, seed=33)
    for (x, ps, k, fc) in ((140, "play", "person", 1), (300, "play", "sage", 1), (460, "play", "person", -1)):
        figure(S, ps, x, 830, 1.9, fc, k, fill="#14070e")
        S.add(f'<circle cx="{f(x + fc * 1.9 * 6)}" cy="{f(830 - 1.9 * 44)}" r="5" fill="{GOLD}"/><circle cx="{f(x + fc * 1.9 * 12)}" cy="{f(830 - 1.9 * 52)}" r="5" fill="{GOLD}"/>')
    diya(S, 220, 840, 0.6, glow_r=3)
    diya(S, 380, 840, 0.6, glow_r=3)
    vignette(S, 0.35)


@scene("c34", "At the end, the journey home to Rāma's abode")
def c34(S):
    sky(S, [(0, "#1a1a4a"), (0.4, "#7a5a9a"), (0.7, "#f0b08a"), (1, "#ffe6c0")])
    glow(S, 300, 220, 260, "#fff0c8", 0.8)
    city(S, 300, 130, 470, "#f6d28a", win="#fff8e0", scale=0.55, seed=34, hmin=60, hmax=180, golden=True)
    cloudbank(S, 310, "#fff4e8", 0.95, 1.4, 6, hi="#f0c8a0", seed=34)
    # the river, with lamps floating
    river(S, 560, 900, "#e8a87a", "#3a2a5a", "#fff0d0", 0.45)
    for (x, y, s) in ((300, 820, 1.4), (230, 720, 1.0), (360, 650, 0.8), (290, 600, 0.6)):
        leaf_diya(S, x, y, s)
    # the soul's path of light
    S.add('<path d="M300,800 C250,650 380,500 300,330" fill="none" stroke="#fff4d0" stroke-width="2" stroke-dasharray="2 8" opacity=".8"/>')
    vignette(S, 0.3)


@scene("c35", "One sincere devotion is enough")
def c35(S):
    sky(S, [(0, "#05030a"), (1, "#140a10")])
    glow(S, 300, 520, 360, "#ffb84a", 0.55)
    glow(S, 300, 520, 160, "#ffe0a0", 0.65)
    figure(S, "seated", 300, 640, 3.0, 1, fill="#2a140a", gold="#ffcf6a", accent="#e05a2a")
    diya(S, 300, 790, 2.0, glow_r=2.2)
    particles(S, 30, 150, 300, 450, 700, "#ffd890", 1.8)
    vignette(S, 0.5)


@scene("c36", "Remember the mighty hero, and the chains of distress fall away")
def c36(S):
    sky(S, [(0, "#1a1a3a"), (0.45, "#8a4a5a"), (0.75, "#f6a35a"), (1, "#ffe8b8")])
    sun(S, 300, 700, 120, rays=True, ray_a=0.35, n=48)
    ridge(S, 900, 760, "#3a1a24", 6, seed=36)
    figure(S, "giant", 300, 780, 3.4, 1, fill="#1d0c14")
    gada(S, (300 + 3.4 * 17, 780 - 3.4 * 104), -1.2, 3.4)
    chain_broken(S, 70, 260, 1.6, "#c8b8a0", 0.8, 5, 0.5)
    chain_broken(S, 420, 200, 1.6, "#c8b8a0", 0.8, 5, -0.3)
    chain_broken(S, 470, 470, 1.3, "#c8b8a0", 0.6, 3, 1.1)
    chain_broken(S, 60, 520, 1.2, "#c8b8a0", 0.6, 3, -0.8)
    vignette(S, 0.3)


@scene("c37", "Jai, jai, jai! Be my Guru, Lord Hanumān")
def c37(S):
    sky(S, [(0, "#2a1a10"), (0.5, "#8a5a2a"), (1, "#f6d29a")])
    tree(S, 300, 720, 3.6, "#2a1f10", seed=37)
    glow(S, 300, 600, 220, "#ffe2a0", 0.6)
    S.add('<path d="M200,720 L400,720 L380,690 L220,690 Z" fill="#5a3a1a"/>')
    figure(S, "teach", 300, 690, 2.4, 1, fill="#2a140a", halo="#ffe6a8")
    for x in (100, 300, 500):
        banner(S, (x, 900), 1.8 if x != 300 else 2.2, SAFFRON, GOLD, L=110 if x != 300 else 150, flip=1 if x < 300 else -1)
    figure(S, "namaste", 150, 880, 1.6, 1, "person", fill="#1a0c06")
    figure(S, "namaste", 450, 880, 1.6, -1, "child", fill="#1a0c06")
    vignette(S, 0.35)


@scene("c38", "A hundred recitations: the prison opens, the bonds fall away")
def c38(S):
    sky(S, [(0, "#1a1028"), (0.5, "#a04a3a"), (1, "#f6b56a")])
    sun(S, 300, 330, 70, ray_a=0.3)
    fort(S, 900, "#3a1a18", 560, seed=38)
    # monkeys swarming the walls, as in the legend of the hymn's composition
    for i in range(16):
        x = S.r.uniform(20, 580)
        y = 548 + S.r.uniform(-4, 4)
        figure(S, S.r.choice(["run", "stand", "leap"]), x, y, S.r.uniform(0.32, 0.45), S.r.choice([-1, 1]), "vanara", fill="#1a0a0a")
    # a barred window, bars broken open, light pouring out
    S.add(f'<path d="M240,820 L240,690 Q300,640 360,690 L360,820 Z" fill="{S.lin([(0, "#fff6d8"), (1, "#ffbf55")])}"/>')
    glow(S, 300, 740, 180, "#ffe0a0", 0.6)
    for x in (264, 288, 312, 336):
        bend = 0 if x in (264, 336) else (-30 if x == 288 else 30)
        S.add(f'<path d="M{x},690 Q{x + bend},755 {x},820" stroke="#2a1410" stroke-width="5" fill="none"/>')
    mala(S, 300, 755, 90, 100, "#f2c37a", "#e04a2a", a=0.55)
    vignette(S, 0.35)


@scene("c39", "Śiva, Lord of Gaurī, stands witness")
def c39(S):
    night(S)
    stars(S, 140, 0, 600)
    moon(S, 300, 120, 30)
    peak(S, 300, 700, 640, 460, "#26305a", "#eef0ff")
    glow(S, 300, 520, 240, "#c8d0ff", 0.4)
    figure(S, "dhyana", 300, 600, 2.4, 1, "shiva", fill="#1a2348", halo="#e8ecff")
    S.add('<path d="M372,350 L372,620 M358,372 Q358,388 372,392 Q386,388 386,372 M372,350 l-6,10 M372,350 l6,10" stroke="#e8ecff" stroke-width="3" fill="none"/>')
    S.add('<path d="M300,480 C320,520 270,560 300,640 C330,700 260,760 300,900" fill="none" stroke="#bfe0ff" stroke-width="5" opacity=".5"/>')
    ridge(S, 900, 760, "#0d1230", 5, seed=39)
    # the open book of the Chalisa
    glow(S, 300, 830, 120, "#ffe0a0", 0.7)
    S.add('<path d="M220,840 Q260,820 300,836 Q340,820 380,840 L380,850 Q340,832 300,848 Q260,832 220,850 Z" fill="#fff0c8"/>')
    vignette(S, 0.4)


@scene("c40", "Tulsidas, forever Hari's servant: 'Lord, make my heart your home'")
def c40(S):
    sky(S, [(0, "#2a1640"), (0.45, "#b0506a"), (0.7, "#f39a5a"), (1, "#ffd98a")])
    sun(S, 420, 520, 40, ray_a=0.2)
    for (x, w, h) in ((90, 70, 220), (170, 50, 160), (480, 80, 260), (560, 50, 170)):
        shikhara(S, x, 560, w, h, "#4a1a2a", flag=SAFFRON)
    S.add('<rect x="0" y="540" width="600" height="30" fill="#4a1a2a"/>')
    river(S, 570, 720, "#f0a06a", "#5a2a4a", "#ffe6c0", 0.45)
    boat(S, 440, 640, 0.9, "#2a0f18", lamp=True)
    steps(S, 900, 720, "#5a2a28", 9, line="#fff0d0")
    glow(S, 260, 760, 140, "#ffd88a", 0.55)
    figure(S, "write", 240, 800, 2.4, 1, "poet", fill="#1a0a10")
    palm_leaf(S, 240 + 2.4 * 15, 800 - 2.4 * 33, 62, 14, ang=-10)
    # a heart of light for the Lord to dwell in
    hx, hy = 240 + 2.4 * 2, 800 - 2.4 * 40
    S.add(f'<path d="M{hx},{hy + 10} C{hx - 22},{hy - 4} {hx - 12},{hy - 22} {hx},{hy - 10} C{hx + 12},{hy - 22} {hx + 22},{hy - 4} {hx},{hy + 10} Z" fill="#ffe08a" opacity=".9"/>')
    glow(S, hx, hy, 40, "#fff0b0", 0.8)
    vignette(S, 0.3)


# ───────────── Closing doha ─────────────

@scene("d3", "Dwell in my heart, with Rāma, Lakṣmaṇa and Sītā")
def d3(S):
    sky(S, [(0, "#3a0f2a"), (0.5, "#b03a2a"), (1, "#f6b04a")])
    mandala(S, 300, 400, 270, "#ffe3a8", 0.4, 28)
    mandala(S, 300, 400, 190, "#ffe9b8", 0.5, 16)
    glow(S, 300, 420, 300, "#ffd88a", 0.6)
    figure(S, "heart", 300, 820, 5.2, 1, fill="#2a0c10", gold="#ffd36b", heart=True)
    lotus_seat(S, 300, 835, 2.6, "#f7c27a", "#8a3a1a")
    particles(S, 70, color="#fff0c0")
    vignette(S, 0.3)
