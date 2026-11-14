#!/usr/bin/env python3
"""Local relay so headless `claude -p` sessions reach Claude through OpenRouter on the
bring-your-own-key route, pinned to the Anthropic provider.

    python3 -I or_shim.py --port 8765 --log <dir>/shim.jsonl [--max-tokens N]

Sessions get ANTHROPIC_BASE_URL=http://127.0.0.1:<port> and a dummy ANTHROPIC_AUTH_TOKEN.
For every POST to /v1/messages it adds `provider: {only: [anthropic], allow_fallbacks:
false}` to the JSON body and forwards it to https://openrouter.ai/api/v1/messages through
the environment's HTTPS proxy (which supplies the real key). With --max-tokens it lowers a
larger `max_tokens` to N, because OpenRouter refuses a request whose worst-case cost passes
the key's remaining limit, even on the BYOK route. It streams the reply back unchanged and
appends one line per request to the log: time, model, max_tokens sent, HTTP status, and
the usage/cost fields when the reply carries them. Other paths are forwarded unchanged.
"""
import argparse, json, threading, time, urllib.error, urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

UPSTREAM = "https://openrouter.ai/api"
PROVIDER = {"only": ["anthropic"], "allow_fallbacks": False}
lock = threading.Lock()


class H(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, *a):
        pass

    def _relay(self, method):
        n = int(self.headers.get("Content-Length") or 0)
        body = self.rfile.read(n) if n else None
        rec = {"ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "path": self.path}
        if body and self.path.split("?")[0].endswith("/v1/messages") and method == "POST":
            j = json.loads(body)
            j["provider"] = PROVIDER
            if A.max_tokens and j.get("max_tokens", 0) > A.max_tokens:
                rec["max_tokens_requested"] = j["max_tokens"]
                j["max_tokens"] = A.max_tokens
            rec.update(model=j.get("model"), max_tokens=j.get("max_tokens"), stream=bool(j.get("stream")))
            body = json.dumps(j).encode()
        headers = {k: v for k, v in self.headers.items()
                   if k.lower() not in ("host", "content-length", "authorization", "x-api-key", "accept-encoding", "connection")}
        headers["Authorization"] = "Bearer dummy"  # the environment's proxy replaces it
        path = self.path if self.path.startswith("/v1") else self.path
        req = urllib.request.Request(UPSTREAM + path, data=body, method=method, headers=headers)
        try:
            resp = urllib.request.urlopen(req, timeout=900)
            status = resp.status
        except urllib.error.HTTPError as e:
            resp, status = e, e.code
        rec["status"] = status
        self.send_response(status)
        for k, v in resp.headers.items():
            if k.lower() not in ("transfer-encoding", "connection", "content-length", "content-encoding"):
                self.send_header(k, v)
        self.send_header("Transfer-Encoding", "chunked")
        self.end_headers()
        tail = b""
        while True:
            chunk = resp.read1(65536) if hasattr(resp, "read1") else resp.read(65536)
            if not chunk:
                break
            tail = (tail + chunk)[-20000:]
            self.wfile.write(b"%x\r\n%s\r\n" % (len(chunk), chunk))
            self.wfile.flush()
        self.wfile.write(b"0\r\n\r\n")
        # usage and cost: the last "usage" object in the stream (message_delta) or the body
        t = tail.decode("utf-8", "replace")
        i = t.rfind('"usage"')
        if i >= 0:
            rec["usage_tail"] = t[i:i + 900]
        if status >= 400:
            rec["error_tail"] = t[-900:]
        with lock, open(A.log, "a") as f:
            f.write(json.dumps(rec) + "\n")

    def do_POST(self):
        self._relay("POST")

    def do_GET(self):
        self._relay("GET")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--log", required=True)
    ap.add_argument("--max-tokens", type=int, default=0)
    A = ap.parse_args()
    ThreadingHTTPServer(("127.0.0.1", A.port), H).serve_forever()
