# logslice

A fast log filtering and aggregation tool that lets you query structured logs from the terminal using a simple DSL.

---

## Installation

```bash
pip install logslice
```

Or install from source:

```bash
git clone https://github.com/yourname/logslice.git && cd logslice && pip install .
```

---

## Usage

Pipe logs into `logslice` and query them using the built-in DSL:

```bash
# Filter logs by level and time range
cat app.log | logslice 'level == "error" and timestamp > "2024-01-15T08:00:00"'

# Aggregate log counts by status code
cat access.log | logslice 'group_by(status) | count()'

# Filter and select specific fields
logslice -f app.log 'service == "auth" | select(timestamp, message, user_id)'
```

**Read directly from a file:**

```bash
logslice -f /var/log/app.log 'level in ["warn", "error"]'
```

**Output as JSON or table:**

```bash
logslice -f app.log --format table 'level == "error"'
```

---

## Features

- Supports JSON and logfmt structured log formats
- Simple, readable DSL for filtering and aggregation
- Streams large log files without loading them fully into memory
- Outputs results as plain text, JSON, or formatted tables

---

## License

MIT © 2024 [yourname](https://github.com/yourname)