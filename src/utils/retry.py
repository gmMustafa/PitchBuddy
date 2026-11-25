import httpx
from tenacity import retry, retry_if_exception, stop_after_attempt, wait_exponential


def is_rate_limit(exc: BaseException) -> bool:
    status = getattr(exc, "status_code", None) or getattr(getattr(exc, "response", None), "status_code", None)
    if status == 429:
        return True
    msg = str(exc).lower()
    return any(s in msg for s in ("429", "rate limit", "rate_limit", "quota exceeded"))


def _is_retryable(exc: BaseException) -> bool:
    status = getattr(exc, "status_code", None)
    if isinstance(exc, httpx.HTTPStatusError):
        status = exc.response.status_code
    if status in (502, 503):
        return True
    msg = str(exc).lower()
    # Short per-minute limits are worth one or two retries; daily limits are not.
    if is_rate_limit(exc) and "per day" not in msg and "tokens per day" not in msg:
        return True
    return "unavailable" in msg or "503" in msg


api_retry = retry(
    retry=retry_if_exception(_is_retryable),
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    reraise=True,
)
