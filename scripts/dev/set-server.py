#!/usr/bin/env python3

import argparse
import re
import socket
from pathlib import Path


def get_local_ip():
    """Определяет IP текущей машины в локальной сети."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        # Соединяться реально не нужно.
        # Это позволяет ОС выбрать подходящий интерфейс.
        sock.connect(("8.8.8.8", 80))
        return sock.getsockname()[0]
    finally:
        sock.close()


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "config",
        type=Path,
        help="Path to pacman.conf"
    )

    parser.add_argument(
        "port",
        type=int,
        help="Repository server port"
    )

    parser.add_argument(
        "--repo",
        default="gryphon",
        help="Repository name (default: gryphon)"
    )

    args = parser.parse_args()

    if not args.config.exists():
        raise SystemExit(f"Config not found: {args.config}")

    ip = get_local_ip()
    server = f"http://{ip}:{args.port}"

    text = args.config.read_text()

    pattern = (
        rf"(\[{re.escape(args.repo)}\]"
        rf".*?"
        rf"^\s*Server\s*=\s*)[^\n]*"
    )

    new_text, count = re.subn(
        pattern,
        rf"\g<1>{server}",
        text,
        count=1,
        flags=re.MULTILINE | re.DOTALL,
    )

    if count == 0:
        raise SystemExit(
            f"Server not found inside [{args.repo}]"
        )

    args.config.write_text(new_text)

    print(f"Repository server: {server}")
    print(f"Updated [{args.repo}] in {args.config}")


if __name__ == "__main__":
    main()