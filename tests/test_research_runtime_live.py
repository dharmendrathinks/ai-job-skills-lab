"""Opt-in tests of the installed Codex binary, using a local fake model server.

RUN_CODEX_BOUNDARY_TESTS=1 python -m unittest tests.test_research_runtime_live
No inference, API key, provider account, or external network is used by the fake
model endpoint. Normal CI skips this machine-specific qualification suite.
"""
import json
import os
from pathlib import Path
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from tools.research_runtime import CodexWorker

SCHEMA = {"type": "object", "properties": {"ok": {"type": "boolean"}},
          "required": ["ok"], "additionalProperties": False}


@unittest.skipUnless(os.environ.get("RUN_CODEX_BOUNDARY_TESTS") == "1", "opt-in installed-runtime qualification")
class InstalledBoundaryTests(unittest.TestCase):
    def test_forced_calls_are_unregistered_before_execution(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            canary = root / "canary.txt"
            canary.write_text("synthetic-canary-do-not-disclose")
            marker = root / "must-not-exist.txt"
            calls = [
                ("exec_command", {"cmd": f"cat {canary}; touch {marker}"}),
                ("write_stdin", {"session_id": 1, "chars": "echo forbidden"}),
                ("view_image", {"path": str(canary)}),
                ("web.run", {"open": [{"ref_id": "https://example.com/"}]}),
                ("mcp__fixture__read", {"path": str(canary)}),
                ("spawn_agent", {"message": "Read the local canary"}),
                ("thread/start", {"environments": [{"id": "local"}]}),
                ("exec", {"code": "await tools.exec_command({cmd:'echo forbidden'})"}),
            ]
            requests, errors = [], []

            class Handler(BaseHTTPRequestHandler):
                def log_message(self, *args):
                    pass

                def do_POST(self):
                    try:
                        if self.headers.get("Authorization"):
                            errors.append("unexpected authentication header")
                        data = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
                        requests.append(data)
                        self.send_response(200)
                        self.send_header("Content-Type", "text/event-stream")
                        self.end_headers()
                        items = []
                        if len(requests) == 1:
                            for index, (name, arguments) in enumerate(calls):
                                items.append({"type": "function_call", "id": f"item_{index}",
                                              "call_id": f"call_{index}", "name": name,
                                              "arguments": json.dumps(arguments)})
                            items.append({"type": "custom_tool_call", "id": "patch_item", "call_id": "patch_call",
                                          "name": "apply_patch", "input": f"*** Begin Patch\n*** Add File: {marker}\n+forbidden\n*** End Patch"})
                        else:
                            items = [{"type": "message", "id": "answer", "role": "assistant", "status": "completed",
                                      "content": [{"type": "output_text", "text": '{"ok":true}'}]}]
                        events = [{"type": "response.created", "response": {"id": "response_1"}}]
                        events += [{"type": "response.output_item.done", "item": item} for item in items]
                        events += [{"type": "response.completed", "response": {"id": "response_1", "status": "completed",
                                    "output": items, "usage": {"input_tokens": 10, "output_tokens": 10,
                                                               "total_tokens": 20}}}]
                        for event in events:
                            self.wfile.write(("data: " + json.dumps(event) + "\n\n").encode())
                        self.wfile.flush()
                    except Exception as exc:
                        errors.append(type(exc).__name__)

            server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                with CodexWorker(root, timeout=30, _test_backend=f"http://127.0.0.1:{server.server_port}/v1") as worker:
                    response, execution = worker.run("Synthetic adversarial qualification. Return JSON.", SCHEMA)
                self.assertEqual(response, {"ok": True})
                self.assertEqual(errors, [])
                self.assertGreaterEqual(len(requests), 2)
                for request in requests:
                    self.assertEqual(request.get("tools", []), [])
                outputs = [item for request in requests[1:] for item in request["input"]
                           if item["type"] in ("function_call_output", "custom_tool_call_output")]
                self.assertEqual(len({item["call_id"] for item in outputs}), 9)
                for item in outputs:
                    self.assertIn("unsupported", str(item["output"]).lower())
                    self.assertNotIn("synthetic-canary-do-not-disclose", str(item))
                self.assertFalse(marker.exists())
                self.assertEqual(canary.read_text(), "synthetic-canary-do-not-disclose")
                self.assertEqual(execution["authentication"], "fixture")
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=3)
