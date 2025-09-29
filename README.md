# Capital Gains

## Contexto

A Command-Line Interface (CLI) for calculating the tax due on profits or losses from stock market operations (or equity trading).

## Requirements

  - [Python](https://www.python.org/)
  - [uv](https://docs.astral.sh/uv/)
  - [pre-commit (development only)](https://www.google.com/search?q=)

The command `pre-commit install` is required before making any changes to the code.
With every new **commit**, the code will be adjusted according to the pre-defined styles.

## How to Run the Project

Run the project locally using the command:

```sh
uv run capital-gains < entrada.txt
```

or build the container

```sh
docker image build --tag capital_gains .
```

and run the tests inside it:

```sh
docker container run --interactive capital_gains < entrada.txt
```

-----

## How to Run the Project Tests

Run the tests locally using the command:

```sh
uv run pytest
```

To run the tests with **coverage reports** for the `capital_gains` module, use:

```sh
uv run pytest --cov=capital_gains tests/
```

or build the container for testing

```sh
docker image build --target=builder --tag capital_gains:test .
```

and run the tests inside it:

```sh
docker container run --interactive capital_gains:test pytest
```

## Technical and/or Architectural Decisions

- Code built using **Test-Driven Development (TDD)**, using the example cases as input for project evolution.

- Data objects will be **immutable**.

- The execution of the CLI and tests can be done locally or using the provided container.

- Use of [Pytest](https://docs.pytest.org/en/stable/) to write simpler and more readable tests.

## Code Styles

The code has been consistently checked and formatted using the **Ruff** tool (which combines linter and formatting functionalities). Additionally, types have been verified using the **mypy** tool.

The **pre-commit** tool will ensure your code adheres to the styles defined in the project.

## Notes

In the file [NOTES.md](NOTES.md), I've documented several ideas and discussions that emerged throughout the project's development. This compilation captures the key thought processes and conversations that informed our direction.


## TODO
- aumentar coverage (cli)
- tem como não precisar importar domínio do cli?
