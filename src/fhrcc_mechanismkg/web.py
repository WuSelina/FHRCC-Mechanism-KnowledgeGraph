"""Export the graph as a single-file interactive explorer (Cytoscape.js from a CDN, no build step)."""
from __future__ import annotations
import json
import textwrap
from pathlib import Path
from typing import Any, Dict, List
from .analysis import (
    GROUP_LABELS,
    NODE_GROUPS,
    cost_parts,
    is_hypothesis,
    is_inhibitory,
    reachable,
)
from .graph import Graph
from .layout import layered_layout
from .reasoning.path_search import k_shortest_paths_explainable

CYTOSCAPE_URL = "https://cdn.jsdelivr.net/npm/cytoscape@3.30.4/dist/cytoscape.min.js"


def build_payload(graph: Graph, source: str, k: int = 5, max_hops: int = 14) -> Dict[str, Any]:
    pos = layered_layout(graph)
    nodes = []
    for n in graph.nodes.values():
        x, y = pos[n.id]
        nodes.append(
            {
                "id": n.id,
                "label": textwrap.fill(n.name, 20),
                "name": n.name,
                "type": n.type,
                "group": NODE_GROUPS.get(n.type, "mechanism"),
                "description": n.description,
                "tags": n.tags,
                "x": x * 215,
                "y": y * 78,
            }
        )
    edges = []
    for i, e in enumerate(graph.edges):
        edges.append(
            {
                "id": f"e{i}",
                "source": e.subject,
                "target": e.object,
                "predicate": e.predicate,
                "weight": e.weight,
                "evidence": e.evidence_level,
                "mechanism": e.mechanism,
                "notes": e.notes,
                "hyp": is_hypothesis(e),
                "inh": is_inhibitory(e),
                "cost": round(sum(cost_parts(e)), 3),
            }
        )
    eid = {(e["source"], e["predicate"], e["target"]): e["id"] for e in edges}

    targets = [n.id for n in graph.nodes.values() if n.type == "phenotype" and n.id != source]
    paths: Dict[str, List[Dict[str, Any]]] = {}
    supported_only: Dict[str, bool] = {}
    for t in targets:
        found = k_shortest_paths_explainable(graph, source, t, k = k, max_hops = max_hops)
        if not found:
            continue
        paths[t] = [
            {
                "cost": round(p.total_cost, 3),
                "hops": len(p.steps),
                "edges": [eid[(s.edge.subject, s.edge.predicate, s.edge.object)] for s in p.steps],
            }
            for p in found
        ]
        supported_only[t] = reachable(graph, source, t, include_hypothesis = False)

    return {
        "source": source,
        "nodes": nodes,
        "edges": edges,
        "paths": paths,
        "supportedReach": supported_only,
        "groupLabels": GROUP_LABELS,
        "defaultTarget": "phenotype:cancer" if "phenotype:cancer" in paths else next(iter(paths), None),
    }


def write_explorer(graph: Graph, out_path: str, source: str) -> None:
    payload = json.dumps(build_payload(graph, source), ensure_ascii = False).replace("</", "<\\/")
    html = TEMPLATE.replace("__DATA__", payload).replace("__CYTOSCAPE__", CYTOSCAPE_URL)
    p = Path(out_path)
    p.parent.mkdir(parents = True, exist_ok = True)
    p.write_text(html, encoding = "utf-8")


TEMPLATE = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>FHRCC Mechanism Explorer</title>
<meta name="description" content="Interactive knowledge graph of mechanisms linking FH loss to cancer in fumarate hydratase-deficient renal cell carcinoma.">
<style>
:root {
  --page:#f9f9f7; --surface:#fcfcfb; --ink:#0b0b0b; --ink2:#52514e; --muted:#898781;
  --grid:#e1e0d9; --line:#c3c2b7; --c-molecular:#2a78d6; --c-mechanism:#1baf7a; --c-phenotype:#eb6834;
  --hi:#0b0b0b; --tint:.16;
}
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    --page:#0d0d0d; --surface:#1a1a19; --ink:#ffffff; --ink2:#c3c2b7; --muted:#898781;
    --grid:#2c2c2a; --line:#383835; --c-molecular:#3987e5; --c-mechanism:#199e70; --c-phenotype:#d95926;
    --hi:#ffffff; --tint:.28;
  }
}
:root[data-theme="dark"] {
  --page:#0d0d0d; --surface:#1a1a19; --ink:#ffffff; --ink2:#c3c2b7; --muted:#898781;
  --grid:#2c2c2a; --line:#383835; --c-molecular:#3987e5; --c-mechanism:#199e70; --c-phenotype:#d95926;
  --hi:#ffffff; --tint:.28;
}
* { box-sizing: border-box; }
body { margin:0; background:var(--page); color:var(--ink); font-family: system-ui, -apple-system, "Segoe UI", sans-serif; line-height:1.45; }
header { padding: 20px 16px 8px; max-width: 1400px; margin: 0 auto; }
h1 { font-size: 22px; margin: 0 0 4px; }
header p { margin: 0; color: var(--ink2); max-width: 78ch; font-size: 14px; }
.controls { display:flex; flex-wrap:wrap; gap:12px 20px; align-items:center; padding: 12px 16px; max-width:1400px; margin:0 auto; font-size:14px; }
.controls label { color: var(--ink2); display:flex; align-items:center; gap:6px; }
select, button { font: inherit; color: var(--ink); background: var(--surface); border:1px solid var(--line); border-radius:6px; padding:5px 8px; }
button { cursor:pointer; }
button:hover, select:hover { border-color: var(--muted); }
:focus-visible { outline: 2px solid var(--c-molecular); outline-offset: 2px; }
main { display:grid; grid-template-columns: 1fr 340px; gap:12px; padding: 0 16px 16px; max-width:1400px; margin:0 auto; }
#cy { height: 82vh; min-height: 620px; background: var(--surface); border:1px solid var(--grid); border-radius:10px; }
aside { background: var(--surface); border:1px solid var(--grid); border-radius:10px; padding: 14px; max-height: 82vh; min-height:620px; overflow:auto; font-size:13.5px; }
aside h2 { font-size: 15px; margin: 0 0 6px; }
aside h3 { font-size: 12px; text-transform: uppercase; letter-spacing:.04em; color: var(--muted); margin: 16px 0 6px; }
.muted { color: var(--ink2); }
.step { border-left: 3px solid var(--line); padding: 2px 0 2px 10px; margin: 0 0 10px; }
.step.hyp { border-left-color: var(--c-phenotype); }
.step .pred { color: var(--ink2); font-size: 12.5px; }
.chip { display:inline-block; font-size:11.5px; padding:0 7px; border-radius:99px; border:1px solid var(--line); color:var(--ink2); margin-left:4px; white-space:nowrap; }
.chip.hyp { border-color: var(--c-phenotype); color: var(--ink); }
.callout { border:1px solid var(--grid); border-left: 3px solid var(--c-phenotype); border-radius:6px; padding:8px 10px; margin: 10px 0; background: color-mix(in srgb, var(--c-phenotype) 8%, var(--surface)); }
.legend { display:flex; flex-wrap:wrap; gap:6px 16px; padding: 0 16px 12px; max-width:1400px; margin:0 auto; font-size:12.5px; color: var(--ink2); }
.legend span { display:inline-flex; align-items:center; gap:6px; }
.sw { width:14px; height:14px; border-radius:4px; border:2px solid; }
.ln { width:26px; height:0; border-top:2px solid var(--muted); }
.ln.dash { border-top-style: dashed; }
.ln.hi { border-top-color: var(--hi); border-top-width:3px; }
.tbar { width:26px; height:0; border-top:2px solid var(--muted); position:relative; }
.tbar::after { content:""; position:absolute; right:0; top:-6px; height:10px; border-right:2px solid var(--muted); }
details { max-width:1400px; margin: 0 auto; padding: 0 16px 24px; font-size: 13px; }
summary { cursor:pointer; color: var(--ink2); }
table { border-collapse: collapse; width:100%; margin-top:8px; }
th, td { text-align:left; padding:4px 8px; border-bottom:1px solid var(--grid); }
th { color: var(--muted); font-weight:600; }
footer { max-width:1400px; margin:0 auto; padding: 0 16px 28px; color: var(--muted); font-size:12.5px; }
@media (max-width: 900px) { main { grid-template-columns: 1fr; } aside { max-height:none; } #cy { height: 60vh; } }
</style>
</head>
<body>
<header>
  <h1>FH-deficient RCC mechanism explorer</h1>
  <p>How might loss of fumarate hydratase (FH) lead to cancer? Each box is a biological entity or state; each arrow is a causal claim with a confidence weight and an evidence level. Pick an outcome to see the lowest-cost explanations, or hide hypothesis-level edges to see how much of the map rests on established evidence.</p>
</header>

<div class="controls">
  <label>Outcome <select id="target"></select></label>
  <label>Explanation <select id="rank"></select></label>
  <label><input type="checkbox" id="fade"> Fade hypothesis-level edges</label>
  <button id="reset" type="button">Reset view</button>
</div>

<div class="legend" id="legend" aria-label="Legend"></div>

<main>
  <div id="cy" role="img" aria-label="Interactive graph of FH-loss mechanisms. A table of all edges follows below."></div>
  <aside id="panel" aria-live="polite"></aside>
</main>

<details>
  <summary>Table view: all edges</summary>
  <table id="edge-table"><thead><tr><th>From</th><th>Relation</th><th>To</th><th>Evidence</th><th>Weight</th></tr></thead><tbody></tbody></table>
</details>

<footer>Study tool and exploratory project, not clinical guidance. Paths are possible explanations, not predictions. Source and method: see the repository README.</footer>

<script id="kg-data" type="application/json">__DATA__</script>
<script src="__CYTOSCAPE__"></script>
<script>
(function () {
  const D = JSON.parse(document.getElementById('kg-data').textContent);
  const $ = (id) => document.getElementById(id);
  const css = (v) => getComputedStyle(document.documentElement).getPropertyValue(v).trim();
  const nameOf = Object.fromEntries(D.nodes.map(n => [n.id, n.name]));
  const edgeById = Object.fromEntries(D.edges.map(e => [e.id, e]));
  const pretty = (s) => s.replace(/_/g, ' ');
  const esc = (s) => String(s == null ? '' : s).replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));

  if (typeof cytoscape === 'undefined') {
    $('cy').innerHTML = '<p style="padding:16px" class="muted">The graph library could not be loaded (it is fetched from a CDN). Please check your connection. The table below lists every edge.</p>';
  }

  // ---- legend
  const leg = [];
  for (const g of Object.keys(D.groupLabels)) leg.push(`<span><i class="sw" style="border-color:var(--c-${g});background:color-mix(in srgb, var(--c-${g}) 20%, transparent)"></i>${esc(D.groupLabels[g])}</span>`);
  leg.push('<span><i class="ln"></i>Supported edge</span>', '<span><i class="ln dash"></i>Hypothesis-level edge</span>', '<span><i class="tbar"></i>Inhibitory</span>', '<span><i class="ln hi"></i>Selected explanation</span>', '<span>Line width = confidence</span>');
  $('legend').innerHTML = leg.join('');

  // ---- table view
  $('edge-table').tBodies[0].innerHTML = D.edges.map(e =>
    `<tr><td>${esc(nameOf[e.source])}</td><td>${esc(pretty(e.predicate))}</td><td>${esc(nameOf[e.target])}</td><td>${esc(pretty(e.evidence))}</td><td>${e.weight.toFixed(2)}</td></tr>`).join('');

  // ---- controls
  const tsel = $('target'), rsel = $('rank');
  Object.keys(D.paths).forEach(t => { const o = document.createElement('option'); o.value = t; o.textContent = nameOf[t]; tsel.appendChild(o); });
  tsel.value = D.defaultTarget;
  function fillRanks() {
    rsel.innerHTML = '';
    (D.paths[tsel.value] || []).forEach((p, i) => { const o = document.createElement('option'); o.value = i; o.textContent = `#${i + 1} (cost ${p.cost.toFixed(2)}, ${p.hops} steps)`; rsel.appendChild(o); });
  }

  let cy = null;
  function styles() {
    const ink = css('--ink'), muted = css('--muted'), hi = css('--hi'), tint = parseFloat(css('--tint'));
    const col = (g) => css('--c-' + g);
    const s = [
      { selector: 'node', style: { 'shape': 'round-rectangle', 'label': 'data(label)', 'text-wrap': 'wrap', 'text-max-width': 120, 'text-valign': 'center', 'text-halign': 'center', 'font-size': 11, 'color': ink, 'width': 'label', 'height': 'label', 'padding': '9px', 'border-width': 2, 'background-opacity': tint } },
      { selector: 'edge', style: { 'curve-style': 'bezier', 'line-color': muted, 'target-arrow-color': muted, 'target-arrow-shape': 'triangle', 'arrow-scale': 1.1, 'width': 'mapData(weight, 0.2, 0.9, 1, 4)', 'opacity': 0.7 } },
      { selector: 'edge.inh', style: { 'target-arrow-shape': 'tee' } },
      { selector: 'edge.hyp', style: { 'line-style': 'dashed', 'line-dash-pattern': [6, 4] } },
      { selector: 'edge.faded', style: { 'opacity': 0.08 } },
      { selector: '.dim', style: { 'opacity': 0.22 } },
      { selector: 'edge.on', style: { 'line-color': hi, 'target-arrow-color': hi, 'opacity': 1, 'z-index': 20, 'width': 'mapData(weight, 0.2, 0.9, 2.5, 5.5)' } },
      { selector: 'node.on', style: { 'border-width': 3.5, 'opacity': 1 } },
      { selector: 'node:selected', style: { 'border-width': 4, 'overlay-opacity': 0 } },
    ];
    for (const g of Object.keys(D.groupLabels)) s.push({ selector: `node[group = "${g}"]`, style: { 'background-color': col(g), 'border-color': col(g) } });
    return s;
  }

  function build() {
    if (typeof cytoscape === 'undefined') return;
    cy = cytoscape({
      container: $('cy'),
      elements: [
        ...D.nodes.map(n => ({ data: { id: n.id, label: n.label, group: n.group }, position: { x: n.x, y: n.y } })),
        ...D.edges.map(e => ({ data: { id: e.id, source: e.source, target: e.target, weight: e.weight }, classes: (e.hyp ? 'hyp ' : '') + (e.inh ? 'inh' : '') })),
      ],
      layout: { name: 'preset' },
      style: styles(),
      wheelSensitivity: 0.25,
      minZoom: 0.25, maxZoom: 2.5,
    });
    cy.on('tap', 'node', (ev) => showNode(ev.target.id()));
    cy.on('tap', (ev) => { if (ev.target === cy) { cy.$(':selected').unselect(); showPath(); } });
    cy.on('tap', 'edge', (ev) => showEdge(ev.target.id()));
  }

  function evChip(e) { return `<span class="chip${e.hyp ? ' hyp' : ''}">${esc(pretty(e.evidence))}</span>`; }

  function applyFade() {
    if (!cy) return;
    const on = $('fade').checked;
    cy.edges('.hyp').toggleClass('faded', on);
    cy.edges('.hyp.on').removeClass('faded');
  }

  function showPath() {
    const t = tsel.value, r = parseInt(rsel.value || '0', 10) || 0;
    const p = (D.paths[t] || [])[r];
    if (cy) { cy.elements().removeClass('on dim'); }
    if (!p) { $('panel').innerHTML = '<p class="muted">No path found.</p>'; return; }
    const ids = new Set(p.edges);
    if (cy) {
      cy.elements().addClass('dim');
      const nodes = new Set([D.source]);
      p.edges.forEach(id => { const e = edgeById[id]; nodes.add(e.source); nodes.add(e.target); });
      cy.edges().filter(e => ids.has(e.id())).removeClass('dim').addClass('on');
      cy.nodes().filter(n => nodes.has(n.id())).removeClass('dim').addClass('on');
      applyFade();
    }
    const hypN = p.edges.filter(id => edgeById[id].hyp).length;
    let h = `<h2>${esc(nameOf[D.source])} → ${esc(nameOf[t])}</h2><p class="muted">Explanation #${r + 1}: cost ${p.cost.toFixed(2)} across ${p.hops} steps. Lower cost means higher-confidence, more specific edges.</p>`;
    if (!D.supportedReach[t]) h += `<div class="callout"><b>No route uses supported edges alone.</b> Every route from ${esc(nameOf[D.source])} to ${esc(nameOf[t])} passes through at least one hypothesis-level edge${hypN ? ` (this one has ${hypN})` : ''}. That is where new evidence would change the map most.</div>`;
    h += '<h3>Steps</h3>';
    p.edges.forEach((id, i) => {
      const e = edgeById[id];
      h += `<div class="step${e.hyp ? ' hyp' : ''}"><div>${i + 1}. ${esc(nameOf[e.source])} → ${esc(nameOf[e.target])}</div><div class="pred">${esc(pretty(e.predicate))}, w = ${e.weight.toFixed(2)}${evChip(e)}</div>${e.mechanism ? `<div class="muted">${esc(e.mechanism)}</div>` : ''}${e.notes ? `<div class="muted"><i>${esc(e.notes)}</i></div>` : ''}</div>`;
    });
    h += '<p class="muted">Click any box or arrow for details.</p>';
    $('panel').innerHTML = h;
  }

  function showNode(id) {
    const n = D.nodes.find(x => x.id === id);
    const ins = D.edges.filter(e => e.target === id), outs = D.edges.filter(e => e.source === id);
    const li = (e, other) => `<li>${esc(pretty(e.predicate))} ${esc(nameOf[other])}${evChip(e)}</li>`;
    $('panel').innerHTML = `<h2>${esc(n.name)}</h2><p class="muted">${esc(pretty(n.type))}${n.tags.length ? ' · ' + esc(n.tags.map(pretty).join(', ')) : ''}</p>${n.description ? `<p>${esc(n.description)}</p>` : ''}
      <h3>Caused or influenced by</h3><ul>${ins.map(e => li(e, e.source)).join('') || '<li class="muted">nothing upstream in this graph</li>'}</ul>
      <h3>Leads to</h3><ul>${outs.map(e => li(e, e.target)).join('') || '<li class="muted">terminal node</li>'}</ul>
      <p><button type="button" id="back">Back to selected explanation</button></p>`;
    $('back').onclick = showPath;
  }

  function showEdge(id) {
    const e = edgeById[id];
    $('panel').innerHTML = `<h2>${esc(nameOf[e.source])} → ${esc(nameOf[e.target])}</h2><p>${esc(pretty(e.predicate))}${evChip(e)}<br><span class="muted">confidence w = ${e.weight.toFixed(2)}, edge cost ${e.cost.toFixed(2)}</span></p>${e.mechanism ? `<h3>Mechanism</h3><p>${esc(e.mechanism)}</p>` : ''}${e.notes ? `<h3>Notes</h3><p>${esc(e.notes)}</p>` : ''}<p><button type="button" id="back">Back to selected explanation</button></p>`;
    $('back').onclick = showPath;
  }

  tsel.onchange = () => { fillRanks(); showPath(); };
  rsel.onchange = showPath;
  $('fade').onchange = () => { applyFade(); };
  $('reset').onclick = () => { if (cy) cy.fit(undefined, 30); tsel.value = D.defaultTarget; fillRanks(); showPath(); };

  const mq = window.matchMedia('(prefers-color-scheme: dark)');
  const restyle = () => { if (cy) cy.style(styles()); };
  mq.addEventListener ? mq.addEventListener('change', restyle) : mq.addListener(restyle);

  build();
  fillRanks();
  showPath();
  if (cy) cy.fit(undefined, 30);
  window.addEventListener('resize', () => { if (cy) cy.fit(undefined, 30); });
})();
</script>
</body>
</html>
"""


