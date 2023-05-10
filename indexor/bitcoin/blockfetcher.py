import asyncio
from concurrent.futures import ThreadPoolExecutor

from indexor.bitcoin.rpc import Rpc


class BlockFetcher:
    executor: ThreadPoolExecutor
    rpcs: list[Rpc] = []

    futures: list[asyncio.Future[dict]] = []

    height: int
    end: int

    queue: int

    def __init__(
            self,
            rpc: Rpc,
            executor: ThreadPoolExecutor,
            queue: int,
    ) -> None:
        self.executor = executor
        self.queue = queue

        for _ in range(0, queue):
            self.rpcs.append(Rpc(rpc.auth_str))

    def start(self, start: int, end: int) -> None:
        self.height = start - 1
        self.end = end

        for _ in range(0, self.queue):
            if not self.add():
                break

    def add(self) -> bool:
        if self.height >= self.end:
            return False

        self.height += 1
        self.futures.append(asyncio.get_event_loop().run_in_executor(
            self.executor,
            self.rpcs[self.height % self.queue].get_block_by_number,
            self.height,
        ))
        return True

    async def get(self) -> dict | None:
        if len(self.futures) == 0:
            return None

        return await self.futures.pop(0)
