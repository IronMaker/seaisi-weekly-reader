from __future__ import annotations

from urllib.request import Request, urlopen


class OfficialHttpClient:
    def __init__(self, timeout: int = 30):
        self.timeout = timeout

    def get(self, url: str) -> tuple[int, str, str]:
        request = Request(url, headers={"User-Agent": "SEAISIWeeklyReader/1.0 (+official-source-only)"})
        try:
            with urlopen(request, timeout=self.timeout) as response:
                return response.status, response.read().decode("utf-8", "replace"), response.geturl()
        except Exception as exc:
            status = getattr(exc, "code", 0) or 0
            return status, "", url
