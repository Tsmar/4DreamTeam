from __future__ import annotations

import html
import json
import re
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path, PurePosixPath
from typing import Any
from urllib.parse import parse_qs, quote, unquote, urlparse

from fourdt_wiki.cli import SECTION_KEYS, find_page, search_pages, section_body, status_payload, wiki_pages


STYLE = """
:root {
  color-scheme: light dark;
  --bg: #f7f8f3;
  --ink: #232522;
  --muted: #676d65;
  --line: #d9ded2;
  --panel: #ffffff;
  --accent: #0c6b58;
  --accent-weak: #e4f3ef;
  --danger: #8f2d25;
}
@media (prefers-color-scheme: dark) {
  :root {
    --bg: #181b1a;
    --ink: #f0f2ec;
    --muted: #aeb7ac;
    --line: #37413d;
    --panel: #202522;
    --accent: #79d8bf;
    --accent-weak: #153a32;
    --danger: #ff9b8d;
  }
}
:root[data-theme="light"] {
  color-scheme: light;
  --bg: #f7f8f3;
  --ink: #232522;
  --muted: #676d65;
  --line: #d9ded2;
  --panel: #ffffff;
  --accent: #0c6b58;
  --accent-weak: #e4f3ef;
  --danger: #8f2d25;
}
:root[data-theme="dark"] {
  color-scheme: dark;
  --bg: #181b1a;
  --ink: #f0f2ec;
  --muted: #aeb7ac;
  --line: #37413d;
  --panel: #202522;
  --accent: #79d8bf;
  --accent-weak: #153a32;
  --danger: #ff9b8d;
}
* { box-sizing: border-box; }
body {
  margin: 0;
  font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  color: var(--ink);
  background: var(--bg);
}
a { color: var(--accent); cursor: pointer; text-decoration: none; }
a:hover { text-decoration: underline; }
.shell { max-width: 1180px; margin: 0 auto; padding: 104px 24px 48px; }
.topbar {
  position: fixed;
  z-index: 20;
  top: 0;
  left: 0;
  right: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  border-bottom: 1px solid var(--line);
  background: color-mix(in srgb, var(--bg) 96%, transparent);
  backdrop-filter: blur(10px);
}
.topbar-inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 18px;
  width: 100%;
  max-width: 1180px;
  padding: 16px 24px;
}
.brand { display: flex; flex: 1 1 auto; min-width: 0; flex-direction: column; gap: 2px; }
.brand strong { font-size: 22px; letter-spacing: 0; }
.brand span { color: var(--muted); font-size: 13px; }
.top-actions { display: flex; flex: 0 1 430px; align-items: center; justify-content: flex-end; gap: 12px; min-width: 0; }
.top-link { color: var(--muted); font-size: 13px; font-weight: 650; }
.theme-toggle {
  display: inline-flex;
  flex: 0 0 auto;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border: 1px solid var(--line);
  border-radius: 6px;
  background: var(--panel);
  color: var(--ink);
  cursor: pointer;
}
.theme-toggle svg { width: 18px; height: 18px; }
.theme-toggle .theme-icon-dark { display: none; }
:root[data-theme="dark"] .theme-toggle .theme-icon-light { display: none; }
:root[data-theme="dark"] .theme-toggle .theme-icon-dark { display: block; }
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) .theme-toggle .theme-icon-light { display: none; }
  :root:not([data-theme="light"]) .theme-toggle .theme-icon-dark { display: block; }
}
.menu-toggle { display: none; }
.menu-button {
  display: none;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border: 1px solid var(--line);
  border-radius: 6px;
  background: var(--panel);
  color: var(--ink);
  font-size: 22px;
  line-height: 1;
}
.search { position: relative; display: flex; min-width: 320px; }
.search-icon {
  position: absolute;
  left: 12px;
  top: 50%;
  width: 16px;
  height: 16px;
  transform: translateY(-50%);
  color: var(--muted);
  pointer-events: none;
}
.search input {
  width: 100%;
  border: 1px solid var(--line);
  border-radius: 6px;
  padding: 10px 12px 10px 36px;
  font-size: 14px;
  background: var(--panel);
}
.layout { display: grid; grid-template-columns: 280px minmax(0, 1fr); gap: 22px; align-items: start; }
.sidebar, .content {
  background: var(--panel);
  border: 1px solid var(--line);
  border-radius: 8px;
}
.sidebar { padding: 14px; position: sticky; top: 88px; max-height: calc(100vh - 112px); overflow: auto; }
.sidebar h2, .content h1 { margin: 0; }
.sidebar h2 { font-size: 13px; color: var(--muted); text-transform: uppercase; }
.nav-group { margin-top: 16px; }
.nav-group:first-of-type { margin-top: 10px; }
.nav-group h3 {
  margin: 0 0 6px;
  color: var(--muted);
  font-size: 11px;
  font-weight: 750;
  text-transform: uppercase;
}
.page-list { list-style: none; margin: 12px 0 0; padding: 0; display: flex; flex-direction: column; gap: 4px; }
.nav-group .page-list { margin-top: 0; }
.page-list a {
  display: block;
  border-radius: 6px;
  padding: 8px 9px;
  color: var(--ink);
  overflow-wrap: anywhere;
}
.page-list a.active, .page-list a:hover, .page-list a:focus-visible {
  background: var(--accent-weak);
  outline: none;
  text-decoration: none;
}
.content { padding: 24px; min-width: 0; }
.breadcrumbs {
  margin: 0 0 10px;
  color: var(--muted);
  font-size: 13px;
}
.meta { color: var(--muted); font-size: 13px; margin: 6px 0 18px; }
.pill {
  display: inline-flex;
  align-items: center;
  border: 1px solid var(--line);
  border-radius: 999px;
  padding: 2px 8px;
  margin-right: 5px;
  color: var(--muted);
  font-size: 12px;
}
a.pill:hover, a.pill:focus-visible { background: var(--accent-weak); color: var(--accent); text-decoration: none; }
.section { border-top: 1px solid var(--line); padding-top: 18px; margin-top: 18px; }
.section h2 { font-size: 17px; margin: 0 0 10px; }
.markdown { line-height: 1.58; overflow-wrap: anywhere; }
.markdown pre {
  overflow: auto;
  padding: 12px;
  border-radius: 6px;
  background: var(--accent-weak);
}
.markdown code { background: var(--accent-weak); padding: 1px 4px; border-radius: 4px; }
.markdown ul { padding-left: 22px; }
.result { border-top: 1px solid var(--line); padding: 14px 0; }
.result:first-of-type { border-top: 0; }
.result h2 a {
  display: block;
  border-radius: 6px;
  padding: 6px 0;
}
.result h2 a:hover, .result h2 a:focus-visible {
  background: var(--accent-weak);
  outline: none;
  text-decoration: none;
}
.empty { color: var(--muted); }
.error { color: var(--danger); }
@media (max-width: 820px) {
  .shell { padding-top: 88px; }
  .topbar-inner {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 12px 16px;
  }
  .brand { flex: 0 1 auto; min-width: 0; }
  .brand strong { font-size: 16px; white-space: nowrap; }
  .brand span, .top-link { display: none; }
  .menu-button { display: inline-flex; flex: 0 0 auto; }
  .search { min-width: 0; width: 100%; }
  .top-actions { flex: 1 1 220px; justify-content: flex-end; min-width: 120px; }
  .layout { display: block; }
  .sidebar {
    position: fixed;
    z-index: 30;
    top: 64px;
    bottom: 0;
    left: 0;
    width: min(84vw, 320px);
    max-height: none;
    border-radius: 0 8px 0 0;
    transform: translateX(-105%);
    transition: transform 160ms ease;
  }
  .menu-toggle:checked ~ .layout .sidebar { transform: translateX(0); }
}
@media (max-width: 520px) {
  .brand { display: none; }
  .top-actions { flex-basis: auto; min-width: 0; }
}
"""

SCRIPT = """
<script>
(() => {
  const root = document.documentElement;
  const themeButton = document.querySelector('[data-theme-toggle]');
  const storedTheme = localStorage.getItem('4dt-theme');
  const systemTheme = () => window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  const currentTheme = () => root.dataset.theme || storedTheme || systemTheme();
  if (storedTheme === 'light' || storedTheme === 'dark') {
    root.dataset.theme = storedTheme;
  }
  const syncThemeButton = () => {
    if (!themeButton) return;
    const theme = currentTheme();
    themeButton.setAttribute('aria-label', theme === 'dark' ? 'Switch to light theme' : 'Switch to dark theme');
    themeButton.setAttribute('title', theme === 'dark' ? 'Light theme' : 'Dark theme');
  };
  themeButton?.addEventListener('click', () => {
    const next = currentTheme() === 'dark' ? 'light' : 'dark';
    root.dataset.theme = next;
    localStorage.setItem('4dt-theme', next);
    syncThemeButton();
  });
  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', syncThemeButton);
  syncThemeButton();

  const form = document.querySelector('[data-search-form]');
  if (!form) return;
  const input = form.querySelector('input[name="q"]');
  let timer = 0;
  const runSearch = () => {
    const query = input.value.trim();
    window.clearTimeout(timer);
    timer = window.setTimeout(() => {
      const current = new URL(window.location.href);
      if (query.length >= 2) {
        if (current.pathname !== '/search' || current.searchParams.get('q') !== query) {
          window.location.href = `/search?q=${encodeURIComponent(query)}`;
        }
      } else if (current.pathname === '/search' && !query) {
        window.location.href = '/';
      }
    }, 180);
  };
  form.addEventListener('submit', (event) => event.preventDefault());
  input.addEventListener('input', runSearch);
  input.addEventListener('keydown', (event) => {
    if (event.key !== 'Escape') return;
    event.preventDefault();
    input.value = '';
    window.clearTimeout(timer);
    if (window.location.pathname === '/search') {
      window.location.href = '/';
    }
  });
})();
</script>
"""

HEAD_SCRIPT = """
<script>
(() => {
  const theme = localStorage.getItem('4dt-theme');
  if (theme === 'light' || theme === 'dark') {
    document.documentElement.dataset.theme = theme;
  }
})();
</script>
"""


def nav_group_for(relpath: str) -> str:
    path = PurePosixPath(relpath)
    if len(path.parts) > 1:
        return titleize_path_part(path.parts[0])
    return "Reference"


def include_in_sidebar(relpath: str) -> bool:
    return not relpath.startswith("changelog/")


def escape(value: Any) -> str:
    return html.escape(str(value), quote=True)


def page_href(page_id: str, section: str | None = None) -> str:
    href = f"/page/{quote(page_id)}"
    if section:
        href += f"#{quote(section)}"
    return href


def tag_href(tag: str) -> str:
    return f"/tag/{quote(tag)}"


def titleize_path_part(part: str) -> str:
    stem = PurePosixPath(part).stem
    return " ".join(word.upper() if word.lower() == "readme" else word.capitalize() for word in stem.split("-"))


def breadcrumb_html(page_relpath: str, title: str) -> str:
    parts = PurePosixPath(page_relpath).with_suffix("").parts
    if not parts:
        return ""
    crumbs = [titleize_path_part(part) for part in parts[:-1]] + [title]
    return '<nav class="breadcrumbs" aria-label="Breadcrumbs">' + " / ".join(escape(crumb) for crumb in crumbs) + "</nav>"


def tag_counts(workspace: Path) -> list[dict[str, Any]]:
    counts: dict[str, int] = {}
    for page in wiki_pages(workspace):
        for tag in page.tags or []:
            counts[tag] = counts.get(tag, 0) + 1
    return [{"tag": tag, "count": count} for tag, count in sorted(counts.items())]


def pages_for_tag(workspace: Path, tag: str) -> list[Any]:
    return sorted((page for page in wiki_pages(workspace) if tag in (page.tags or [])), key=lambda page: page.relpath)


LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")


def normalize_wiki_path(base_relpath: str | None, target: str) -> str:
    if not base_relpath:
        return str(PurePosixPath(target))
    base_dir = PurePosixPath(base_relpath).parent
    normalized = PurePosixPath(base_dir, target)
    parts: list[str] = []
    for part in normalized.parts:
        if part in {"", "."}:
            continue
        if part == "..":
            if parts:
                parts.pop()
            continue
        parts.append(part)
    return "/".join(parts)


def resolve_link_href(target: str, base_relpath: str | None, page_lookup: dict[str, str] | None) -> str:
    parsed = urlparse(target)
    if parsed.scheme in {"http", "https", "mailto"}:
        return target
    if target.startswith("#"):
        return target
    if target.startswith("/"):
        return target

    path, _hash, fragment = target.partition("#")
    normalized = normalize_wiki_path(base_relpath, unquote(path))
    page_id = (page_lookup or {}).get(normalized)
    if page_id:
        return page_href(page_id, fragment or None)
    return target


def format_text_links(text: str, base_relpath: str | None, page_lookup: dict[str, str] | None) -> str:
    rendered: list[str] = []
    index = 0
    for match in LINK_RE.finditer(text):
        rendered.append(escape(text[index : match.start()]))
        label = match.group(1)
        target = match.group(2)
        href = resolve_link_href(target, base_relpath, page_lookup)
        rendered.append(f'<a href="{escape(href)}">{escape(label)}</a>')
        index = match.end()
    rendered.append(escape(text[index:]))
    return "".join(rendered)


def format_inline(text: str, base_relpath: str | None = None, page_lookup: dict[str, str] | None = None) -> str:
    parts = text.split("`")
    if len(parts) == 1:
        return format_text_links(text, base_relpath, page_lookup)
    rendered: list[str] = []
    for index, part in enumerate(parts):
        if index % 2:
            rendered.append(f"<code>{escape(part)}</code>")
        else:
            rendered.append(format_text_links(part, base_relpath, page_lookup))
    return "".join(rendered)


def render_markdown(text: str, base_relpath: str | None = None, page_lookup: dict[str, str] | None = None) -> str:
    lines = text.strip().splitlines()
    output: list[str] = []
    in_list = False
    in_code = False
    code_lines: list[str] = []
    paragraph: list[str] = []

    def flush_paragraph() -> None:
        nonlocal paragraph
        if paragraph:
            output.append(f"<p>{format_inline(' '.join(paragraph), base_relpath, page_lookup)}</p>")
            paragraph = []

    def flush_list() -> None:
        nonlocal in_list
        if in_list:
            output.append("</ul>")
            in_list = False

    for raw_line in lines:
        line = raw_line.rstrip()
        if line.strip().startswith("```"):
            flush_paragraph()
            flush_list()
            if in_code:
                output.append(f"<pre><code>{escape(chr(10).join(code_lines))}</code></pre>")
                code_lines = []
                in_code = False
            else:
                in_code = True
            continue
        if in_code:
            code_lines.append(line)
            continue
        if not line.strip():
            flush_paragraph()
            flush_list()
            continue
        if line.startswith("- "):
            flush_paragraph()
            if not in_list:
                output.append("<ul>")
                in_list = True
            output.append(f"<li>{format_inline(line[2:].strip(), base_relpath, page_lookup)}</li>")
            continue
        flush_list()
        if line.startswith("### "):
            flush_paragraph()
            output.append(f"<h3>{format_inline(line[4:].strip(), base_relpath, page_lookup)}</h3>")
        elif line.startswith("## "):
            flush_paragraph()
            output.append(f"<h2>{format_inline(line[3:].strip(), base_relpath, page_lookup)}</h2>")
        elif line.startswith("# "):
            flush_paragraph()
            output.append(f"<h1>{format_inline(line[2:].strip(), base_relpath, page_lookup)}</h1>")
        else:
            paragraph.append(line.strip())

    if in_code:
        output.append(f"<pre><code>{escape(chr(10).join(code_lines))}</code></pre>")
    flush_paragraph()
    flush_list()
    return "\n".join(output) if output else "<p class=\"empty\">Empty section.</p>"


def render_shell(workspace: Path, title: str, body: str, *, active_page_id: str | None = None, query: str = "") -> str:
    pages = sorted((page for page in wiki_pages(workspace) if include_in_sidebar(page.relpath)), key=lambda page: page.relpath)
    grouped_items: dict[str, list[str]] = {}
    for page in pages:
        page_id = page.frontmatter.get("id", page.relpath)
        active = " class=\"active\"" if page_id == active_page_id else ""
        item = f"<li><a{active} href=\"{page_href(page_id)}\">{escape(page.frontmatter.get('title', page.relpath))}</a></li>"
        group = nav_group_for(page.relpath)
        grouped_items.setdefault(group, []).append(item)
    nav_groups = []
    for label in sorted(grouped_items):
        items = grouped_items[label]
        if items:
            nav_groups.append(
                f"<section class=\"nav-group\"><h3>{escape(label)}</h3><ul class=\"page-list\">{''.join(items)}</ul></section>"
            )
    page_count = len(pages)
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(title)} - 4DreamTeam Workspace View</title>
  {HEAD_SCRIPT}
  <style>{STYLE}</style>
</head>
<body>
  <main class="shell">
    <input class="menu-toggle" id="menu-toggle" type="checkbox" aria-label="Toggle wiki navigation">
    <header class="topbar">
      <div class="topbar-inner">
        <label class="menu-button" for="menu-toggle" aria-label="Open wiki navigation">&#9776;</label>
        <a class="brand" href="/">
          <strong>4DreamTeam</strong>
          <span>Workspace View · Wiki · {page_count} managed pages</span>
        </a>
        <div class="top-actions">
          <a class="top-link" href="/tags">Tags</a>
          <form class="search" action="/search" method="get" data-search-form>
            <span class="search-icon" aria-hidden="true">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="11" cy="11" r="7"></circle>
                <path d="m20 20-3.5-3.5"></path>
              </svg>
            </span>
            <input type="search" name="q" value="{escape(query)}" placeholder="Search wiki" aria-label="Search wiki">
          </form>
          <button class="theme-toggle" type="button" data-theme-toggle aria-label="Toggle theme">
            <svg class="theme-icon-light" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
              <circle cx="12" cy="12" r="4"></circle>
              <path d="M12 2v2"></path><path d="M12 20v2"></path><path d="m4.93 4.93 1.41 1.41"></path><path d="m17.66 17.66 1.41 1.41"></path><path d="M2 12h2"></path><path d="M20 12h2"></path><path d="m6.34 17.66-1.41 1.41"></path><path d="m19.07 4.93-1.41 1.41"></path>
            </svg>
            <svg class="theme-icon-dark" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
              <path d="M20.99 12.79A8.5 8.5 0 1 1 11.21 3.01 6.5 6.5 0 0 0 20.99 12.79Z"></path>
            </svg>
          </button>
        </div>
      </div>
    </header>
    <div class="layout">
      <nav class="sidebar" aria-label="Wiki pages">
        <h2>Wiki</h2>
        {''.join(nav_groups) or '<p class="empty">No pages yet.</p>'}
      </nav>
      <article class="content">
        {body}
      </article>
    </div>
  </main>
  {SCRIPT}
</body>
</html>"""


def render_home(workspace: Path) -> str:
    status = status_payload(workspace)
    body = [
        "<h1>Workspace View</h1>",
        f"<p class=\"meta\">Status: {escape(status['status'])}. Storage: {escape(status['wiki']['storage'])}.</p>",
    ]
    issues = status.get("issues") or []
    if issues:
        body.append("<section class=\"section\"><h2>Issues</h2>")
        for issue in issues:
            body.append(f"<p class=\"error\">{escape(issue.get('code', 'issue'))}: {escape(issue.get('message', ''))}</p>")
        body.append("</section>")
    else:
        body.extend(
            [
                "<div class=\"markdown\">",
                "<p>Use this local panel to inspect managed workspace knowledge while agents work. The first surface is the wiki; future surfaces can add board, memory, source, or release views without expanding domain CLIs.</p>",
                "<h2>Reading Boundaries</h2>",
                "<ul>",
                "<li>Product pages explain purpose, users, value, scope, and acceptance meaning.</li>",
                "<li>Workflow pages explain role movement, handoffs, and operating rules.</li>",
                "<li>Architecture pages explain repository and runtime structure.</li>",
                "<li>Domain pages explain one subsystem at a time.</li>",
                "<li>Contracts and schemas define stable tool APIs and storage details.</li>",
                "</ul>",
                "</div>",
            ]
        )
    return render_shell(workspace, "Home", "\n".join(body))


def render_page(workspace: Path, page_or_id: str) -> tuple[int, str]:
    try:
        page = find_page(workspace, page_or_id)
    except Exception as exc:
        return 404, render_shell(workspace, "Not Found", f"<h1>Page not found</h1><p class=\"error\">{escape(exc)}</p>")
    page_id = page.frontmatter.get("id", page.relpath)
    page_lookup = {wiki_page.relpath: wiki_page.frontmatter.get("id", wiki_page.relpath) for wiki_page in wiki_pages(workspace)}
    tags = "".join(f"<a class=\"pill\" href=\"{tag_href(tag)}\">{escape(tag)}</a>" for tag in (page.tags or []))
    title = page.frontmatter.get("title", page.relpath)
    body = [
        breadcrumb_html(page.relpath, title),
        f"<h1>{escape(title)}</h1>",
        (
            f"<p class=\"meta\">{escape(page.relpath)} · "
            f"{escape(page.frontmatter.get('kind', 'unknown'))} · "
            f"{escape(page.frontmatter.get('status', 'unknown'))}</p>"
        ),
        tags,
    ]
    for section_key, heading in SECTION_KEYS.items():
        try:
            content = section_body(page, section_key)
        except Exception:
            content = ""
        body.append(
            f"<section class=\"section\" id=\"{escape(section_key)}\">"
            f"<h2>{escape(heading)}</h2>"
            f"<div class=\"markdown\">{render_markdown(content, page.relpath, page_lookup)}</div>"
            "</section>"
        )
    return 200, render_shell(workspace, page.frontmatter.get("title", page.relpath), "\n".join(body), active_page_id=page_id)


def render_search(workspace: Path, query: str, limit: int = 20) -> str:
    body = [f"<h1>Search</h1>", f"<p class=\"meta\">Query: {escape(query) if query else 'empty'}</p>"]
    matches = search_pages(workspace, query, limit) if query.strip() else []
    if not matches:
        body.append("<p class=\"empty\">No results.</p>")
    for match in matches:
        page_id = match.get("id", "")
        sections = match.get("match_sections") or []
        section_links = " ".join(
            f"<a class=\"pill\" href=\"{page_href(page_id, section)}\">{escape(section)}</a>" for section in sections
        )
        body.append(
            "<section class=\"result\">"
            f"<h2><a href=\"{page_href(page_id)}\">{escape(match.get('title', page_id))}</a></h2>"
            f"<p class=\"meta\">{escape(match.get('path', ''))} · {escape(match.get('kind', ''))} · {escape(match.get('status', ''))}</p>"
            f"{section_links}"
            "</section>"
        )
    return render_shell(workspace, "Search", "\n".join(body), query=query)


def render_tags(workspace: Path) -> str:
    body = ["<h1>Tags</h1>", "<p class=\"meta\">Managed wiki tags by page count.</p>"]
    tags = tag_counts(workspace)
    if not tags:
        body.append("<p class=\"empty\">No tags.</p>")
    for item in tags:
        tag = item["tag"]
        body.append(
            "<section class=\"result\">"
            f"<h2><a href=\"{tag_href(tag)}\">{escape(tag)}</a></h2>"
            f"<p class=\"meta\">{item['count']} page{'s' if item['count'] != 1 else ''}</p>"
            "</section>"
        )
    return render_shell(workspace, "Tags", "\n".join(body))


def render_tag(workspace: Path, tag: str) -> tuple[int, str]:
    pages = pages_for_tag(workspace, tag)
    body = [f"<h1>Tag: {escape(tag)}</h1>", f"<p class=\"meta\">{len(pages)} related page{'s' if len(pages) != 1 else ''}.</p>"]
    if not pages:
        body.append("<p class=\"empty\">No pages for this tag.</p>")
        return 404, render_shell(workspace, f"Tag {tag}", "\n".join(body))
    for page in pages:
        page_id = page.frontmatter.get("id", page.relpath)
        body.append(
            "<section class=\"result\">"
            f"<h2><a href=\"{page_href(page_id)}\">{escape(page.frontmatter.get('title', page.relpath))}</a></h2>"
            f"<p class=\"meta\">{escape(page.relpath)} · {escape(page.frontmatter.get('kind', ''))} · {escape(page.frontmatter.get('status', ''))}</p>"
            "</section>"
        )
    return 200, render_shell(workspace, f"Tag {tag}", "\n".join(body))


def html_response(body: str, *, status: int = 200) -> tuple[int, str, bytes, str]:
    reason = "OK" if status == 200 else "Not Found"
    return status, reason, body.encode("utf-8"), "text/html; charset=utf-8"


def route_request(workspace: Path, raw_path: str) -> tuple[int, str, bytes, str]:
    parsed = urlparse(raw_path)
    path = parsed.path
    if path == "/healthz":
        body = json.dumps({"ok": True, "status": "ready"}, ensure_ascii=False).encode("utf-8")
        return 200, "OK", body, "application/json; charset=utf-8"
    if path == "/":
        return html_response(render_home(workspace))
    if path == "/search":
        query = parse_qs(parsed.query).get("q", [""])[0]
        return html_response(render_search(workspace, query))
    if path == "/tags":
        return html_response(render_tags(workspace))
    if path.startswith("/tag/"):
        status, body = render_tag(workspace, unquote(path.removeprefix("/tag/")))
        return html_response(body, status=status)
    if path.startswith("/page/"):
        page_or_id = unquote(path.removeprefix("/page/"))
        status, body = render_page(workspace, page_or_id)
        return html_response(body, status=status)
    return html_response(render_shell(workspace, "Not Found", "<h1>Not found</h1>"), status=404)


def make_handler(workspace: Path) -> type[BaseHTTPRequestHandler]:
    class WikiRequestHandler(BaseHTTPRequestHandler):
        server_version = "4dt-web/0.1.0"

        def do_GET(self) -> None:  # noqa: N802 - stdlib handler API
            status, reason, body, content_type = route_request(workspace, self.path)
            self.send_response(status, reason)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, format: str, *args: Any) -> None:
            print(f"4dt-web serve: {self.address_string()} - {format % args}", file=sys.stderr)

    return WikiRequestHandler


def serve(workspace: Path, host: str, port: int) -> dict[str, Any]:
    server = ThreadingHTTPServer((host, port), make_handler(workspace))
    url = f"http://{host}:{server.server_port}/"
    print(f"4dt-web serve: {url}", file=sys.stderr)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return {"url": url, "host": host, "port": server.server_port}
