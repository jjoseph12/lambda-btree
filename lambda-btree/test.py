import os
import argparse
import pandas as pd
from bokeh.models import ColumnDataSource, Select, Div, CustomJS
from bokeh.plotting import figure, show
from bokeh.layouts import row, column, Spacer
from bokeh.palettes import Category10
from bokeh.palettes import Category10, Category20


# Parse command-line arguments
parser = argparse.ArgumentParser(description="Load CSV data for Bokeh visualization.")
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument("file", type=str, nargs='?', help="Path to a single CSV file.")
group.add_argument("-folder", type=str, help="Path to a folder containing CSV files.")
args = parser.parse_args()

# Dictionaries to hold data sources
data_sources = {}  # Data for the first plot (unique entropy over time)
source2_sources = {}  # Data for the second plot (lambda expression analysis)

# Variable to keep track of maximum time_step
max_time_step = 0

# Define the cumulative unique counts function
def cumulative_unique_counts(x):
    seen = set()
    counts = []
    for item in x:
        seen.add(item)
        counts.append(len(seen))
    return counts

# Load data based on input
if args.folder:
    # Check if the folder path is valid
    if os.path.isdir(args.folder):
        for filename in os.listdir(args.folder):
            if filename.endswith(".csv"):
                file_path = os.path.join(args.folder, filename)
                df = pd.read_csv(file_path)
                # Ensure required columns exist
                if 'time_series_number' in df.columns and 'lambda_expression' in df.columns:
                    # Add a 'time_step' column if not present
                    if 'time_step' not in df.columns:
                        df['time_step'] = df.groupby('time_series_number').cumcount() + 1  # Start time_step from 1

                    # Compute unique entropy
                    df['unique_entropy'] = df.groupby('time_series_number')['lambda_expression'].transform(cumulative_unique_counts)

                    # Update max_time_step
                    max_time_step = max(max_time_step, df['time_step'].max())

                    # Prepare data source for the first plot (Unique Entropy Over Time)
                    data_sources[filename] = ColumnDataSource(data=dict(
                        time_step=df['time_step'],
                        unique_entropy=df['unique_entropy'],
                        lambda_expression=df['lambda_expression']
                    ))

                    # Prepare data source for the second plot
                    lambda_x = df['time_step'].unique()
                    lambda_y = df.groupby('time_step')['lambda_expression'].nunique().values
                    source2_sources[filename] = ColumnDataSource(data=dict(x=lambda_x, y=lambda_y))
        if not data_sources:
            raise ValueError("No valid CSV files found in the specified folder.")
    else:
        raise ValueError("The specified path is not a directory.")
else:
    # Load a single CSV file
    if os.path.isfile(args.file) and args.file.endswith(".csv"):
        df = pd.read_csv(args.file)
        if 'time_series_number' in df.columns and 'lambda_expression' in df.columns:
            # Add a 'time_step' column if not present
            if 'time_step' not in df.columns:
                df['time_step'] = df.groupby('time_series_number').cumcount() + 1  # Start time_step from 1

            # Compute unique entropy
            df['unique_entropy'] = df.groupby('time_series_number')['lambda_expression'].transform(cumulative_unique_counts)

            # Update max_time_step
            max_time_step = max(max_time_step, df['time_step'].max())

            # Prepare data source for the first plot (Unique Entropy Over Time)
            filename = os.path.basename(args.file)
            data_sources[filename] = ColumnDataSource(data=dict(
                time_step=df['time_step'],
                unique_entropy=df['unique_entropy'],
                lambda_expression=df['lambda_expression']
            ))

            # Prepare data source for the second plot
            lambda_x = df['time_step'].unique()
            lambda_y = df.groupby('time_step')['lambda_expression'].nunique().values
            source2_sources[filename] = ColumnDataSource(data=dict(x=lambda_x, y=lambda_y))
        else:
            raise ValueError("The specified CSV file does not contain the time series and lamaba columns.")
    else:
        raise ValueError("The specified path is not a valid CSV file.")

csv_options = list(data_sources.keys())

# Initial data source for the second plot
source2 = source2_sources[csv_options[0]]

# Div elements for UI
title_div = Div(text="<h1 style='margin-bottom: 20px;'><b>Lambda Expression Analysis Tool</b></h1>", width=400)
info_div = Div(text="<p style='margin-top: 20px;'>Select a point on the green graph to see its data here.</p>", width=250)

# Simulation selection widget
simulation_select = Select(title="Select CSV File", value=csv_options[0], options=csv_options, width=200)

# Plot 1: Unique entropy over time for all CSV files
p1 = figure(title="Unique Entropy Over Time", x_axis_label="Time", y_axis_label="Unique Entropy",
            tools="tap", width=700, height=400, x_range=(0, max_time_step))


num_files = len(data_sources)
if num_files <= 10:
    colors = Category10[10]
else:
    colors = Category20[20]

# Add a line for each CSV file in the first plot
for idx, (filename, source) in enumerate(data_sources.items()):
    color = colors[idx % len(colors)]
    p1.line('time_step', 'unique_entropy', source=source, line_width=2, legend_label=filename, color=color)

p1.legend.click_policy = "hide"

# Plot 2: Number of unique lambda expressions at each time step for selected CSV file
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
show(layout)
