"""Write latest.json for the featured YouTube video on chuckscasa.com.

The featured video is pinned (set FEATURED_ID). This looks up its title with
YouTube's public oEmbed endpoint so the page shows the real title.
To feature a different video: change FEATURED_ID, commit, and the action reruns.
"""
import json
import pathlib
import urllib.parse
import urllib.request

FEATURED_ID = "ort2onukh9o"
OUT = pathlib.Path(__file__).resolve().parent.parent / "latest.json"
UA = {"User-Agent": "Mozilla/5.0 (chuckscasa.com featured-video bot)"}


def main() -> None:
    watch = f"https://www.youtube.com/watch?v={FEATURED_ID}"
    oembed = "https://www.youtube.com/oembed?format=json&url=" + urllib.parse.quote(watch, safe="")
    title = ""
    try:
        with urllib.request.urlopen(urllib.request.Request(oembed, headers=UA), timeout=30) as r:
            title = json.load(r).get("title", "")
    except Exception as e:  # keep the page working even if the lookup fails
        print("Title lookup failed:", e)

    data = {"id": FEATURED_ID, "title": title}
    new = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    if OUT.exists() and OUT.read_text(encoding="utf-8") == new:
        print("No change")
        return
    OUT.write_text(new, encoding="utf-8")
    print("Featured:", title or FEATURED_ID)


if __name__ == "__main__":
    main()
