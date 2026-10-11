import sys

from .cli import run


def main() -> None:
    run(sys.stdin, sys.stdout)


if __name__ == "__main__":
    main()
