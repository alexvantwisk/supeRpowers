# lubridate Recipes

Date and date-time arithmetic, parsing, components, time zones, and rounding.
Always use lubridate over base `as.Date()` / `strptime()` — the parser names
encode the format and the components are explicit. All code uses `|>` and
`<-`.

---

## Parsers

```r
# Order-encoded parsers — name = component order
ymd("2025-04-27")                # 2025-04-27
mdy("04/27/2025")                # 2025-04-27
dmy("27 Apr 2025")               # 2025-04-27
ymd_hms("2025-04-27 14:30:00")   # POSIXct

# Mixed input formats — parse_date_time() with a vector of orders
mixed <- c("2025-01-15", "01/15/2025", "January 15, 2025", "15-Jan-2025")
parse_date_time(mixed, orders = c("ymd", "mdy", "BdY", "dby"))
```

**Rule:** When dates may be in mixed formats, use `parse_date_time()` with
multiple `orders`. Never silently coerce with `as.Date()` — it returns NA
for any format it doesn't recognise without warning.

---

## Components: Extract and Set

```r
ts <- ymd_hms("2025-04-27 14:30:45")

year(ts)    # 2025
month(ts)   # 4
month(ts, label = TRUE, abbr = FALSE)  # April (factor)
day(ts)     # 27
wday(ts, label = TRUE, week_start = 1) # Sun (factor)
hour(ts); minute(ts); second(ts)
yday(ts)    # day of year
week(ts)    # ISO week is `isoweek()`

# Set components (rare — usually compute, don't mutate)
year(ts) <- 2024
```

Use `wday(..., week_start = 1)` to make Monday day 1 (ISO) — the default is
Sunday, which surprises non-US users.

---

## Durations vs Periods vs Intervals

```r
# Period — calendar-aware ("add 1 month" handles variable month lengths)
ymd("2025-01-31") + months(1)        # 2025-02-28 (clamped)
ymd("2025-01-31") %m+% months(1)     # 2025-02-28 (explicit clamp; safer)

# Duration — exact seconds (DST-blind)
ymd_hms("2025-03-09 01:00:00", tz = "America/New_York") + ddays(1)
#> 2025-03-10 02:00:00 EDT  (24 exact hours; clock skipped 2-3 AM)

# Interval — anchored span
i <- interval(ymd("2025-01-01"), ymd("2025-12-31"))
i / years(1)        # length in years
i / months(1)       # length in months
ymd("2025-06-15") %within% i   # TRUE
```

**Rule:** Use `period()`s (`days()`, `months()`, `years()`) for
calendar-aware arithmetic ("3 months later"). Use `duration()`s (`ddays()`,
`dweeks()`) for exact-time arithmetic (timestamps, scientific intervals).

---

## %m+% / %m-% — Month-Safe Arithmetic

```r
# Naive +months() can produce NA for month-end dates
ymd("2025-01-31") + months(1)        # 2025-02-31 → NA in some versions

# %m+% / %m-% snap to the last valid day of the target month
ymd("2025-01-31") %m+% months(1)     # 2025-02-28
ymd("2024-01-31") %m-% months(1)     # 2023-12-31
```

Always use `%m+%` / `%m-%` when adding months to a date that might be the
31st (or to Feb 29 leap-year dates).

---

## Time Zones: with_tz() vs force_tz()

```r
ts <- ymd_hms("2025-04-27 14:30:00", tz = "UTC")

# with_tz() — same instant, displayed in another zone (CONVERT)
with_tz(ts, "America/New_York")     # 2025-04-27 10:30:00 EDT (clock changes, instant unchanged)

# force_tz() — change the zone label, keep the wall-clock (RELABEL)
force_tz(ts, "America/New_York")    # 2025-04-27 14:30:00 EDT (clock unchanged, instant moved)
```

**Decision tree:**
- "Convert this UTC timestamp to the user's local time" → `with_tz()`
- "These local timestamps were stored without a zone — assert they were
  Eastern" → `force_tz()`

Use `Sys.timezone()` to detect the system zone; never rely on `Sys.time()`
returning a specific zone in scripts.

---

## Rounding: floor_date() / ceiling_date() / round_date()

```r
ts <- ymd_hms("2025-04-27 14:37:21")

floor_date(ts, "hour")        # 2025-04-27 14:00:00
floor_date(ts, "15 mins")     # 2025-04-27 14:30:00
floor_date(ts, "month")       # 2025-04-01
ceiling_date(ts, "month")     # 2025-05-01
round_date(ts, "10 mins")     # 2025-04-27 14:40:00

# Common pipeline: bin timestamps to a grid for time-series aggregation
events |>
  mutate(bin = floor_date(ts, "1 hour")) |>
  summarise(n = n(), .by = bin)
```

`floor_date()` is the standard for time-series binning — it produces equal-
width bins and aligns to natural boundaries.

---

## Date Sequences and Ranges

```r
# Generate a regular sequence
seq(ymd("2025-01-01"), ymd("2025-12-31"), by = "month")
seq(ymd_hms("2025-01-01 00:00:00"), by = "15 mins", length.out = 96)

# Today, yesterday, n days ago
today()
today() - days(7)
now(tzone = "UTC")
```

---

## Gotchas

| Trap | Fix |
|------|-----|
| `as.Date()` silently returns NA on unrecognised formats | Use `parse_date_time()` with `orders =` and inspect failures |
| `+ months(1)` returns NA for Jan 31 | Use `%m+% months(1)` |
| `with_tz()` vs `force_tz()` confusion | `with_tz()` = convert, `force_tz()` = relabel |
| Default `wday()` makes Sunday day 1 | Pass `week_start = 1` for ISO (Monday) |
| Duration arithmetic crosses DST silently | Use periods (`days()`) for calendar logic, durations (`ddays()`) for exact time |
| `week()` ≠ ISO week | Use `isoweek()` for ISO-8601 week numbering |
| Time-zone-naive `POSIXct` defaults to system zone | Always pass `tz =` explicitly when parsing |
| `floor_date(x, "1 month")` rounds down to the 1st | That's the correct behaviour — for end-of-month use `ceiling_date(x, "month") - days(1)` |
