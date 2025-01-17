from bokeh.models import ColumnDataSource, Legend, LegendItem, TapTool
from bokeh.plotting import figure, curdoc
from bokeh.layouts import column
import sqlite3
import pandas as pd
import numpy as np

# Globals
db_name = 'src/alchemy_data.db'
data_map = {}  # Store data for each experiment for dynamic updates
source2 = ColumnDataSource(data=dict(time_step=[], unique_expressions=[]))  # For second graph

def list_experiment_tables(db_name):
    conn = sqlite3.connect(db_name)
    try:
        query = "SELECT name FROM sqlite_master WHERE type='table'"
        tables = pd.read_sql_query(query, conn)['name'].tolist()
        experiment_tables = [table for table in tables if table.startswith('experiment_')]
    finally:
        conn.close()
    return experiment_tables

def load_data_from_sqlite(db_name, table_name):
    conn = sqlite3.connect(db_name)
    try:
        query = f"""
        SELECT id, lambda_expression 
        FROM {table_name}
        ORDER BY id
        """
        df = pd.read_sql_query(query, conn)
        # Calculate unique entropy
        df['unique_entropy'] = [len(set(df['lambda_expression'].iloc[:i+1])) 
                              for i in range(len(df))]
        # Calculate number of unique expressions
        df['unique_expressions'] = df['lambda_expression'].apply(lambda x: len(set(x.split())))  # Adjust as needed
        return df
    except Exception as e:
        print(f"Database error: {e}")
        return pd.DataFrame()
    finally:
        conn.close()

# Get experiment tables
experiment_tables = list_experiment_tables(db_name)
if not experiment_tables:
    raise ValueError(f"No experiment tables found in the database '{db_name}'")

# Plot 1 (Unique Entropy Over Time)
p1 = figure(
    title="Unique Entropy Over Time (All Experiments)",
    x_axis_label="Time",
    y_axis_label="Unique Entropy",
    width=800,
    height=400,
    tools="tap"  # Tap tool for selection
)

# Plot 2 (Number of Unique Expressions Over Time)
p2 = figure(
    title="Number of Unique Expressions Over Time (Selected Experiment)",
    x_axis_label="Time",
    y_axis_label="Number of Unique Expressions",
    width=800,
    height=400
)
p2.line('time_step', 'unique_expressions', source=source2, line_width=2, color="green")  # Add a blank line initially

# Add lines and legends for all experiments in Plot 1
legend_items1 = []
colors = ['blue', 'green', 'red', 'purple', 'orange', 'magenta']  # Add more colors if needed
line_renderers = []  # Store renderers for matching taps
line_to_table_map = {}  # Map renderers to experiment tables

for idx, table in enumerate(experiment_tables):
    df = load_data_from_sqlite(db_name, table)
    if not df.empty:
        # Data for Plot 1
        source1 = ColumnDataSource(data=dict(
            time_step=df['id'].tolist(),
            unique_entropy=df['unique_entropy'].tolist(),
        ))
        # Store unique_expressions data for dynamic updates
        data_map[table] = dict(
            time_step=df['id'].tolist(),
            unique_expressions=df['unique_expressions'].tolist()
        )

        # Add line to Plot 1
        color = colors[idx % len(colors)]
        line1 = p1.line('time_step', 'unique_entropy', source=source1, line_width=2, color=color, name=table)
        line_renderers.append(line1)
        line_to_table_map[line1] = table  # Map renderer to its experiment table
        legend_items1.append(LegendItem(label=table, renderers=[line1]))

# Add legend to Plot 1
legend1 = Legend(items=legend_items1)
p1.add_layout(legend1, 'right')
p1.legend.click_policy = "hide"

# Tap tool callback to update Plot 2
def update_second_plot(event):
    tap_x = event.x
    tap_y = event.y
    print(f"Tap coordinates: x={tap_x}, y={tap_y}")

    closest_renderer = None
    min_distance = float('inf')

    for renderer in line_renderers:
        line_source = renderer.data_source
        x_vals = np.array(line_source.data['time_step'])
        y_vals = np.array(line_source.data['unique_entropy'])

        # Check if the line is visible
        if renderer.visible:
            distances = np.sqrt((x_vals - tap_x)**2 + (y_vals - tap_y)**2)
            closest_point_distance = distances.min()

            if closest_point_distance < min_distance:
                min_distance = closest_point_distance
                closest_renderer = renderer

    if closest_renderer and closest_renderer in line_to_table_map:
        selected_table = line_to_table_map[closest_renderer]
        print(f"Selected experiment: {selected_table}")
        source2.data = data_map[selected_table]  # Update the second plot
    else:
        print("No line was selected.")

# Attach TapTool event
p1.on_event('tap', update_second_plot)

# Layout (Stack both plots vertically)
layout = column(p1, p2)

curdoc().add_root(layout)
curdoc().title = "Lambda Expression Analysis Tool"
