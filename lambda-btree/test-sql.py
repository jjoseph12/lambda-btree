import sqlite3
import pandas as pd
from bokeh.models import ColumnDataSource, Select, Div, CustomJS
from bokeh.plotting import figure, show
from bokeh.layouts import row, column, Spacer
from bokeh.palettes import Category10, Category20
from bokeh.io import output_file

import sqlite3
import pandas as pd

def load_data_from_sqlite(db_name='src/alchemy_data.db'):
    conn = sqlite3.connect(db_name)
    
    query = """
    SELECT series_number AS time_series_number, lambda_expression, 
           ROW_NUMBER() OVER(PARTITION BY series_number ORDER BY id) AS time_step
    FROM alchemy_data
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    # Calculate cumulative unique entropy per series
    df['unique_entropy'] = df.groupby('time_series_number')['lambda_expression'].transform(cumulative_unique_counts)
    
    return df

# Function to calculate cumulative unique counts
def cumulative_unique_counts(x):
    seen = set()
    counts = []
    for item in x:
        seen.add(item)
        counts.append(len(seen))
    return counts

# Load data from SQLite database
df = load_data_from_sqlite()

# Split data by series for visualization
data_sources = {}
source2_sources = {}
max_time_step = df['time_step'].max()

# Group by series and create ColumnDataSource for each
for series_num, series_df in df.groupby('time_series_number'):
    data_sources[f"Series {series_num}"] = ColumnDataSource(data=dict(
        time_step=series_df['time_step'],
        unique_entropy=series_df['unique_entropy'],
        lambda_expression=series_df['lambda_expression']
    ))

    # Data for second plot (unique lambda expressions at each time step)
    lambda_x = series_df['time_step'].unique()
    lambda_y = series_df.groupby('time_step')['lambda_expression'].nunique().values
    source2_sources[f"Series {series_num}"] = ColumnDataSource(data=dict(x=lambda_x, y=lambda_y))

csv_options = list(data_sources.keys())

# Initial data source for the second plot
source2 = source2_sources[csv_options[0]]

# Div elements for UI
title_div = Div(text="<h1 style='margin-bottom: 20px;'><b>Lambda Expression Analysis Tool</b></h1>", width=400)
info_div = Div(text="<p style='margin-top: 20px;'>Select a point on the green graph to see its data here.</p>", width=250)

# Simulation selection widget
simulation_select = Select(title="Select Series", value=csv_options[0], options=csv_options, width=200)

# Plot 1: Unique entropy over time for all series
p1 = figure(title="Unique Entropy Over Time", x_axis_label="Time", y_axis_label="Unique Entropy",
            tools="tap", width=700, height=400, x_range=(0, max_time_step))

num_files = len(data_sources)
if num_files <= 10:
    colors = Category10[10]
else:
    colors = Category20[20]

# Add a line for each series in the first plot
for idx, (series_name, source) in enumerate(data_sources.items()):
    color = colors[idx % len(colors)]
    p1.line('time_step', 'unique_entropy', source=source, line_width=2, legend_label=series_name, color=color)

p1.legend.click_policy = "hide"

# Plot 2: Number of unique lambda expressions at each time step for selected series
p2 = figure(title="Lambda Expression Analysis", x_axis_label="Time Step",
            y_axis_label="Number of Unique Expressions", tools="tap", width=700, height=400)
p2.line('x', 'y', source=source2, line_width=2, line_color="green")
p2.scatter('x', 'y', source=source2, size=6, color="green", alpha=0.6)

# JS callback for updating the data sources based on selection
update_callback = CustomJS(args=dict(source2=source2, source2_sources=source2_sources), code="""
    var selected_file = cb_obj.value;
    source2.data = source2_sources[selected_file].data;
    source2.change.emit();
""")
simulation_select.js_on_change('value', update_callback)

# JS callback for showing data when selecting a single point on the green graph
green_graph_callback = CustomJS(args=dict(source=source2, info_div=info_div), code="""
    var selected_indices = source.selected.indices;
    if (selected_indices.length > 0) {
        var last_selected_index = selected_indices[selected_indices.length - 1];
        source.selected.indices = [last_selected_index];  // Clear old points and keep the last one only

        var x_value = source.data['x'][last_selected_index];
        var y_value = source.data['y'][last_selected_index];
        var info_text = '<p style="margin-top: 20px;"><b>Selected Point Info:</b><br>';
        info_text += 'Time Step: ' + x_value + ', Number of Unique Expressions: ' + y_value + '</p>';
        info_div.text = info_text;
    } else {
        info_div.text = '<p style="margin-top: 20px;">Select a point on the green graph to see its data here.</p>';
    }
    source.change.emit();  // Emit change to update the visualization
""")
source2.selected.js_on_change('indices', green_graph_callback)

# Layout
layout = column(
    title_div,
    row(p1, Spacer(width=100)), 
    Spacer(height=20),
    row(column(simulation_select, Spacer(height=10), info_div, width=250), p2)
)

# Show the result
output_file("lambda_expression_analysis.html")
show(layout)
