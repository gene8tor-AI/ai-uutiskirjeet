"""Verify public Pages RSS and refresh status, not only repository commits."""
from pathlib import Path
import hashlib
import time
import urllib.request
import xml.etree.ElementTree as ET

BASE = "https://gene8tor-ai.github.io/ai-uutiskirjeet/"

def main():
    expected = {name: hashlib.sha256(Path(name).read_bytes()).hexdigest() for name in ("feeds/ai-news.xml", "feeds/status.json")}
    deadline = time.monotonic() + 300
    while time.monotonic() < deadline:
        matched = True
        for name, digest in expected.items():
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                matched = False
                break
            try:
                req = urllib.request.Request(BASE + name + "?verify=" + digest[:16], headers={"User-Agent": "Loitsu-RSS-Verification/1.0", "Cache-Control": "no-cache"})
                with urllib.request.urlopen(req, timeout=min(10, remaining)) as response:
                    data = response.read(8 * 1024 * 1024)
                    if response.status != 200 or hashlib.sha256(data).hexdigest() != digest:
                        matched = False
                    elif name.endswith(".xml"):
                        root = ET.fromstring(data)
                        if root.tag != "rss" or not root.findall("channel/item"):
                            raise ValueError("Published RSS has no valid items")
            except Exception as exc:
                matched = False
                print("Pages verification waiting:", name, type(exc).__name__)
        if matched:
            print("PASS: public HTTP200, RSS2.0 and exact XML/status snapshots", expected)
            return
        remaining = deadline - time.monotonic()
        if remaining > 0:
            time.sleep(min(10, remaining))
    raise SystemExit("Published RSS/status do not match committed snapshots after bounded 300s wait")

if __name__ == "__main__":
    main()
