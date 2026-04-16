# R Class Systems Guide

Detailed comparison of S3, S4, R7, and R6 with constructors, methods, and usage
examples for each system.

**Sources:**
- Advanced R 2e ch. 12 "Base types" through ch. 16 "Trade-offs" — <https://adv-r.hadley.nz/oo.html>
- S3: Advanced R ch. 13 — <https://adv-r.hadley.nz/s3.html>
- S4: Advanced R ch. 15 — <https://adv-r.hadley.nz/s4.html>
- R7 package — <https://rconsortium.github.io/S7/> (R7 was renamed to S7)
- R6 package — <https://r6.r-lib.org/>
- `?methods::setClass`, `?methods::setGeneric`
- Bioconductor S4 guidance — <https://contributions.bioconductor.org/r-code.html>

---

## Decision Tree

```
Need mutable state (caching, connections, environments)?
  YES -> R6
  NO  -> Is this a Bioconductor package or formal interface contract?
    YES -> S4
    NO  -> Greenfield project wanting modern features?
      YES -> R7 (if stable enough for your timeline)
      NO  -> S3 (default choice for most packages)
```

**Rule of thumb:** Start with S3 unless you have a specific reason not to.

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

## R7 — Modern Successor to S3/S4

Developed by the R Consortium as a unification of S3 and S4. Available via the
`R7` package. Best for greenfield projects with no Bioconductor dependency.

### Class Definition

```r
library(R7)

temperature <- new_class("temperature",
  properties = list(
    value = class_double,
    unit  = new_property(class_character, default = "celsius",
      validator = function(value) {
        if (!value %in% c("celsius", "fahrenheit", "kelvin")) {
          sprintf("Unknown unit: %s", value)
        }
      }
    )
  ),
  validator = function(self) {
    if (self@unit == "kelvin" && any(self@value < 0)) {
      "Kelvin values cannot be negative"
    }
  }
)
```

### Generics and Methods

```r
convert <- new_generic("convert", "x")

method(convert, temperature) <- function(x, to = "fahrenheit") {
  if (x@unit == "celsius" && to == "fahrenheit") {
    temperature(value = x@value * 9 / 5 + 32, unit = "fahrenheit")
  } else {
    cli::cli_abort("Conversion not supported.")
  }
}
```

### Usage

```r
temp <- temperature(value = c(36.6, 37.2), unit = "celsius")
temp@value
#> [1] 36.6 37.2

convert(temp, to = "fahrenheit")
```

**Key features:** Properties (not slots or attributes), built-in validation,
compatible with S3 generics, cleaner syntax than S4.

**Caveat:** R7 is maturing but not yet required by any major ecosystem. Check
current stability before adopting for CRAN packages.

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

| Feature | S3 | S4 | R7 | R6 |
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
