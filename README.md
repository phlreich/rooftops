# Frankfurt Rooftop Day — Map

Interactive map of the [Frankfurt Rooftop Day 2026](https://visitfrankfurt.travel/rooftop-day)
venues — Leaflet + OpenStreetMap tiles, no API keys, fully self-contained.

## Files

- `geocode.py` — geocodes the venue list via Nominatim → writes `venues.json`
- `enrich.py` — scrapes visitfrankfurt.travel → adds each venue's event-page
  `url`, downloads its photo into `images/`, and records the photo `credit`
- `build.py` — inlines `venues.json` into `index.html`
- `venues.json` — venue data (name, address, time, entry, category, coords,
  plus `url` / `image` / `credit`)
- `images/` — venue photos (WebP) pulled from the official event pages
- `index.html` — the built map; serve `index.html` + `images/` together

## Rebuild

```bash
python geocode.py   # refresh coordinates from addresses (optional, rate-limited)
python enrich.py    # refresh event links + venue photos from visitfrankfurt.travel
python build.py     # regenerate index.html from venues.json
```

Run `enrich.py` after `geocode.py` (it augments `venues.json` in place;
re-running `geocode.py` rewrites the file and drops the enrichment). `index.html`
is committed (it's what gets served), but it is fully regenerable from
`venues.json` + `build.py`.

Photos are sourced from each venue's Rooftop Day event page on
visitfrankfurt.travel; attribution is shown in each popup. One venue (Sabor
Restaurant) has no photo on the source page, so it shows a link only.

> Entry free/paid is a best-guess by venue type — verify on each venue's page before you go.
