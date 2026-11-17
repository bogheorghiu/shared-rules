This repo holds the boards overview (`overview/index.html`, `overview/app.js`) and the sample data it reads (`data/boards.json`).
In `data/boards.json`, a link `{from, to, why}` means board `from` is waiting on board `to`; `why` says for what.
The page fetches `../data/boards.json`, which a `file://` URL blocks: serve the repo with `python3 -m http.server` and open `/overview/`, or run `python3 tools/shot.py shots/overview` for desktop and phone screenshots.
Run `python3 -m unittest tests/test_page.py` before committing.
Write commit messages in plain English.
