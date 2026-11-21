"""Gera os SVGs animados do perfil (banner, faixa de stack, cards e rodapé)."""
import os, html

OUT = os.path.join(os.path.dirname(__file__), "..", "assets")
os.makedirs(OUT, exist_ok=True)

BG = "#070b18"
VIOLET, CYAN, EMERALD, PINK = "#8b5cf6", "#22d3ee", "#34d399", "#f472b6"
FG, MUTED = "#f1f5f9", "#94a3b8"
SANS = "'Segoe UI', -apple-system, Helvetica, Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, Consolas, 'Liberation Mono', monospace"


def save(name, svg):
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(svg)


def wave_path(w, h, amp, base, wl):
    """Onda senoidal (aprox. por curvas) com largura 2*w para loop contínuo."""
    d = f"M0,{base}"
    x = 0
    up = True
    while x < 2 * w:
        cx = x + wl / 2
        cy = base - amp if up else base + amp
        d += f" Q{cx},{cy} {x + wl},{base}"
        x += wl
        up = not up
    return d + f" V{h} H0 Z"


def banner():
    W, H = 1200, 420
    phrases = [
        "Desenvolvedor Java júnior @ Memora",
        "Spring Boot · Angular · PostgreSQL",
        "Sistemas para o governo do estado",
    ]
    fs, cw = 26, 26 * 0.6
    per, T = 5.0, 5.0 * len(phrases)
    ty = 262
    type_css, type_el = [], []
    for k, p in enumerate(phrases):
        n = len(p)
        full = n * cw
        s = k * per / T * 100
        a = (k * per + 1.6) / T * 100   # terminou de digitar
        b = (k * per + 3.9) / T * 100   # começa a apagar
        e = (k * per + 4.6) / T * 100   # apagou
        x0 = (W - full) / 2
        def kf(prop, top):
            pts = [(0, 0), (s, 0), (a, top), (b, top), (e, 0), (100, 0)]
            if s == 0:
                pts = pts[1:]
            return " ".join(f"{pc:.3f}%{{{prop.format(v=v)}}}" for pc, v in pts)
        type_css.append(f"@keyframes w{k}{{{kf('transform:scaleX({v})', 1)}}}")
        type_css.append(f"@keyframes c{k}{{{kf('transform:translateX({v:.1f}px)', full)}}}")
        if s > 0:
            type_css.append(f"@keyframes o{k}{{0%,{s-0.01:.3f}%{{opacity:0}}{s:.3f}%,{e+0.6:.3f}%{{opacity:1}}{e+0.61:.3f}%,100%{{opacity:0}}}}")
        else:
            type_css.append(f"@keyframes o{k}{{0%,{e+0.6:.3f}%{{opacity:1}}{e+0.61:.3f}%,100%{{opacity:0}}}}")
        type_el.append(f'''
  <clipPath id="clip{k}"><rect x="{x0:.1f}" y="{ty-30}" height="44" width="{full+4:.1f}" style="transform-box:fill-box;transform-origin:left;transform:scaleX(0);animation:w{k} {T}s steps({n}) infinite"/></clipPath>
  <g style="animation:o{k} {T}s linear infinite">
    <text x="{x0:.1f}" y="{ty}" clip-path="url(#clip{k})" font-family="{MONO}" font-size="{fs}" fill="{FG}">{html.escape(p)}</text>
    <rect x="{x0+3:.1f}" y="{ty-24}" width="3" height="30" fill="{CYAN}" style="animation:c{k} {T}s steps({n}) infinite, blink 1s steps(1) infinite"/>
  </g>''')

    waves = []
    for i, (amp, base, wl, col, op, dur) in enumerate([
        (18, 345, 300, VIOLET, .28, 16), (14, 362, 240, CYAN, .2, 11), (10, 380, 200, EMERALD, .16, 8)]):
        waves.append(f'<path d="{wave_path(W, H, amp, base, wl)}" fill="{col}" opacity="{op}">'
                     f'<animateTransform attributeName="transform" type="translate" from="0 0" to="-{wl*2*(W//(wl*2))} 0" dur="{dur}s" repeatCount="indefinite"/></path>')
    # partículas
    import random
    rnd = random.Random(7)
    parts = []
    for _ in range(46):
        x, y = rnd.uniform(0, W), rnd.uniform(40, 360)
        r = rnd.uniform(.8, 2.2)
        d = rnd.uniform(6, 14)
        dl = -rnd.uniform(0, d)
        col = rnd.choice([FG, CYAN, VIOLET])
        parts.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r:.1f}" fill="{col}" class="p" style="animation-duration:{d:.1f}s;animation-delay:{dl:.1f}s"/>')

    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Rafael Brandão, desenvolvedor Java">
<defs>
  <linearGradient id="nameb" x1="0" x2="1" gradientUnits="objectBoundingBox" spreadMethod="repeat">
    <stop offset="0" stop-color="{CYAN}"/><stop offset=".33" stop-color="{VIOLET}"/><stop offset=".66" stop-color="{PINK}"/><stop offset="1" stop-color="{CYAN}"/>
    <animateTransform attributeName="gradientTransform" type="translate" values="0 0;1 0" dur="6s" repeatCount="indefinite"/>
  </linearGradient>
  <filter id="blur" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="60"/></filter>
  <filter id="glow" x="-20%" y="-50%" width="140%" height="200%"><feGaussianBlur stdDeviation="14"/></filter>
  <radialGradient id="vig" cx=".5" cy=".45" r=".75"><stop offset=".6" stop-color="{BG}" stop-opacity="0"/><stop offset="1" stop-color="{BG}" stop-opacity=".9"/></radialGradient>
  <clipPath id="frame"><rect width="{W}" height="{H}" rx="22"/></clipPath>
</defs>
<style>
  .blob{{animation:drift 18s ease-in-out infinite alternate}}
  .b2{{animation-duration:23s;animation-direction:alternate-reverse}}
  .b3{{animation-duration:29s}}
  @keyframes drift{{0%{{transform:translate(0,0) scale(1)}}50%{{transform:translate(160px,40px) scale(1.25)}}100%{{transform:translate(-120px,-30px) scale(.9)}}}}
  .p{{animation-name:rise;animation-timing-function:linear;animation-iteration-count:infinite}}
  @keyframes rise{{0%{{transform:translateY(40px);opacity:0}}20%{{opacity:.8}}80%{{opacity:.5}}100%{{transform:translateY(-120px);opacity:0}}}}
  @keyframes blink{{50%{{opacity:0}}}}
  .reveal{{animation:reveal 1.6s cubic-bezier(.2,.7,.2,1) both}}
  @keyframes reveal{{from{{opacity:0;transform:translateY(24px);letter-spacing:22px}}to{{opacity:1;transform:none}}}}
  {"".join(type_css)}
</style>
<g clip-path="url(#frame)">
  <rect width="{W}" height="{H}" fill="{BG}"/>
  <g filter="url(#blur)" opacity=".85">
    <circle class="blob" cx="260" cy="140" r="170" fill="{VIOLET}"/>
    <circle class="blob b2" cx="900" cy="120" r="160" fill="{CYAN}" opacity=".7"/>
    <circle class="blob b3" cx="620" cy="330" r="150" fill="{PINK}" opacity=".45"/>
  </g>
  {"".join(parts)}
  {"".join(waves)}
  <rect width="{W}" height="{H}" fill="url(#vig)"/>
  <g class="reveal" style="transform-box:fill-box;transform-origin:center">
    <text x="{W/2}" y="186" text-anchor="middle" font-family="{SANS}" font-size="86" font-weight="800" letter-spacing="6" fill="url(#nameb)" filter="url(#glow)" opacity=".55">RAFAEL BRANDÃO</text>
    <text x="{W/2}" y="186" text-anchor="middle" font-family="{SANS}" font-size="86" font-weight="800" letter-spacing="6" fill="url(#nameb)">RAFAEL BRANDÃO</text>
  </g>
  {"".join(type_el)}
  <rect width="{W}" height="{H}" rx="22" fill="none" stroke="#ffffff" stroke-opacity=".08"/>
</g>
</svg>'''


STACK = ["Java", "Spring Boot", "Angular", "TypeScript", "PostgreSQL", "Oracle", "MySQL",
         "APIs REST", "Microsserviços", "JWT", "PrimeNG", "Bootstrap", "SCSS", "Git"]


def stack():
    W, H = 1200, 96
    cols = [VIOLET, CYAN, EMERALD, PINK]
    x, pills = 0, []
    for i, s in enumerate(STACK):
        w = len(s) * 10.2 + 52
        c = cols[i % 4]
        pills.append(
            f'<g transform="translate({x:.0f},26)"><rect width="{w:.0f}" height="44" rx="22" fill="{c}" fill-opacity=".12" stroke="{c}" stroke-opacity=".55"/>'
            f'<circle cx="22" cy="22" r="5" fill="{c}"/><text x="36" y="28.5" font-family="{SANS}" font-size="17" font-weight="600" fill="{FG}">{s}</text></g>')
        x += w + 14
    span = x
    row = "".join(pills)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Stack: {', '.join(STACK)}">
<defs>
  <linearGradient id="fade" x1="0" x2="1"><stop offset="0" stop-color="{BG}"/><stop offset=".08" stop-color="{BG}" stop-opacity="0"/><stop offset=".92" stop-color="{BG}" stop-opacity="0"/><stop offset="1" stop-color="{BG}"/></linearGradient>
  <clipPath id="frame"><rect width="{W}" height="{H}" rx="22"/></clipPath>
</defs>
<style>.track{{animation:scroll {span/55:.1f}s linear infinite}} @keyframes scroll{{to{{transform:translateX(-{span:.0f}px)}}}}</style>
<g clip-path="url(#frame)">
  <rect width="{W}" height="{H}" fill="{BG}"/>
  <g class="track"><g>{row}</g><g transform="translate({span:.0f},0)">{row}</g></g>
  <rect width="{W}" height="{H}" fill="url(#fade)"/>
  <rect width="{W}" height="{H}" rx="22" fill="none" stroke="#ffffff" stroke-opacity=".08"/>
</g>
</svg>'''


def card(idx, title, lines, tags, c1, c2):
    W, H = 590, 300
    body = "".join(f'<text x="36" y="{148 + i*26}" font-family="{SANS}" font-size="17" fill="{MUTED}">{html.escape(l)}</text>' for i, l in enumerate(lines))
    x, chips = 36, []
    for t in tags:
        w = len(t) * 8.4 + 26
        chips.append(f'<rect x="{x:.0f}" y="244" width="{w:.0f}" height="30" rx="15" fill="#ffffff" fill-opacity=".06" stroke="#ffffff" stroke-opacity=".14"/>'
                     f'<text x="{x+13:.0f}" y="264" font-family="{MONO}" font-size="13.5" fill="{FG}">{t}</text>')
        x += w + 10
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Projeto {html.escape(title)}">
<defs>
  <linearGradient id="border" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="{c1}"/><stop offset=".5" stop-color="{c2}"/><stop offset="1" stop-color="{c1}"/>
    <animateTransform attributeName="gradientTransform" type="rotate" values="0 .5 .5;360 .5 .5" dur="8s" repeatCount="indefinite"/>
  </linearGradient>
  <linearGradient id="sheen" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity=".09"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
  <filter id="blur" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="40"/></filter>
  <clipPath id="frame"><rect x="2" y="2" width="{W-4}" height="{H-4}" rx="20"/></clipPath>
</defs>
<style>
  .sheen{{animation:sweep 5s ease-in-out infinite;animation-delay:{idx*1.4}s}}
  @keyframes sweep{{0%{{transform:translateX(-300px) skewX(-20deg)}}60%,100%{{transform:translateX({W+100}px) skewX(-20deg)}}}}
  .orb{{animation:float 9s ease-in-out infinite alternate}}
  @keyframes float{{to{{transform:translate(-60px,40px)}}}}
</style>
<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="21" fill="url(#border)"/>
<g clip-path="url(#frame)">
  <rect width="{W}" height="{H}" fill="{BG}"/>
  <circle class="orb" cx="{W-60}" cy="40" r="110" fill="{c1}" opacity=".35" filter="url(#blur)"/>
  <text x="36" y="62" font-family="{MONO}" font-size="15" fill="{c2}">0{idx+1} / projeto</text>
  <text x="36" y="108" font-family="{SANS}" font-size="34" font-weight="800" fill="{FG}">{html.escape(title)}</text>
  {body}
  {"".join(chips)}
  <text x="{W-36}" y="108" text-anchor="end" font-family="{SANS}" font-size="28" fill="{FG}" opacity=".7">↗</text>
  <rect class="sheen" x="0" y="0" width="160" height="{H}" fill="url(#sheen)"/>
</g>
</svg>'''


def footer():
    W, H = 1200, 120
    waves = []
    for amp, base, wl, col, op, dur in [(14, 50, 300, VIOLET, .28, 14), (10, 66, 240, CYAN, .2, 10), (8, 84, 200, EMERALD, .16, 7)]:
        waves.append(f'<path d="{wave_path(W, H, amp, base, wl)}" fill="{col}" opacity="{op}">'
                     f'<animateTransform attributeName="transform" type="translate" from="0 0" to="-{wl*2*(W//(wl*2))} 0" dur="{dur}s" repeatCount="indefinite"/></path>')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">
<defs><clipPath id="frame"><rect width="{W}" height="{H}" rx="22"/></clipPath></defs>
<g clip-path="url(#frame)"><rect width="{W}" height="{H}" fill="{BG}"/>{"".join(waves)}</g>
</svg>'''


save("banner.svg", banner())
save("stack.svg", stack())
save("card-laec.svg", card(0, "LAEC",
    ["Gerenciamento e agendamento do Laboratório de",
     "Análise Experimental do Comportamento da UNIALFA.",
     "Back-end em microsserviços com gateway e auth."],
    ["Spring Boot", "PostgreSQL", "Angular", "JWT"], VIOLET, CYAN))
save("card-calculadora.svg", card(1, "Calculadora UNIALFA",
    ["Simulador das notas N1 a N4 conforme a",
     "Resolução 063/2023: mostra a situação do aluno",
     "e quanto falta tirar em cada etapa."],
    ["Angular", "TypeScript", "Testes"], CYAN, EMERALD))
save("footer.svg", footer())
print("ok")
