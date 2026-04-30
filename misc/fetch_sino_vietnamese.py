'''
Copyright 2026 by Chad Redman <chad at zhtoolkit.com>
License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html

Fetch Sino-Vietnamese words and their Chinese character equivalents from
the English Wiktionary "Sino-Vietnamese words" category via the MediaWiki API.

Wikitext pages are cached in misc/data/VN/wikitext_cache/ so re-runs only fetch
missing pages. Use --refresh to force a full re-fetch.

Output: TSV with columns  vietnamese <TAB> chinese
Usage:  python fetch_sino_vietnamese.py [--refresh] [output.txt]
'''

import os
import re
import sys
import time
import requests

API_URL = "https://en.wiktionary.org/w/api.php"
CATEGORY = "Category:Sino-Vietnamese_words"
CACHE_DIR = "data/VN/wikitext_cache"
BATCH_SIZE = 50
POLITE_DELAY = 0.5  # seconds between network requests

SESSION = requests.Session()
SESSION.headers.update({"User-Agent": "VocabularyExtractor/1.0 (https://zhtoolkit.com; chad@zhtoolkit.com)"})

_ETYM_RE = re.compile(r'\{\{vi-etym-sino\|([^|}]+)')
_VI_SECTION_RE = re.compile(r'==Vietnamese==(.*?)(?=\n==[^=]|\Z)', re.DOTALL)
_CEDICT_RE = re.compile(r'^(\S+)\s+(\S+)\s+\[([^\]]+)\]\s+/.*/$')


def _cache_path(title):
    safe = title.replace("/", "_")
    return os.path.join(CACHE_DIR, safe + ".txt")


def load_cached(title):
    path = _cache_path(title)
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return f.read()
    return None


def save_cached(title, wikitext):
    os.makedirs(CACHE_DIR, exist_ok=True)
    with open(_cache_path(title), "w", encoding="utf-8") as f:
        f.write(wikitext)


def get_category_members():
    members = []
    params = {
        "action": "query",
        "list": "categorymembers",
        "cmtitle": CATEGORY,
        "cmlimit": 500,
        "cmprop": "title",
        "format": "json",
    }
    while True:
        data = SESSION.get(API_URL, params=params).json()
        members.extend(cm["title"] for cm in data["query"]["categorymembers"])
        if "continue" not in data:
            break
        params["cmcontinue"] = data["continue"]["cmcontinue"]
        time.sleep(POLITE_DELAY)
    return members


def fetch_wikitext_batch(titles):
    params = {
        "action": "query",
        "titles": "|".join(titles),
        "prop": "revisions",
        "rvprop": "content",
        "rvslots": "main",
        "format": "json",
    }
    data = SESSION.get(API_URL, params=params).json()
    result = {}
    for page in data["query"]["pages"].values():
        if "revisions" in page:
            result[page["title"]] = page["revisions"][0]["slots"]["main"]["*"]
    return result


def get_wikitext(titles, refresh):
    """Return {title: wikitext}, using cache where available."""
    cached = {}
    missing = []
    for title in titles:
        wikitext = None if refresh else load_cached(title)
        if wikitext is not None:
            cached[title] = wikitext
        else:
            missing.append(title)

    fetched = {}
    for i in range(0, len(missing), BATCH_SIZE):
        batch = missing[i:i + BATCH_SIZE]
        print(f"  Fetching pages {i + 1}–{min(i + BATCH_SIZE, len(missing))} of {len(missing)} uncached ...", end="\r")
        batch_result = fetch_wikitext_batch(batch)
        for title, wikitext in batch_result.items():
            save_cached(title, wikitext)
        fetched.update(batch_result)
        time.sleep(POLITE_DELAY)

    if missing:
        print()

    return {**cached, **fetched}


def load_cedict(path):
    """Return {char: (traditional, simplified, pinyin)} indexing both simplified and traditional forms."""
    lookup = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            m = _CEDICT_RE.match(line)
            if m:
                traditional, simplified, pinyin = m.group(1), m.group(2), m.group(3)
                entry = (traditional, simplified, pinyin)
                lookup.setdefault(traditional, entry)
                lookup.setdefault(simplified, entry)
    return lookup


def extract_pairs(title, wikitext):
    m = _VI_SECTION_RE.search(wikitext)
    if not m:
        return []
    vi_section = m.group(1)
    return [(title, match.group(1).strip()) for match in _ETYM_RE.finditer(vi_section)]


def main():
    args = sys.argv[1:]
    refresh = "--refresh" in args
    args = [a for a in args if a != "--refresh"]
    out_path = args[0] if args else "../data/VN/Sino_Vietnamese.txt"

    cedict_path = "../dict/CN/cedict_ts-merged-refs.txt"
    print(f"Loading {cedict_path} ...")
    cedict = load_cedict(cedict_path)
    print(f"  {len(cedict)} entries loaded")

    print(f"Fetching members of {CATEGORY} ...")
    titles = get_category_members()
    print(f"  {len(titles)} pages found")

    pages = get_wikitext(titles, refresh)

    pairs = []
    for title, wikitext in pages.items():
        pairs.extend(extract_pairs(title, wikitext))

    print(f"{len(pairs)} Vietnamese–Chinese pairs extracted")

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("vietnamese\tchinese\n")
        for viet, chinese in pairs:
            entry = cedict.get(chinese)
            if entry:
                trad, simp, pinyin = entry
                chinese_col = f"{trad}|{simp} [{pinyin}]" if trad != simp else f"{trad} [{pinyin}]"
            else:
                chinese_col = chinese
            f.write(f"{viet}\t{chinese_col}\n")

    print(f"Saved to {out_path}")


if __name__ == "__main__":
    main()
