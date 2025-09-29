import json
from collections.abc import Iterable, Iterator
from typing import IO

from .tax import (
    Operation,
    OperationResult,
    process_operations_batch,
)


def readlines(reader: Iterable[str]) -> Iterator[str]:
    for line in reader:
        if line.strip():
            yield line


def parse_json_line(line: str) -> list[Operation]:
    raw_ops_list = json.loads(line)
    return [Operation.from_dict(raw_ops) for raw_ops in raw_ops_list]


def dump_json(tax_list: list[OperationResult], output: IO[str]) -> None:
    formatted_list = [{"tax": float(res.tax.amount)} for res in tax_list]

    json.dump(formatted_list, output)
    output.write("\n")


def process_operations(
    reader_stream: Iterable[str],
    writer_stream: IO[str],
) -> None:
    # functional style
    # deque hack can be used to consume lazy map without create a list
    # this will reduce memory footprint
    # deque(
    #     map(
    #         partial(dump_json, output=writer_stream),
    #         map(calculate_taxes, map(parse_json_line, readlines(reader_stream))),
    #     ),
    #     maxlen=0,
    # )
    for line in readlines(reader_stream):
        dump_json(
            process_operations_batch(parse_json_line(line)),
            writer_stream,
        )
