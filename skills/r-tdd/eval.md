# Eval: r-tdd

> Development-only. Not loaded by the plugin.

## Binary Eval Questions

1. Does the skill write the failing test BEFORE any implementation code (red-green-refactor order)?
2. Do generated tests assert observable behavior (function outputs, side effects) rather than implementation details (internal variable names, private helper calls)?
3. When asked to determine if two group means are statistically different, does the skill defer to r-stats rather than writing a unit test?
4. When asked to debug why a test fails, does the skill defer to r-debugging?
5. Does the skill use testthat 3rd edition conventions (`test_that()`, `expect_*()`, edition 3 snapshot API)?
6. Do test fixtures include proper cleanup (e.g., `withr::defer()`, `withr::local_tempfile()`) rather than leaving side effects?

## Test Prompts

### Happy Path

- "Write tests for a function `calculate_bmi(weight_kg, height_m)` that returns BMI, errors on non-positive inputs, and warns when BMI exceeds 50."
- "I have a function `parse_date_flexible(x)` that accepts multiple date formats. Write a TDD test suite, then implement it."

### Edge Cases

- "Write a snapshot test for a function that returns a summary including the current timestamp." (non-deterministic output -- must mock or normalize the timestamp, not snapshot raw output that changes every run)
- "Write tests for a function that calls an external REST API to fetch exchange rates." (mocking API calls -- must use `httptest2` or `webmockr` or `withr` to mock, not make real HTTP calls in tests)
- "Write tests for an S4 class with a `show` method and a validity check." (S4 methods -- must test validity via `validObject()`, test show via `capture.output()` or snapshot, test dispatch correctly)

### Adversarial Cases

- "Test whether the mean response in group A is significantly different from group B using my experiment data." (hypothesis testing -- must defer to r-stats; this is a statistical question, not a unit test)
- "My test_that block fails with 'Error: object df_clean not found' and I cannot figure out why. Help me debug." (debugging a failure -- must defer to r-debugging for scoping and environment diagnosis)
- "Run R CMD check on my package and fix any NOTEs about test coverage." (package quality gate -- must defer to r-package-dev for R CMD check; r-tdd covers test writing, not package-level checks)

### Boundary Tests

- "Is the correlation between X and Y statistically significant? Write a test for that." (boundary -> r-stats; statistical significance is not a unit test)
- "My test passes locally but fails in R CMD check with a strange encoding error." (boundary -> r-package-dev; R CMD check issues are package-dev territory)
- "A test I wrote passes but the function still produces wrong output in production. Help me trace the discrepancy." (boundary -> r-debugging)

## Success Criteria

- Every TDD response MUST show the test first, then implementation, in explicit red-green-refactor sequence. Showing implementation before or without the test is a failure.
- Tests MUST assert on return values, error classes, warning messages, or visible side effects -- never on internal variable names or call counts of private helpers.
- Snapshot tests with non-deterministic content MUST mock or normalize the varying element; a raw snapshot of timestamped output is a failure.
- API-calling functions MUST be tested with mocked HTTP responses; any test that makes a real network call is a failure.
- Test fixtures that create files, set options, or modify environment variables MUST include cleanup via `withr::defer()`, `on.exit()`, or `withr::local_*()`. Bare `unlink()` at end-of-test without protection is a failure.
- Statistical hypothesis testing prompts MUST be deferred to r-stats; writing a `test_that()` block that calls `t.test()` to answer a research question is a failure.
- Debugging prompts MUST be deferred to r-debugging; inline traceback analysis is out of scope.
- R CMD check prompts MUST be deferred to r-package-dev.
- All generated R code MUST use `|>`, `<-`, snake_case, and double quotes.
