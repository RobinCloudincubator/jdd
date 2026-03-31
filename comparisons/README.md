# Comparison folders

Each subfolder is one comparison. Use these filenames:

| File | Role |
|------|------|
| `left.json` | Left pane JSON (semantic “before” / first document) |
| `right.json` | Right pane JSON |
| `notes.txt` | Notes textarea; commit this file so clones get your notes |

## Open in the app

With the site served over HTTP (Docker or `php -S` — see below), open:

`index.html?case=<folder-name>`

Example: `index.html?case=example` loads `comparisons/example/left.json`, `right.json`, and `notes.txt`, runs Compare, and auto-saves the notes field back to `notes.txt` as you type (debounced).

## Saving `notes.txt`

The browser cannot write arbitrary paths on disk by itself. This project includes `save-notes.php`, which writes `notes.txt` under `comparisons/<case>/`.

- **Docker** (Ubuntu or Alpine image in this repo): PHP-FPM runs behind nginx; notes save works out of the box.
- **Local without Docker**: from the project root run  
  `php -S localhost:8080`  
  then open `http://localhost:8080/index.html?case=example`.

Pure static hosting (no PHP) can still **load** JSON and notes; saving notes requires PHP or copying text manually into `notes.txt`.

## New comparison

1. Create `comparisons/my-topic/left.json` and `right.json` (and optionally empty `notes.txt`).
2. Open `?case=my-topic`. If the folder did not exist yet, typing in Notes can create `comparisons/my-topic/` via `save-notes.php`; you still need to add the two JSON files yourself (or copy from elsewhere).
