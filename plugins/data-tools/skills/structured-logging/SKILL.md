---
name: structured-logging
description: This skill should be used when the user asks to "analyze data with SQLite", "query logs", "find patterns in test results", or "correlate errors across files". Automatically activates when parsing large output (>100 lines), correlating data from multiple sources, tracking state across operations, aggregating results (counts, averages, grouping), or querying the same dataset multiple times. Not for tiny datasets (<50 records) with a single simple query.
---

# SQLite for Structured Data

## Decision Check

Before writing any data analysis code, evaluate:

1. Will the data be queried more than once? -> **Use SQLite**
2. Are GROUP BY, COUNT, AVG, or JOIN operations needed? -> **Use SQLite**
3. Is custom Python/jq parsing code about to be written? -> **Use SQLite instead**
4. Is the dataset >100 records? -> **Use SQLite**

If the answer to any question above is YES, use SQLite. Do not write custom parsing code.

```bash
# Custom code for every query:
cat data.json | jq '.[] | select(.status=="failed")' | jq -r '.error_type' | sort | uniq -c

# SQL does the work:
sqlite3 data.db "SELECT error_type, COUNT(*) FROM errors WHERE status='failed' GROUP BY error_type"
```

## Core Principle

**SQLite is just a file** -- no server, no setup, zero dependencies. Apply it when custom parsing code would otherwise be written or data would be re-processed for each query.

## When to Use SQLite

Apply when ANY of these conditions hold:

- **>100 records** -- JSON/grep becomes unwieldy
- **Multiple aggregations** -- GROUP BY, COUNT, AVG needed
- **Multiple queries** -- Follow-up questions about the same data are expected
- **Correlation needed** -- Joining data from multiple sources
- **State tracking** -- Queryable progress/status over time is needed

## When NOT to Use SQLite

Skip SQLite when ALL of these are true:

- <50 records total
- Single simple query
- No aggregations needed
- No follow-up questions expected

For tiny datasets with simple access, JSON/grep is fine.

## Red Flags -- Use SQLite Instead

STOP and use SQLite when about to:

- Write Python/Node code to parse JSON/CSV for analysis
- Run the same jq/grep command with slight variations
- Write custom aggregation logic (COUNT, AVG, GROUP BY in code)
- Manually correlate data by timestamps or IDs
- Create temp files to store intermediate results
- Process the same data multiple times for different questions

**All of these mean: Load into SQLite once, query with SQL.**

## The Threshold

| Scenario | Tool | Why |
|----------|------|-----|
| 50 test results, one-time summary | Python/jq | Fast, appropriate |
| 200+ test results, find flaky tests | **SQLite** | GROUP BY simpler than code |
| 3 log files, correlate by time | **SQLite** | JOIN simpler than manual grep |
| Track 1000+ file processing state | **SQLite** | Queries beat JSON parsing |

**Rule of thumb:** If parsing code is being written or data is being re-processed, use SQLite instead.

## Available Tools

### sqlite3 (always available)

```bash
sqlite3 ~/.claude-logs/project.db
```

### sqlite-utils (optional, simplifies import)

Check availability before use:

```bash
command -v sqlite-utils >/dev/null 2>&1 && echo "available" || echo "not installed"
```

If sqlite-utils is available:
```bash
sqlite-utils insert data.db table_name data.json --pk=id
sqlite-utils query data.db "SELECT * FROM table"
```

If sqlite-utils is NOT available, fall back to sqlite3 with manual import:
```bash
sqlite3 data.db <<EOF
CREATE TABLE IF NOT EXISTS results (status TEXT, error_message TEXT);
.mode json
.import data.json results
EOF
```

Alternatively, install sqlite-utils: `uv tool install sqlite-utils`

## Quick Start

### Store Location
```bash
~/.claude-logs/<project-name>.db  # Persists across sessions
```

### Basic Workflow
```bash
# 1. Connect
PROJECT=$(basename $(git rev-parse --show-toplevel 2>/dev/null || pwd))
sqlite3 ~/.claude-logs/$PROJECT.db

# 2. Create table (first time)
CREATE TABLE results (
  id INTEGER PRIMARY KEY,
  name TEXT,
  status TEXT,
  duration_ms INTEGER
);

# 3. Load data
INSERT INTO results (name, status, duration_ms)
SELECT json_extract(value, '$.name'),
       json_extract(value, '$.status'),
       json_extract(value, '$.duration_ms')
FROM json_each(readfile('data.json'));

# 4. Query (SQL does the work)
SELECT status, COUNT(*), AVG(duration_ms)
FROM results
GROUP BY status;
```

## Key Mindset Shift

**From:** "Process data once and done"
**To:** "Make data queryable"

Benefits:
- Follow-up questions require no re-processing -- data is already loaded
- Different analyses run instantly against the same dataset
- State persists across sessions
- SQL handles complexity -- less custom code needed

## Additional Resources

- **`./references/patterns.md`** -- Python vs SQL side-by-side comparison and real-world examples (test analysis, error correlation, file processing state)
