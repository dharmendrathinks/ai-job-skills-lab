"""Protocol failure paths without a CLI, account, model or network."""
from collections import deque
import queue
import time
import unittest
from unittest.mock import Mock

from tools.research_evidence import EvidenceError
from tools.research_runtime import CodexWorker


class ProtocolTests(unittest.TestCase):
    def worker(self):
        worker = object.__new__(CodexWorker)
        worker.events = queue.Queue()
        worker.pending = deque()
        worker.timeout = .01
        worker.thread_id = "synthetic"
        worker.send = Mock()
        worker.rpc = Mock(return_value={"turn": {"id": "turn"}})
        return worker

    def test_timeout_defers_without_retry(self):
        worker = self.worker()
        with self.assertRaisesRegex(EvidenceError, "deadline"):
            worker.run("owned input", {})
        worker.rpc.assert_called_once()

    def test_dynamic_request_is_denied(self):
        worker = self.worker()
        worker.events.put({"id": 1, "method": "item/tool/call", "params": {}})
        with self.assertRaisesRegex(EvidenceError, "unexpected runtime request"):
            worker.receive(time.monotonic() + 1)
        self.assertIn("error", worker.send.call_args.args[0])

    def test_invalid_model_json_is_not_persistable(self):
        worker = self.worker()
        worker.events.put({"method": "item/completed", "params": {"turnId": "turn",
                           "item": {"type": "agentMessage", "text": "not JSON"}}})
        worker.events.put({"method": "turn/completed", "params": {"turn": {"id": "turn", "status": "completed"}}})
        with self.assertRaisesRegex(EvidenceError, "invalid JSON"):
            worker.run("owned input", {})

    def test_quota_error_omits_source_text_and_has_no_fallback(self):
        worker = self.worker()
        worker.events.put({"method": "turn/completed", "params": {"turn": {"id": "turn", "status": "failed",
                           "error": {"message": "quota exhausted secret-source-text"}}}})
        with self.assertRaisesRegex(EvidenceError, "quota-exhausted; deferred without fallback") as failure:
            worker.run("owned input", {})
        self.assertNotIn("secret-source-text", str(failure.exception))
        worker.rpc.assert_called_once()
