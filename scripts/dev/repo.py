#!/usr/bin/env python3

from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
import threading
import argparse
import os


class PacmanServer(ThreadingHTTPServer):
    allow_reuse_address = True


def main():
    parser = argparse.ArgumentParser(
        description=""
    )

    parser.add_argument(
        "repository",
        type=Path,
        help="Path to the Pacman repository directory"
    )

    parser.add_argument(
        "-p",
        "--port",
        type=int,
        default=8000,
        help="HTTP server port (default: 8000)"
    )

    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Address to listen on (default: 0.0.0.0)"
    )

    args = parser.parse_args()

    repo_dir = args.repository.resolve()

    repo_dir.mkdir(parents=True, exist_ok=True)

    os.chdir(repo_dir)

    server = PacmanServer(
        (args.host, args.port),
        SimpleHTTPRequestHandler
    )

    thread = threading.Thread(
        target=server.serve_forever,
        daemon=True
    )
    thread.start()

    print(f"Repository: {repo_dir}")
    print(f"Address:    http://localhost:{args.port}/")
    print()
    print("Server is running.")
    print("Press ENTER to stop the server...")

    try:
        input()
    except KeyboardInterrupt:
        pass
    finally:
        print()
        print("Stopping server...")

        server.shutdown()
        server.server_close()
        thread.join()

        print("Server stopped.")


if __name__ == "__main__":
    main()