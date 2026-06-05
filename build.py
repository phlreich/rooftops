#!/usr/bin/env python3
"""Build a self-contained index.html from venues.json (data inlined)."""
import json

with open("venues.json", encoding="utf-8") as f:
    venues = [v for v in json.load(f) if v.get("lat") and v.get("lon")]

data_js = json.dumps(venues, ensure_ascii=False)

HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Frankfurt Rooftop Day — Sat 6 June 2026</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"
  integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY=" crossorigin="">
<style>
  :root{
    --free:#1a9850; --paid:#e0820a; --bg:#0f1115; --panel:#171a21;
    --line:#272b35; --text:#e8eaed; --muted:#9aa0ab;
  }
  *{box-sizing:border-box}
  html,body{height:100%;margin:0}
  body{font:14px/1.45 system-ui,Segoe UI,Roboto,Helvetica,Arial,sans-serif;
    color:var(--text);background:var(--bg);display:flex;flex-direction:column}
  header{padding:12px 16px;background:var(--panel);border-bottom:1px solid var(--line);
    display:flex;flex-wrap:wrap;align-items:center;gap:14px}
  header h1{font-size:16px;margin:0;font-weight:650}
  header .sub{color:var(--muted);font-size:12px}
  .filters{display:flex;gap:8px;margin-left:auto;flex-wrap:wrap}
  .chip{display:inline-flex;align-items:center;gap:7px;padding:6px 12px;border-radius:999px;
    border:1px solid var(--line);background:#1d212a;cursor:pointer;user-select:none;font-size:13px}
  .chip input{display:none}
  .chip .dot{width:11px;height:11px;border-radius:50%}
  .chip.free .dot{background:var(--free)}
  .chip.paid .dot{background:var(--paid)}
  .chip.off{opacity:.4;filter:grayscale(.6)}
  .chip .cnt{color:var(--muted);font-variant-numeric:tabular-nums}
  .layout{flex:1;display:flex;min-height:0}
  #sidebar{width:320px;flex-shrink:0;overflow-y:auto;background:var(--panel);
    border-right:1px solid var(--line)}
  .item{padding:11px 14px;border-bottom:1px solid var(--line);cursor:pointer}
  .item:hover{background:#1d212a}
  .item.hidden{display:none}
  .item .nm{font-weight:600;display:flex;align-items:center;gap:7px}
  .item .nm .dot{width:9px;height:9px;border-radius:50%;flex-shrink:0}
  .item .meta{color:var(--muted);font-size:12px;margin-top:3px}
  #map{flex:1}
  .leaflet-popup-content{margin:12px 14px;font:13px/1.45 system-ui,sans-serif;min-width:200px}
  .pop-nm{font-size:15px;font-weight:650;margin-bottom:6px;color:#111}
  .badges{display:flex;gap:6px;flex-wrap:wrap;margin-bottom:8px}
  .badge{font-size:11px;font-weight:600;padding:2px 8px;border-radius:999px;color:#fff}
  .badge.free{background:var(--free)} .badge.paid{background:var(--paid)}
  .badge.cat{background:#3a4150}
  .pop-row{color:#333;margin:3px 0}
  .pop-row b{color:#000}
  .pop a{display:inline-block;margin-top:8px;color:#1565c0;text-decoration:none;font-weight:600}
  .note{font-size:11px;color:var(--muted);width:100%;margin-top:2px}
  @media(max-width:680px){
    #sidebar{display:none}
    header h1{font-size:14px}
  }
</style>
</head>
<body>
<header>
  <div>
    <h1>🍹 Frankfurt Rooftop Day</h1>
    <div class="sub">Saturday, 6 June 2026 · <span id="visCount"></span> venues shown</div>
  </div>
  <div class="filters">
    <label class="chip free" id="chipFree"><input type="checkbox" checked>
      <span class="dot"></span>Free entry <span class="cnt" id="cFree"></span></label>
    <label class="chip paid" id="chipPaid"><input type="checkbox" checked>
      <span class="dot"></span>Paid entry <span class="cnt" id="cPaid"></span></label>
  </div>
  <div class="note">Entry free/paid is a best-guess by venue type (the official page lists pricing only on each venue's own sub-page) — verify before you go. Source: visitfrankfurt.travel/rooftop-day</div>
</header>
<div class="layout">
  <div id="sidebar"></div>
  <div id="map"></div>
</div>

<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"
  integrity="sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo=" crossorigin=""></script>
<script>
const VENUES = __DATA__;
const COLORS = {free:"#1a9850", paid:"#e0820a"};

const map = L.map("map", {scrollWheelZoom:true}).setView([50.110, 8.682], 13);
L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
  maxZoom:19, attribution:'&copy; OpenStreetMap contributors'
}).addTo(map);

function pinIcon(entry){
  const c = COLORS[entry] || "#888";
  return L.divIcon({
    className:"", iconSize:[26,38], iconAnchor:[13,38], popupAnchor:[0,-34],
    html:`<svg width="26" height="38" viewBox="0 0 26 38" xmlns="http://www.w3.org/2000/svg">
      <path d="M13 0C5.8 0 0 5.8 0 13c0 9.2 13 25 13 25s13-15.8 13-25C26 5.8 20.2 0 13 0z" fill="${c}"/>
      <circle cx="13" cy="13" r="5" fill="#fff"/></svg>`
  });
}

function popupHtml(v){
  const dir = `https://www.google.com/maps/dir/?api=1&destination=${v.lat},${v.lon}`;
  const free = v.entry === "free";
  return `<div class="pop">
    <div class="pop-nm">${v.name}</div>
    <div class="badges">
      <span class="badge ${v.entry}">${free ? "Free entry" : "Paid entry"}</span>
      <span class="badge cat">${v.category}</span>
    </div>
    <div class="pop-row"><b>From ${v.time}</b></div>
    <div class="pop-row">${v.description}</div>
    <div class="pop-row" style="color:#666">${v.address}</div>
    <a href="${dir}" target="_blank" rel="noopener">↗ Directions</a>
  </div>`;
}

// Build markers + sidebar
const sidebar = document.getElementById("sidebar");
VENUES.forEach((v, i) => {
  v._marker = L.marker([v.lat, v.lon], {icon: pinIcon(v.entry)})
    .bindPopup(popupHtml(v));
  v._item = document.createElement("div");
  v._item.className = "item";
  v._item.innerHTML =
    `<div class="nm"><span class="dot" style="background:${COLORS[v.entry]}"></span>${v.name}</div>
     <div class="meta">From ${v.time} · ${v.category} · ${v.entry === "free" ? "Free" : "Paid"}</div>`;
  v._item.onclick = () => {
    map.setView([v.lat, v.lon], 16, {animate:true});
    v._marker.openPopup();
  };
  sidebar.appendChild(v._item);
});

const counts = {free:0, paid:0};
VENUES.forEach(v => counts[v.entry]++);
document.getElementById("cFree").textContent = `(${counts.free})`;
document.getElementById("cPaid").textContent = `(${counts.paid})`;

const chipFree = document.getElementById("chipFree");
const chipPaid = document.getElementById("chipPaid");
const cbFree = chipFree.querySelector("input");
const cbPaid = chipPaid.querySelector("input");

function applyFilter(){
  const show = {free: cbFree.checked, paid: cbPaid.checked};
  chipFree.classList.toggle("off", !show.free);
  chipPaid.classList.toggle("off", !show.paid);
  let vis = 0;
  VENUES.forEach(v => {
    const on = show[v.entry];
    if (on){ v._marker.addTo(map); v._item.classList.remove("hidden"); vis++; }
    else { map.removeLayer(v._marker); v._item.classList.add("hidden"); }
  });
  document.getElementById("visCount").textContent = vis;
}
cbFree.onchange = applyFilter;
cbPaid.onchange = applyFilter;

applyFilter();
map.fitBounds(VENUES.map(v => [v.lat, v.lon]), {padding:[40,40]});
</script>
</body>
</html>
"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(HTML.replace("__DATA__", data_js))

print(f"Built index.html with {len(venues)} venues.")
