import json
from collections.abc import Iterator
from typing import IO, Any, Protocol, TypeVar

from .tax import (
    Money,
    Operation,
    OperationResult,
)

_T_co = TypeVar("_T_co", covariant=True)


class SupportsReadline(Protocol[_T_co]):
    def readline(self, length: int = ..., /) -> _T_co: ...


class OperationTaxEncoder(json.JSONEncoder):
    def default(self, obj: object) -> Any:
        match obj:
            case OperationResult(_, tax):
                return {"tax": float(tax.amount)}
            case _:
                return super().default(obj)


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
