"""Write latest.json with the newest long-form (non-Shorts) upload on the Chuck's Casa channel.

Runs in GitHub Actions. Reads YouTube's built-in "long-form uploads" playlist feed
(playlist id UULF + channel id without the UC prefix), which already excludes Shorts.
The plain channel feed only lists the last 15 uploads, which can all be Shorts.
Leaves latest.json untouched if there is nothing to show.
"""
import json
import pathlib
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET

CHANNEL_ID = "UCxi5F3Kxk_29OiK_wKtVEeA"  # youtube.com/@chuckscasa
LONG_FORM_PLAYLIST = "UULF" + CHANNEL_ID[2:]
FEED = f"https://www.youtube.com/feeds/videos.xml?playlist_id={LONG_FORM_PLAYLIST}"
OUT = pathlib.Path(__file__).resolve().parent.parent / "latest.json"
UA = {"User-Agent": "Mozilla/5.0 (chuckscasa.com latest-video bot)"}
NS = {"a": "http://www.w3.org/2005/Atom", "yt": "http://www.youtube.com/xml/schemas/2015"}


def main() -> None:
    try:
        with urllib.request.urlopen(urllib.request.Request(FEED, headers=UA), timeout=30) as r:
            root = ET.fromstring(r.read())
    except urllib.error.HTTPError as e:
        # 404 = the channel has no long-form videos yet
        print(f"Feed returned {e.code}; latest.json left as is")
        return

    entries = root.findall("a:entry", NS)
    print(f"{len(entries)} long-form videos in feed")
    if not entries:
        print("Nothing to show; latest.json left as is")
        return

    newest = max(entries, key=lambda e: e.findtext("a:published", default="", namespaces=NS))
    data = {
        "id": newest.findtext("yt:videoId", namespaces=NS),
        "title": newest.findtext("a:title", namespaces=NS) or "",
        "published": newest.findtext("a:published", namespaces=NS) or "",
    }
    new = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    if OUT.exists() and OUT.read_text(encoding="utf-8") == new:
        print("No change")
        return
    OUT.write_text(new, encoding="utf-8")
    print("Updated:", data["title"])


if __name__ == "__main__":
    main()
