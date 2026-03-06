# SQLite Patterns and Comparisons

## Python vs SQL: Side-by-Side

**Task:** Find error types and their counts from test results.

### Python Approach (What agents default to):
```python
import json
from collections import defaultdict

# Load and parse
with open('test-results.json') as f:
    data = json.load(f)

# Custom aggregation logic
errors_by_type = defaultdict(int)
for record in data:
    if record['status'] == 'failed' and record['error_message']:
        # Extract error type (custom parsing)
        error_type = record['error_message'].split(':')[0]
        errors_by_type[error_type] += 1

# Sort and display (more custom code)
sorted_errors = sorted(errors_by_type.items(), key=lambda x: x[1], reverse=True)
for error_type, count in sorted_errors:
    print(f"{error_type}: {count}")
```

### SQLite Approach (Simpler):
```bash
# Load once
sqlite3 data.db <<EOF
CREATE TABLE IF NOT EXISTS results (status TEXT, error_message TEXT);
.import --json test-results.json results
EOF

# Query (SQL does aggregation)
sqlite3 data.db "
  SELECT substr(error_message, 1, instr(error_message, ':')-1) as error_type,
         COUNT(*) as count
  FROM results
  WHERE status='failed' AND error_message IS NOT NULL
  GROUP BY error_type
  ORDER BY count DESC
"
```

With Python, parsing/aggregation logic must be rewritten for each query. With SQL, declare what is needed and query the same data repeatedly.

## Real-World Examples

### Example 1: Test Analysis (224 results)
**Without SQLite:** Python code, loaded to memory, custom aggregation logic, data discarded.

**With SQLite:**
```sql
CREATE TABLE test_runs (test_name TEXT, status TEXT, duration_ms INT, run_id TEXT);
-- Load once
INSERT INTO test_runs SELECT ...;

-- Query many times (no re-processing)
-- Find flaky tests
SELECT test_name,
       SUM(CASE WHEN status='pass' THEN 1 ELSE 0 END) as passes,
       SUM(CASE WHEN status='fail' THEN 1 ELSE 0 END) as fails
FROM test_runs
GROUP BY test_name
HAVING passes > 0 AND fails > 0;

-- Slowest tests
SELECT test_name, AVG(duration_ms) FROM test_runs GROUP BY test_name ORDER BY AVG(duration_ms) DESC LIMIT 10;
```

### Example 2: Error Correlation (3 log files)
**Without SQLite:** Used jq/grep/pipes, re-processed for each question, manual timestamp correlation.

**With SQLite:**
```sql
CREATE TABLE errors (timestamp TEXT, service TEXT, error_type TEXT, message TEXT);
-- Load all 3 files once
INSERT INTO errors SELECT ...;

-- Find cross-service failures (JOIN is easier than grep)
SELECT e1.timestamp, e1.service, e2.service
FROM errors e1 JOIN errors e2
ON datetime(e1.timestamp) BETWEEN datetime(e2.timestamp, '-5 minutes') AND datetime(e2.timestamp, '+5 minutes')
WHERE e1.service != e2.service;

-- Error frequency
SELECT error_type, COUNT(*) FROM errors GROUP BY error_type ORDER BY COUNT(*) DESC;
```

### Example 3: File Processing State (50 files)
**Without SQLite:** Custom JSON parsing code, manual state updates, custom query logic.

**With SQLite:**
```sql
CREATE TABLE files (name TEXT PRIMARY KEY, status TEXT, error TEXT, completed_at TEXT);

-- Initialize
INSERT INTO files (name, status) VALUES ('file1.txt', 'pending');

-- Update state
UPDATE files SET status='completed', completed_at=datetime('now') WHERE name='file1.txt';

-- Queries (no custom code)
SELECT COUNT(*) FROM files WHERE status='completed';
SELECT * FROM files WHERE status='failed';
SELECT * FROM files WHERE status='pending' LIMIT 1;  -- next file
```

Note: For only 50 files with simple queries, JSON is actually fine. Apply SQLite when complex queries or >100 files are involved.
