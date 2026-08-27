#!/usr/bin/env python3
"""Open actions from wiki/daily/ as a clickable checklist on localhost.

    python3 skills/today/scripts/todo.py         # start the server (if not running) and open the page
    python3 skills/today/scripts/todo.py stop    # stop it

Ticking a box rewrites `- [ ]` to `- [x]` in the daily note the line came from.
The daily notes stay the single source of truth; this page is only a view on them.
Standard library only, bound to 127.0.0.1.
"""
import html
import json
import os
import re
import sys
import threading
import urllib.request
import webbrowser
from datetime import date
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DAILY = ROOT / "wiki" / "daily"
PORT = 8642
URL = f"http://127.0.0.1:{PORT}/"

NOTE = re.compile(r"^\d{4}-\d{2}-\d{2}\.md$")
BOX = re.compile(r"^- \[( |x)\] ")


# --- read -------------------------------------------------------------------

def open_actions():
    """Every unchecked box across wiki/daily/, newest note first."""
    groups = []
    for path in sorted(DAILY.glob("*.md"), reverse=True):
        if not NOTE.match(path.name):
            continue
        items = []
        for n, line in enumerate(path.read_text().splitlines()):
            if line.startswith("- [ ] "):
                items.append({"file": path.name, "line": n, "text": line[6:]})
        if items:
            groups.append((path.stem, items))
    return groups


def toggle(file, line, done):
    """Flip one checkbox in place. Returns the new line, or None if the target moved."""
    if not NOTE.match(file):
        return None
    path = DAILY / file
    lines = path.read_text().split("\n")
    if not (0 <= line < len(lines)) or not BOX.match(lines[line]):
        return None
    lines[line] = "- [x] " + lines[line][6:] if done else "- [ ] " + lines[line][6:]
    path.write_text("\n".join(lines))
    return lines[line]


# --- render -----------------------------------------------------------------

def render_text(text):
    """Escape, then light up links, [[wiki links]] and `code`."""
    t = html.escape(text, quote=False)
    t = re.sub(r"https?://[^\s<)]+", lambda m: f'<a href="{m[0]}" target="_blank" rel="noopener">{m[0].split("//", 1)[1].split("/", 1)[0]}</a>', t)
    t = re.sub(r"\[\[topics/([^\]]+)\]\]", r'<span class="topic">\1</span>', t)
    t = re.sub(r"\[\[([^\]]+)\]\]", r'<span class="person">\1</span>', t)
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
    return t


def render_page():
    today = date.today()
    groups = open_actions()
    total = sum(len(items) for _, items in groups)
    body = []
    for day, items in groups:
        age = (today - date.fromisoformat(day)).days
        when = "today" if age == 0 else f"{age}d ago"
        body.append(f'<section><h2>{day} <small>{date.fromisoformat(day):%a} · {when}</small></h2>')
        for it in items:
            body.append(
                f'<label class="item"><input type="checkbox" data-file="{it["file"]}" data-line="{it["line"]}">'
                f'<span>{render_text(it["text"])}</span></label>'
            )
        body.append("</section>")
    if not groups:
        body.append("<p class='empty'>Nothing open. 🎉</p>")
    return PAGE.replace("{{TOTAL}}", str(total)).replace("{{TODAY}}", today.isoformat()).replace("{{BODY}}", "\n".join(body))


PAGE = """<!doctype html>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Open actions</title>
<style>
  :root { color-scheme: light dark; --muted: #888; --line: #e3e3e3; --code: #f1f1f1; --person: #dbe9ff; --topic: #e6f5e0; }
  @media (prefers-color-scheme: dark) { :root { --line: #333; --code: #2a2a2a; --person: #1e3a5f; --topic: #1f3d1f; } }
  body { font: 15px/1.5 -apple-system, system-ui, sans-serif; max-width: 760px; margin: 2.5rem auto; padding: 0 1.25rem; }
  h1 { font-size: 1.4rem; margin: 0 0 .25rem; }
  h1 small, h2 small { color: var(--muted); font-weight: normal; font-size: .85em; margin-left: .5rem; }
  .status { color: var(--muted); font-size: .9rem; margin-bottom: 1.5rem; }
  h2 { font-size: 1rem; margin: 1.5rem 0 .5rem; padding-bottom: .25rem; border-bottom: 1px solid var(--line); }
  .item { display: grid; grid-template-columns: 1.1rem 1fr; gap: .7rem; padding: .35rem 0; cursor: pointer; align-items: start; }
  .item input { margin: .3rem 0 0; }
  .item.done > span { opacity: .45; text-decoration: line-through; }
  .item.busy { opacity: .6; pointer-events: none; }
  a { color: inherit; text-decoration: underline dotted; }
  code { background: var(--code); padding: 0 .3em; border-radius: 3px; font-size: .92em; }
  .person, .topic { padding: 0 .35em; border-radius: 3px; }
  .person { background: var(--person); } .topic { background: var(--topic); }
  .empty { color: var(--muted); }
  .error { color: #c33; }
</style>
<h1>Open actions <small id="count">{{TOTAL}}</small></h1>
<div class="status">{{TODAY}} · a tick rewrites the box in <code>wiki/daily/&lt;date&gt;.md</code> · reload to refresh</div>
{{BODY}}
<script>
  const count = document.getElementById('count');
  document.querySelectorAll('.item input').forEach(box => box.addEventListener('change', async () => {
    const item = box.closest('.item');
    item.classList.add('busy');
    const r = await fetch('/toggle', { method: 'POST', body: JSON.stringify({ file: box.dataset.file, line: +box.dataset.line, done: box.checked }) });
    item.classList.remove('busy');
    if (!r.ok) { box.checked = !box.checked; item.classList.add('error'); item.title = 'Line moved — reload the page'; return; }
    item.classList.toggle('done', box.checked);
    count.textContent = document.querySelectorAll('.item:not(.done)').length;
  }));
</script>
"""


# --- serve ------------------------------------------------------------------

class Handler(BaseHTTPRequestHandler):
    def log_message(self, *_):
        pass

    def _send(self, code, body, ctype="text/html; charset=utf-8"):
        data = body.encode()
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path != "/":
            return self._send(404, "not found", "text/plain")
        self._send(200, render_page())

    def do_POST(self):
        if self.path == "/quit":
            self._send(200, "bye", "text/plain")
            threading.Thread(target=self.server.shutdown).start()
            return
        if self.path != "/toggle":
            return self._send(404, "not found", "text/plain")
        req = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))))
        new = toggle(str(req.get("file", "")), int(req.get("line", -1)), bool(req.get("done")))
        if new is None:
            return self._send(409, json.dumps({"error": "line moved; reload"}), "application/json")
        self._send(200, json.dumps({"line": new}), "application/json")


def main(argv):
    if argv[1:] == ["stop"]:
        try:
            urllib.request.urlopen(urllib.request.Request(URL + "quit", method="POST"), timeout=2)
            print("stopped")
        except OSError:
            print("not running")
        return

    try:
        server = HTTPServer(("127.0.0.1", PORT), Handler)
    except OSError:  # already listening — just open the page
        print(URL)
        webbrowser.open(URL)
        return

    if argv[1:] == ["--foreground"]:
        print(URL)
        webbrowser.open(URL)
        server.serve_forever()
        return

    if os.fork():  # parent: open the page and return the terminal
        print(URL, flush=True)
        webbrowser.open(URL)
        os._exit(0)
    # child: detach and serve until `todo.py stop`
    os.setsid()
    devnull = os.open(os.devnull, os.O_RDWR)
    for fd in (0, 1, 2):
        os.dup2(devnull, fd)
    server.serve_forever()


if __name__ == "__main__":
    main(sys.argv)
