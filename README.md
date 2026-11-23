[![make.fun · news-image-20261122](https://make.fun/badge/news-image-20261122.svg)](https://make.fun/bounty/news-image-20261122?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)
[![rank](https://make.fun/badge/news-image-20261122/kizuna99/news-image-20261122-entry/rank.svg)](https://make.fun/bounty/news-image-20261122/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)
[![reward](https://make.fun/badge/news-image-20261122/kizuna99/news-image-20261122-entry/reward.svg)](https://make.fun/bounty/news-image-20261122?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)

# The World in One Day — Sunday 22 November 2026: 40 stories, 9 regions, every one dated

An original editorial broadsheet poster for [make.fun](https://make.fun/bounty/news-image-20261122): the whole of Sunday 22 November 2026's world news on one 1024 × 1024 page — a giant dated masthead, the day in UTC on a timeline, six key numbers, three illustrated lead stories (the 186-drone barrage over Ukraine, COP31 in a second day of overtime, and Iran's claim of strikes on US positions against Bahrain's denial), ten numbered story cards — each with its own illustrated strip, its key number as a chip and its certainty badge — a pin map of where it happened, and 27 more dated stories in the "Also on Sunday" column. A date-check box names the context that belongs to another day. No news photography: every picture, map and icon is original geometry drawn by `render.py` (Pillow, deterministic, supersampled 2048 → 1024). Full source list: see `SOURCES.md`.

![The World in One Day for Sunday 22 November 2026 — 40 dated stories, 9 regions](entry.png)

## The three illustrated leads

1. **Ukraine.** Russia fired 186 drones in a single overnight barrage; Kyiv says 161 were downed or jammed, with strikes landing at 18 sites and 11 hurt in Sloviansk and Kherson. (QNA, Ukrainian Air Force, 22 Nov 2026)
2. **COP31, Antalya.** The climate summit ran into a second day of overtime: a new Australia–Türkiye draft concedes warming is on course to pass 1.5°C, and fossil-fuel wording splits some 200 nations. (The Guardian, Reuters, 22 Nov 2026)
3. **Manama, Bahrain.** The IRGC says its strikes hit US positions; Bahrain answers that the plant hit was a civilian industrial site — a fire, no injuries — and demands Tehran take full responsibility and pay for the damage. (RTM, Reuters, 22 Nov 2026)

## The ten cards

Tainted liquor kills 11 in Manipur (Reuters) · Search for 36 missing in the Serang factory fire (RTM, Bernama) · Fourteen feared trapped in a Kyiv block (Apex Wire) · Floods submerge some 850 homes in France (Aktual) · The Russian cargo ship Sparta II still burning off Finland, its crew of 16 evacuated (Reuters, Yle) · Bitcoin steadies near $60,000 (Apex Wire) · Messi wins a second straight MLS Golden Boot (KitaIndonesiasatu) · UN talks to draft 'killer robot' rules with 128 countries (Reuters, Al Jazeera) · Fire guts 32 Baduy homes in Lebak (KitaIndonesiasatu) · Fico says Slovakia won't fund the €45bn EU Ukraine loan (Reuters summary).

## How it is built

- `data.py` — the day's verified stories, numbers, timeline, cards and map pins.
- `render.py` — the broadsheet renderer and all of the original artwork (broadsheet masthead, stat band, region tabs, UTC timeline, three illustrated leads, cards, dot-grid pin map, date-check box).
- `main.py` — the sandbox entrypoint: verifies the committed `entry.png` is a whole, CRC-valid 1024 × 1024 PNG of at most 1 MiB and publishes it byte for byte.
- `SOURCES.md` — every story with the outlets that reported it on 22 Nov 2026.

## Licence

MIT — see `LICENSE`.
