## Notes

### Problem

To solve a tax calculation problem, and having prior domain knowledge, I want to use a ["Money" object](https://martinfowler.com/eaaCatalog/money.html) capable of performing arithmetic and comparison operations between itself and with scalars. All monetary values will have two decimal places.

### Solution

I will use dataclasses to create a **Money object** with an amount and currency. A default currency (BRL) will be used, but the system will be ready to support other currencies in the future. Arithmetic ($+$, $-$, $*$, $/$), and comparison ($<$, $>$, $\ge$, $\le$, $==$, $\ne$) operations will be implemented for the Money object.

---

### Problem

Given a list of financial operations, calculate the **tax** to be paid on each operation.

Some rules:

- The tax percentage paid is **20%** on the profit obtained from the operation. That is, tax will be paid when there is a sale operation whose price is higher than the **weighted average purchase price**.

- To determine if the operation resulted in a profit or loss, you must calculate the **weighted average price**. Thus, when you buy shares, you must recalculate the weighted average price using this formula: $\text{new-weighted-average} = ((\text{current-share-qty} \times \text{current-weighted-average}) + (\text{purchased-share-qty} \times \text{purchase-price})) / (\text{current-share-qty} + \text{purchased-share-qty})$. For example, if you bought 10 shares for R\$ 20.00, sold 5, then bought another 5 for R\$ 10.00, the weighted average is $((5 \times 20.00) + (5 \times 10.00)) / (5 + 5) = 15.00$.

- You must use **past losses** to deduct against multiple future profits, until the entire loss is deducted.

- Losses occur when you sell shares at a value lower than the weighted average purchase price. In this case, **no tax** must be paid, and you must subtract the loss from subsequent profits before calculating the tax.

- You pay **no tax** if the total value of the operation (share unit cost $\times$ quantity) is less than or equal to R\$ 20,000.00. Use the total operation value, not the profit obtained, to determine whether tax should be paid. And don't forget to deduct the loss from subsequent profits.

- **No tax** is paid on buy operations.

- No operation will sell more shares than you currently own.

### Solution

The solution was to break the problem into two distinct parts: buying and selling. To maintain the premise of immutable objects, each operation returns a new state after its processing is complete.

During a purchase, the weighted average price is calculated, and the quantity of shares is incremented, though the tax rate is zero. The sale operation was broken down into smaller components, such as calculating profit or loss and then verifying if tax should be charged on the operation.

Crucially, each operation processing step takes an initial investment state and returns a result containing the tax value to be applied and the new state after the operation is processed. This design allows for the sequential processing of multiple operations effectively.

---

### Problem

Binary floating point cannot represent most decimal fractions exactly. `Decimal(1.005)` is `1.00499999...`, so a `Money` built from or multiplied by a float can round the wrong way before the two-place rounding ever runs. The CLI already converts the JSON input through `str` before building a `Decimal`, but nothing stopped another caller from passing a float directly.

### Solution

`Money` accepts only `Decimal` for its amount, and the `Scalar` type used by `*` and `/` is `int | Decimal`. The operators check the operand at runtime and return `NotImplemented` for anything else, so `Money * 0.5` raises a `TypeError` instead of silently going through float. Callers must spell out `Decimal("0.5")`, which makes the precision explicit at the call site.

---

### Problem

An excessive repetition of code and the introduction of magic values were identified when initializing or returning monetary values equal to zero (e.g., `Money(amount=0.00)`). This repetition negatively impacts code readability and maintainability.

### Solution

To solve the issue of repeated zero monetary values, an **alternative constructor** was created within the **`Money`** class (or a class method/helper function) called **`zero`** (e.g., `Money.zero()`). This constructor allows a **`Money`** object with a zero value to be initialized in a clean and expressive way, encapsulating the logic for a standard zero value and keeping the code more **clean** and **readable**.

---

### Problem

The logic for calculating and applying the accumulated loss was overly complex due to the use of multiple conditional statements (if/else). Specifically, the function responsible for updating the loss (e.g., calculate_loss) could be simplified. The three separate conditions were harder to read and maintain than necessary.

### Solution

The complexity in the loss calculation logic was reduced by refactoring the conditional statements into a single, more concise mathematical expression: Math.max(0, loss + (result * -1)). This change simplifies the code by ensuring that the accumulated loss is correctly offset by any profits (result), but never goes below zero, eliminating the need for complex branch logic and improving the method's readability and simplicity. Later, the taxable profit and the carried-forward loss were recognised as the same net value with opposite signs, so `handle_sell` computes `net = gross_profit - accumulated_loss` once and derives `taxable = max(0, net)` and `new_loss = max(0, -net)` from it. The former nested helpers closed over nothing, so `calculate_tax` became a module-level function with its own tests.

---

### Problem

A common development risk was identified: the **"it works on my machine"** problem. This risk stems from inconsistencies between local development environments and the eventual deployment environment, potentially leading to hard-to-debug integration or runtime issues.

### Solution

To ensure environment parity and eliminate the "it works on my machine" issue, a robust **Setup for local or container execution (Docker)** was implemented. By providing a clear process and configuration for running the application inside a **Docker container**, we guarantee that the execution environment (dependencies, operating system libraries, etc.) remains consistent across all developer machines and deployment stages.

---

### Problem

There was a risk of introducing subtle bugs and reducing code quality due to the lack of static analysis and inconsistent coding styles among developers. Specifically, it was necessary to **guarantee that type hints were respected before runtime** and to enforce a consistent, high-quality style across the codebase.

### Solution

To ensure type consistency and quality, the following tools were integrated:

1.  **ty**: This tool was adopted to perform **static type checking**, ensuring that all type hints are respected and catching type-related errors before the code is executed.
2.  **Tooling for consistent style using linter and prek**: Linters were configured to enforce a unified coding style. These tools were integrated with **prek** (a fast pre-commit hooks runner) to automatically check and format code before every commit, guaranteeing that all changes adhere to the defined style and quality standards.

---

### Problem

While simply returning the final calculated tax is sufficient for the primary goal, it lacks **transparency** and **auditability**. The consumer of the processing logic (the calling code) would have no way to validate or debug the intermediate steps—such as the calculated profit, the loss deduction amount, or the updated state—if the final tax value seemed incorrect.

### Solution

The design decision was made to return a **detailed result object** for *each step* of the operation processing, rather than just the final tax amount. This result object (**`OperationResult`**) contains not only the final **`tax`** but also the **`new_state`**, which carries the updated **`quantity`**, **`weighted_average_price`** and **`accumulated_loss`**. This enables the calling method to **audit** or **validate** every step of the calculation, significantly increasing the system's transparency and debuggability.

---

### Problem

The CLI functions that consume or produce streams were typed using **`IO[str]`**, which exposes the full IO interface (read, write, seek, close, etc.). This is more permissive than necessary: `dump_json` only needs to call `write()` on its output, and any caller-supplied object satisfying just that contract should be accepted. Using `IO[str]` unnecessarily narrows the set of acceptable arguments and couples the signature to the full file-like protocol.

### Solution

The argument types were narrowed to the **`io.Writer`** protocol (and analogously `io.Reader` where applicable), following the rationale: *"The protocols `io.Reader` and `io.Writer` offer a simpler alternative for argument types, when only the `read()` or `write()` methods are accessed."* This makes the signatures express exactly what the functions require, enabling any object that implements just `write()` to be passed in, and improving both readability and testability.

---

### Problem

The specification only says to round monetary values to the second decimal place, without naming a rounding mode. `Decimal.quantize` uses the context default, `ROUND_HALF_EVEN` (banker's rounding), so an exact tie such as `10.025` becomes `10.02` rather than the `10.03` many readers expect from school rounding. The tie is reachable through the weighted average price: buying 1 share at 10.00 and then 1 at 10.05 gives exactly `10.025`. The tax itself can never hit a tie, because a two-place profit multiplied by 0.20 always ends in an even digit.

### Solution

Banker's rounding was kept as a deliberate choice. It is the `Decimal` default, it is the mode recommended by IEEE 754 for monetary work because it does not bias totals upward over many operations, and the specification's own examples (`16.67`, `3700.00`) are unaffected by the choice. The trade-off is that a weighted average ending in an exact 5 at the third decimal place rounds to the nearest even cent. Should a reviewer or future requirement prefer `ROUND_HALF_UP`, the change is a single `rounding=` argument in `Money.__post_init__`.

---

### Problem

The specification's examples print the tax with two decimal places, such as `{"tax": 0.00}` and `{"tax": 10000.00}`. JSON numbers carry no notion of decimal places, and the standard library encoder only accepts `float` as a non-integer numeric type. Converting the `Decimal` amount to `float` therefore prints `{"tax": 0.0}` and `{"tax": 10000.0}`, which differ from the examples only in how trailing zeros are shown.

### Solution

The output stays a JSON number produced by `float` and the cosmetic difference is accepted. The values are numerically identical to the examples, so any consumer that parses the JSON gets the same result. Precision is not at risk: the `Money` object has already rounded the amount to two places before the conversion, so the `float` never carries more digits than the `Decimal` had. The alternatives were rejected because each trades a single `json.dump` call for something worse: serializing as a string changes the field type and breaks numeric comparisons; building the JSON by hand replaces the encoder with formatting code that has to be maintained; and a `float` subclass with a custom `__repr__` relies on an implementation detail of the C encoder.

---

### Problem

`process_operations` is a pipeline: read lines, parse each one, process the batch, dump the result. A functional style was considered, chaining lazy `map` calls and consuming the result through a `deque` with `maxlen=0` so that no intermediate list is ever built:

```python
deque(
    map(
        partial(dump_json, output=writer_stream),
        map(process_operations_batch, map(parse_json_line, readlines(reader_stream))),
    ),
    maxlen=0,
)
```

### Solution

The explicit `for` loop was kept. It is equally lazy, since `readlines` is a generator and each line is parsed, processed and written before the next one is read, so the memory footprint is the same. The loop reads top to bottom without requiring the reader to know the `deque(maxlen=0)` idiom, and it does not need `functools.partial` to bind the output stream. The functional version is recorded here rather than left as a comment in the code, where it had already drifted out of sync with the function names it referenced.

---
