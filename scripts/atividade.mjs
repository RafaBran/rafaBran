// Gera o gráfico de atividade do perfil a partir das contribuições do último ano.
// Uso: GITHUB_TOKEN=... GITHUB_USER=RafaBran node scripts/atividade.mjs dist
//      MOCK=1 node scripts/atividade.mjs dist   (dados de teste, sem rede)

import { mkdirSync, writeFileSync } from "node:fs";
import { join } from "node:path";

const outDir = process.argv[2] ?? "dist";

async function fetchWeeks() {
  if (process.env.MOCK) {
    return Array.from({ length: 53 }, (_, w) =>
      Array.from({ length: 7 }, (_, d) => {
        const i = w * 7 + d;
        const r = Math.abs(Math.sin(i * 12.9898) * 43758.5453) % 1;
        const trend = 0.5 + 0.5 * Math.sin(w / 6);
        const count = d % 6 && r > 0.3 ? Math.floor(r * 9 * trend) : 0;
        const date = new Date(Date.UTC(2025, 10, 16) + i * 864e5).toISOString().slice(0, 10);
        return { date, count };
      }));
  }
  const query = `query($login:String!){user(login:$login){contributionsCollection{
    contributionCalendar{weeks{contributionDays{date contributionCount}}}}}}`;
  const res = await fetch("https://api.github.com/graphql", {
    method: "POST",
    headers: { Authorization: `bearer ${process.env.GITHUB_TOKEN}`, "Content-Type": "application/json" },
    body: JSON.stringify({ query, variables: { login: process.env.GITHUB_USER } }),
  });
  if (!res.ok) throw new Error(`GitHub API ${res.status}: ${await res.text()}`);
  const json = await res.json();
  if (json.errors) throw new Error(JSON.stringify(json.errors));
  return json.data.user.contributionsCollection.contributionCalendar.weeks.map((w) =>
    w.contributionDays.map((d) => ({ date: d.date, count: d.contributionCount })));
}

const BG = "#070b18", FG = "#f1f5f9", MUTED = "#94a3b8";
const VIOLET = "#8b5cf6", CYAN = "#22d3ee", PINK = "#f472b6";
const SANS = "'Segoe UI', -apple-system, Helvetica, Arial, sans-serif";
const MONO = "ui-monospace, SFMono-Regular, Consolas, monospace";
const MESES = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"];

// curva suave (Catmull-Rom -> Bézier)
function smooth(pts, floor) {
  let d = `M${pts[0][0]},${pts[0][1]}`;
  for (let i = 0; i < pts.length - 1; i++) {
    const p0 = pts[i - 1] ?? pts[i], p1 = pts[i], p2 = pts[i + 1], p3 = pts[i + 2] ?? p2;
    const c1 = [p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6];
    const c2 = [p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6];
    c1[1] = Math.min(c1[1], floor); c2[1] = Math.min(c2[1], floor);
    d += ` C${c1.map((v) => v.toFixed(1))} ${c2.map((v) => v.toFixed(1))} ${p2.map((v) => v.toFixed(1))}`;
  }
  return d;
}

function render(weeks) {
  const W = 1200, H = 360;
  const days = weeks.flat();
  const totals = weeks.map((w) => w.reduce((s, d) => s + d.count, 0));
  const total = totals.reduce((a, b) => a + b, 0);
  const active = days.filter((d) => d.count > 0).length;
  let streak = 0, run = 0;
  for (const d of days) { run = d.count > 0 ? run + 1 : 0; streak = Math.max(streak, run); }
  const best = Math.max(...totals);

  const gx = 330, gw = W - gx - 50, gy = 70, gh = 220;
  const max = Math.max(1, best);
  const pts = totals.map((v, i) => [gx + (i / (totals.length - 1)) * gw, gy + gh - (v / max) * gh]);
  const line = smooth(pts, gy + gh);
  const area = `${line} L${gx + gw},${gy + gh} L${gx},${gy + gh} Z`;

  const grid = [0.25, 0.5, 0.75, 1].map((f) =>
    `<line x1="${gx}" x2="${gx + gw}" y1="${gy + gh - f * gh}" y2="${gy + gh - f * gh}" stroke="#ffffff" stroke-opacity=".06"/>`).join("");
  const months = [];
  let last = -1;
  weeks.forEach((w, i) => {
    const m = Number(w[0].date.slice(5, 7)) - 1;
    if (m !== last && i > 0) {
      months.push(`<text x="${pts[i][0].toFixed(0)}" y="${gy + gh + 28}" text-anchor="middle" font-family="${MONO}" font-size="12" fill="${MUTED}">${MESES[m]}</text>`);
    }
    last = m;
  });
  const fmt = (v) => v.toLocaleString("pt-BR");
  const stat = (y, v, l, c) =>
    `<text x="48" y="${y}" font-family="${SANS}" font-size="40" font-weight="800" fill="${c}">${v}</text>` +
    `<text x="48" y="${y + 24}" font-family="${SANS}" font-size="14" fill="${MUTED}">${l}</text>`;
  const hoje = days.at(-1).date.split("-").reverse().join("/");

  return `<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 ${W} ${H}" width="${W}" height="${H}" role="img" aria-label="${total} contribuições no último ano">
<defs>
  <linearGradient id="stroke" x1="0" x2="1"><stop offset="0" stop-color="${VIOLET}"/><stop offset=".5" stop-color="${CYAN}"/><stop offset="1" stop-color="${PINK}"/></linearGradient>
  <linearGradient id="fill" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="${CYAN}" stop-opacity=".35"/><stop offset="1" stop-color="${VIOLET}" stop-opacity="0"/></linearGradient>
  <filter id="glow" x="-10%" y="-50%" width="120%" height="200%"><feGaussianBlur stdDeviation="8"/></filter>
  <filter id="dotglow" x="-200%" y="-200%" width="500%" height="500%"><feGaussianBlur stdDeviation="6"/></filter>
  <clipPath id="frame"><rect width="${W}" height="${H}" rx="22"/></clipPath>
</defs>
<g clip-path="url(#frame)">
  <rect width="${W}" height="${H}" fill="${BG}"/>
  <text x="48" y="58" font-family="${MONO}" font-size="14" fill="${CYAN}">atividade / últimos 12 meses</text>
  ${stat(122, fmt(total), "contribuições", FG)}
  ${stat(198, fmt(active), "dias com atividade", FG)}
  ${stat(274, `${streak}d`, "maior sequência", FG)}
  ${grid}
  <path d="${area}" fill="url(#fill)"/>
  <path d="${line}" fill="none" stroke="url(#stroke)" stroke-width="8" opacity=".55" filter="url(#glow)"/>
  <path id="curve" d="${line}" fill="none" stroke="url(#stroke)" stroke-width="3" stroke-linecap="round"/>
  <g>
    <circle r="12" fill="${CYAN}" filter="url(#dotglow)"/>
    <circle r="4.5" fill="#ffffff"/>
    <animateMotion dur="9s" repeatCount="indefinite" calcMode="linear"><mpath xlink:href="#curve"/></animateMotion>
  </g>
  ${months.join("")}
  <text x="${W - 50}" y="${H - 18}" text-anchor="end" font-family="${MONO}" font-size="11" fill="${MUTED}">atualizado em ${hoje}</text>
  <rect width="${W}" height="${H}" rx="22" fill="none" stroke="#ffffff" stroke-opacity=".08"/>
</g>
</svg>`;
}

const weeks = await fetchWeeks();
mkdirSync(outDir, { recursive: true });
writeFileSync(join(outDir, "atividade.svg"), render(weeks));
console.log(`gráfico gerado com ${weeks.length} semanas`);
