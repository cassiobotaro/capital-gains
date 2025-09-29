import sys

from .cli import dump_json, parse_json_line, readlines
from .tax import process_operations_batch


def main() -> None:
    # functional style
    # deque hack can be used to consume lazy map without create a list
    # this will reduce memory footprint
    # deque(
    #     map(
    #         partial(dump_json, output=sys.stdout),
    #         map(calculate_taxes, map(parse_json_line, readlines(sys.stdin))),
    #     ),
    #     maxlen=0,
    # )
    for line in readlines(sys.stdin):
        dump_json(
            process_operations_batch(parse_json_line(line)),
            sys.stdout,
        )


if __name__ == "__main__":
    main()
