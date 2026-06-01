from __future__ import annotations

import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "packages" / "web" / "src"))
sys.path.insert(0, str(ROOT / "packages" / "wiki" / "src"))

from fourdt_web.cli import main
from fourdt_web.server import route_request
from fourdt_wiki.cli import main as wiki_main


def run_help(args: list[str]) -> tuple[int, str]:
    stdout = io.StringIO()
    with contextlib.redirect_stdout(stdout), self_exit_to_code() as code:
        main(args)
    return code[0], stdout.getvalue()


def run_wiki(args: list[str]) -> tuple[int, dict[str, object]]:
    stdout = io.StringIO()
    with contextlib.redirect_stdout(stdout):
        exit_code = wiki_main(args)
    return exit_code, json.loads(stdout.getvalue())


@contextlib.contextmanager
def self_exit_to_code():
    code = [0]
    try:
        yield code
    except SystemExit as exc:
        code[0] = int(exc.code or 0)


class WebCliTests(unittest.TestCase):
    def test_help_exposes_read_only_server(self) -> None:
        exit_code, output = run_help(["--help"])

        self.assertEqual(exit_code, 0)
        self.assertIn("4dt-web", output)
        self.assertIn("Workspace View", output)

        exit_code, output = run_help(["serve", "--help"])
        self.assertEqual(exit_code, 0)
        self.assertIn("127.0.0.1", output)

    def test_routes_render_page_list_page_and_search(self) -> None:
        with tempfile.TemporaryDirectory() as raw_tmp:
            workspace = Path(raw_tmp)
            run_wiki(["--workspace", str(workspace), "--json", "init"])
            run_wiki(
                [
                    "--workspace",
                    str(workspace),
                    "--json",
                    "page",
                    "create",
                    "domains/payments.md",
                    "--title",
                    "Payments",
                    "--type",
                    "domain",
                    "--tag",
                    "Payment Domain",
                ]
            )
            run_wiki(
                [
                    "--workspace",
                    str(workspace),
                    "--json",
                    "page",
                    "section-set",
                    "domains-payments",
                    "summary",
                    "--content",
                    "Payments handles billing context.",
                ]
            )
            run_wiki(
                [
                    "--workspace",
                    str(workspace),
                    "--json",
                    "page",
                    "create",
                    "architecture/billing.md",
                    "--title",
                    "Billing Architecture",
                    "--type",
                    "architecture",
                    "--tag",
                    "Payment Domain",
                ]
            )
            run_wiki(
                [
                    "--workspace",
                    str(workspace),
                    "--json",
                    "page",
                    "section-set",
                    "architecture-billing",
                    "related",
                    "--content",
                    "- [Payments](../domains/payments.md)\n- [Payments summary](../domains/payments.md#summary)",
                ]
            )
            for relpath, title in (
                ("workflows/task-lifecycle.md", "Task Lifecycle"),
                ("workflows/wiki.md", "Wiki"),
                ("workflows/readme-maintenance.md", "README Maintenance"),
                ("changelog/2026-06-01.md", "Changelog 2026-06-01"),
            ):
                run_wiki(
                    [
                        "--workspace",
                        str(workspace),
                        "--json",
                        "page",
                        "create",
                        relpath,
                        "--title",
                        title,
                        "--type",
                        "changelog" if relpath.startswith("changelog/") else "flow",
                    ]
                )

            status, _reason, body, content_type = route_request(workspace, "/")
            self.assertEqual(status, 200)
            self.assertEqual(content_type, "text/html; charset=utf-8")
            home = body.decode("utf-8")
            self.assertIn("<strong>4DreamTeam</strong>", home)
            self.assertIn('href="/tags"', home)
            self.assertIn('class="menu-button"', home)
            self.assertIn('data-search-form', home)
            self.assertIn('class="search-icon"', home)
            self.assertIn('data-theme-toggle', home)
            top_actions = home[home.index('<div class="top-actions">') : home.index("</div>", home.index('<div class="top-actions">'))]
            self.assertLess(top_actions.index('data-search-form'), top_actions.index('data-theme-toggle'))
            self.assertIn("prefers-color-scheme: dark", home)
            self.assertIn("localStorage.getItem('4dt-theme')", home)
            self.assertIn("input.addEventListener('input', runSearch)", home)
            self.assertIn("event.key !== 'Escape'", home)
            self.assertNotIn('<button type="submit">Search</button>', home)
            self.assertIn(".top-actions { display: flex; flex: 0 1 430px;", home)
            self.assertIn(".top-actions { flex: 1 1 220px;", home)
            self.assertIn("position: fixed;", home)
            self.assertIn("menu-toggle:checked", home)
            self.assertIn("Reading Boundaries", home)
            self.assertIn("<h3>Start</h3>", home)
            self.assertIn("<h3>Workflows</h3>", home)
            workflows_nav = home[home.index("<h3>Workflows</h3>") :]
            self.assertLess(workflows_nav.index(">README Maintenance<"), workflows_nav.index(">Task Lifecycle<"))
            self.assertLess(workflows_nav.index(">Task Lifecycle<"), workflows_nav.index(">Wiki<"))
            self.assertIn("<h3>Domains</h3>", home)
            self.assertIn("/page/domains-payments", home)
            self.assertIn(">Changelog<", home)
            self.assertNotIn("Changelog 2026-06-01", home)

            status, _reason, body, _content_type = route_request(workspace, "/page/domains-payments")
            self.assertEqual(status, 200)
            page = body.decode("utf-8")
            self.assertIn("Payments", page)
            self.assertIn('class="breadcrumbs"', page)
            self.assertIn("Domains / Payments", page)
            self.assertIn("Payments handles billing context.", page)
            self.assertIn("Workspace View", page)
            self.assertIn('<a class="pill" href="/tag/payment-domain">payment-domain</a>', page)

            status, _reason, body, _content_type = route_request(workspace, "/page/architecture-billing")
            self.assertEqual(status, 200)
            related_page = body.decode("utf-8")
            self.assertIn('<a href="/page/domains-payments">Payments</a>', related_page)
            self.assertIn('<a href="/page/domains-payments#summary">Payments summary</a>', related_page)

            status, _reason, body, _content_type = route_request(workspace, "/tags")
            self.assertEqual(status, 200)
            tags = body.decode("utf-8")
            self.assertIn("Tags", tags)
            self.assertIn('<a href="/tag/payment-domain">payment-domain</a>', tags)
            self.assertIn("2 pages", tags)

            status, _reason, body, _content_type = route_request(workspace, "/tag/payment-domain")
            self.assertEqual(status, 200)
            tag_page = body.decode("utf-8")
            self.assertIn("Tag: payment-domain", tag_page)
            self.assertIn("/page/domains-payments", tag_page)
            self.assertIn("/page/architecture-billing", tag_page)

            status, _reason, body, _content_type = route_request(workspace, "/search?q=billing")
            self.assertEqual(status, 200)
            search = body.decode("utf-8")
            self.assertIn("Query: billing", search)
            self.assertIn('<h2><a href="/page/domains-payments">Payments</a></h2>', search)
            self.assertIn("/page/domains-payments#summary", search)
            self.assertIn(".menu-toggle:checked ~ .layout .sidebar", search)
            self.assertIn("max-height: calc(100vh - 112px)", search)

    def test_healthz_is_json(self) -> None:
        with tempfile.TemporaryDirectory() as raw_tmp:
            status, _reason, body, content_type = route_request(Path(raw_tmp), "/healthz")

            self.assertEqual(status, 200)
            self.assertEqual(content_type, "application/json; charset=utf-8")
            self.assertEqual(json.loads(body), {"ok": True, "status": "ready"})


if __name__ == "__main__":
    unittest.main()
