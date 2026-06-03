"""
Serve the stock-ranking live demo UI and run the orchestrator on demand.

Usage:
    uv run python demo_server.py

Then open:
    http://127.0.0.1:8000/
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import threading
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parent
INDEX_PATH = ROOT / "index.html"
RUN_LOCK = threading.Lock()


class DemoHandler(BaseHTTPRequestHandler):
    server_version = "StockRankingDemo/0.1"

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path in ("/", "/index.html"):
            self._send_file(INDEX_PATH, "text/html; charset=utf-8")
        elif parsed.path == "/api/run":
            self._run_orchestrator()
        elif parsed.path == "/api/health":
            self._send_json({"ok": True})
        else:
            self.send_error(HTTPStatus.NOT_FOUND, "Not found")

    def do_HEAD(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path in ("/", "/index.html"):
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
        elif parsed.path == "/api/health":
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "application/json")
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
        else:
            self.send_error(HTTPStatus.NOT_FOUND, "Not found")

    def log_message(self, fmt: str, *args: object) -> None:
        sys.stderr.write("%s - - [%s] %s\n" % (self.client_address[0], self.log_date_time_string(), fmt % args))

    def _send_file(self, path: Path, content_type: str) -> None:
        if not path.exists():
            self.send_error(HTTPStatus.NOT_FOUND, f"Missing {path.name}")
            return
        body = path.read_bytes()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _send_json(self, payload: dict[str, object]) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _send_sse(self, event: str, data: str) -> None:
        message = f"event: {event}\n"
        for line in data.splitlines() or [""]:
            message += f"data: {line}\n"
        message += "\n"
        self.wfile.write(message.encode("utf-8"))
        self.wfile.flush()

    def _run_orchestrator(self) -> None:
        if not RUN_LOCK.acquire(blocking=False):
            self._start_sse()
            self._send_sse("error_event", "Another orchestrator run is already active.")
            self.close_connection = True
            return

        self._start_sse()
        process: subprocess.Popen[str] | None = None
        try:
            self._send_sse("output", "Starting live orchestrator process: python -u run_stock_ranking.py")
            process = subprocess.Popen(
                [sys.executable, "-u", "run_stock_ranking.py"],
                cwd=ROOT,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
            )

            assert process.stdout is not None
            for line in process.stdout:
                self._send_sse("output", line.rstrip("\n"))

            return_code = process.wait()
            if return_code == 0:
                self._send_sse("done", "Run complete.")
            else:
                self._send_sse("error_event", f"Process exited with status {return_code}.")
            self.close_connection = True
        except BrokenPipeError:
            if process and process.poll() is None:
                process.terminate()
            return
        except Exception as exc:
            self._send_sse("error_event", f"{type(exc).__name__}: {exc}")
            self.close_connection = True
        finally:
            RUN_LOCK.release()

    def _start_sse(self) -> None:
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "text/event-stream; charset=utf-8")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Connection", "close")
        self.end_headers()


def main() -> None:
    parser = argparse.ArgumentParser(description="Serve the AAPL stock-ranking live demo.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()

    server = ThreadingHTTPServer((args.host, args.port), DemoHandler)
    print(f"Serving live demo at http://{args.host}:{args.port}/", flush=True)
    print("Press Ctrl+C to stop.", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
