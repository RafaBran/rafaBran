// Gera uma "placa de Petri" a partir do gráfico de contribuições do GitHub.
// Cada dia do último ano é uma colônia, disposta em filotaxia (ângulo áureo),
// do dia mais antigo (centro) ao mais recente (borda). O tamanho e a cor
// da colônia acompanham o número de contribuições do dia.
//
// Uso: GITHUB_TOKEN=... GITHUB_USER=RafaBran node scripts/petri.mjs dist
//      MOCK=1 node scripts/petri.mjs dist   (dados de teste, sem rede)

import { mkdirSync, writeFileSync } from "node:fs";
import { join } from "node:path";

const outDir = process.argv[2] ?? "dist";
const user = process.env.GITHUB_USER;

async function fetchDays() {
  if (process.env.MOCK) {
    const days = [];
    const start = new Date(Date.UTC(2025, 10, 21));
    for (let i = 0; i < 365; i++) {
      const d = new Date(start.getTime() + i * 864e5);
      const weekday = d.getUTCDay() % 6 !== 0;
      const r = Math.abs(Math.sin(i * 12.9898) * 43758.5453) % 1;
      const count = weekday && r > 0.25 ? Math.floor(r * r * 14) : r > 0.85 ? 1 : 0;
      days.push({ date: d.toISOString().slice(0, 10), count });
    }
    return days;
  }
  const query = `query($login:String!){user(login:$login){contributionsCollection{
    contributionCalendar{weeks{contributionDays{date contributionCount}}}}}}`;
  const res = await fetch("https://api.github.com/graphql", {
    method: "POST",
    headers: {
      Authorization: `bearer ${process.env.GITHUB_TOKEN}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ query, variables: { login: user } }),
  });
  if (!res.ok) throw new Error(`GitHub API ${res.status}: ${await res.text()}`);
  const json = await res.json();
  if (json.errors) throw new Error(JSON.stringify(json.errors));
  return json.data.user.contributionsCollection.contributionCalendar.weeks
    .flatMap((w) => w.contributionDays)
    .map((d) => ({ date: d.date, count: d.contributionCount }));
}

const THEMES = {
  dark: {
    bg: "#0d1117", fg: "#e6edf3", muted: "#8b949e", agar: "#1b2a1f", rim: "#3d4a40",
    empty: "#2a3a2e", levels: ["#0e4429", "#006d32", "#26a641", "#39d353"],
  },
  light: {
    bg: "#ffffff", fg: "#1f2328", muted: "#59636e", agar: "#f3f8ec", rim: "#c9d6c0",
    empty: "#dfe8d6", levels: ["#9be9a8", "#40c463", "#30a14e", "#216e39"],
  },
};

const SANS = "-apple-system, 'Segoe UI', Helvetica, Arial, sans-serif";
const GOLDEN = Math.PI * (3 - Math.sqrt(5)); // ~137,5°

function render(days, t) {
  const W = 900, H = 420;
  const cx = 230, cy = 210, R = 172;
  const n = days.length;
  const max = Math.max(1, ...days.map((d) => d.count));
  const total = days.reduce((s, d) => s + d.count, 0);
  const active = days.filter((d) => d.count > 0).length;

  // maior sequência de dias seguidos com contribuição
  let streak = 0, run = 0;
  for (const d of days) { run = d.count > 0 ? run + 1 : 0; streak = Math.max(streak, run); }

  const spacing = (R - 12) / Math.sqrt(n);
  const colonies = days.map((d, i) => {
    const r = spacing * Math.sqrt(i + 0.5);
    const a = i * GOLDEN;
    const x = (cx + r * Math.cos(a)).toFixed(1);
    const y = (cy + r * Math.sin(a)).toFixed(1);
    if (d.count === 0) return `<circle cx="${x}" cy="${y}" r="1.6" fill="${t.empty}"/>`;
    const q = d.count / max;
    const level = Math.min(3, Math.floor(q * 4));
    const size = (2.6 + 4.4 * Math.sqrt(q)).toFixed(2);
    const recent = i >= n - 14;
    const cls = recent ? ` class="new" style="animation-delay:${((i % 7) * 0.3).toFixed(1)}s"` : "";
    return `<circle cx="${x}" cy="${y}" r="${size}" fill="${t.levels[level]}"${cls}><title>${d.date}: ${d.count}</title></circle>`;
  });

  const tx = 470;
  const fmt = (v) => v.toLocaleString("pt-BR");
  const stat = (y, value, label) =>
    `<text x="${tx}" y="${y}" font-family="${SANS}" font-size="30" font-weight="700" fill="${t.fg}">${value}</text>` +
    `<text x="${tx}" y="${y + 22}" font-family="${SANS}" font-size="14" fill="${t.muted}">${label}</text>`;

  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${W} ${H}" width="${W}" height="${H}" role="img" aria-label="Placa de Petri com ${total} contribuições no último ano">
<style>
  .new{transform-box:fill-box;transform-origin:center;animation:pulse 2.4s ease-in-out infinite}
  @keyframes pulse{50%{transform:scale(1.35);opacity:.75}}
</style>
<rect width="${W}" height="${H}" rx="14" fill="${t.bg}"/>
<circle cx="${cx}" cy="${cy}" r="${R + 8}" fill="none" stroke="${t.rim}" stroke-width="3"/>
<circle cx="${cx}" cy="${cy}" r="${R}" fill="${t.agar}" stroke="${t.rim}" stroke-width="1.5"/>
${colonies.join("\n")}
<text x="${tx}" y="62" font-family="${SANS}" font-size="20" font-weight="700" fill="${t.fg}">Cultura de commits</text>
<text x="${tx}" y="86" font-family="${SANS}" font-size="14" fill="${t.muted}">cada colônia é um dia do último ano, em filotaxia (137,5°)</text>
<text x="${tx}" y="106" font-family="${SANS}" font-size="14" fill="${t.muted}">do centro (mais antigo) à borda (mais recente)</text>
${stat(160, fmt(total), "contribuições no último ano")}
${stat(232, fmt(active), "dias com atividade")}
${stat(304, `${streak} dias`, "maior sequência seguida")}
<text x="${tx}" y="380" font-family="${SANS}" font-size="12" fill="${t.muted}">atualizada em ${days.at(-1).date.split("-").reverse().join("/")}</text>
</svg>`;
}

const days = await fetchDays();
mkdirSync(outDir, { recursive: true });
for (const [name, t] of Object.entries(THEMES)) {
  writeFileSync(join(outDir, `petri-${name}.svg`), render(days, t));
}
console.log(`placa gerada com ${days.length} dias`);
