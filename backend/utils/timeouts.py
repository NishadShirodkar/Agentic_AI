from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeout
from typing import Any, Callable

HTTP_TIMEOUT_SECONDS = 5


class StageTimeoutError(Exception):
    pass


def run_with_timeout(
    func: Callable[..., Any],
    *args: Any,
    timeout_seconds: int = HTTP_TIMEOUT_SECONDS,
    **kwargs: Any,
) -> Any:
    with ThreadPoolExecutor(max_workers=1) as pool:
        future = pool.submit(func, *args, **kwargs)
        try:
            return future.result(timeout=timeout_seconds)
        except FuturesTimeout as exc:
            raise StageTimeoutError(f"Timed out after {timeout_seconds}s") from exc
