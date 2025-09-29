import sys

from .cli import process_operations


def main() -> None:
    process_operations(sys.stdin, sys.stdout)


if __name__ == "__main__":
    main()
