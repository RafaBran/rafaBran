"""Gera os SVGs estáticos do perfil: banner com dupla hélice e cladograma da stack."""
import math, os

OUT = os.path.join(os.path.dirname(__file__), "..", "assets")

THEMES = {
    "dark": dict(bg="#0d1117", fg="#e6edf3", muted="#8b949e", a="#3fb950", b="#58a6ff",
                 pair=["#3fb950", "#58a6ff", "#d2a8ff", "#f0883e"], line="#30363d"),
    "light": dict(bg="#ffffff", fg="#1f2328", muted="#59636e", a="#1a7f37", b="#0969da",
                  pair=["#1a7f37", "#0969da", "#8250df", "#bc4c00"], line="#d0d7de"),
}
SANS = "-apple-system, 'Segoe UI', Helvetica, Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, Consolas, 'Liberation Mono', monospace"


def banner(t):
    W, H = 900, 240
    cy, A = 120, 62
    n, x0, dx = 22, 36, 18
    period = 3.2
    parts = []
    for i in range(n):
        x = x0 + i * dx
        delay = -(i * 0.28)
        color = t["pair"][i % 4]
        parts.append(
            f'<line class="rung" x1="{x}" y1="{cy-A}" x2="{x}" y2="{cy+A}" stroke="{color}" '
            f'style="animation-delay:{delay:.2f}s"/>'
            f'<circle class="top" cx="{x}" cy="{cy}" r="5" fill="{t["a"]}" style="animation-delay:{delay:.2f}s"/>'
            f'<circle class="bot" cx="{x}" cy="{cy}" r="5" fill="{t["b"]}" style="animation-delay:{delay:.2f}s"/>'
        )
    tx = 470
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Rafael Brandão, biólogo e desenvolvedor">
<style>
  .rung,.top,.bot{{animation-duration:{period}s;animation-iteration-count:infinite;animation-direction:alternate;animation-timing-function:ease-in-out;transform-box:fill-box}}
  .rung{{stroke-width:2.2;stroke-linecap:round;opacity:.55;transform-origin:center;animation-name:flip}}
  .top{{animation-name:up}} .bot{{animation-name:down}}
  @keyframes flip{{from{{transform:scaleY(1)}}to{{transform:scaleY(-1)}}}}
  @keyframes up{{from{{transform:translateY(-{A}px)}}to{{transform:translateY({A}px)}}}}
  @keyframes down{{from{{transform:translateY({A}px)}}to{{transform:translateY(-{A}px)}}}}
  .cursor{{animation:blink 1.1s steps(1) infinite}}
  @keyframes blink{{50%{{opacity:0}}}}
</style>
<rect width="{W}" height="{H}" rx="14" fill="{t["bg"]}"/>
{''.join(parts)}
<text x="{tx}" y="96" font-family="{SANS}" font-size="40" font-weight="700" fill="{t["fg"]}">Rafael Brandão</text>
<text x="{tx}" y="132" font-family="{SANS}" font-size="19" fill="{t["muted"]}">Biólogo · Desenvolvedor Java</text>
<text x="{tx}" y="178" font-family="{MONO}" font-size="15" fill="{t["a"]}">ATG<tspan fill="{t["muted"]}"> // todo gene começa aqui</tspan></text>
<text x="{tx}" y="202" font-family="{MONO}" font-size="15" fill="{t["b"]}">main()<tspan fill="{t["muted"]}"> // todo programa também</tspan><tspan class="cursor" fill="{t["fg"]}">▍</tspan></text>
</svg>'''


# Árvore: (rótulo, grupo, filhos)
TREE = ("", None, [
    ("Back-end", 0, [
        ("Java", 0, [
            ("Spring Boot", 0, [
                ("APIs REST", 0, []),
                ("Microsserviços", 0, []),
                ("Autenticação JWT", 0, []),
            ]),
        ]),
    ]),
    ("Front-end", 1, [
        ("TypeScript", 1, [
            ("Angular", 1, [
                ("PrimeNG", 1, []),
                ("Bootstrap", 1, []),
            ]),
        ]),
        ("SCSS", 1, []),
    ]),
    ("Dados", 2, [
        ("SQL", 2, [
            ("PostgreSQL", 2, []),
            ("Oracle", 2, []),
            ("MySQL", 2, []),
        ]),
    ]),
])


def cladogram(t):
    W, H = 900, 420
    top, row = 78, 38
    x_root, step = 40, 150
    colors = [t["a"], t["b"], t["pair"][3]]
    els, labels = [], []
    counter = [0]
    seg = [0]

    def layout(node, depth):
        label, g, kids = node
        x = x_root + depth * step
        if not kids:
            y = top + counter[0] * row
            counter[0] += 1
            return x, y
        pos = [layout(k, depth + 1) for k in kids]
        y = sum(p[1] for p in pos) / len(pos)
        for (cx, cy_), k in zip(pos, kids):
            c = colors[k[1]]
            d = f"M{x},{y:.1f} V{cy_:.1f} H{cx}" if not k[2] else f"M{x},{y:.1f} V{cy_:.1f} H{cx}"
            # folhas estendem o ramo até a coluna final
            if not k[2]:
                d = f"M{x},{y:.1f} V{cy_:.1f} H{x_root + 4*step}"
            delay = 0.12 * seg[0]
            seg[0] += 1
            els.append(f'<path d="{d}" stroke="{c}" pathLength="1" class="br" style="animation-delay:{delay:.2f}s"/>')
            if k[2]:
                labels.append(f'<text x="{cx - 8}" y="{cy_ - 8:.1f}" text-anchor="end" class="node" fill="{c}" style="animation-delay:{delay+0.4:.2f}s">{k[0]}</text>')
                els.append(f'<circle cx="{cx}" cy="{cy_:.1f}" r="3.5" fill="{c}" class="dot" style="animation-delay:{delay+0.4:.2f}s"/>')
            else:
                lx = x_root + 4 * step
                labels.append(f'<circle cx="{lx}" cy="{cy_:.1f}" r="5" fill="{c}" class="dot" style="animation-delay:{delay+0.4:.2f}s"/>')
                labels.append(f'<text x="{lx + 14}" y="{cy_ + 5:.1f}" class="leaf" fill="{t["fg"]}" style="animation-delay:{delay+0.4:.2f}s">{k[0]}</text>')
        return x, y

    _, ry = layout(TREE, 0)
    els.insert(0, f'<circle cx="{x_root}" cy="{ry:.1f}" r="5" fill="{t["muted"]}"/>')
    legend = "".join(
        f'<circle cx="{560 + i*110}" cy="36" r="5" fill="{colors[i]}"/>'
        f'<text x="{574 + i*110}" y="41" class="leg" fill="{t["muted"]}">{n}</text>'
        for i, n in enumerate(["Back-end", "Front-end", "Dados"]))
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Cladograma da stack de tecnologias">
<style>
  .br{{fill:none;stroke-width:2.4;stroke-linecap:round}}
  .leaf{{font:500 16px {SANS}}} .node{{font:600 13px {MONO}}} .leg{{font:14px {SANS}}}
  @keyframes grow{{to{{stroke-dashoffset:0}}}}
  @keyframes show{{to{{opacity:1}}}}
</style>
<rect width="{W}" height="{H}" rx="14" fill="{t["bg"]}"/>
<text x="{x_root}" y="40" font-family="{SANS}" font-size="20" font-weight="700" fill="{t["fg"]}">Filogenia da stack</text>
<text x="{x_root}" y="62" font-family="{SANS}" font-size="14" fill="{t["muted"]}">cladograma das tecnologias que uso, do ancestral comum às folhas</text>
{''.join(els)}
{''.join(labels)}
{legend}
</svg>'''


for name, t in THEMES.items():
    with open(os.path.join(OUT, f"banner-{name}.svg"), "w", encoding="utf-8") as f:
        f.write(banner(t))
    with open(os.path.join(OUT, f"filogenia-{name}.svg"), "w", encoding="utf-8") as f:
        f.write(cladogram(t))
print("ok")
