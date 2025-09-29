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

An excessive repetition of code and the introduction of magic values were identified when initializing or returning monetary values equal to zero (e.g., `Money(amount=0.00)`). This repetition negatively impacts code readability and maintainability.

### Solution

To solve the issue of repeated zero monetary values, an **alternative constructor** was created within the **`Money`** class (or a class method/helper function) called **`zero`** (e.g., `Money.zero()`). This constructor allows a **`Money`** object with a zero value to be initialized in a clean and expressive way, encapsulating the logic for a standard zero value and keeping the code more **clean** and **readable**.

---

### Problem

The logic for calculating and applying the accumulated loss was overly complex due to the use of multiple conditional statements (if/else). Specifically, the function responsible for updating the loss (e.g., calculate_loss) could be simplified. The three separate conditions were harder to read and maintain than necessary.

### Solution

The complexity in the loss calculation logic was reduced by refactoring the conditional statements into a single, more concise mathematical expression: Math.max(0, loss + (result * -1)). This change simplifies the code by ensuring that the accumulated loss is correctly offset by any profits (result), but never goes below zero, eliminating the need for complex branch logic and improving the method's readability and simplicity.

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

1.  **Mypy**: This tool was adopted to perform **static type checking**, ensuring that all type hints are respected and catching type-related errors before the code is executed.
2.  **Tooling for consistent style using linter and pre-commit**: Linters were configured to enforce a unified coding style. These tools were integrated with **pre-commit hooks** to automatically check and format code before every commit, guaranteeing that all changes adhere to the defined style and quality standards.

---

### Problem

While simply returning the final calculated tax is sufficient for the primary goal, it lacks **transparency** and **auditability**. The consumer of the processing logic (the calling code) would have no way to validate or debug the intermediate steps—such as the calculated profit, the loss deduction amount, or the updated state—if the final tax value seemed incorrect.

### Solution

The design decision was made to return a **detailed result object** for *each step* of the operation processing, rather than just the final tax amount. This result object contains not only the final **`tax`** but also the **`new_state`** and potentially other intermediate values (like **`profit_calculated`** or **`loss_applied`**). This enables the calling method to **audit** or **validate** every step of the calculation, significantly increasing the system's transparency and debuggability.

---
