import marimo

__generated_with = "0.14.5"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import altair as alt
    import dlt
    return alt, dlt, mo


@app.cell
def _(dlt):
    pipeline = dlt.attach(
        "agent_logs_pipeline", destination="playground", dataset_name="agent_logs"
    )
    dataset = pipeline.dataset()
    return (dataset,)


@app.cell
def _(mo):
    mo.md("# Agent Logs Usage Report")
    return


@app.cell
def _(mo):
    mo.md("## Daily Activity Trend")
    return


@app.cell
def _(dataset):
    df_chart1 = dataset("""
        SELECT
            date_trunc('day', timestamp) AS day,
            count(*) AS assistant_messages
        FROM logs
        WHERE type = 'assistant'
        GROUP BY 1
        ORDER BY 1
    """).df()
    return (df_chart1,)


@app.cell
def _(alt, df_chart1, mo):
    _chart = alt.Chart(df_chart1).mark_line(point=True).encode(
        x=alt.X("day:T", title="Day"),
        y=alt.Y("assistant_messages:Q", title="Assistant messages"),
        tooltip=["day:T", "assistant_messages:Q"]
    ).properties(title="Agent Logs Daily Activity")
    _chart
    return


@app.cell
def _(mo):
    mo.md("## Daily Token Usage")
    return


@app.cell
def _(dataset):
    df_chart2 = dataset("""
        WITH daily AS (
            SELECT
                date_trunc('day', timestamp) AS day,
                sum(usage__output_tokens) AS output_tokens,
                sum(usage__input_tokens) AS input_tokens
            FROM logs
            WHERE type = 'assistant'
            GROUP BY 1
        )
        SELECT day, 'output_tokens' AS token_type, output_tokens AS tokens FROM daily
        UNION ALL
        SELECT day, 'input_tokens' AS token_type, input_tokens AS tokens FROM daily
        ORDER BY day
    """).df()
    return (df_chart2,)


@app.cell
def _(alt, df_chart2, mo):
    _chart = alt.Chart(df_chart2).mark_line(point=True).encode(
        x=alt.X("day:T", title="Day"),
        y=alt.Y("tokens:Q", title="Tokens"),
        color=alt.Color("token_type:N", title="Token type"),
        tooltip=["day:T", "token_type:N", "tokens:Q"]
    ).properties(title="Daily Token Usage (Input vs Output)")
    _chart
    return


@app.cell
def _(mo):
    mo.md("## Model Usage Breakdown")
    return


@app.cell
def _(dataset):
    df_chart3 = dataset("""
        SELECT
            message__model AS model,
            count(*) AS message_count
        FROM logs
        WHERE message__model IS NOT NULL
        GROUP BY 1
        ORDER BY 2 DESC
    """).df()
    return (df_chart3,)


@app.cell
def _(alt, df_chart3, mo):
    _chart = alt.Chart(df_chart3).mark_bar().encode(
        x=alt.X("message_count:Q", title="Messages"),
        y=alt.Y("model:N", sort="-x", title="Model"),
        tooltip=["model:N", "message_count:Q"]
    ).properties(title="Model Usage Breakdown")
    _chart
    return


@app.cell
def _(mo):
    mo.md("## Tool Usage Frequency")
    return


@app.cell
def _(dataset):
    df_chart4 = dataset("""
        SELECT
            name AS tool_name,
            count(*) AS call_count
        FROM logs__message__content
        WHERE name IS NOT NULL
        GROUP BY 1
        ORDER BY 2 DESC
    """).df()
    return (df_chart4,)


@app.cell
def _(alt, df_chart4, mo):
    _chart = alt.Chart(df_chart4).mark_bar().encode(
        x=alt.X("call_count:Q", title="Calls"),
        y=alt.Y("tool_name:N", sort="-x", title="Tool"),
        tooltip=["tool_name:N", "call_count:Q"]
    ).properties(title="Tool Usage Frequency")
    _chart
    return


if __name__ == "__main__":
    app.run()
