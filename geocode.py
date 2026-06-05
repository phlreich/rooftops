#!/usr/bin/env python3
"""Geocode Frankfurt Rooftop Day 2026 venues via Nominatim and emit venues.js."""
import json
import time
import urllib.parse
import urllib.request

# entry: "free" or "paid" — best-guess by venue type since the source page does
# not list per-venue pricing on the overview. Easy to flip per venue.
VENUES = [
    # name, address, time, entry, category, description
    ("Museum für Kommunikation", "Schaumainkai 53, 60596 Frankfurt", "16:00", "paid", "Museum", "Rooftop terrace with guided tour."),
    ("World Club Dome Festival", "Mörfelder Landstraße 362, 60528 Frankfurt", "12:30", "paid", "Festival", "Music festival at Deutsche Bank Park with rooftop vibes."),
    ("Römer-Balkon (Rathaus)", "Römerberg 23, 60311 Frankfurt", "16:00", "free", "Landmark", "Open house day with balcony access at City Hall."),
    ("FOUR Frankfurt", "Junghofstraße 5, 60323 Frankfurt", "16:00", "free", "Tour", "Guided architectural tours."),
    ("OOSTEN", "Mayfarthstraße 4, 60314 Frankfurt", "14:00", "free", "Bar", "Bar and nightlife venue by the river."),
    ("Zentralbibliothek", "Hasengasse 4, 60311 Frankfurt", "21:00", "free", "Culture", "Evening rooftop party and nightlife."),
    ("WESTEND TOWER – Rooms and Roofs", "Grüneburgweg 58-62, 60322 Frankfurt", "16:00", "paid", "Wellness", "Yoga sessions on the rooftop."),
    ("Primus-Linie", "Eiserner Steg, 60311 Frankfurt", "19:30", "paid", "Cruise", "Sunset river cruise with skyline views."),
    ("Villa Sander", "Mainzer Landstraße 10, 60325 Frankfurt", "16:00", "free", "Tour", "Architectural guided tour."),
    ("Frankfurt Sightseeing GmbH", "Paulsplatz, 60311 Frankfurt", "17:30", "paid", "Tour", "Hop-on-hop-off bus tours."),
    ("Alte Nikolaikirche", "Am Römerberg 9, 60311 Frankfurt", "19:00", "free", "Church", "Church roof gallery tour."),
    ("Freigut Bootshaus", "Schaumainkai, 60594 Frankfurt", "14:00", "free", "Bar", "Waterside bar and nightlife by the Main."),
    ("The Florentin", "Paul-Ehrlich-Straße 9, 60596 Frankfurt", "16:00", "free", "Hotel", "Urban retreat with a design focus."),
    ("Main Bad Bornheim", "Am Bornheimer Hang 2, 60386 Frankfurt", "16:00", "paid", "Pool", "Public pool with rooftop terrace."),
    ("Jüdisches Museum Frankfurt", "Bertha-Pappenheim-Platz 1, 60311 Frankfurt", "17:30", "paid", "Museum", "Culinary and cultural event."),
    ("TaunusTurm", "Neue Mainzer Straße 33-35, 60311 Frankfurt", "16:00", "paid", "Observation", "Tower observation deck and family tours."),
    ("Ruby Louise Hotel & Bar", "Neue Rothofstraße 8, 60313 Frankfurt", "16:00", "free", "Bar", "Rooftop bar with evening entertainment."),
    ("OMNITURM", "Große Gallusstraße 16-18, 60312 Frankfurt", "17:00", "free", "Bar", "Rooftop nightlife venue."),
    ("OAKS Bar", "Güterplatz 1, 60327 Frankfurt", "16:00", "free", "Bar", "Bar with skyline views."),
    ("Sofitel Frankfurt Opera", "Opernplatz 16, 60313 Frankfurt", "17:00", "free", "Bar", "Elegant rooftop lounge."),
    ("Lazuli Bar & Kitchen", "Junghofstraße 7, 60311 Frankfurt", "14:00", "free", "Restaurant", "Dining and beverage service."),
    ("Occhio d'Oro", "Eschenheimer Tor 2, 60318 Frankfurt", "16:00", "free", "Restaurant", "Restaurant with terrace."),
    ("Restaurant & Skybar oben", "Senckenberganlage 13, 60325 Frankfurt", "18:00", "free", "Bar", "Fine dining with sunset views."),
    ("MyZeil FOODTOPIA", "Zeil 106-110, 60313 Frankfurt", "17:30", "free", "Food", "Rooftop food court venue."),
    ("The Blasky Hotel & Rooftop", "Ziegelhüttenweg 43, 60598 Frankfurt", "17:00", "free", "Hotel", "Hotel rooftop with dining."),
    ("Citybeach / CityAlm", "Carl-Theodor-Reiffenstein-Platz 5, 60313 Frankfurt", "10:00", "free", "Beach club", "Rooftop beach club atmosphere."),
    ("Gaia", "Kaiserhofstraße 12, 60313 Frankfurt", "16:30", "free", "Bar", "Rooftop lounge."),
    ("THE VIEW", "Zeil 116-126, 60313 Frankfurt", "09:30", "free", "Bar", "Department-store rooftop bar."),
    ("Radio Frankfurt Skyline Studios", "Nibelungenplatz 3, 60318 Frankfurt", "16:00", "free", "Music", "DJ sets and live music broadcast."),
    ("Upper East Site", "Schwedlerstraße 8, 60314 Frankfurt", "16:00", "free", "Bar", "Nightlife with live music."),
    ("Sabor Restaurant", "Adickesallee 36, 60322 Frankfurt", "16:00", "free", "Restaurant", "Spanish cuisine with a view."),
    ("The Suite Garden Hotel", "Fellnerstraße 3, 60322 Frankfurt", "13:00", "paid", "Wellness", "Wellness activities including pilates."),
    ("Sternwarte des Physikalischen Vereins", "Robert-Mayer-Straße 2, 60325 Frankfurt", "16:00", "paid", "Observatory", "Observatory with telescope viewings."),
    ("Rententurm (Historisches Museum)", "Saalhof 1, 60311 Frankfurt", "16:00", "paid", "Museum", "Historic tower with city views."),
    ("Städel Museum", "Schaumainkai 63, 60596 Frankfurt", "18:00", "paid", "Museum", "Rooftop terrace access."),
    ("Haus zur Goldenen Waage", "Markt 5, 60311 Frankfurt", "18:00", "paid", "Tour", "Historic building architectural tour."),
    ("Dreikönigskirche", "Dreikönigsstraße 32, 60594 Frankfurt", "16:00", "free", "Church", "Church tower access."),
    ("25hours Hotel The Trip", "Niddastraße 58, 60329 Frankfurt", "16:00", "free", "Hotel", "Glamping-style rooftop experience."),
    ("Caricatura Museum", "Weckmarkt 17, 60311 Frankfurt", "16:00", "paid", "Museum", "Comic art museum exhibition."),
    ("ROMANFABRIK", "Hanauer Landstraße 186, 60314 Frankfurt", "16:00", "paid", "Music", "Live music concert venue."),
    ("Skyline Plaza", "Europa-Allee 6, 60327 Frankfurt", "15:00", "free", "Shopping", "Rooftop garden with shopping access."),
    ("TOWER185 / FIFTY HEIGHTS", "Friedrich-Ebert-Anlage 35-37, 60327 Frankfurt", "16:15", "paid", "Wellness", "Yoga sessions on the rooftop."),
    ("pme Familienservice GmbH", "Senckenberganlage 16, 60325 Frankfurt", "16:00", "free", "Family", "Family-friendly rooftop gathering."),
]

# Manual overrides where Nominatim is unreliable (landmarks / bridges).
OVERRIDES = {
    "Römer-Balkon (Rathaus)": (50.110523, 8.681944),
    "Primus-Linie": (50.109970, 8.682680),       # Eiserner Steg jetty
    "Freigut Bootshaus": (50.103780, 8.678200),  # Sachsenhausen Mainufer
    "World Club Dome Festival": (50.068610, 8.645560),  # Deutsche Bank Park
}

UA = "FrankfurtRooftopMap/1.0 (personal use)"


def geocode(query):
    url = "https://nominatim.openstreetmap.org/search?" + urllib.parse.urlencode(
        {"q": query, "format": "json", "limit": 1, "countrycodes": "de"}
    )
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.load(r)
    if data:
        return float(data[0]["lat"]), float(data[0]["lon"])
    return None


out = []
for name, address, t, entry, cat, desc in VENUES:
    if name in OVERRIDES:
        lat, lon = OVERRIDES[name]
        src = "override"
    else:
        coords = None
        for q in (address + ", Frankfurt am Main, Germany", address):
            try:
                coords = geocode(q)
            except Exception as e:
                print(f"  ! error for {name}: {e}")
                coords = None
            time.sleep(1.1)
            if coords:
                break
        if coords:
            lat, lon = coords
            src = "nominatim"
        else:
            lat, lon = None, None
            src = "FAILED"
    print(f"[{src:9}] {name} -> {lat}, {lon}")
    out.append({
        "name": name, "address": address, "time": t, "entry": entry,
        "category": cat, "description": desc, "lat": lat, "lon": lon,
    })

with open("venues.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=2)

failed = [v["name"] for v in out if v["lat"] is None]
print(f"\nDone. {len(out)} venues, {len(failed)} failed: {failed}")
