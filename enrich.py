#!/usr/bin/env python3
"""Enrich venues.json with Rooftop Day event links + venue photos.

Scrapes the official visitfrankfurt.travel Rooftop Day overview page, matches
each venue to its event sub-page, and writes three fields into venues.json:

    url     - the venue's Rooftop Day event page (visitfrankfurt.travel)
    image   - a local WebP photo downloaded into images/ (or absent)
    credit  - photo attribution as published on the source page

Photos are pulled through the site's own image CDN at a fixed size and saved as
WebP. Re-runnable; like geocode.py it reads live from the source.

Run order:  python geocode.py  ->  python enrich.py  ->  python build.py
"""
import json
import html
import os
import re
import sys
import urllib.parse
import urllib.request

SOURCE = "https://www.visitfrankfurt.travel/rooftop-day"
EVENT_BASE = "https://www.visitfrankfurt.travel/event/"
UA = "FrankfurtRooftopMap/1.0 (personal use)"
IMG_DIR = "images"
IMG_W, IMG_H, IMG_Q = 720, 432, 80  # popup photo size / quality

# venues.json "name" -> Rooftop Day event sub-page slug.
# Verified by hand against the source listing; every venue maps 1:1.
SLUG = {
    "Museum für Kommunikation": "rooftop-day-im-museum-fuer-kommunikation",
    "World Club Dome Festival": "rooftop-day-beim-world-club-dome-festival",
    "Römer-Balkon (Rathaus)": "rooftop-day-auf-dem-roemer-balkon",
    "FOUR Frankfurt": "rooftop-day-im-four-frankfurt",
    "OOSTEN": "rooftop-day-im-oosten",
    "Zentralbibliothek": "rooftop-day-in-der-zentralbibliothek",
    "WESTEND TOWER – Rooms and Roofs": "rooftop-day-im-westend-tower-rooms-and-roofs",
    "Primus-Linie": "rooftop-day-mit-der-primus-linie-sunset-x-skyline-tour",
    "Villa Sander": "rooftop-day-in-der-villa-sander",
    "Frankfurt Sightseeing GmbH": "rooftop-day-bei-der-frankfurt-sightseeing-gmbh",
    "Alte Nikolaikirche": "rooftop-day-auf-der-dachgalerie-der-alten-nikolaikirche",
    "Freigut Bootshaus": "rooftop-day-im-freigut-bootshaus",
    "The Florentin": "rooftop-day-im-the-florentin",
    "Main Bad Bornheim": "rooftop-day-im-main-bad-bornheim",
    "Jüdisches Museum Frankfurt": "rooftop-day-im-life-deli-im-juedischen-museum-frankfurt",
    "TaunusTurm": "rooftop-day-auf-dem-taunusturm",
    "Ruby Louise Hotel & Bar": "rooftop-day-im-ruby-louise-hotel-bar",
    "OMNITURM": "abgesagt-rooftop-day-auf-der-omniturm-dachterrasse",  # cancelled by venue
    "OAKS Bar": "rooftop-day-in-der-oaks-bar-im-nh-collection-frankfurt-spin",
    "Sofitel Frankfurt Opera": "rooftop-day-im-sofitel-frankfurt-opera",
    "Lazuli Bar & Kitchen": "rooftop-day-im-lazuli-bar-kitchen-kimpton-main-frankfurt",
    "Occhio d'Oro": "rooftop-day-im-occhio-doro",
    "Restaurant & Skybar oben": "rooftop-day-im-restaurant-skybar-oben",
    "MyZeil FOODTOPIA": "rooftop-day-im-foodtopia-im-shopping-center-myzeil",
    "The Blasky Hotel & Rooftop": "rooftop-day-im-the-blasky-hotel-rooftop",
    "Citybeach / CityAlm": "rooftop-day-im-citybeach",
    "Gaia": "rooftop-day-im-gaia",
    "THE VIEW": "rooftop-day-im-the-view",
    "Radio Frankfurt Skyline Studios": "rooftop-day-bei-den-radio-frankfurt-skyline-studios",
    "Upper East Site": "rooftop-day-in-der-upper-east-site",
    "Sabor Restaurant": "rooftop-day-im-sabor-restaurant",
    "The Suite Garden Hotel": "rooftop-day-im-the-suite-garden-hotel",
    "Sternwarte des Physikalischen Vereins": "rooftop-day-in-der-sternwarte-des-physikalischen-vereins",
    "Rententurm (Historisches Museum)": "rooftop-day-im-rententurm-im-historischen-museum-frankfurt",
    "Städel Museum": "rooftop-day-auf-dem-staedel-dach-im-staedel-museum",
    "Haus zur Goldenen Waage": "rooftop-day-im-belvederchen-im-haus-zur-goldenen-waage",
    "Dreikönigskirche": "rooftop-day-in-der-dreikoenigskirche",
    "25hours Hotel The Trip": "rooftop-day-im-25hours-hotel-the-trip",
    "Caricatura Museum": "rooftop-day-im-caricatura-museum-frankfurt-museum-fuer-komische-kunst",
    "ROMANFABRIK": "rooftop-day-in-der-romanfabrik",
    "Skyline Plaza": "rooftop-day-im-skyline-garden-rooftop-des-skyline-plaza",
    "TOWER185 / FIFTY HEIGHTS": "rooftop-day-auf-dem-tower185/fifty-heights",
    "pme Familienservice GmbH": "rooftop-day-bei-der-pme-familienservice-gmbh",
}

_TRANS = str.maketrans({"ä": "ae", "ö": "oe", "ü": "ue", "ß": "ss",
                        "Ä": "ae", "Ö": "oe", "Ü": "ue", "é": "e", "'": ""})


def slugify(name):
    s = name.lower().translate(_TRANS)
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return re.sub(r"-+", "-", s)


def get(url, binary=False):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read() if binary else r.read().decode("utf-8")


def parse_cards(doc):
    """Return {event_url: {"dam": <orig img url or None>, "credit": str}}."""
    cards = {}
    pat = re.compile(
        r'<div class="teaser-card result-item".*?'
        r'<a href="(https://www\.visitfrankfurt\.travel/event/[^"]+)"',
        re.S)
    # Slice the document at each card boundary so regexes stay local to one card.
    starts = [m.start() for m in re.finditer(r'<div class="teaser-card result-item"', doc)]
    starts.append(len(doc))
    for i in range(len(starts) - 1):
        body = doc[starts[i]:starts[i + 1]]
        href = re.search(r'<a href="(https://www\.visitfrankfurt\.travel/event/[^"]+)"', body)
        if not href:
            continue
        url = href.group(1)
        if url in cards:
            continue
        img = re.search(r'srcset="//img\.destination\.one/remote/\.webp\?url=([^"&]+)', body)
        dam = urllib.parse.unquote(img.group(1)) if img else None
        cop = re.search(r'copyright__text" title="([^"]*)"', body)
        credit = ""
        if cop:
            credit = html.unescape(cop.group(1))
            credit = re.sub(r"&copy;|&ensp;|©", "", credit).strip()
        cards[url] = {"dam": dam, "credit": credit}
    return cards


def proxy_url(dam):
    return (f"https://img.destination.one/remote/.webp?url={urllib.parse.quote(dam, safe='')}"
            f"&scale=both&mode=crop&quality={IMG_Q}&width={IMG_W}&height={IMG_H}")


def main():
    venues = json.load(open("venues.json", encoding="utf-8"))

    missing = [v["name"] for v in venues if v["name"] not in SLUG]
    if missing:
        sys.exit(f"No event slug mapped for: {missing}")

    print(f"Fetching {SOURCE} ...")
    cards = parse_cards(get(SOURCE))
    print(f"Parsed {len(cards)} event cards.")

    os.makedirs(IMG_DIR, exist_ok=True)
    no_photo = []
    for v in venues:
        url = EVENT_BASE + SLUG[v["name"]]
        v["url"] = url
        card = cards.get(url, {})
        dam = card.get("dam")
        if dam:
            v["credit"] = card.get("credit", "")
            path = f"{IMG_DIR}/{slugify(v['name'])}.webp"
            with open(path, "wb") as f:
                f.write(get(proxy_url(dam), binary=True))
            v["image"] = path
            print(f"[ok ] {v['name']} -> {path}")
        else:
            v.pop("image", None)
            v.pop("credit", None)
            no_photo.append(v["name"])
            print(f"[--- ] {v['name']} (no source photo, link only)")

    json.dump(venues, open("venues.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    print(f"\nDone. {len(venues)} venues, {len(no_photo)} without photo: {no_photo}")


if __name__ == "__main__":
    main()
