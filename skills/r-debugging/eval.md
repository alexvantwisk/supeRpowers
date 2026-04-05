# Eval: r-debugging

> Development-only. Not loaded by the plugin.

## Binary Eval Questions

1. When asked to "debug" a function that is correct but slow, does the skill defer to r-performance rather than applying diagnostic debugging techniques?
2. When the user reports a bug and asks the skill to also write tests for the fix, does the skill defer the test-writing portion to r-tdd?
3. When encountering a suppressed warning (`suppressWarnings()`), does the skill diagnose the root cause rather than endorsing the suppression?
4. When debugging inside a Shiny reactive context, does the skill recommend Shiny-aware tools (`reactlog`, `browser()` inside `observe()`) rather than only base R debugging?
5. When a user asks why their statistical model gives "wrong" results, does the skill defer to r-stats for model diagnostics rather than treating it as a code bug?
6. Does the skill follow the reproduce-isolate-diagnose-fix-test workflow rather than jumping directly to a fix?
7. Does all generated code use `|>` and `<-` exclusively (no `%>%` or `=` for assignment)?

## Test Prompts

### Happy Path

- "My function returns NULL instead of a data frame when the input has zero rows. Here's the code: [function with missing early-return guard]. Help me find and fix the bug."
- "I'm getting 'object not found' errors inside a dplyr pipeline but the column definitely exists. The error is: Error in `mutate()`: object 'patient_id' not found."

### Edge Cases

- "My Shiny app's reactive value updates but the plot doesn't re-render. I've tried adding `browser()` but it never triggers. How do I debug reactive dependencies?"
- "This code works on a vector of length 10 but silently gives wrong results on length 7. I suspect vector recycling but I'm not sure where." (Must identify recycling without length-multiple warning)
- "My function works in the global environment but fails inside a package with 'could not find function' errors. The function is imported via NAMESPACE."

### Adversarial Cases

- "My data processing function takes 3 minutes to run. Can you debug why it's so slow and fix the performance issue?" (boundary: performance profiling should defer to r-performance)
- "I found a bug in my utility function. Debug it and then write a full testthat test suite so it doesn't regress." (boundary: debugging is in scope, test suite writing should defer to r-tdd)
- "My linear regression gives an R-squared of 0.02 which seems wrong. Debug the model to find out why the fit is bad." (boundary: model diagnostics should defer to r-stats)

### Boundary Tests

- "Profile this function to find where it spends the most time." boundary -> r-performance
- "Write unit tests for this function that currently has a known bug." boundary -> r-tdd
- "My mixed-effects model has singular fit warnings. What's wrong?" boundary -> r-stats

## Success Criteria

- Happy path responses MUST follow the reproduce-isolate-diagnose-fix-test sequence explicitly, not just emit a corrected function.
- The zero-row input bug fix MUST include a guard clause or explicit handling for edge-case inputs, not just fix the specific reported case.
- The 'object not found' response MUST diagnose data masking or `.data` pronoun issues, not suggest renaming the column.
- Shiny reactive debugging MUST mention `reactlog` or `reactiveConsole(TRUE)` or `observe({ browser() })` -- not only `browser()` at the top level.
- Vector recycling response MUST explain R's silent recycling rule (no warning when the longer length is a multiple) and demonstrate how to detect it.
- Environment scoping response MUST discuss NAMESPACE imports, `::` usage, or `@importFrom` directives.
- Performance-focused prompt MUST be deferred to r-performance; response must NOT contain `profvis` or `bench::mark` code.
- Test-writing portion of the combined prompt MUST be deferred to r-tdd; response must NOT produce a `test_that()` block.
- Statistical model prompt MUST be deferred to r-stats; response must NOT produce model diagnostic code (e.g., `plot(model)`, `summary(model)`).
- Response must NOT suggest `rm(list = ls())` in any context, especially not inside functions.
- Response must NOT endorse `suppressWarnings()` or `try(silent = TRUE)` as fixes without diagnosing the underlying cause.
- Response must NOT use `%>%`, `=` for assignment, or single quotes for strings.
