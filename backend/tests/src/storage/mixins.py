from pathlib import Path
from typing import Awaitable, Callable


class FileOperationMixin:
    def _save(self, path: str, data: bytes):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, mode="wb") as f:
            f.write(data)

    def _get_coro_with_bytes(
        self, data: bytes
    ) -> Callable[[int], Awaitable[bytearray | None]]:
        pos = 0

        async def get_chunk(size: int) -> bytearray | None:
            nonlocal pos
            if pos >= len(data) - 1:
                return None

            end = pos + size
            if end > len(data):
                end = len(data)

            chunk = data[pos:end]
            pos = end - 1
            return bytearray(chunk)

        return get_chunk
