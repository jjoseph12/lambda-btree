
import sqlite3
import pandas as pd
from bokeh.models import ColumnDataSource, Select, Div, CustomJS
from bokeh.plotting import figure, show
from bokeh.layouts import row, column, Spacer
from bokeh.palettes import Category10, Category20
from bokeh.io import output_file


# def list_experiment_tables(db_name='src/alchemy_data.db'):
#     """
#     List all experiment tables in the database.
#     """
#     conn = sqlite3.connect(db_name)
#     cursor = conn.cursor()
    
#     # Query all table names
#     cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
#     tables = [row[0] for row in cursor.fetchall()]
    
#     conn.close()

#     # Filter tables with names starting with 'experiment_'
#     experiment_tables = [table for table in tables if table.startswith('experiment_')]
#     print("Experiment tables found:", experiment_tables)
#     return experiment_tables


# def load_data_from_sqlite(db_name, table_name):
#     """
#     Load data from the specified table in the SQLite database.
#     """
#     conn = sqlite3.connect(db_name)
    
#     query = f"""
#     SELECT series_number AS time_series_number, lambda_expression, 
#            ROW_NUMBER() OVER(PARTITION BY series_number ORDER BY id) AS time_step
#     FROM {table_name}
#     """
#     df = pd.read_sql_query(query, conn)
#     conn.close()
    
#     # Calculate cumulative unique entropy per series
#     df['unique_entropy'] = df.groupby('time_series_number')['lambda_expression'].transform(cumulative_unique_counts)
    
#     return df


# def cumulative_unique_counts(x):
#     """
#     Calculate cumulative unique counts for a series.
#     """
#     seen = set()
#     counts = []
#     for item in x:
#         seen.add(item)
#         counts.append(len(seen))
#     return counts


# # Database and Initial Table
# db_name = 'src/alchemy_data.db'
# experiment_tables = list_experiment_tables(db_name)

# if not experiment_tables:
#     raise ValueError(f"No experiment tables found in the database: {db_name}")

# # Load data from the first experiment table as the default
# current_table = experiment_tables[0]
# df = load_data_from_sqlite(db_name, current_table)

# # Split data by series for visualization
# data_sources = {}
# source2_sources = {}
# max_time_step = df['time_step'].max()

# # Group by series and create ColumnDataSource for each
# for series_num, series_df in df.groupby('time_series_number'):
#     data_sources[f"Series {series_num}"] = ColumnDataSource(data=dict(
#         time_step=series_df['time_step'],
#         unique_entropy=series_df['unique_entropy'],
#         lambda_expression=series_df['lambda_expression']
#     ))

#     # Data for second plot (unique lambda expressions at each time step)
#     lambda_x = series_df['time_step'].unique()
#     lambda_y = series_df.groupby('time_step')['lambda_expression'].nunique().values
#     source2_sources[f"Series {series_num}"] = ColumnDataSource(data=dict(x=lambda_x, y=lambda_y))

# csv_options = list(data_sources.keys())

# if not csv_options:
#     raise ValueError("No valid series data found in the table.")

# # Initial data source for the second plot
# source2 = source2_sources[csv_options[0]]

# # Div elements for UI
# title_div = Div(text=f"<h1 style='margin-bottom: 20px;'><b>Lambda Expression Analysis Tool</b> (Table: {current_table})</h1>", width=400)
# info_div = Div(text="<p style='margin-top: 20px;'>Select a point on the green graph to see its data here.</p>", width=250)

# # Experiment table selection widget
# table_select = Select(title="Select Experiment Table", value=current_table, options=experiment_tables, width=300)

# # Simulation selection widget
# simulation_select = Select(title="Select Series", value=csv_options[0], options=csv_options, width=200)

# # Plot 1: Unique entropy over time for all series
# p1 = figure(title="Unique Entropy Over Time", x_axis_label="Time", y_axis_label="Unique Entropy",
#             tools="tap", width=700, height=400, x_range=(0, max_time_step))

# num_files = len(data_sources)
# if num_files <= 10:
#     colors = Category10[10]
# else:
#     colors = Category20[20]

# # Add a line for each series in the first plot
# for idx, (series_name, source) in enumerate(data_sources.items()):
#     color = colors[idx % len(colors)]
#     p1.line('time_step', 'unique_entropy', source=source, line_width=2, legend_label=series_name, color=color)

# p1.legend.click_policy = "hide"

# # Plot 2: Number of unique lambda expressions at each time step for selected series
# p2 = figure(title="Lambda Expression Analysis", x_axis_label="Time Step",
#             y_axis_label="Number of Unique Expressions", tools="tap", width=700, height=400)
# p2.line('x', 'y', source=source2, line_width=2, line_color="green")
# p2.scatter('x', 'y', source=source2, size=6, color="green", alpha=0.6)

# # JS callback for updating the data sources based on selected series
# update_callback = CustomJS(args=dict(source2=source2, source2_sources=source2_sources), code="""
#     var selected_file = cb_obj.value;
#     source2.data = source2_sources[selected_file].data;
#     source2.change.emit();
# """)
# simulation_select.js_on_change('value', update_callback)

# # JS callback for updating table selection
# update_table_callback = CustomJS(args=dict(table_select=table_select), code="""
#     window.location.reload();  // Reload the page when a different table is selected
# """)
# table_select.js_on_change('value', update_table_callback)

# # JS callback for showing data when selecting a single point on the green graph
# green_graph_callback = CustomJS(args=dict(source=source2, info_div=info_div), code="""
#     var selected_indices = source.selected.indices;
#     if (selected_indices.length > 0) {
#         var last_selected_index = selected_indices[selected_indices.length - 1];
#         source.selected.indices = [last_selected_index];  // Clear old points and keep the last one only

#         var x_value = source.data['x'][last_selected_index];
#         var y_value = source.data['y'][last_selected_index];
#         var info_text = '<p style="margin-top: 20px;"><b>Selected Point Info:</b><br>';
#         info_text += 'Time Step: ' + x_value + ', Number of Unique Expressions: ' + y_value + '</p>';
#         info_div.text = info_text;
#     } else {
#         info_div.text = '<p style="margin-top: 20px;'>Select a point on the green graph to see its data here.</p>';
#     }
#     source.change.emit();  // Emit change to update the visualization
# """)
# source2.selected.js_on_change('indices', green_graph_callback)

# # JS callback for updating data sources based on experiment table and series selection
# update_experiment_callback = CustomJS(args=dict(data_sources=data_sources, source2_sources=source2_sources, info_div=info_div), code="""
#     var experiment_table = table_select.value;
#     var series = simulation_select.value;

#     // Update the title to reflect the current experiment table
#     title_div.text = <h1 style='margin-bottom: 20px;'><b>Lambda Expression Analysis Tool</b> (Table: ${experiment_table})</h1>;

#     // Check if the selected series exists in the data_sources for the new experiment
#     var series_key = ${experiment_table}_${series};
#     if (data_sources[series_key]) {
#         // Update p1 data source (Unique Entropy Over Time)
#         p1_source.data = data_sources[series_key].data;

#         // Update p2 data source (Lambda Expression Analysis)
#         source2.data = source2_sources[series_key].data;

#         // Reset the info div
#         info_div.text = "<p style='margin-top: 20px;'>Select a point on the green graph to see its data here.</p>";

#         // Emit changes to refresh plots
#         p1_source.change.emit();
#         source2.change.emit();
#     } else {
#         console.error(Data for series ${series} in experiment table ${experiment_table} not found.);
#     }
# """);

# # Attach the callback to the table_select widget
# table_select.js_on_change('value', update_experiment_callback);
# simulation_select.js_on_change('value', update_experiment_callback);

# # Layout: Stack graphs vertically and include experiment/series selection
# layout = column(
#     title_div,
#     row(table_select, Spacer(width=50), simulation_select, Spacer(width=50), info_div),
#     Spacer(height=20),
#     p1,  # First graph: Unique Entropy Over Time
#     Spacer(height=50),
#     p2   # Second graph: Lambda Expression Analysis
# )

# # Show the result
# output_file("lambda_expression_analysis.html")
# show(layout)

import sqlite3
import pandas as pd
from bokeh.models import ColumnDataSource, Select, Div, CustomJS
from bokeh.plotting import figure, show
from bokeh.layouts import row, column, Spacer
from bokeh.palettes import Category10, Category20
from bokeh.io import output_file


def list_experiment_tables(db_name='src/alchemy_data.db'):
    """
    List all experiment tables in the database.
    """
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    # Query all table names
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    
    conn.close()

    # Filter tables with names starting with 'experiment_'
    experiment_tables = [table for table in tables if table.startswith('experiment_')]
    print("Experiment tables found:", experiment_tables)
    return experiment_tables


def load_data_from_sqlite(db_name, table_name):
    """
    Load data from the specified table in the SQLite database.
    """
    conn = sqlite3.connect(db_name)
    
    query = f"""
    SELECT series_number AS time_series_number, lambda_expression, 
           ROW_NUMBER() OVER(PARTITION BY series_number ORDER BY id) AS time_step
    FROM {table_name}
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    # Calculate cumulative unique entropy per series
    df['unique_entropy'] = df.groupby('time_series_number')['lambda_expression'].transform(cumulative_unique_counts)
    
    return df


def cumulative_unique_counts(x):
    """
    Calculate cumulative unique counts for a series.
    """
    seen = set()
    counts = []
    for item in x:
        seen.add(item)
        counts.append(len(seen))
    return counts


# Database and Initial Table
db_name = 'src/alchemy_data.db'
experiment_tables = list_experiment_tables(db_name)

if not experiment_tables:
    raise ValueError(f"No experiment tables found in the database: {db_name}")

# Load data from the first experiment table as the default
current_table = experiment_tables[0]
df = load_data_from_sqlite(db_name, current_table)

# Data Sources for Visualization
data_sources = {}
source2_sources = {}
max_time_step = df['time_step'].max()

# Prepare data sources
def prepare_data_sources(df, current_table):
    data_sources = {}
    source2_sources = {}
    max_time_step = df['time_step'].max()

    for series_num, series_df in df.groupby('time_series_number'):
        key = f"{current_table}_Series {series_num}"
        data_sources[key] = ColumnDataSource(data=dict(
            time_step=series_df['time_step'],
            unique_entropy=series_df['unique_entropy'],
            lambda_expression=series_df['lambda_expression']
        ))

        lambda_x = series_df['time_step'].unique()
        lambda_y = series_df.groupby('time_step')['lambda_expression'].nunique().values
        source2_sources[key] = ColumnDataSource(data=dict(x=lambda_x, y=lambda_y))

    return data_sources, source2_sources, max_time_step


data_sources, source2_sources, max_time_step = prepare_data_sources(df, current_table)

csv_options = [f"Series {series_num}" for series_num in df['time_series_number'].unique()]

if not csv_options:
    raise ValueError("No valid series data found in the table.")

# Initial Data Source
source2 = source2_sources[f"{current_table}_{csv_options[0]}"]

# Div Elements for UI
title_div = Div(text=f"<h1 style='margin-bottom: 20px;'><b>Lambda Expression Analysis Tool</b> (Table: {current_table})</h1>", width=400)
info_div = Div(text="<p style='margin-top: 20px;'>Select a point on the green graph to see its data here.</p>", width=250)

# Experiment Table Selection Widget
table_select = Select(title="Select Experiment Table", value=current_table, options=experiment_tables, width=300)

# Simulation Selection Widget
simulation_select = Select(title="Select Series", value=csv_options[0], options=csv_options, width=200)

# Plot 1: Unique Entropy Over Time
p1 = figure(title="Unique Entropy Over Time", x_axis_label="Time", y_axis_label="Unique Entropy",
            tools="tap", width=700, height=400, x_range=(0, max_time_step))

# Plot 2: Lambda Expression Analysis
p2 = figure(title="Lambda Expression Analysis", x_axis_label="Time Step",
            y_axis_label="Number of Unique Expressions", tools="tap", width=700, height=400)

# Add Lines for Each Series
for idx, (key, source) in enumerate(data_sources.items()):
    color = Category10[10][idx % 10]
    if current_table in key:
        p1.line('time_step', 'unique_entropy', source=source, line_width=2, legend_label=key.split('_')[1], color=color)

p2.line('x', 'y', source=source2, line_width=2, line_color="green")
p2.scatter('x', 'y', source=source2, size=6, color="green", alpha=0.6)

# Callback to Reload Data when Table or Series is Selected
def update_data_callback(attr, old, new):
    global current_table, csv_options, data_sources, source2_sources

    # Update the table if needed
    if attr == 'value' and table_select.value != current_table:
        current_table = table_select.value
        df = load_data_from_sqlite(db_name, current_table)
        data_sources, source2_sources, max_time_step = prepare_data_sources(df, current_table)

        # Update options for series dropdown
        csv_options = [f"Series {series_num}" for series_num in df['time_series_number'].unique()]
        simulation_select.options = csv_options
        simulation_select.value = csv_options[0]

        # Update plot sources
        p1.renderers = []
        for idx, (key, source) in enumerate(data_sources.items()):
            if current_table in key:
                color = Category10[10][idx % 10]
                p1.line('time_step', 'unique_entropy', source=source, line_width=2, legend_label=key.split('_')[1], color=color)

    # Update the selected series
    selected_series_key = f"{current_table}_{simulation_select.value}"
    if selected_series_key in source2_sources:
        source2.data = source2_sources[selected_series_key].data

    # Update the title
    title_div.text = f"<h1 style='margin-bottom: 20px;'><b>Lambda Expression Analysis Tool</b> (Table: {current_table})</h1>"

# Attach Callbacks
table_select.on_change('value', update_data_callback)
simulation_select.on_change('value', update_data_callback)

# Layout
layout = column(
    title_div,
    row(table_select, Spacer(width=50), simulation_select, Spacer(width=50), info_div),
    Spacer(height=20),
    p1,
    Spacer(height=50),
    p2
)

# Show the Result
output_file("lambda_expression_analysis.html")
show(layout)
