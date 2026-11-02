from __future__ import annotations

import re
from typing import Any
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup, FeatureNotFound, Tag

from .database import DatabaseRepository


class ForumParser:
    HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/131.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml",
    }

    def __init__(self, timeout: float = 15.0) -> None:
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update(self.HEADERS)

    @staticmethod
    def _comment_id(node: Tag) -> int | None:
        candidates = [
            node.get("id"), node.get("data-id"), node.get("data-comment-id"),
            node.get("data-comment-body"),
        ]
        parent = node.parent
        while isinstance(parent, Tag):
            candidates.append(parent.get("data-comment-body"))
            parent = parent.parent
        for candidate in candidates:
            if isinstance(candidate, str):
                match = re.search(r"(?:comment|post)?[-_]?([0-9]+)$", candidate)
                if match:
                    return int(match.group(1))
        return None

    @staticmethod
    def _author(comment: Tag) -> str | None:
        for selector in (".comment__user", ".user-info__nickname", ".tm-user-info__username", "a[data-user-login]"):
            node = comment.select_one(selector)
            if node:
                value = node.get("data-user-login") or node.get_text(" ", strip=True)
                if value:
                    return str(value).lstrip("@")
        return None

    @staticmethod
    def _message(comment: Tag) -> str | None:
        for selector in (".comment__body", ".comment__message", ".tm-comment__body-content", ".tm-article-body"):
            node = comment.select_one(selector)
            if node:
                for unwanted in node.select("script, style, .comment__controls, .tm-comment__buttons"):
                    unwanted.decompose()
                value = node.decode_contents().strip()
                if value:
                    return value
        return None

    def parse_html(self, html: str, base_url: str = "https://habr.com") -> list[dict[str, Any]]:
        try:
            soup = BeautifulSoup(html, "lxml")
        except FeatureNotFound:
            soup = BeautifulSoup(html, "html.parser")
        parsed: list[dict[str, Any]] = []
        seen: set[int] = set()
        for comment in soup.select(".comment, .tm-comment"):
            comment_id = self._comment_id(comment)
            author = self._author(comment)
            message = self._message(comment)
            if comment_id is None:
                anchor = comment.select_one("a[href*='#comment'], a[href*='/comments/']")
                if anchor and isinstance(anchor.get("href"), str):
                    match = re.search(r"(?:comment[_/]|comments/)(\d+)", str(anchor["href"]))
                    if match:
                        comment_id = int(match.group(1))
            if comment_id is not None and author and message and comment_id not in seen:
                parsed.append({"id": comment_id, "name": author, "message": message, "url": urljoin(base_url, str(comment.get("data-url", "")))})
                seen.add(comment_id)
        return parsed

    def parse_page(self, url: str) -> list[dict[str, Any]]:
        response = self.session.get(url, timeout=self.timeout)
        response.raise_for_status()
        return self.parse_html(response.text, url)

    @staticmethod
    def save_to_db(parsed_data: list[dict[str, Any]], repository: DatabaseRepository) -> int:
        saved = 0
        for item in parsed_data:
            try:
                repository.add(int(item["id"]), str(item["name"]), str(item["message"]))
                saved += 1
            except __import__("sqlite3").IntegrityError:
                continue
        return saved
