# R Class Systems Guide

Detailed comparison of S3, S4, S7, and R6 with constructors, methods, and usage
examples for each system.

**Sources:**
- Advanced R 2e ch. 12 "Base types" through ch. 16 "Trade-offs" — <https://adv-r.hadley.nz/oo.html>
- S3: Advanced R ch. 13 — <https://adv-r.hadley.nz/s3.html>
- S4: Advanced R ch. 15 — <https://adv-r.hadley.nz/s4.html>
- S7 package (formerly R7) — <https://rconsortium.github.io/S7/>
- R6 package — <https://r6.r-lib.org/>
- `?methods::setClass`, `?methods::setGeneric`
- Bioconductor S4 guidance — <https://contributions.bioconductor.org/r-code.html>

---

## Decision Tree

```
Need mutable state (caching, connections, environments)?
  YES -> R6
  NO  -> Bioconductor package or interfacing with existing S4 ecosystem?
    YES -> S4
    NO  -> Greenfield class hierarchy?
      YES -> S7 (default for new code in 2025+)
      NO  -> S3 (one-off methods on existing classes; minimal ceremony)
```

**Rule of thumb (2025+):** S7 for new class hierarchies. S3 for adding a
method or two to an existing object. R6 only when you genuinely need
reference semantics. S4 only for Bioconductor compatibility.

---

## S3 — Informal, Simple, Ubiquitous

The default class system. Used by base R, tidyverse, and most CRAN packages.

### Constructor Pattern (Three Functions)

```r
# Low-level constructor -- creates the object, no validation
new_temperature <- function(value, unit = "celsius") {
  stopifnot(is.double(value))
  stopifnot(is.character(unit), length(unit) == 1)
  structure(
    value,
    unit = unit,
    class = "temperature"
  )
}

# Validator -- checks invariants
validate_temperature <- function(x) {
  unit <- attr(x, "unit")
  if (!unit %in% c("celsius", "fahrenheit", "kelvin")) {
    cli::cli_abort("Unknown unit: {.val {unit}}.")
  }
  if (unit == "kelvin" && any(x < 0)) {
    cli::cli_abort("Kelvin values cannot be negative.")
  }
  x
}

# User-facing constructor -- friendly interface with coercion
temperature <- function(value, unit = "celsius") {
  value <- as.double(value)
  validate_temperature(new_temperature(value, unit))
}
```

### Defining Methods

```r
# Generic (if creating your own)
convert <- function(x, ...) {
  UseMethod("convert")
}

# Method for temperature class
convert.temperature <- function(x, to = "fahrenheit", ...) {
  from <- attr(x, "unit")
  if (from == "celsius" && to == "fahrenheit") {
    temperature(x * 9 / 5 + 32, unit = "fahrenheit")
  } else if (from == "fahrenheit" && to == "celsius") {
    temperature((x - 32) * 5 / 9, unit = "celsius")
  } else {
    cli::cli_abort("Conversion from {.val {from}} to {.val {to}} not supported.")
  }
}

# Implement standard generics: format, print, [, c, etc.
print.temperature <- function(x, ...) {
  cat(paste0(as.numeric(x), "\u00B0", toupper(substr(attr(x, "unit"), 1, 1))), "\n")
  invisible(x)
}
```

### Inheritance and NextMethod

```r
# Subclass: child first, parent second in class vector
new_body_temp <- function(value, unit = "celsius", patient_id = NA_character_) {
  obj <- new_temperature(value, unit)
  attr(obj, "patient_id") <- patient_id
  class(obj) <- c("body_temp", "temperature")
  obj
}

# NextMethod delegates to parent class method
print.body_temp <- function(x, ...) {
  cat("Patient:", attr(x, "patient_id"), "| ")
  NextMethod()
  invisible(x)
}
```

---

## S4 — Formal, Strict, Bioconductor

Required by Bioconductor. Features: typed slots, formal validity, multiple
dispatch.

### Class Definition

```r
setClass("GenomicRange",
  slots = list(
    chromosome = "character",
    start      = "integer",
    end        = "integer",
    strand     = "character"
  ),
  prototype = list(
    strand = "+"
  ),
  validity = function(object) {
    errors <- character()
    if (any(object@start > object@end)) {
      errors <- c(errors, "start must be <= end")
    }
    if (!all(object@strand %in% c("+", "-", "*"))) {
      errors <- c(errors, "strand must be +, -, or *")
    }
    if (length(errors) == 0) TRUE else errors
  }
)
```

### Constructor

```r
GenomicRange <- function(chromosome, start, end, strand = "+") {
  new("GenomicRange",
    chromosome = as.character(chromosome),
    start      = as.integer(start),
    end        = as.integer(end),
    strand     = as.character(strand)
  )
}
```

### Generics and Methods

```r
# Define generic
setGeneric("width", function(x) standardGeneric("width"))

# Implement method
setMethod("width", "GenomicRange", function(x) {
  x@end - x@start + 1L
})

# show() is the S4 equivalent of print()
setMethod("show", "GenomicRange", function(object) {
  cat(sprintf("%s:%d-%d(%s)\n",
    object@chromosome, object@start, object@end, object@strand))
})
```

### Inheritance and Usage

```r
setClass("AnnotatedRange",
  contains = "GenomicRange",
  slots = list(gene_name = "character", score = "numeric")
)

# callNextMethod() is S4's equivalent of NextMethod()
setMethod("show", "AnnotatedRange", function(object) {
  callNextMethod()
  cat("  Gene:", object@gene_name, "\n")
})

gr <- GenomicRange("chr1", 1000L, 2000L, "+")
width(gr)          #> [1] 1001
validObject(gr)    # Explicit validity check
```

**Key differences from S3:** Access slots with `@` (not `$`), use `is(obj, "Class")`
instead of `inherits()`, define generics with `setGeneric()`.

---

## S7 — Modern Successor to S3 / S4

`S7` is the R Consortium's modern class system. It is on CRAN and intended
as the long-term successor to S3 and S4. Use it for new class hierarchies
unless you have a specific reason to use one of the others.

The project was initially released as `R7` and renamed to `S7` before its
0.1.0 CRAN release. Older blog posts may still say `library(R7)`; the API
is unchanged — install and load `S7` instead.

### Constructor: `new_class()`

```r
library(S7)

range_class <- new_class("range",
  properties = list(
    min = class_double,
    max = class_double
  ),
  validator = function(self) {
    if (length(self@min) != 1 || length(self@max) != 1) {
      "@min and @max must be length 1"
    } else if (self@min > self@max) {
      "@min must be <= @max"
    }
  }
)

x <- range_class(min = 1, max = 10)
x@min                                # 1
```

Properties replace S4 slots and S3 attributes. Access via `@`. Validation
runs on construction and on any property assignment.

### Methods: `new_generic()` + `method()`

```r
range_print <- new_generic("range_print", "x")
method(range_print, range_class) <- function(x) {
  cat(sprintf("[%g, %g]\n", x@min, x@max))
}

range_print(x)                       # [1, 10]
```

Generic registration is explicit — no `UseMethod()` magic, no S4
`setGeneric()` ceremony.

### Inheritance

```r
positive_range <- new_class("positive_range",
  parent = range_class,
  validator = function(self) {
    if (self@min < 0) "@min must be >= 0"
  }
)
```

Multiple inheritance is not supported (intentional simplification vs S4).

### S3 → S7 Migration

| S3 | S7 |
|---|---|
| `structure(list(...), class = "foo")` | `foo_class <- new_class("foo", properties = list(...))` |
| `attr(x, "name")` / `x$name` | `x@name` |
| `print.foo <- function(x, ...) {}` | `method(print, foo_class) <- function(x, ...) {}` |
| `UseMethod("fn")` | `new_generic("fn", "x")` |

Migrate incrementally: register S7 methods on `class_any` to handle existing
S3 objects, then re-shape internals over time. `S7::S7_dispatch()` interops
with both directions.

### S4 → S7 Migration

| S4 | S7 |
|---|---|
| `setClass("foo", representation(...))` | `foo_class <- new_class("foo", properties = list(...))` |
| Slots (`@`) | Properties (`@`, same syntax) |
| `setValidity` | `validator = function(self) {}` |
| `setGeneric` + `setMethod` | `new_generic` + `method()` |
| `@include` for collation | Same — S7 still requires Collate when generics depend on classes defined later |
| Multiple dispatch | Multi-arg generics: `new_generic("fn", c("x", "y"))` |

S7 was designed to make S4-style packages migrateable. The `methods` import
goes away; `S7` becomes the single dependency.

### When NOT to Use S7

- Mutable state needed → use R6.
- Bioconductor package (interop with `BiocGenerics`/`SummarizedExperiment`)
  → use S4.
- Adding one or two methods to an existing S3 object → just write S3 methods.

**DESCRIPTION:** `Imports: S7` (CRAN) — not `R7`.

---

## R6 — Reference Semantics for Mutable State

Objects are modified in place (not copied). Use for: database connections,
caches, API clients, state machines, environments that accumulate results.

### Class Definition

```r
library(R6)

ApiClient <- R6::R6Class("ApiClient",
  public = list(
    base_url = NULL,
    initialize = function(base_url, api_key) {
      self$base_url <- base_url
      private$api_key <- api_key
      private$cache <- list()
    },
    get = function(endpoint) {
      url <- paste0(self$base_url, "/", endpoint)
      if (!is.null(private$cache[[url]])) return(private$cache[[url]])
      response <- private$make_request(url)
      private$cache[[url]] <- response
      response
    },
    clear_cache = function() {
      private$cache <- list()
      invisible(self)
    }
  ),
  private = list(
    api_key = NULL,
    cache = NULL,
    make_request = function(url) {
      httr2::request(url) |>
        httr2::req_headers(Authorization = paste("Bearer", private$api_key)) |>
        httr2::req_perform() |>
        httr2::resp_body_json()
    }
  )
)
```

### Usage and Inheritance

```r
client <- ApiClient$new("https://api.example.com", api_key = "secret")
data <- client$get("users")          # Fetches from API
data <- client$get("users")          # Returns cached result
client2 <- client$clone(deep = TRUE) # Clone to avoid shared mutation

# Inheritance via inherit argument
AuthClient <- R6::R6Class("AuthClient",
  inherit = ApiClient,
  public = list(
    login = function(user, pass) { invisible(self) }
  )
)
```

**Key differences:** `$new()` to construct, `self` / `private` access, modify
in place (no copy-on-modify), `$clone()` for explicit copies.

**Warning:** R6 objects bypass R's functional paradigm. Use only when mutable
state is genuinely needed. Most packages should prefer S3.

---

## Comparison Summary

| Feature | S3 | S4 | S7 | R6 |
|---------|----|----|----|----|
| Complexity | Low | High | Medium | Medium |
| Formal definition | No | Yes | Yes | Yes |
| Validation | Manual | `validity` | `validator` | Manual |
| Access | `$` / attributes | `@` slots | `@` properties | `$` methods |
| Dispatch | Single | Multiple | Single | None (methods on object) |
| Semantics | Copy | Copy | Copy | Reference (mutable) |
| Inheritance | `c("child", "parent")` | `contains` | `parent` | `inherit` |
| CRAN packages | Vast majority | Bioconductor | Emerging | Niche |
| Best for | General use | Formal interfaces | Modern projects | Mutable state |
