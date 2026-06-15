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
    border:1px solid var(--line);background:#1d212a;color:var(--text);cursor:pointer;
    font:inherit;font-size:13px;user-select:none}
  .chip input{display:none}
  .chip .dot{width:11px;height:11px;border-radius:50%}
  .chip.free .dot{background:var(--free)}
  .chip.paid .dot{background:var(--paid)}
  .chip .ic{font-size:13px;line-height:1}
  .chip.off{opacity:.4;filter:grayscale(.6)}
  .chip .cnt{color:var(--muted);font-variant-numeric:tabular-nums}
  .filters .sep{width:1px;align-self:stretch;background:var(--line);margin:0 3px}
  .layout{flex:1;display:flex;min-height:0}
  #sidebar{width:320px;flex-shrink:0;overflow-y:auto;background:var(--panel);
    border-right:1px solid var(--line)}
  .item{padding:10px 14px;border-bottom:1px solid var(--line);cursor:pointer;
    display:flex;gap:11px;align-items:center}
  .item:hover{background:#1d212a}
  .item.hidden{display:none}
  .item .thumb{width:56px;height:56px;border-radius:8px;object-fit:cover;flex-shrink:0;
    background:#1d212a;border:1px solid var(--line)}
  .item .body{min-width:0;flex:1}
  .item .nm{font-weight:600;display:flex;align-items:center;gap:7px}
  .item .nm .dot{width:9px;height:9px;border-radius:50%;flex-shrink:0}
  .item .meta{color:var(--muted);font-size:12px;margin-top:3px}
  .item .meta .bk{color:#9b95f2}
  #map{flex:1}
  .leaflet-popup-content-wrapper{overflow:hidden;padding:0}
  .leaflet-popup-content{margin:0;font:13px/1.45 system-ui,sans-serif;width:270px!important}
  .pop-img{display:block;width:100%;height:152px;object-fit:cover;background:#e9ecef}
  .pop-credit{font-size:10px;color:#8a8f98;padding:4px 14px 0;text-align:right}
  .pop-body{padding:11px 14px 13px}
  .pop-nm{font-size:15px;font-weight:650;margin-bottom:6px;color:#111}
  .badges{display:flex;gap:6px;flex-wrap:wrap;margin-bottom:8px}
  .badge{font-size:11px;font-weight:600;padding:2px 8px;border-radius:999px;color:#fff}
  .badge.free{background:var(--free)} .badge.paid{background:var(--paid)}
  .badge.cat{background:#3a4150}
  .badge.book{background:#5b54c9}
  .pop-row{color:#333;margin:3px 0}
  .pop-row b{color:#000}
  .pop-links{margin-top:10px;display:flex;gap:16px;flex-wrap:wrap}
  .pop-links a{color:#1565c0;text-decoration:none;font-weight:600}
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
    <span class="sep"></span>
    <label class="chip book" id="chipBookReq"><input type="checkbox" checked>
      <span class="ic">📋</span>Booking required <span class="cnt" id="cBookReq"></span></label>
    <label class="chip book" id="chipBookNo"><input type="checkbox" checked>
      <span class="ic">🚶</span>Walk-in <span class="cnt" id="cBookNo"></span></label>
    <span class="sep"></span>
    <label class="chip restaurant" id="chipRestaurant"><input type="checkbox" checked>
      <span class="ic">🍽️</span>Restaurants <span class="cnt" id="cRestaurant"></span></label>
  </div>
  <div class="note">Entry (free/paid) and booking status are taken from each venue's official Rooftop Day page — still worth confirming there before you go. Source: visitfrankfurt.travel/rooftop-day</div>
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
const RESTAURANT_CATEGORIES = new Set(["Restaurant", "Food"]);

function isRestaurant(v){
  return RESTAURANT_CATEGORIES.has(v.category) || /\brestaurant\b/i.test(v.name);
}

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

function esc(s){
  return String(s).replace(/&/g,"&amp;").replace(/</g,"&lt;")
    .replace(/>/g,"&gt;").replace(/"/g,"&quot;");
}

function popupHtml(v){
  const dir = `https://www.google.com/maps/dir/?api=1&destination=${v.lat},${v.lon}`;
  const free = v.entry === "free";
  const img = v.image
    ? `<img class="pop-img" src="${esc(v.image)}" alt="${esc(v.name)}" loading="lazy">
       ${v.credit ? `<div class="pop-credit">© ${esc(v.credit)}</div>` : ""}`
    : "";
  const site = v.url
    ? `<a href="${esc(v.url)}" target="_blank" rel="noopener">↗ Event page</a>` : "";
  return `<div class="pop">
    ${img}
    <div class="pop-body">
      <div class="pop-nm">${esc(v.name)}</div>
      <div class="badges">
        <span class="badge ${v.entry}">${free ? "Free entry" : "Paid entry"}</span>
        <span class="badge cat">${esc(v.category)}</span>
        ${v.booking ? `<span class="badge book">📋 Booking required</span>` : ""}
      </div>
      <div class="pop-row"><b>From ${esc(v.time)}</b></div>
      <div class="pop-row">${esc(v.description)}</div>
      <div class="pop-row" style="color:#666">${esc(v.address)}</div>
      <div class="pop-links">${site}<a href="${dir}" target="_blank" rel="noopener">↗ Directions</a></div>
    </div>
  </div>`;
}

// Build markers + sidebar
const sidebar = document.getElementById("sidebar");
VENUES.forEach((v, i) => {
  v._marker = L.marker([v.lat, v.lon], {icon: pinIcon(v.entry)})
    .bindPopup(popupHtml(v));
  v._item = document.createElement("div");
  v._item.className = "item";
  const thumb = v.image
    ? `<img class="thumb" src="${esc(v.image)}" alt="" loading="lazy">`
    : `<div class="thumb"></div>`;
  v._item.innerHTML =
    `${thumb}
     <div class="body">
       <div class="nm"><span class="dot" style="background:${COLORS[v.entry]}"></span>${esc(v.name)}</div>
       <div class="meta">From ${esc(v.time)} · ${esc(v.category)} · ${v.entry === "free" ? "Free" : "Paid"}${v.booking ? ` · <span class="bk">📋 Booking</span>` : ""}</div>
     </div>`;
  v._item.onclick = () => {
    map.setView([v.lat, v.lon], 16, {animate:true});
    v._marker.openPopup();
  };
  sidebar.appendChild(v._item);
});

const counts = {free:0, paid:0};
const bookCounts = {req:0, no:0};
VENUES.forEach(v => { counts[v.entry]++; bookCounts[v.booking ? "req" : "no"]++; });
const restaurantCount = VENUES.filter(isRestaurant).length;
document.getElementById("cFree").textContent = `(${counts.free})`;
document.getElementById("cPaid").textContent = `(${counts.paid})`;
document.getElementById("cBookReq").textContent = `(${bookCounts.req})`;
document.getElementById("cBookNo").textContent = `(${bookCounts.no})`;
document.getElementById("cRestaurant").textContent = `(${restaurantCount})`;

const chipFree = document.getElementById("chipFree");
const chipPaid = document.getElementById("chipPaid");
const chipBookReq = document.getElementById("chipBookReq");
const chipBookNo = document.getElementById("chipBookNo");
const chipRestaurant = document.getElementById("chipRestaurant");
const cbFree = chipFree.querySelector("input");
const cbPaid = chipPaid.querySelector("input");
const cbBookReq = chipBookReq.querySelector("input");
const cbBookNo = chipBookNo.querySelector("input");
const cbRestaurant = chipRestaurant.querySelector("input");

function applyFilter(){
  const entryShow = {free: cbFree.checked, paid: cbPaid.checked};
  const bookShow = {req: cbBookReq.checked, no: cbBookNo.checked};
  const restaurantShow = cbRestaurant.checked;
  chipFree.classList.toggle("off", !entryShow.free);
  chipPaid.classList.toggle("off", !entryShow.paid);
  chipBookReq.classList.toggle("off", !bookShow.req);
  chipBookNo.classList.toggle("off", !bookShow.no);
  chipRestaurant.classList.toggle("off", !restaurantShow);
  let vis = 0;
  VENUES.forEach(v => {
    const restaurant = isRestaurant(v);
    const on = entryShow[v.entry] && bookShow[v.booking ? "req" : "no"] &&
      (restaurantShow || !restaurant);
    if (on){ v._marker.addTo(map); v._item.classList.remove("hidden"); vis++; }
    else { map.removeLayer(v._marker); v._item.classList.add("hidden"); }
  });
  document.getElementById("visCount").textContent = vis;
}
[cbFree, cbPaid, cbBookReq, cbBookNo, cbRestaurant].forEach(cb => cb.onchange = applyFilter);

applyFilter();
map.fitBounds(VENUES.map(v => [v.lat, v.lon]), {padding:[40,40]});
</script>
</body>
</html>
"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(HTML.replace("__DATA__", data_js))

print(f"Built index.html with {len(venues)} venues.")
