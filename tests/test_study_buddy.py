import json
import unittest
from unittest.mock import patch

from mindmate.study_buddy import OLLAMA_CHAT_URL, ask_ollama


class FakeResponse:
    def __init__(self, content):
        self.content = content

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self):
        return self.content


class AskOllamaTests(unittest.TestCase):
    @patch("mindmate.study_buddy.urllib.request.urlopen")
    def test_sends_chat_and_returns_local_model_reply(self, urlopen):
        urlopen.return_value = FakeResponse(
            b'{"message": {"content": "Try active recall."}}'
        )
        messages = [{"role": "user", "content": "How should I revise?"}]

        answer = ask_ollama(messages, "gemma3:1b")

        self.assertEqual(answer, "Try active recall.")
        request = urlopen.call_args.args[0]
        self.assertEqual(request.full_url, OLLAMA_CHAT_URL)
        self.assertEqual(request.get_method(), "POST")
        self.assertEqual(request.get_header("Content-type"), "application/json")
        self.assertEqual(
            json.loads(request.data),
            {"model": "gemma3:1b", "messages": messages, "stream": False},
        )
        self.assertEqual(urlopen.call_args.kwargs["timeout"], 180)

    @patch("mindmate.study_buddy.urllib.request.urlopen")
    def test_rejects_empty_model_reply(self, urlopen):
        urlopen.return_value = FakeResponse(b'{"message": {"content": "  "}}')

        with self.assertRaisesRegex(ValueError, "empty reply"):
            ask_ollama([], "gemma3:1b")


if __name__ == "__main__":
    unittest.main()
