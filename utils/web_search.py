from typing import Any
from ddgs import DDGS


def _ddgs_result(query_result):
    return [
        {
            "title": r.get("title", ""),
            "url": r.get("href", ""),
            "content": r.get("body", ""),
        }
        for r in query_result
    ]


def _ddgs_web_search(query: str, n: int) -> list[dict[str, Any]]:
    ddgs = DDGS(timeout=10)
    result = ddgs.text(query, n=n)
    return _ddgs_result(result)


def web_search(query, n) -> list[dict[str, Any]]:
    return _ddgs_web_search(query, n)
