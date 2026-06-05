# Frankfurt Rooftop Day — Map

Interactive map of the [Frankfurt Rooftop Day 2026](https://visitfrankfurt.travel/rooftop-day)
venues — Leaflet + OpenStreetMap tiles, no API keys, fully self-contained.

## Files

- `geocode.py` — geocodes the venue list via Nominatim → writes `venues.json`
- `build.py` — inlines `venues.json` into a single self-contained `index.html`
- `venues.json` — venue data (name, address, time, entry, category, coords)
- `index.html` — the built map; open directly in a browser, no server needed

## Rebuild

```bash
python geocode.py   # refresh coordinates from addresses (optional, rate-limited)
python build.py     # regenerate index.html from venues.json
```

`index.html` is committed (it's what gets served), but it is fully regenerable
from `venues.json` + `build.py`.

> Entry free/paid is a best-guess by venue type — verify on each venue's page before you go.
