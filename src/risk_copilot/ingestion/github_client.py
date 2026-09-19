from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone


API_VERSION = "2022-11-28"


class GitHubAPIError(RuntimeError):
    pass


class GitHubRateLimitError(GitHubAPIError):
    def __init__(self, message: str, reset_epoch: int | None = None) -> None:
        super().__init__(message)
        self.reset_epoch = reset_epoch

    @property
    def reset_at(self) -> str | None:
        if self.reset_epoch is None:
            return None
        return datetime.fromtimestamp(self.reset_epoch, tz=timezone.utc).isoformat()


@dataclass
class RateLimitState:
    limit: int | None = None
    remaining: int | None = None
    reset_epoch: int | None = None


class GitHubClient:
    """Small GitHub REST client with process-local TTL caching and rate-limit safety."""

    _cache: dict[str, tuple[float, object, dict[str, str]]] = {}

    def __init__(
        self,
        token: str | None = None,
        timeout: int = 30,
        cache_ttl_seconds: int = 300,
    ) -> None:
        self.token = token or os.getenv("GITHUB_TOKEN")
        self.timeout = timeout
        self.cache_ttl_seconds = max(int(cache_ttl_seconds), 0)
        self.rate_limit = RateLimitState()
        self.base_url = "https://api.github.com"

    @property
    def authenticated(self) -> bool:
        return bool(self.token)

    def _headers(self) -> dict[str, str]:
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": API_VERSION,
            "User-Agent": "risk-copilot-v2",
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def _cache_key(self, url: str) -> str:
        # Keep authenticated/anonymous caches separate without storing the token itself.
        return f"{'auth' if self.authenticated else 'anon'}:{url}"

    def _cached(self, url: str):
        if self.cache_ttl_seconds <= 0:
            return None
        key = self._cache_key(url)
        cached = self._cache.get(key)
        if not cached:
            return None
        stored_at, payload, headers = cached
        if time.time() - stored_at > self.cache_ttl_seconds:
            self._cache.pop(key, None)
            return None
        self._update_rate_limit(headers)
        return payload, headers

    def _store_cache(self, url: str, payload, headers: dict[str, str]) -> None:
        if self.cache_ttl_seconds > 0:
            self._cache[self._cache_key(url)] = (time.time(), payload, headers)

    def _request_json(self, url: str):
        cached = self._cached(url)
        if cached is not None:
            return cached

        request = urllib.request.Request(url, headers=self._headers(), method="GET")
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                body = response.read().decode("utf-8")
                headers = {k.lower(): v for k, v in response.headers.items()}
                self._update_rate_limit(headers)
                payload = json.loads(body)
                self._store_cache(url, payload, headers)
                return payload, headers
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            headers = {k.lower(): v for k, v in exc.headers.items()} if exc.headers else {}
            self._update_rate_limit(headers)
            if exc.code in {403, 429} and self.rate_limit.remaining == 0:
                reset = self.rate_limit.reset_epoch
                reset_text = (
                    datetime.fromtimestamp(reset, tz=timezone.utc).isoformat()
                    if reset is not None
                    else "the GitHub reset window"
                )
                raise GitHubRateLimitError(
                    f"GitHub API rate limit reached. Try again after {reset_text}, "
                    "or configure GITHUB_TOKEN for a higher authenticated limit.",
                    reset_epoch=reset,
                ) from exc
            raise GitHubAPIError(f"GitHub API error {exc.code}: {detail[:500]}") from exc
        except urllib.error.URLError as exc:
            raise GitHubAPIError(f"GitHub network error: {exc.reason}") from exc

    def _update_rate_limit(self, headers):
        def as_int(v):
            try:
                return int(v) if v is not None else None
            except ValueError:
                return None

        self.rate_limit = RateLimitState(
            limit=as_int(headers.get("x-ratelimit-limit")),
            remaining=as_int(headers.get("x-ratelimit-remaining")),
            reset_epoch=as_int(headers.get("x-ratelimit-reset")),
        )

    @staticmethod
    def _next_link(link_header):
        if not link_header:
            return None
        for part in link_header.split(","):
            bits = [x.strip() for x in part.split(";")]
            if len(bits) >= 2 and bits[1] == 'rel="next"':
                return bits[0].strip("<>")
        return None

    def _paginate(self, path, params=None):
        params = dict(params or {})
        params.setdefault("per_page", 100)
        url = f"{self.base_url}{path}?{urllib.parse.urlencode(params)}"
        rows = []
        while url:
            # Only stop before another page is needed. A successful final page should still be usable.
            if self.rate_limit.remaining == 0:
                raise GitHubRateLimitError(
                    "GitHub API rate limit reached before the next page could be loaded.",
                    reset_epoch=self.rate_limit.reset_epoch,
                )
            payload, headers = self._request_json(url)
            if not isinstance(payload, list):
                raise GitHubAPIError(f"Expected list payload from {url}")
            rows.extend(payload)
            next_url = self._next_link(headers.get("link"))
            if next_url and self.rate_limit.remaining is not None and self.rate_limit.remaining <= 1:
                raise GitHubRateLimitError(
                    "GitHub API rate limit is too low to load the next page safely.",
                    reset_epoch=self.rate_limit.reset_epoch,
                )
            url = next_url
        return rows

    @staticmethod
    def _repo_parts(repo):
        if repo.count("/") != 1:
            raise ValueError("repo must be in owner/name form")
        return tuple(repo.split("/", 1))

    def list_milestones(self, repo, state="all"):
        owner, name = self._repo_parts(repo)
        return self._paginate(f"/repos/{owner}/{name}/milestones", {"state": state, "sort": "due_on"})

    def list_milestone_items(self, repo, milestone_number):
        owner, name = self._repo_parts(repo)
        return self._paginate(
            f"/repos/{owner}/{name}/issues",
            {"state": "all", "milestone": milestone_number},
        )

    def list_issue_events(self, repo, issue_number):
        owner, name = self._repo_parts(repo)
        return self._paginate(f"/repos/{owner}/{name}/issues/{issue_number}/events")

    def list_pull_reviews(self, repo, pull_number):
        owner, name = self._repo_parts(repo)
        return self._paginate(f"/repos/{owner}/{name}/pulls/{pull_number}/reviews")

    def list_commits(self, repo, since, until):
        owner, name = self._repo_parts(repo)
        return self._paginate(
            f"/repos/{owner}/{name}/commits",
            {"since": since, "until": until},
        )
