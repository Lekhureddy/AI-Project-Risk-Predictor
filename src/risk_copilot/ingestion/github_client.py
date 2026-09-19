from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any

API_VERSION = "2022-11-28"


class GitHubAPIError(RuntimeError):
    pass


@dataclass
class RateLimitState:
    limit: int | None = None
    remaining: int | None = None
    reset_epoch: int | None = None


class GitHubClient:
    """Minimal GitHub REST client for public engineering-delivery data."""

    def __init__(self, token: str | None = None, timeout: int = 30) -> None:
        self.token = token or os.getenv("GITHUB_TOKEN")
        self.timeout = timeout
        self.rate_limit = RateLimitState()
        self.base_url = "https://api.github.com"

    def _headers(self) -> dict[str, str]:
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": API_VERSION,
            "User-Agent": "risk-copilot-v2",
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def _request_json(self, url: str):
        request = urllib.request.Request(url, headers=self._headers(), method="GET")
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                body = response.read().decode("utf-8")
                headers = {k.lower(): v for k, v in response.headers.items()}
                self._update_rate_limit(headers)
                return json.loads(body), headers
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
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
            payload, headers = self._request_json(url)
            if not isinstance(payload, list):
                raise GitHubAPIError(f"Expected list payload from {url}")
            rows.extend(payload)
            url = self._next_link(headers.get("link"))
            if self.rate_limit.remaining is not None and self.rate_limit.remaining <= 2:
                raise GitHubAPIError("GitHub API rate limit nearly exhausted.")
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
        return self._paginate(f"/repos/{owner}/{name}/issues", {"state": "all", "milestone": milestone_number})

    def list_issue_events(self, repo, issue_number):
        owner, name = self._repo_parts(repo)
        return self._paginate(f"/repos/{owner}/{name}/issues/{issue_number}/events")

    def list_pull_reviews(self, repo, pull_number):
        owner, name = self._repo_parts(repo)
        return self._paginate(f"/repos/{owner}/{name}/pulls/{pull_number}/reviews")

    def list_commits(self, repo, since, until):
        owner, name = self._repo_parts(repo)
        return self._paginate(f"/repos/{owner}/{name}/commits", {"since": since, "until": until})
