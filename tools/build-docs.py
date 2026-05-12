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

<nav class="top">
  <a href="/" class="logo"><img src="/logo-120.png" alt="SubVault">SubVault <span class="crumb">$crumb</span></a>
  <div class="nav-links">
$top_nav
  </div>
</nav>

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
