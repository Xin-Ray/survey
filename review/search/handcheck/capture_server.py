#!/usr/bin/env python3
"""Tiny loopback server that catches the labelling page's localStorage on page load.
The page POSTs its state to 127.0.0.1:8787/labels; we write labels + CSV to disk."""
import csv, json, os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HERE = os.path.dirname(os.path.abspath(__file__))
KEY = [r for r in csv.DictReader(open(os.path.join(HERE, "sample60_key.csv")))]

class H(BaseHTTPRequestHandler):
    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.send_header("Access-Control-Allow-Private-Network", "true")
    def do_OPTIONS(self):
        self.send_response(204); self._cors(); self.end_headers()
    def do_GET(self):
        self.send_response(200); self._cors()
        self.send_header("Content-Type", "text/plain"); self.end_headers()
        self.wfile.write(b"capture server up\n")
    def do_POST(self):
        n = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(n).decode("utf-8", "replace")
        if self.path.startswith("/ieee"):
            try:
                recs = json.loads(raw)
            except Exception:
                self.send_response(400); self._cors(); self.end_headers(); return
            arm = "b" if self.path.endswith("b") else "a"
            out = os.path.join(os.path.dirname(HERE), f"ieee_{arm}.csv")
            cols = ["Document Title", "Authors", "Publication Title", "Publication Year",
                    "Volume", "Issue", "Start Page", "End Page", "Abstract", "DOI",
                    "Document Identifier", "PDF Link"]
            with open(out, "w", newline="") as f:
                w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
                w.writeheader()
                for r in recs:
                    w.writerow({c: (r.get(c) or "") for c in cols})
            print(f"wrote {out}: {len(recs)} records", flush=True)
            self.send_response(200); self._cors()
            self.send_header("Content-Type", "text/plain"); self.end_headers()
            self.wfile.write(f"ok {len(recs)}\n".encode()); return
        try:
            state = json.loads(raw)
        except Exception:
            self.send_response(400); self._cors(); self.end_headers(); return
        open(os.path.join(HERE, "handcheck60_state.json"), "w").write(json.dumps(state, indent=1, ensure_ascii=False))
        done = 0
        with open(os.path.join(HERE, "handcheck60_labels.csv"), "w", newline="") as f:
            w = csv.writer(f); w.writerow(["index", "pmid", "decision", "fails", "note"])
            for r in KEY:
                s = state.get(r["pmid"]) or {}
                dec = (s.get("decision") or "")
                done += bool(dec)
                w.writerow([r["index"], r["pmid"], dec, "|".join(s.get("fails") or []), s.get("note") or ""])
        print(f"captured {done}/60 decisions", flush=True)
        self.send_response(200); self._cors()
        self.send_header("Content-Type", "text/plain"); self.end_headers()
        self.wfile.write(f"ok {done}/60\n".encode())
    def log_message(self, *a): pass

if __name__ == "__main__":
    print("listening on 127.0.0.1:8787", flush=True)
    ThreadingHTTPServer(("127.0.0.1", 8787), H).serve_forever()
