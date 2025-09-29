import json
import sys
from collections.abc import Iterator
from typing import IO, Protocol, TypeVar

from .tax import (
    Money,
    Operation,
    OperationResult,
    process_operations_batch,
)

_T_co = TypeVar("_T_co", covariant=True)


class SupportsReadline(Protocol[_T_co]):
    def readline(self, __length: int = ...) -> _T_co: ...


class OperationTaxEncoder(json.JSONEncoder):
    def default(self, obj):
        match obj:
            case OperationResult():
                return {"tax": float(obj.tax.amount)}
            case _:
                return json.JSONEncoder.default(self, obj)


def readlines(reader: SupportsReadline[str]) -> Iterator[str]:
    while (line := reader.readline()) != "\n":
        yield line


def parse_json_line(line: str) -> list[Operation]:
    return [
        Operation(
            operation=raw_ops["operation"],
            unit_cost=raw_ops["unit-cost"],
            quantity=raw_ops["quantity"],
        )
        for raw_ops in json.loads(line, parse_float=Money)
    ]


def dump_json(tax_list: list[OperationResult], output: IO[str]) -> None:
    json.dump(tax_list, output, cls=OperationTaxEncoder)
    output.write("\n")


def main():
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
