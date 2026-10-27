import json
import sys
from collections.abc import Iterable, Iterator
from decimal import Decimal
from io import Writer
from itertools import takewhile
from typing import TypedDict

from .money import Money
from .tax import (
    Operation,
    OperationKind,
    OperationResult,
    process_operations_batch,
)

RawOperation = TypedDict(
    "RawOperation",
    {
        "operation": OperationKind,
        "unit-cost": Decimal | int,
        "quantity": int,
    },
    closed=True,
)


def lines_until_blank(reader: Iterable[str]) -> Iterator[str]:
    return takewhile(str.strip, reader)


def parse_json_line(line: str) -> list[Operation]:
    raw_ops_list: list[RawOperation] = json.loads(line, parse_float=Decimal)
    return [
        Operation(
            kind=raw["operation"],
            unit_cost=Money(Decimal(raw["unit-cost"])),
            quantity=raw["quantity"],
        )
        for raw in raw_ops_list
    ]


def dump_json(tax_list: Iterable[OperationResult], output: Writer[str]) -> None:
    formatted_list = [{"tax": float(res.tax.amount)} for res in tax_list]

    json.dump(formatted_list, output)
    output.write("\n")


def run(
    reader_stream: Iterable[str],
    writer_stream: Writer[str],
) -> None:
    for line in lines_until_blank(reader_stream):
        dump_json(
            process_operations_batch(parse_json_line(line)),
            writer_stream,
        )


def main() -> None:
    run(sys.stdin, sys.stdout)
