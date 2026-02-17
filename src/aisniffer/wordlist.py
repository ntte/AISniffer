from __future__ import annotations

from pathlib import Path
import random
import re

import os
import json
from openai import OpenAI

COMMON_BASE = [
    "admin", "login", "logout", "dashboard", "panel", "manage",
    "api", "docs", "swagger", "openapi", "health", "status",
    "backup", "old", "test", "dev", "staging", "debug",
    "uploads", "download", "export", "import",
    "report", "reports", "invoice", "billing", "pay", "payment",
    "user", "users", "account", "accounts", "profile",
    "config", "settings", "setup",
    "index", "home", "main",
]

def _dedupe_keep_order(items: list[str]) -> list[str]:
    seen = set()
    out = []
    for x in items:
        if x not in seen:
            out.append(x)
            seen.add(x)
    return out

def generate_non_targeted_wordlist(size: int = 5000) -> list[str]:
    """
    Offline non-targeted wordlist. This is NOT as good as SecLists,
    but works as a default.
    """
    if size < 50:
        size = 50

    words = []
    words.extend(COMMON_BASE)

    # Simple expansions/permutations
    suffixes = ["", "1", "2", "old", "bak", "backup", "test", "dev", "tmp"]
    prefixes = ["", "new", "old", "test", "dev"]
    separators = ["", "-", "_"]

    for base in COMMON_BASE:
        for pre in prefixes:
            for suf in suffixes:
                for sep1 in separators:
                    for sep2 in separators:
                        parts = []
                        if pre:
                            parts.append(pre)
                        parts.append(base)
                        if suf:
                            parts.append(suf)
                        w = (sep1.join(parts) if sep1 else sep2.join(parts)).strip(sep1 + sep2)
                        w = re.sub(r"[-_]{2,}", "-", w)
                        if w:
                            words.append(w)

    words = _dedupe_keep_order(words)

    # If still not enough, add randomized combinations
    while len(words) < size:
        a = random.choice(COMMON_BASE)
        b = random.choice(COMMON_BASE)
        sep = random.choice(["-", "_", ""])
        words.append(f"{a}{sep}{b}")

    return words[:size]

def generate_ai_wordlist_placeholder(keyword: str, max_words: int = 2000) -> list[str]:
    """
    Placeholder for LLM-based generation. For now: generate
    keyword-centered permutations +  nearby “webby” terms.
    """
    keyword = keyword.strip().lower()
    web_terms = [
        "admin", "login", "panel", "dashboard", "manage", "config", "settings",
        "report", "reports", "export", "download", "upload", "api", "docs"
    ]

    bases = [keyword]
    # small variants
    bases.extend([
        keyword.replace(" ", ""),
        keyword.replace(" ", "_"),
        keyword.replace(" ", "-"),
        keyword + "s",
    ])
    bases = _dedupe_keep_order([b for b in bases if b])

    words = []
    for b in bases:
        words.append(b)
        for t in web_terms:
            words.append(f"{b}/{t}")
            words.append(f"{t}/{b}")
            words.append(f"{b}_{t}")
            words.append(f"{b}-{t}")

    words = _dedupe_keep_order(words)
    return words[:max_words]

def write_wordlist(words: list[str], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(words) + "\n", encoding="utf-8")




def _sanitize_candidate(s: str) -> str | None:
    s = s.strip()
    if not s:
        return None

    # If the model outputs a full URL, strip scheme+host
    s = re.sub(r"^https?://[^/]+", "", s).strip()

    # allow word/path-like tokens only
    if not re.fullmatch(r"[A-Za-z0-9/_\-.%]+", s):
        return None

    if s == "/":
        return None

    return s
