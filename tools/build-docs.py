#!/usr/bin/env python3
"""Generate docs/*.html from a shared layout plus per-page sources in docs/_src/.

Edit a page's content by editing its source file in docs/_src/.
Edit the shared shell (head, nav, sidebar, footer) by editing this file.

Run:
    python3 tools/build-docs.py          # rebuild all pages
    python3 tools/build-docs.py --check  # exit 1 if checked-in HTML is stale

No external dependencies. Standard library only.
"""

from __future__ import annotations

import argparse
import re
import string
import sys
from pathlib import Path

REPO    = Path(__file__).resolve().parent.parent
SRC_DIR = REPO / "docs" / "_src"
OUT_DIR = REPO / "docs"

# Sidebar order = list order.
PAGES = [
    {"slug": "index",           "title": "SubVault — Docs",                 "label": "Overview",        "url": "/docs",                 "crumb": "/ docs"},
    {"slug": "setup",           "title": "Setup — SubVault Docs",           "label": "Setup",           "url": "/docs/setup",           "crumb": "/ docs / setup"},
    {"slug": "tools",           "title": "Tools — SubVault Docs",           "label": "Tools",           "url": "/docs/tools",           "crumb": "/ docs / tools"},
    {"slug": "troubleshooting", "title": "Troubleshooting — SubVault Docs", "label": "Troubleshooting", "url": "/docs/troubleshooting", "crumb": "/ docs / troubleshooting"},
]

TOP_NAV = [
    ("Security", "/security"),
    ("Privacy",  "/privacy/"),
    ("GitHub",   "https://github.com/gavinb-code/subvault"),
]

FOOTER_LINKS = [
    ("subvault.ai", "/"),
    ("Dashboard",   "/dashboard"),
    ("Security",    "/security"),
    ("Privacy",     "/privacy/"),
    ("Terms",       "/terms/"),
]

# string.Template uses $var syntax, so literal "{" and "}" in HTML pass
# through unchanged.
LAYOUT = string.Template("""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>$title</title>
<meta name="description" content="$description">
<link rel="icon" type="image/svg+xml" href="/favicon.svg">
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/docs/docs.css">
</head>
<body>

<div id="svnav" role="banner">
<div class="svn-in">
<a class="svn-brand" href="/"><span class="svn-mark" aria-hidden="true"><svg width="30" height="30" viewBox="0 0 32 32"><rect x="6" y="8" width="20" height="4" rx="2" fill="white" opacity="0.45"/><rect x="6" y="14" width="20" height="4" rx="2" fill="white" opacity="0.7"/><rect x="6" y="20" width="20" height="4" rx="2" fill="white"/></svg></span>SubVault</a>
<div class="svn-right"><div class="dd"><button class="dd-btn" type="button" aria-expanded="false" aria-haspopup="true">Docs<svg class="car" width="10" height="6" viewBox="0 0 10 6" fill="none" aria-hidden="true"><path d="M1 1l4 4 4-4" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/></svg></button><div class="dd-menu" role="menu" hidden><a role="menuitem" href="/docs">Overview</a><a role="menuitem" href="/docs/setup.html">Setup</a><a role="menuitem" href="/docs/tools.html">Tools</a><a role="menuitem" href="/docs/troubleshooting.html">Troubleshooting</a></div></div><a class="svn-gh" href="https://github.com/subvaultlabs/subvault" aria-label="SubVault on GitHub"><svg width="15" height="15" viewBox="0 0 16 16" fill="currentColor" aria-hidden="true"><path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82a7.42 7.42 0 0 1 4 0c1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.01 8.01 0 0 0 16 8c0-4.42-3.58-8-8-8z"/></svg><span class="svn-hide">GitHub</span></a><a class="svn-btn" href="/?signup=1">Join early access</a></div>
</div>
</div>
<style>
#svnav{position:sticky;top:0;z-index:50;background:rgba(240,239,245,.82);backdrop-filter:blur(14px);-webkit-backdrop-filter:blur(14px);border-bottom:1px solid rgba(13,12,18,.08);margin:0 0 24px}
#svnav .svn-in{max-width:1180px;margin:0 auto;padding:0 32px;height:68px;display:flex;align-items:center;gap:34px}
#svnav a{text-decoration:none}
#svnav .svn-brand{display:flex;align-items:center;gap:11px;font-family:'IBM Plex Mono',ui-monospace,monospace;font-weight:600;font-size:17px;letter-spacing:-.3px;color:#0D0C12}
#svnav .svn-mark{width:30px;height:30px;border-radius:8px;background:#0D0C12;display:grid;place-items:center;flex:none}
#svnav .svn-right{margin-left:auto;display:flex;align-items:center;gap:10px}
#svnav .svn-gh{display:inline-flex;align-items:center;gap:8px;font-family:'IBM Plex Mono',ui-monospace,monospace;font-size:13px;color:rgba(13,12,18,.62);border:1px solid rgba(13,12,18,.08);border-radius:8px;padding:9px 13px;min-height:44px}
#svnav .svn-gh:hover{color:#0D0C12;border-color:rgba(13,12,18,.14)}
#svnav .svn-btn{display:inline-flex;align-items:center;justify-content:center;min-height:48px;padding:0 26px;border-radius:10px;font-family:'DM Sans',sans-serif;font-weight:600;font-size:15.5px;background:#2060E8;color:#fff;box-shadow:0 1px 2px rgba(13,12,18,.10),0 8px 24px -10px rgba(32,96,232,.55);transition:background .15s ease}
#svnav .svn-btn:hover{background:#1A4FC4}
#svnav .dd{position:relative}
#svnav .dd-btn{display:inline-flex;align-items:center;gap:7px;font-family:'IBM Plex Mono',ui-monospace,monospace;font-size:13px;color:rgba(13,12,18,.62);border:1px solid rgba(13,12,18,.08);border-radius:8px;padding:9px 13px;min-height:44px;background:transparent;cursor:pointer}
#svnav .dd-btn:hover{color:#0D0C12;border-color:rgba(13,12,18,.14)}
#svnav .dd-btn .car{transition:transform .15s ease}
#svnav .dd-btn[aria-expanded="true"] .car{transform:rotate(180deg)}
#svnav .dd-menu{position:absolute;top:calc(100% + 8px);right:0;background:#fff;border:1px solid rgba(13,12,18,.10);border-radius:12px;box-shadow:0 16px 40px -14px rgba(13,12,18,.3);padding:6px;min-width:196px;z-index:60}
#svnav .dd-menu a{display:block;padding:9px 12px;border-radius:8px;font-family:'DM Sans',sans-serif;font-size:14.5px;font-weight:500;color:rgba(13,12,18,.62)}
#svnav .dd-menu a:hover{color:#0D0C12;background:rgba(13,12,18,.05)}
@media (max-width:560px){#svnav .svn-hide{display:none}#svnav .svn-gh{padding:9px 11px}#svnav .svn-in{gap:14px;padding:0 18px}#svnav .svn-btn{min-height:44px;padding:0 18px;font-size:14.5px}}
</style>
<script>
(function(){var b=document.querySelector('#svnav .dd-btn'),m=document.querySelector('#svnav .dd-menu');if(!b||!m)return;function c(){m.hidden=true;b.setAttribute('aria-expanded','false')}
b.addEventListener('click',function(e){e.stopPropagation();var o=m.hidden;m.hidden=!o;b.setAttribute('aria-expanded',o?'true':'false')});
document.addEventListener('click',function(e){if(!m.hidden&&!m.contains(e.target)&&e.target!==b)c()});
document.addEventListener('keydown',function(e){if(e.key==='Escape')c()});
})();
</script>

<div class="layout">
<aside>
  <h3>Docs</h3>
  <ul>
$sidebar
  </ul>
</aside>

<main>
$content
</main>
</div>

<footer>
$footer
</footer>

$scripts
</body>
</html>
""")

# Source files start with an HTML-comment metadata block, then the body
# (everything inside <main>). Example:
#
#     <!-- description: Setup guide for SubVault.
#          scripts: tabs -->
#     <h1>Setup</h1>
#     ...
#
# `description` is required. `scripts` is an optional comma-separated list of
# script names from SCRIPT_REGISTRY.

META_RE = re.compile(r"^<!--\s*(.*?)\s*-->\s*", re.DOTALL)


def parse_source(text: str) -> tuple[dict[str, str], str]:
    match = META_RE.match(text)
    if not match:
        raise ValueError("source file missing leading <!-- meta --> block")
    meta: dict[str, str] = {}
    for line in match.group(1).splitlines():
        line = line.strip()
        if not line or ":" not in line:
            continue
        key, _, value = line.partition(":")
        meta[key.strip()] = value.strip()
    if "description" not in meta:
        raise ValueError("source file metadata missing 'description'")
    body = text[match.end():].strip() + "\n"
    return meta, body


SCRIPT_REGISTRY = {
    "tabs": """<script>
(function () {
  function show(name, btn) {
    document.querySelectorAll(".tab").forEach(function (t) { t.classList.remove("active"); });
    document.querySelectorAll(".tab-panel").forEach(function (p) { p.classList.remove("active"); });
    btn.classList.add("active");
    var panel = document.getElementById("tab-" + name);
    if (panel) panel.classList.add("active");
  }
  document.addEventListener("click", function (e) {
    var btn = e.target.closest(".tab[data-tab]");
    if (btn) show(btn.getAttribute("data-tab"), btn);
  });
})();
</script>""",
}


def render_top_nav() -> str:
    return "\n".join(f'    <a href="{href}">{label}</a>' for label, href in TOP_NAV)


def render_sidebar(current_slug: str) -> str:
    lines = []
    for page in PAGES:
        cls = ' class="current"' if page["slug"] == current_slug else ""
        lines.append(f'    <li><a href="{page["url"]}"{cls}>{page["label"]}</a></li>')
    return "\n".join(lines)


def render_footer() -> str:
    parts = [f'  <a href="{href}">{label}</a>' for label, href in FOOTER_LINKS]
    return " &middot;\n".join(parts)


def render_scripts(meta: dict[str, str]) -> str:
    names = [n.strip() for n in meta.get("scripts", "").split(",") if n.strip()]
    blocks = []
    for name in names:
        if name not in SCRIPT_REGISTRY:
            raise ValueError(f"unknown script in metadata: {name!r}")
        blocks.append(SCRIPT_REGISTRY[name])
    return "\n".join(blocks)


def render_page(page: dict, source_text: str) -> str:
    meta, body = parse_source(source_text)
    return LAYOUT.substitute(
        title=page["title"],
        description=meta["description"],
        crumb=page["crumb"],
        top_nav=render_top_nav(),
        sidebar=render_sidebar(page["slug"]),
        content=body.rstrip() + "\n",
        footer=render_footer(),
        scripts=render_scripts(meta),
    )


def build_all(check_only: bool = False) -> int:
    rc = 0
    for page in PAGES:
        src_path = SRC_DIR / f"{page['slug']}.html"
        out_path = OUT_DIR / f"{page['slug']}.html"
        if not src_path.exists():
            print(f"  ERROR: source missing: {src_path}", file=sys.stderr)
            return 1
        rendered = render_page(page, src_path.read_text(encoding="utf-8"))
        if check_only:
            existing = out_path.read_text(encoding="utf-8") if out_path.exists() else ""
            if existing != rendered:
                print(f"  ✗ out-of-date: {out_path.relative_to(REPO)}")
                rc = 1
            else:
                print(f"  ✓ up-to-date:  {out_path.relative_to(REPO)}")
        else:
            out_path.write_text(rendered, encoding="utf-8")
            print(f"  wrote {out_path.relative_to(REPO)} ({len(rendered)} bytes)")
    return rc


def main() -> int:
    ap = argparse.ArgumentParser(description="Generate docs/*.html from docs/_src/*.html")
    ap.add_argument("--check", action="store_true",
                    help="exit 1 if checked-in docs HTML would differ from a fresh build")
    args = ap.parse_args()
    return build_all(check_only=args.check)


if __name__ == "__main__":
    sys.exit(main())
