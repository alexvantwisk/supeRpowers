# stringr Recipes

Idiomatic string manipulation with `stringr`. Always prefer stringr over base
`grep`/`sub`/`gsub` — consistent argument order (`string` first), vectorised,
and locale-aware. All code uses `|>` and `<-`.

> **stringr 1.6.0 (Nov 2025)** introduced two breaking changes:
> 1. All relevant functions now **preserve names** — `str_to_upper(c(a = "x"))`
>    returns a named vector. Update downstream code that assumed unnamed
>    output.
> 2. In `str_replace_all()` a *replacement function* now receives all values
>    in a single vector (one call instead of one per element) — much faster
>    but breaks per-element callbacks. `str_like(ignore_case)` is also
>    deprecated; `str_like()` is now case-sensitive (matches SQL `LIKE`).

---

## Detect, Extract, Replace

```r
emails <- c("alice@example.com", "bob+filter@work.org", "no-at-sign")

# Detect — returns logical vector (predicate-style)
str_detect(emails, "@")
emails |> keep(str_detect, "@")               # filter using purrr::keep

# Extract — pull the first match
str_extract(emails, "[^@]+(?=@)")              # username before @
str_extract(emails, "(?<=@).+$")               # domain after @

# Extract all matches per element (returns a list)
str_extract_all("foo123 bar456", "\\d+")

# Replace — swap one match (or all) per element
str_replace("foo bar foo", "foo", "FOO")       # first only
str_replace_all("foo bar foo", "foo", "FOO")  # every match
```

**Decision:** `str_detect()` for filtering; `str_extract()` to capture;
`str_replace_all()` for substitution. Reach for `str_match()` only when you
need capture groups returned as a matrix.

---

## Splitting and Joining

```r
# str_split() returns a list (one element per input string)
"a,b,,c" |> str_split(",")                    # list of length 1
"a,b,,c" |> str_split_1(",")                  # vector of length 4 (single input)

# Fixed-width splits
"2025-04-27" |> str_split_fixed("-", n = 3)   # matrix: year, month, day

# Use separate_wider_delim() for splitting a column inside a data frame
df |> separate_wider_delim(name, delim = " ", names = c("first", "last"))

# Join the inverse — collapse a vector to one string
str_c(c("a", "b", "c"), collapse = ", ")
str_flatten(c("a", "b", "c"), collapse = ", ", last = " and ")
```

For data-frame splits, prefer `separate_wider_delim()` /
`separate_wider_regex()` from tidyr — they integrate cleanly with pipelines
(see `references/tidyr-reshape.md`).

---

## Whitespace, Padding, Case

```r
# Cleanup
str_squish("  hello   world  ")              # "hello world" — collapse whitespace
str_trim(" hello ")                           # "hello"      — only edges
str_pad("42", width = 5, side = "left", pad = "0")  # "00042"
str_truncate("a long string", width = 8)     # "a lon..."

# Case conversion (locale-aware)
str_to_upper("café")
str_to_lower("CAFÉ")
str_to_title("kelly o'brien")                 # "Kelly O'Brien"
```

`str_squish()` is the workhorse for cleaning user-entered text — collapses
internal whitespace AND trims edges in one call.

---

## Regex Fundamentals

```r
# Anchors
str_detect(x, "^foo")    # starts with
str_detect(x, "bar$")    # ends with
str_detect(x, "^exact$") # exact full match (or use fixed())

# Character classes
"[A-Za-z]"   # any letter
"[[:alpha:]]"  # POSIX class — locale-aware
"\\d"        # digit; "\\D" — non-digit
"\\s"        # whitespace; "\\S" — non-whitespace
"\\b"        # word boundary

# Quantifiers
"a?"   # 0 or 1; "a*" — 0+; "a+" — 1+; "a{2,4}" — 2 to 4

# Capture groups (extract specific parts)
str_match("price: $42.99", "\\$(\\d+)\\.(\\d+)")
#> [,1]      [,2]  [,3]
#> "$42.99"  "42"  "99"
```

In R strings, escape backslashes: write `"\\d"` for the regex `\d`. Use raw
strings `r"(\d+)"` (R >= 4.0) to avoid double-escaping.

---

## regex() Modifiers and fixed()/coll()

```r
# Case-insensitive search via regex() modifier
str_detect("Apple Pie", regex("apple", ignore_case = TRUE))

# Multi-line and dotall
str_extract(text, regex("foo.+bar", dotall = TRUE, multiline = TRUE))

# fixed() — interpret as a literal string (faster, no regex special chars)
str_detect(filenames, fixed(".tar.gz"))

# coll() — locale-aware comparison (handles é vs e)
str_detect(names, coll("muller", ignore_case = TRUE, locale = "de"))
```

**Rule:** `fixed()` for literal substrings, `regex()` for patterns,
`coll()` when locale collation matters (sorting names, accent-insensitive
search).

---

## glue Interop

```r
# glue::glue() embeds R expressions into strings — preferred over paste0
name <- "Alice"; n <- 3
glue::glue("{name} has {n} {if (n == 1) 'order' else 'orders'}")

# Inside a pipeline
df |> mutate(label = glue::glue("{name}: {round(score, 2)}"))
```

Use `glue` for any non-trivial string interpolation; reserve `str_c()` /
`paste0()` for simple concatenation.

---

## Gotchas

| Trap | Fix |
|------|-----|
| `grep()` / `sub()` argument order is `pattern, x` | stringr is always `string, pattern` — consistent |
| Backslash escaping confusion | Use raw strings `r"(\d+)"` (R >= 4.0) |
| `str_replace()` only replaces FIRST match | Use `str_replace_all()` for global replacement |
| Regex meta-chars (`. ( ) [ ] $ ^`) treated literally | Wrap in `fixed()` or escape with `\\` |
| Accents not matching | Use `coll()` instead of `regex()` for accent-insensitive |
| `str_split()` returns a list when you wanted a vector | Use `str_split_1()` (single string) or `str_split_fixed()` |
| Trailing newlines in `str_extract()` | Trim with `str_trim()` or anchor pattern more tightly |
| Output gains unwanted names (stringr >= 1.6) | Use `unname()` after the operation, or strip names from input first |
| `str_replace_all(x, p, fn)` callback behaves differently (>= 1.6) | Replacement function now sees the full vector — vectorise the body |
| `str_like(x, "FOO", ignore_case = TRUE)` warns | Deprecated — `str_like()` is case-sensitive; pre-lowercase both sides if needed |
