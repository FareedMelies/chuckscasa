"""Write latest.json with the newest long-form (non-Shorts) upload on the Chuck's Casa channel.

Runs in GitHub Actions. Reads the channel's public RSS feed, checks each entry
against youtube.com/shorts/<id> (a Short answers 200, a regular video redirects),
and keeps the first one that isn't a Short. Leaves latest.json untouched on any failure.
"""
import json
import pathlib
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET

CHANNEL_ID = "UCxi5F3Kxk_29OiK_wKtVEeA"  # youtube.com/@chuckscasa
FEED = f"https://www.youtube.com/feeds/videos.xml?channel_id={CHANNEL_ID}"
OUT = pathlib.Path(__file__).resolve().parent.parent / "latest.json"
UA = {"User-Agent": "Mozilla/5.0 (chuckscasa.com latest-video bot)"}
NS = {"a": "http://www.w3.org/2005/Atom", "yt": "http://www.youtube.com/xml/schemas/2015"}


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


def is_short(video_id: str) -> bool:
    opener = urllib.request.build_opener(NoRedirect)
    req = urllib.request.Request(f"https://www.youtube.com/shorts/{video_id}", headers=UA, method="HEAD")
    try:
        with opener.open(req, timeout=20) as r:
            return r.status == 200
    except urllib.error.HTTPError as e:
        # 3xx (redirect to /watch) means it's a regular video
        return not (300 <= e.code < 400)


def main() -> None:
    req = urllib.request.Request(FEED, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        root = ET.fromstring(r.read())

    for entry in root.findall("a:entry", NS):
        vid = entry.findtext("yt:videoId", namespaces=NS)
        if not vid or is_short(vid):
            continue
        data = {
            "id": vid,
            "title": entry.findtext("a:title", namespaces=NS) or "",
            "published": entry.findtext("a:published", namespaces=NS) or "",
        }
        new = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
        if not OUT.exists() or OUT.read_text(encoding="utf-8") != new:
            OUT.write_text(new, encoding="utf-8")
            print("Updated:", data["title"])
        else:
            print("No change")
        return

    print("No long-form video in the feed; latest.json left as is")


if __name__ == "__main__":
    main()
