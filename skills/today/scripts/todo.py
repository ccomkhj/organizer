#!/usr/bin/env python3
"""Open actions from wiki/daily/ as a clickable checklist on localhost.

    python3 skills/today/scripts/todo.py         # start the server (if not running) and open the page
    python3 skills/today/scripts/todo.py stop    # stop it

Ticking a box rewrites `- [ ]` to `- [x]` in the daily note the line came from.
When wiki/ is a git checkout, each page load and each tick pulls first and each tick
is pushed, so the page and the cloud routine see the same notes. The daily notes
stay the single source of truth; this page is only a view on them.
Standard library only, bound to 127.0.0.1.
"""
import html
import json
import os
import re
import subprocess
import sys
import threading
import urllib.request
import webbrowser
from datetime import date
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
WIKI = ROOT / "wiki"
DAILY = WIKI / "daily"
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


def toggle(file, line, text, done):
    """Flip one checkbox in place. Returns the new line, or None if the target is gone.

    A pull since the page rendered can shift lines, so the box is matched by its text
    and looked up again when it is no longer at its line.
    """
    if not NOTE.match(file):
        return None
    path = DAILY / file
    lines = path.read_text().split("\n")
    if not (0 <= line < len(lines) and BOX.match(lines[line]) and lines[line][6:] == text):
        hits = [n for n, l in enumerate(lines) if BOX.match(l) and l[6:] == text]
        if len(hits) != 1:
            return None
        line = hits[0]
    lines[line] = "- [x] " + lines[line][6:] if done else "- [ ] " + lines[line][6:]
    path.write_text("\n".join(lines))
    return lines[line]


# --- pull / push ------------------------------------------------------------
# The cloud routine writes the wiki too. A page load pulls; a tick pulls, is written
# onto the fresh note, and is pushed at once, so a tick never has to be rebased over
# a cloud edit next to it. All git work is a no-op when wiki/ is not a git checkout.

GIT_LOCK = threading.Lock()


def git(*args, timeout=60):
    env = {**os.environ, "GIT_TERMINAL_PROMPT": "0"}
    try:
        return subprocess.run(["git", "-C", str(WIKI), *args], stdin=subprocess.DEVNULL,
                              capture_output=True, env=env, timeout=timeout).returncode == 0
    except subprocess.TimeoutExpired:
        return False


def pull(timeout=60):
    """Rebase onto origin. A conflict is aborted, keeping local commits for the next try."""
    if git("pull", "--rebase", "--autostash", "-q", timeout=timeout):
        return True
    git("rebase", "--abort")
    return False


def refresh():
    """Pull what the cloud routine synced. False when offline or stuck on a conflict: the notes here may be stale."""
    if not (WIKI / ".git").exists():
        return True
    with GIT_LOCK:
        return pull(timeout=10)


def push(file):
    """Commit one tick and push it. Rejected → pull and push once more; still failing, the commit waits for the next one."""
    if not (WIKI / ".git").exists():
        return
    with GIT_LOCK:
        git("commit", "-qm", f"tick {file}", "--", f"daily/{file}")
        if not git("push", "-q") and pull():
            git("push", "-q")


# --- render -----------------------------------------------------------------

def render_text(text):
    """Escape, then light up links, [[wiki links]] and `code`."""
    t = html.escape(text, quote=False)
    t = re.sub(r"https?://[^\s<)]+", lambda m: f'<a href="{m[0]}" target="_blank" rel="noopener">{m[0].split("//", 1)[1].split("/", 1)[0]}</a>', t)
    t = re.sub(r"\[\[topics/([^\]]+)\]\]", r'<span class="topic">\1</span>', t)
    t = re.sub(r"\[\[([^\]]+)\]\]", r'<span class="person">\1</span>', t)
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
    return t


def render_page(fresh=True):
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
                f'<label class="item"><input type="checkbox" data-file="{it["file"]}" data-line="{it["line"]}" data-text="{html.escape(it["text"])}">'
                f'<span>{render_text(it["text"])}</span></label>'
            )
        body.append("</section>")
    if not groups:
        body.append("<p class='empty'>Nothing open. 🎉</p>")
    page = PAGE if fresh else PAGE.replace('class="banner" hidden>', f'class="banner">{STALE}')
    return page.replace("{{TOTAL}}", str(total)).replace("{{TODAY}}", today.isoformat()).replace("{{BODY}}", "\n".join(body))


STALE = "Could not pull the wiki (offline, or a conflict) — these are the notes on this machine. Ticks still save here; run /today to reconcile."


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
  .banner { background: #c33; color: #fff; padding: .5rem .75rem; border-radius: 4px; margin-bottom: 1rem; }
</style>
<h1>Open actions <small id="count">{{TOTAL}}</small></h1>
<div id="banner" class="banner" hidden></div>
<div class="status">{{TODAY}} · a tick rewrites the box in <code>wiki/daily/&lt;date&gt;.md</code> and pushes it · reload to pull</div>
{{BODY}}
<script>
  const count = document.getElementById('count');
  document.querySelectorAll('.item input').forEach(box => box.addEventListener('change', async () => {
    const item = box.closest('.item');
    item.classList.add('busy');
    let r;
    try { r = await fetch('/toggle', { method: 'POST', body: JSON.stringify({ file: box.dataset.file, line: +box.dataset.line, text: box.dataset.text, done: box.checked }) }); }
    catch (e) { r = null; }
    item.classList.remove('busy');
    if (!r) { box.checked = !box.checked; fail('Server not running — nothing was saved. Run  python3 skills/today/scripts/todo.py  and reload.'); return; }
    if (!r.ok) { box.checked = !box.checked; fail('That line moved in the note — reload the page and tick again.'); return; }
    item.classList.toggle('done', box.checked);
    count.textContent = document.querySelectorAll('.item:not(.done)').length;
  }));
  function fail(msg) { const b = document.getElementById('banner'); b.textContent = msg; b.hidden = false; }
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
        self._send(200, render_page(refresh()))

    def do_POST(self):
        if self.path == "/quit":
            self._send(200, "bye", "text/plain")
            threading.Thread(target=self.server.shutdown).start()
            return
        if self.path != "/toggle":
            return self._send(404, "not found", "text/plain")
        req = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))))
        file = str(req.get("file", ""))
        refresh()
        new = toggle(file, int(req.get("line", -1)), str(req.get("text", "")), bool(req.get("done")))
        if new is None:
            return self._send(409, json.dumps({"error": "line moved; reload"}), "application/json")
        threading.Thread(target=push, args=(file,)).start()
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
