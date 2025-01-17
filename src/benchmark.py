import sqlite3
import pandas as pd
import time
from bokeh.models import ColumnDataSource
from bokeh.plotting import figure, show, output_notebook
from bokeh.layouts import column, row
from bokeh.io import output_file

output_notebook()

# Define file paths and experiment IDs
csv_files = {
    "1000-series": "1000-series.csv",
    "100k": "100k.csv",
    "1m": "1m.csv"
}

sql_experiment_ids = {
    "1000-series": 1,
    "100k": 2,
    "1m": 3
}

db_path = 'alchemy_data.db'  # Path to your SQL database

# Function to load data from CSV and measure time
def load_data_from_csv(file_path):
    start_time = time.time()
    df = pd.read_csv(file_path)
    
    # Add a 'time_step' column to simulate row numbering within each series
    df['time_step'] = df.groupby('time_series_number').cumcount() + 1
    
    load_time = time.time() - start_time
    print(f"CSV '{file_path}' Loading Time: {load_time:.4f} seconds")
    return df, load_time

# Function to load data from SQL based on experiment_id and measure time
def load_data_from_sqlite(db_name, experiment_id):
    conn = sqlite3.connect(db_name)
    query = f"""
    SELECT series_number AS time_series_number, lambda_expression,
           ROW_NUMBER() OVER(PARTITION BY series_number ORDER BY id) AS time_step
    FROM alchemy_data
    WHERE experiment_id = {experiment_id}
    """
    start_time = time.time()
    df = pd.read_sql_query(query, conn)
    conn.close()
    load_time = time.time() - start_time
    print(f"SQL Experiment ID '{experiment_id}' Loading Time: {load_time:.4f} seconds")
    return df, load_time

# Function to prepare data for plotting in Bokeh
def prepare_data_sources(df):
    data_sources = {}
    max_time_step = df['time_step'].max()
    for series_num, series_df in df.groupby('time_series_number'):
        data_sources[f"Series {series_num}"] = ColumnDataSource(data=dict(
            time_step=series_df['time_step'],
            unique_entropy=series_df['lambda_expression']
        ))
    return data_sources, max_time_step

# Function to plot data and measure plotting time
def plot_data(data_sources, max_time_step, title="Unique Entropy Over Time"):
    start_time = time.time()
    
    p = figure(title=title, x_axis_label="Time", y_axis_label="Unique Entropy",
               tools="tap", width=500, height=400, x_range=(0, max_time_step))
    
    colors = ["blue", "green", "red"]  # Adjust as needed
    for idx, (series_name, source) in enumerate(data_sources.items()):
        color = colors[idx % len(colors)]
        p.line('time_step', 'unique_entropy', source=source, line_width=2, legend_label=series_name, color=color)
    
    p.legend.location = "top_left"
    p.legend.click_policy = "hide"
    
    plot_time = time.time() - start_time
    print(f"{title} Plotting Time: {plot_time:.4f} seconds")
    return p, plot_time

# Benchmarking function for each source type (CSV and SQL)
def benchmark_data_sources():
    results = []
    plots = []

    # Benchmark for each CSV file
    for name, file_path in csv_files.items():
        print(f"\nBenchmarking CSV File: {file_path}")
        df_csv, csv_load_time = load_data_from_csv(file_path)
        data_sources_csv, max_time_step_csv = prepare_data_sources(df_csv)
        p_csv, csv_plot_time = plot_data(data_sources_csv, max_time_step_csv, title=f"{name} CSV Plotting")
        results.append((name, 'CSV', csv_load_time, csv_plot_time))
        plots.append(p_csv)

    # Benchmark for each SQL experiment
    for name, experiment_id in sql_experiment_ids.items():
        print(f"\nBenchmarking SQL Experiment ID: {experiment_id}")
        df_sql, sql_load_time = load_data_from_sqlite(db_path, experiment_id)
        data_sources_sql, max_time_step_sql = prepare_data_sources(df_sql)
        p_sql, sql_plot_time = plot_data(data_sources_sql, max_time_step_sql, title=f"{name} SQL Plotting")
        results.append((name, 'SQL', sql_load_time, sql_plot_time))
        plots.append(p_sql)

    # Output benchmark results
    print("\nBenchmark Results:")
    print(f"{'Condition':<15} {'Source':<10} {'Load Time (s)':<15} {'Plot Time (s)':<15} {'Total Time (s)':<15}")
    for name, source_type, load_time, plot_time in results:
        total_time = load_time + plot_time
        print(f"{name:<15} {source_type:<10} {load_time:<15.4f} {plot_time:<15.4f} {total_time:<15.4f}")

    # Display plots side-by-side for comparison
    show(column(*[row(plots[i], plots[i + len(csv_files)]) for i in range(len(csv_files))]))

# Run the benchmark and display plots
benchmark_data_sources()
