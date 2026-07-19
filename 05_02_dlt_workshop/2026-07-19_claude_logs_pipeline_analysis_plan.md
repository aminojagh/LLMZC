# Analysis Plan: claude_logs_pipeline

## Connection
pipeline: claude_logs_pipeline
dataset: claude_logs
destination: duckdb

## Profile Summary
| table | rows | key columns | notes |
|-------|------|-------------|-------|
| claude_logs | 3864 | type, session_id, timestamp, cwd, version, message (JSON), tool_use_result (JSON), attachment (JSON) | single flat table, raw JSON preserved for nested fields (max_table_nesting=0), no child tables. 32 distinct sessions, range 2026-06-29 to 2026-07-19. `cwd` contains local filesystem paths (not treated as PII — user's own machine, single-user report). |

## Questions
1. [x] How has daily activity changed over time? → Chart 1
2. [x] How does token usage trend day to day? → Chart 2
3. [x] Which models are used most? → Chart 3
4. [x] Which tools does Claude Code call most often? → Chart 4
5. [ ] Where does Claude Code time go, by project (cwd)?
6. [ ] What does session-level activity (messages, duration) look like?

## Data Gaps
(none)

## Chart 1: Daily Activity Trend
question: How has daily activity changed over time?
type: line
x: timestamp (daily)
y: count of assistant messages
source: claude_logs

```sql
SELECT
    date_trunc('day', timestamp) AS day,
    count(*) AS assistant_messages
FROM claude_logs
WHERE json_extract_string(message, '$.role') = 'assistant'
GROUP BY 1
ORDER BY 1
```

```altair
alt.Chart(df).mark_line(point=True).encode(
    x=alt.X('day:T', title='Day'),
    y=alt.Y('assistant_messages:Q', title='Assistant messages'),
    tooltip=['day:T', 'assistant_messages:Q']
).properties(title='Claude Code Daily Activity')
```

## Chart 2: Daily Token Usage
question: How does token usage trend day to day?
type: line
x: timestamp (daily)
y: sum(tokens), split by input/output
source: claude_logs

```sql
WITH daily AS (
    SELECT
        date_trunc('day', timestamp) AS day,
        sum(try_cast(json_extract(message, '$.usage.output_tokens') AS BIGINT)) AS output_tokens,
        sum(try_cast(json_extract(message, '$.usage.input_tokens') AS BIGINT)) AS input_tokens
    FROM claude_logs
    WHERE json_extract_string(message, '$.role') = 'assistant'
    GROUP BY 1
)
SELECT day, 'output_tokens' AS token_type, output_tokens AS tokens FROM daily
UNION ALL
SELECT day, 'input_tokens' AS token_type, input_tokens AS tokens FROM daily
ORDER BY day
```

```altair
alt.Chart(df).mark_line(point=True).encode(
    x=alt.X('day:T', title='Day'),
    y=alt.Y('tokens:Q', title='Tokens'),
    color=alt.Color('token_type:N', title='Token type'),
    tooltip=['day:T', 'token_type:N', 'tokens:Q']
).properties(title='Daily Token Usage (Input vs Output)')
```

## Chart 3: Model Usage Breakdown
question: Which models are used most?
type: bar
x: count(*)
y: model
source: claude_logs

```sql
SELECT
    json_extract_string(message, '$.model') AS model,
    count(*) AS message_count
FROM claude_logs
WHERE message IS NOT NULL AND json_extract_string(message, '$.model') IS NOT NULL
GROUP BY 1
ORDER BY 2 DESC
```

```altair
alt.Chart(df).mark_bar().encode(
    x=alt.X('message_count:Q', title='Messages'),
    y=alt.Y('model:N', sort='-x', title='Model'),
    tooltip=['model:N', 'message_count:Q']
).properties(title='Model Usage Breakdown')
```

## Chart 4: Tool Usage Frequency
question: Which tools does Claude Code call most often?
type: bar
x: count(*)
y: tool_name
source: claude_logs

```sql
SELECT
    json_extract_string(elem.value, '$.name') AS tool_name,
    count(*) AS call_count
FROM claude_logs, json_each(json_extract(message, '$.content')) AS elem
WHERE json_extract_string(elem.value, '$.type') = 'tool_use'
GROUP BY 1
ORDER BY 2 DESC
```

```altair
alt.Chart(df).mark_bar().encode(
    x=alt.X('call_count:Q', title='Calls'),
    y=alt.Y('tool_name:N', sort='-x', title='Tool'),
    tooltip=['tool_name:N', 'call_count:Q']
).properties(title='Tool Usage Frequency')
```
