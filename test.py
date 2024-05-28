import argparse
import asyncio
import random
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Callable

import httpx

COLORS = [
    "\33[91m",  # RED
    "\33[92m",  # GREEN
    "\33[93m",  # YELLOW
    "\33[94m",  # BLUE
    "\33[95m",  # VIOLET
    "\33[96m",  # BEIGE
]
COLOR_GRAY = "\33[90m"
COLOR_END = "\033[0m"


def get_index_color(index: int) -> str:
    return COLORS[index % len(COLORS)]


def get_random_color() -> str:
    return COLORS[random.randint(0, 5)]


def get_color_printer(color) -> Callable:
    return lambda *args: print(color, *args, COLOR_END)


def get_time() -> str:
    return datetime.now().strftime("%H:%M:%S")


async def upload_file(url: str, file_path: Path, index: int):
    cprint = get_color_printer(get_index_color(index=index))
    tprint = lambda *args: cprint(f"[API-{index:02}] ", *args)  # noqa: E731
    new_file_path = Path(f"{file_path.stem}_{str(uuid.uuid4())}{file_path.suffix}")
    async with httpx.AsyncClient(timeout=httpx.Timeout(None, read=180.0)) as client:
        with file_path.open(mode="rb") as f:
            tprint(f"Send {'Request':<8} at {get_time()}")
            ts = time.time()
            response = await client.post(
                url,
                data={"data": "Hello World!"},
                files={"file": (f.name, f, "application/octet-stream")},
                headers={"Filename": str(new_file_path)},
            )
        code, data = response.status_code, response.json()
        te = time.time()
        tprint(f"Recv {'Response':<8} at {get_time()} ({code}, {te - ts:.3f}s)")
        assert (
            file_path.stat().st_size == new_file_path.stat().st_size
        ), "Size is not the same"
        new_file_path.unlink()


def build_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", type=str, required=True, help="the input data")
    parser.add_argument(
        "-p", "--port", type=str, required=True, help="the service port"
    )
    parser.add_argument(
        "-n",
        "--request-nums",
        type=int,
        default=2,
        help="the request numbers",
    )
    return parser.parse_args()


async def main(args: argparse.Namespace):
    file_path = Path(args.input)
    url = f"http://127.0.0.1:{args.port}/upload"
    assert file_path.exists(), "file not found"
    cprint = get_color_printer(COLOR_GRAY)

    title = f"""
        \r URL : {url}
        \r SIZE: {file_path.stat().st_size / (1024**3)} GB
        """
    cprint(title)

    ts = time.time()
    tasks = [upload_file(url, file_path, index) for index in range(args.request_nums)]
    await asyncio.gather(*tasks)

    cprint()
    cprint(f"Total Cost: {time.time()-ts:.3f}s")


if __name__ == "__main__":
    asyncio.run(main(build_arguments()))
