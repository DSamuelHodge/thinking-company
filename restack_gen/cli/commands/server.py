"""Development server command.

Implements a lightweight HTTP server with a health check endpoint for
validating a generated Restack project. No external web framework is required.
"""

from __future__ import annotations

import json
import threading
import time
import urllib.request
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

import click

from ...utils.logging import get_logger

LOGGER = get_logger("server")


class _HealthHandler(BaseHTTPRequestHandler):
    """HTTP request handler exposing a /health endpoint."""

    server_env: str = "dev"  # set by factory
    started_at: float = time.time()

    def log_message(self, format: str, *args):  # pragma: no cover - reduce test noise
        LOGGER.info("server: " + format, *args)

    def do_GET(self):  # noqa: N802 - required by BaseHTTPRequestHandler
        if self.path.rstrip("/") == "/health":
            payload = {
                "status": "ok",
                "env": self.server_env,
                "uptime": round(time.time() - self.started_at, 3),
            }
            raw = json.dumps(payload).encode("utf-8")
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(raw)))
            self.end_headers()
            self.wfile.write(raw)
        else:
            self.send_response(HTTPStatus.NOT_FOUND)
            self.end_headers()


def _handler_factory(env: str):
    class Handler(_HealthHandler):
        server_env = env

    return Handler


def _serve(host: str, port: int, handler, stop_event: threading.Event) -> None:
    httpd = HTTPServer((host, port), handler)
    httpd.timeout = 0.5
    LOGGER.info(f"Server listening on http://{host}:{port}")
    while not stop_event.is_set():
        httpd.handle_request()
    LOGGER.info("Server shutting down")


def _simple_reloader(paths: list[Path], on_change, interval: float = 1.0) -> None:
    """Naive polling-based reloader that invokes on_change when files change."""

    def snapshot() -> dict[str, float]:
        stamps: dict[str, float] = {}
        for root in paths:
            if not root.exists():
                continue
            for p in root.rglob("*.py"):
                try:
                    stamps[str(p)] = p.stat().st_mtime
                except FileNotFoundError:
                    continue
        return stamps

    last = snapshot()
    while True:
        time.sleep(interval)
        curr = snapshot()
        if curr != last:
            on_change()
            last = curr


@click.command()
@click.option("--host", default="127.0.0.1", help="Host interface to bind", show_default=True)
@click.option("--port", default=8000, type=int, help="Port to bind", show_default=True)
@click.option(
    "--workers", default=1, type=int, help="Number of worker processes", show_default=True
)
@click.option("--reload", "reload_", is_flag=True, help="Enable auto-reload on file changes")
@click.option(
    "--env",
    type=click.Choice(["dev", "prod", "test"], case_sensitive=False),
    default="dev",
    show_default=True,
    help="Environment mode",
)
@click.option(
    "--health-check",
    is_flag=True,
    help="Start server, perform a health check, then exit (for CI/tests)",
)
@click.pass_obj
def server(
    ctx, host: str, port: int, workers: int, reload_: bool, env: str, health_check: bool
) -> None:
    """Run a lightweight development server with a /health endpoint."""
    if workers != 1:
        click.echo("Warning: --workers>1 not supported in dev server; using a single worker.")

    handler = _handler_factory(env)
    stop_event = threading.Event()

    def run_once():
        t = threading.Thread(target=_serve, args=(host, port, handler, stop_event), daemon=True)
        t.start()
        return t

    thread = run_once()

    if health_check:
        # Allow server to start
        time.sleep(0.2)
        try:
            with urllib.request.urlopen(f"http://{host}:{port}/health", timeout=2) as resp:
                if resp.status == 200:
                    click.echo("✅ Server healthy")
                    return
        except Exception as exc:  # pragma: no cover - network timing variance
            raise SystemExit(f"Health check failed: {exc}") from exc
        finally:
            stop_event.set()
            thread.join(timeout=2)
        return

    if reload_:
        click.echo("Auto-reload enabled (naive polling)")

        def on_change():
            nonlocal thread
            click.echo("Changes detected. Restarting server...")
            stop_event.set()
            thread.join(timeout=2)
            # Reset event and start again
            stop_event.clear()
            thread = run_once()

        watcher_paths = [ctx.project_path]
        try:
            _simple_reloader(watcher_paths, on_change)
        except KeyboardInterrupt:  # pragma: no cover - interactive
            pass
        finally:
            stop_event.set()
            thread.join(timeout=2)
    else:
        click.echo("Press Ctrl+C to stop")
        try:
            while True:
                time.sleep(0.5)
        except KeyboardInterrupt:  # pragma: no cover - interactive
            pass
        finally:
            stop_event.set()
            thread.join(timeout=2)
