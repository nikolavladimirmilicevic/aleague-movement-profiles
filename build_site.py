import json

data = json.load(open('/home/claude/site_data.json'))
DATA_JS = json.dumps(data, ensure_ascii=False, separators=(',', ':'))

HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>A-League movement profiles</title>
<meta name="description" content="How every A-League player moves: off-ball runs, physical output and passing, from SkillCorner broadcast tracking data. Percentile profiles and style similarity search." />
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22%3E%3Ctext y=%22.9em%22 font-size=%2290%22%3E%E2%9A%BD%3C/text%3E%3C/svg%3E" />
<meta property="og:title" content="A-League movement profiles" />
<meta property="og:description" content="Percentile movement profiles and style similarity for 146 A-League players, built on SkillCorner open tracking data." />
<meta property="og:type" content="website" />
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Barlow:wght@400;500;600&family=Barlow+Condensed:wght@500;600;700&display=swap" rel="stylesheet">
<style>
:root{
  --pitch:#0F1A15;      /* floodlit grass, near black but green */
  --pitch-2:#16241D;    /* raised surface */
  --line:#2A3A32;       /* chalk line, dimmed */
  --chalk:#E9EFE8;      /* primary ink */
  --chalk-dim:#8FA096;  /* secondary ink */
  --signal:#E0A33E;     /* the selected player */
  --ghost:#5FB6C4;      /* the compared player */
  --phys:#7FB069; --move:#E0A33E; --pass:#5FB6C4;
}
*,*::before,*::after{box-sizing:border-box}
html,body{margin:0;padding:0}
body{
  background:var(--pitch); color:var(--chalk);
  font-family:Barlow,system-ui,sans-serif; font-size:15px; line-height:1.5;
  -webkit-font-smoothing:antialiased;
}
h1,h2,h3,.cond{font-family:"Barlow Condensed",Barlow,system-ui,sans-serif;font-weight:600;letter-spacing:.01em}
a{color:var(--ghost)}
.wrap{max-width:1180px;margin:0 auto;padding:28px 20px 64px}

/* header ------------------------------------------------------------ */
header{border-bottom:1px solid var(--line);padding-bottom:18px;margin-bottom:22px}
h1{font-size:34px;margin:0 0 4px;line-height:1.05}
.sub{color:var(--chalk-dim);max-width:62ch;margin:0}
.sub b{color:var(--chalk);font-weight:600}

/* layout ------------------------------------------------------------ */
.cols{display:grid;grid-template-columns:270px 1fr;gap:24px;align-items:stretch}
@media(max-width:860px){
  .cols{grid-template-columns:1fr}
  .rail{position:static;min-height:0}
  .panel{position:static}
}

/* left panel -------------------------------------------------------- */
.rail{position:relative;min-height:460px}
.panel{position:absolute;inset:0;background:var(--pitch-2);border:1px solid var(--line);
  border-radius:4px;display:flex;flex-direction:column;min-height:0}
.controls{padding:12px}
input[type=search],select{
  width:100%;background:var(--pitch);color:var(--chalk);
  border:1px solid var(--line);border-radius:3px;padding:8px 10px;
  font-family:inherit;font-size:14px;margin-bottom:8px
}
input:focus-visible,select:focus-visible,button:focus-visible,li:focus-visible{
  outline:2px solid var(--signal);outline-offset:2px}
ul.list{list-style:none;margin:0;padding:0;flex:1 1 auto;min-height:0;overflow-y:auto}
@media(max-width:860px){ul.list{flex:none;max-height:280px}}
ul.list li{
  padding:7px 12px;cursor:pointer;border-top:1px solid var(--line);
  display:flex;justify-content:space-between;gap:8px;align-items:baseline}
ul.list li:hover{background:#1D2E25}
ul.list li[aria-selected=true]{background:#243A2E;box-shadow:inset 3px 0 0 var(--signal)}
.li-name{font-weight:500}
.li-meta{color:var(--chalk-dim);font-size:12.5px;white-space:nowrap}
.count{color:var(--chalk-dim);font-size:13px;padding:8px 12px 10px;border-top:1px solid var(--line);flex:none}

/* player head ------------------------------------------------------- */
.who{display:flex;flex-wrap:wrap;align-items:baseline;gap:10px 14px;margin-bottom:2px}
.who h2{font-size:30px;margin:0;line-height:1}
.who .team{color:var(--chalk-dim)}
.facts{color:var(--chalk-dim);font-size:14px;margin:0 0 18px}

/* fingerprint + notes ----------------------------------------------- */
.top{display:grid;grid-template-columns:minmax(0,420px) 1fr;gap:24px;align-items:start}
@media(max-width:760px){.top{grid-template-columns:1fr}}
svg.fp{width:100%;height:auto;display:block}
.legend{display:flex;gap:14px;flex-wrap:wrap;font-size:13px;color:var(--chalk-dim);margin-top:2px}
.key{display:inline-flex;align-items:center;gap:6px}
.dot{width:9px;height:9px;border-radius:2px;display:inline-block}

.notes h3{font-size:19px;margin:0 0 6px}
.notes ul{margin:0 0 16px;padding-left:0;list-style:none}
.notes li{display:flex;justify-content:space-between;gap:12px;padding:3px 0;border-bottom:1px solid var(--line)}
.pn{font-size:14px}
.pv{font-variant-numeric:tabular-nums;font-weight:600}

/* bars -------------------------------------------------------------- */
.cat{margin-top:26px}
.cat h3{font-size:19px;margin:0 0 8px;display:flex;align-items:center;gap:8px}
.bar-row{display:grid;grid-template-columns:180px 1fr 52px;gap:10px;align-items:center;padding:3px 0}
@media(max-width:560px){.bar-row{grid-template-columns:130px 1fr 46px}}
.bar-lab{font-size:13.5px;color:var(--chalk-dim)}
.track{display:block;background:#0C1410;border:1px solid var(--line);height:14px;border-radius:2px;position:relative;overflow:hidden}
.fill{display:block;height:100%;opacity:.9}
.gmark{position:absolute;top:-2px;bottom:-2px;width:2px;background:var(--ghost)}
.bar-val{text-align:right;font-variant-numeric:tabular-nums;font-size:13.5px}
.raw{color:var(--chalk-dim);font-size:12px}

/* similar ----------------------------------------------------------- */
table{width:100%;border-collapse:collapse;margin-top:6px}
th{text-align:left;font-family:"Barlow Condensed";font-weight:600;font-size:14px;
   color:var(--chalk-dim);border-bottom:1px solid var(--line);padding:4px 6px}
td{padding:5px 6px;border-bottom:1px solid var(--line);font-size:14px}
td.n{font-variant-numeric:tabular-nums;text-align:right}
button.link{background:none;border:0;color:var(--chalk);font:inherit;cursor:pointer;padding:0;text-align:left}
button.link:hover{color:var(--signal)}
button.cmp{background:none;border:1px solid var(--line);color:var(--chalk-dim);
  font:inherit;font-size:12.5px;border-radius:3px;padding:1px 8px;cursor:pointer}
button.cmp:hover{border-color:var(--ghost);color:var(--ghost)}
button.cmp[aria-pressed=true]{border-color:var(--ghost);color:var(--pitch);background:var(--ghost)}

footer{margin-top:44px;padding-top:16px;border-top:1px solid var(--line);
  color:var(--chalk-dim);font-size:13.5px;max-width:72ch}
details.method{margin-top:10px}
details.method summary{cursor:pointer;color:var(--chalk)}
details.method p{margin:8px 0}
</style>
</head>
<body>
<div class="wrap">

<header>
  <h1>A-League movement profiles</h1>
  <p class="sub">How <b>146 players</b> actually moved in the 2024/25 season: the runs they made off the ball,
     the ground they covered, and the passes they attempted. Every number is a percentile
     against others in the same position, from SkillCorner broadcast tracking data.</p>
</header>

<div class="cols">
  <div class="rail"><div class="panel">
    <div class="controls">
      <label for="q" class="sr-only" style="position:absolute;left:-9999px">Search players</label>
      <input id="q" type="search" placeholder="Search player or club" autocomplete="off">
      <select id="pos"><option value="">All positions</option></select>
    </div>
    <ul class="list" id="list" role="listbox" aria-label="Players"></ul>
    <p class="count" id="count"></p>
  </div></div>

  <main id="detail"></main>
</div>

<footer>
  <p>Data: <a href="https://github.com/SkillCorner/opendata">SkillCorner Open Data</a>,
     A-League Men 2024/25 season aggregates, released with PySport.
     Built by Nikola Milićević.</p>
  <details class="method">
    <summary>How the numbers are built</summary>
    <p>Broadcast tracking data is generated by computer vision from TV footage, so it covers far more
       leagues than multi-camera systems but does not see every player in every frame. SkillCorner
       derives run types, physical output and passing from those tracks.</p>
    <p>Rates are normalised by SkillCorner per 30 minutes of team possession, so a player at a
       possession-heavy club is not flattered by volume. Peak speed is the 99th percentile of a
       player's sprint velocity, which discards tracking noise at the very top.</p>
    <p>Each player is then ranked against others in the same position group, because eight kilometres
       from a centre-back and eight from a winger mean different things. Players with fewer than
       eight matches are excluded. Where a player changed role during the season, the role he played
       most is used.</p>
    <p>Similarity is Euclidean distance across all 25 percentiles, within position. It measures how
       alike two players' movement is, not how good they are.</p>
  </details>
</footer>
</div>

<script>
const DB = __DATA__;
const F = DB.features, P = DB.players;
const CATS = ["Physical","Movement","Passing"];
const CATCOLOR = {Physical:"var(--phys)", Movement:"var(--move)", Passing:"var(--pass)"};
const idx = {}; CATS.forEach(c => idx[c] = F.map((f,i)=>[f,i]).filter(x=>x[0].cat===c).map(x=>x[1]));

let sel = P[0], ghost = null;

/* ---------- similarity ---------- */
function similar(p, n){
  const pool = P.filter(o => o.id !== p.id && o.pos === p.pos);
  const worst = Math.sqrt(F.length) * 100;
  return pool.map(o => {
    let s = 0;
    for (let i = 0; i < F.length; i++){
      const a = p.p[i] == null ? 50 : p.p[i], b = o.p[i] == null ? 50 : o.p[i];
      s += (a-b)*(a-b);
    }
    return {o, score: (1 - Math.sqrt(s)/worst) * 100};
  }).sort((x,y) => y.score - x.score).slice(0, n);
}

/* ---------- fingerprint ---------- */
function fingerprint(p, g){
  const N = F.length, S = 420, C = S/2, R0 = 62, R1 = 180;
  const A = i => (i/N) * 2*Math.PI - Math.PI/2;
  const pt = (i, r) => [C + r*Math.cos(A(i)), C + r*Math.sin(A(i))];
  let s = `<svg class="fp" viewBox="0 0 ${S} ${S}" role="img" aria-label="Movement profile of ${p.name}">`;
  // grid rings
  [25,50,75,100].forEach(v => {
    const r = R0 + (R1-R0)*v/100;
    s += `<circle cx="${C}" cy="${C}" r="${r.toFixed(1)}" fill="none" stroke="var(--line)" stroke-width="1"${v===50?' stroke-dasharray="3 3"':''}/>`;
  });
  // wedges
  const w = (2*Math.PI/N) * 0.78;
  for (let i = 0; i < N; i++){
    const v = p.p[i] == null ? 0 : p.p[i];
    const r = R0 + (R1-R0)*v/100;
    const a0 = A(i) - w/2, a1 = A(i) + w/2;
    const x0=C+R0*Math.cos(a0), y0=C+R0*Math.sin(a0);
    const x1=C+R0*Math.cos(a1), y1=C+R0*Math.sin(a1);
    const x2=C+r*Math.cos(a1),  y2=C+r*Math.sin(a1);
    const x3=C+r*Math.cos(a0),  y3=C+r*Math.sin(a0);
    s += `<path d="M${x0.toFixed(1)} ${y0.toFixed(1)} A${R0} ${R0} 0 0 1 ${x1.toFixed(1)} ${y1.toFixed(1)} L${x2.toFixed(1)} ${y2.toFixed(1)} A${r.toFixed(1)} ${r.toFixed(1)} 0 0 0 ${x3.toFixed(1)} ${y3.toFixed(1)} Z" fill="${CATCOLOR[F[i].cat]}" opacity="${(0.35 + 0.55*v/100).toFixed(2)}"/>`;
  }
  // ghost outline
  if (g){
    let d = "";
    for (let i = 0; i <= N; i++){
      const j = i % N, v = g.p[j] == null ? 0 : g.p[j];
      const [x,y] = pt(j, R0 + (R1-R0)*v/100);
      d += (i ? "L" : "M") + x.toFixed(1) + " " + y.toFixed(1) + " ";
    }
    s += `<path d="${d}Z" fill="none" stroke="var(--ghost)" stroke-width="2" stroke-linejoin="round"/>`;
  }
  // category arcs
  CATS.forEach(c => {
    const ii = idx[c]; if (!ii.length) return;
    const a0 = A(ii[0]) - w/2 - 0.02, a1 = A(ii[ii.length-1]) + w/2 + 0.02, r = R1 + 13;
    const big = (a1-a0) > Math.PI ? 1 : 0;
    s += `<path d="M${(C+r*Math.cos(a0)).toFixed(1)} ${(C+r*Math.sin(a0)).toFixed(1)} A${r} ${r} 0 ${big} 1 ${(C+r*Math.cos(a1)).toFixed(1)} ${(C+r*Math.sin(a1)).toFixed(1)}" fill="none" stroke="${CATCOLOR[c]}" stroke-width="2.5"/>`;
  });
  // centre
  s += `<text x="${C}" y="${C-4}" text-anchor="middle" font-family="Barlow Condensed" font-size="21" font-weight="700" fill="var(--chalk)">${p.name}</text>`;
  s += `<text x="${C}" y="${C+15}" text-anchor="middle" font-family="Barlow" font-size="12" fill="var(--chalk-dim)">${p.pos}</text>`;
  return s + "</svg>";
}

/* ---------- detail ---------- */
function bars(p, g){
  return CATS.map(c => {
    const rows = idx[c].map(i => {
      const v = p.p[i], raw = p.v[i];
      const gm = g && g.p[i] != null
        ? `<span class="gmark" style="left:calc(${g.p[i]}% - 1px)" title="${g.name}: ${Math.round(g.p[i])}"></span>` : "";
      return `<div class="bar-row">
        <span class="bar-lab">${F[i].label}</span>
        <span class="track"><span class="fill" style="width:${v==null?0:v}%;background:${CATCOLOR[c]}"></span>${gm}</span>
        <span class="bar-val">${v==null?"&ndash;":Math.round(v)}<span class="raw"> / ${raw==null?"":raw}</span></span>
      </div>`;
    }).join("");
    return `<section class="cat"><h3><span class="dot" style="background:${CATCOLOR[c]}"></span>${c}</h3>${rows}</section>`;
  }).join("");
}

function render(){
  const p = sel, g = ghost;
  const ranked = F.map((f,i) => ({f, v: p.p[i]})).filter(x => x.v != null).sort((a,b) => b.v - a.v);
  const hi = ranked.slice(0,5), lo = ranked.slice(-3).reverse();
  const sims = similar(p, 6);

  document.getElementById("detail").innerHTML = `
    <div class="who"><h2>${p.full}</h2><span class="team">${p.team}</span></div>
    <p class="facts">${p.pos} · ${p.age ? p.age + " years old · " : ""}${p.mp} matches · ${p.min} minutes per match on average</p>

    <div class="top">
      <div>
        ${fingerprint(p, g)}
        <div class="legend">
          ${CATS.map(c => `<span class="key"><span class="dot" style="background:${CATCOLOR[c]}"></span>${c}</span>`).join("")}
          ${g ? `<span class="key"><span class="dot" style="background:var(--ghost)"></span>${g.name}</span>` : ""}
        </div>
      </div>
      <div class="notes">
        <h3>Does most of</h3>
        <ul>${hi.map(x => `<li><span class="pn">${x.f.label}</span><span class="pv">${Math.round(x.v)}</span></li>`).join("")}</ul>
        <h3>Does least of</h3>
        <ul>${lo.map(x => `<li><span class="pn">${x.f.label}</span><span class="pv">${Math.round(x.v)}</span></li>`).join("")}</ul>
      </div>
    </div>

    ${bars(p, g)}

    <section class="cat">
      <h3>Moves most like</h3>
      <table><thead><tr>
        <th>Player</th><th>Club</th><th style="text-align:right">Matches</th>
        <th style="text-align:right">Similarity</th><th></th></tr></thead><tbody>
      ${sims.map(s => `<tr>
        <td><button class="link" data-go="${s.o.id}">${s.o.name}</button></td>
        <td>${s.o.team}</td>
        <td class="n">${s.o.mp}</td>
        <td class="n">${s.score.toFixed(1)}</td>
        <td style="text-align:right"><button class="cmp" data-cmp="${s.o.id}" aria-pressed="${g && g.id === s.o.id}">overlay</button></td>
      </tr>`).join("")}
      </tbody></table>
    </section>`;

  document.querySelectorAll("[data-go]").forEach(b => b.onclick = () => {
    sel = P.find(x => x.id == b.dataset.go); ghost = null; paintList(); render();
    window.scrollTo({top:0, behavior:"smooth"});
  });
  document.querySelectorAll("[data-cmp]").forEach(b => b.onclick = () => {
    const o = P.find(x => x.id == b.dataset.cmp);
    ghost = (ghost && ghost.id === o.id) ? null : o; render();
  });
}

/* ---------- list ---------- */
function paintList(){
  const q = document.getElementById("q").value.trim().toLowerCase();
  const pos = document.getElementById("pos").value;
  const rows = P.filter(p =>
    (!pos || p.pos === pos) &&
    (!q || p.name.toLowerCase().includes(q) || p.full.toLowerCase().includes(q)
        || p.team.toLowerCase().includes(q)));
  document.getElementById("list").innerHTML = rows.map(p =>
    `<li role="option" tabindex="0" data-id="${p.id}" aria-selected="${p.id === sel.id}">
       <span class="li-name">${p.name}</span><span class="li-meta">${p.team}</span></li>`).join("")
    || `<li style="color:var(--chalk-dim)">No player matches that search.</li>`;
  document.getElementById("count").textContent =
    rows.length + (rows.length === 1 ? " player" : " players");
  document.querySelectorAll("#list li[data-id]").forEach(li => {
    const pick = () => { sel = P.find(x => x.id == li.dataset.id); ghost = null; paintList(); render(); };
    li.onclick = pick;
    li.onkeydown = e => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); pick(); } };
  });
}

[...new Set(P.map(p => p.pos))].sort().forEach(v => {
  const o = document.createElement("option"); o.value = o.textContent = v;
  document.getElementById("pos").appendChild(o);
});
document.getElementById("q").oninput = paintList;
document.getElementById("pos").onchange = paintList;
paintList(); render();
</script>
</body>
</html>
"""

open('/home/claude/aleague.html', 'w', encoding='utf-8').write(HTML.replace('__DATA__', DATA_JS))
print("written", len(HTML.replace('__DATA__', DATA_JS)) / 1024, "KB")
