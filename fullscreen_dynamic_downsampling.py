# from bokeh.models import ColumnDataSource, Legend, LegendItem, TapTool
# from bokeh.plotting import figure, curdoc
# from bokeh.layouts import column
# import pandas as pd
# import numpy as np

# # Globals
# data_map = {}  # Store data for each experiment for dynamic updates
# source2 = ColumnDataSource(data=dict(time_step=[], unique_expressions=[]))  # For second graph

# # Generate synthetic data for testing with more randomness
# def generate_synthetic_data(points, experiment_name):
#     # Generate random time steps and unique entropy
#     time_step = np.sort(np.random.uniform(0, points, size=points))  # Random, sorted x-axis values
#     unique_entropy = np.random.uniform(0, 100, size=points)  # Random y-axis values
#     unique_expressions = np.random.randint(1, 10, size=points)  # Random unique expressions
#     return pd.DataFrame({
#         'time_step': time_step,
#         'unique_entropy': unique_entropy,
#         'unique_expressions': unique_expressions,
#         'experiment': experiment_name
#     })


# # Generate synthetic data for three experiments
# experiment_tables = {
#     "experiment_10k": generate_synthetic_data(10000, "experiment_10k"),
#     "experiment_100k": generate_synthetic_data(100000, "experiment_100k"),
#     "experiment_1M": generate_synthetic_data(1000000, "experiment_1M")
# }

# # Plot 1 (Unique Entropy Over Time)
# p1 = figure(
#     title="Unique Entropy Over Time (All Experiments)",
#     x_axis_label="Time",
#     y_axis_label="Unique Entropy",
#     width=1920,  # Full width
#     height=800,  # Larger height
#     tools="tap,pan,box_zoom,wheel_zoom,reset"
# )

# # Plot 2 (Number of Unique Expressions Over Time)
# p2 = figure(
#     title="Number of Unique Expressions Over Time (Selected Experiment)",
#     x_axis_label="Time",
#     y_axis_label="Number of Unique Expressions",
#     width=1920,  # Full width
#     height=800,  # Larger height
#     tools="pan,box_zoom,wheel_zoom,reset"
# )
# p2.line('time_step', 'unique_expressions', source=source2, line_width=2, color="green")  # Add a blank line initially

# # Add lines and legends for all experiments in Plot 1
# legend_items1 = []
# colors = ['blue', 'green', 'red']  # Enough colors for 3 experiments
# line_renderers = []  # Store renderers for matching taps
# line_to_table_map = {}  # Map renderers to experiment tables

# for idx, (table_name, df) in enumerate(experiment_tables.items()):
#     # Ensure data is not empty
#     if df.empty:
#         print(f"Data for {table_name} is empty.")
#         continue

#     # Downsample the initial data (uniform nth-point sampling)
#     nth_point = max(len(df) // 10000, 1)  # Keep ~10,000 points visible initially
#     downsampled_df = df.iloc[::nth_point]

#     # Check if downsampled data is not empty
#     if downsampled_df.empty:
#         print(f"Downsampled data for {table_name} is empty.")
#         continue

#     # Data for Plot 1
#     source1 = ColumnDataSource(data=dict(
#         time_step=downsampled_df['time_step'],
#         unique_entropy=downsampled_df['unique_entropy']
#     ))

#     # Store unique_expressions data for dynamic updates
#     data_map[table_name] = dict(
#         time_step=df['time_step'],
#         unique_expressions=df['unique_expressions']
#     )

#     # Add line to Plot 1
#     color = colors[idx % len(colors)]
#     line1 = p1.line('time_step', 'unique_entropy', source=source1, line_width=2, color=color, name=table_name)
#     line_renderers.append(line1)
#     line_to_table_map[line1] = table_name  # Map renderer to its experiment table
#     legend_items1.append(LegendItem(label=table_name, renderers=[line1]))

# # Add legend to Plot 1
# legend1 = Legend(items=legend_items1)
# p1.add_layout(legend1, 'right')
# p1.legend.click_policy = "hide"

# # Tap tool callback to update Plot 2
# def update_second_plot(event):
#     tap_x = event.x
#     tap_y = event.y

#     # Check for NaN values
#     if np.isnan(tap_x) or np.isnan(tap_y):
#         print("Invalid tap coordinates: x or y is NaN")
#         return

#     closest_renderer = None
#     min_distance = float('inf')

#     # Find the closest renderer (line) to the tap point
#     for renderer in line_renderers:
#         line_source = renderer.data_source
#         x_vals = np.array(line_source.data['time_step'])
#         y_vals = np.array(line_source.data['unique_entropy'])

#         # Check if the line is visible
#         if renderer.visible and len(x_vals) > 0 and len(y_vals) > 0:
#             distances = np.sqrt((x_vals - tap_x) ** 2 + (y_vals - tap_y) ** 2)
#             closest_point_distance = distances.min()

#             if closest_point_distance < min_distance:
#                 min_distance = closest_point_distance
#                 closest_renderer = renderer

#     # If a renderer is selected, update the second graph
#     if closest_renderer and closest_renderer in line_to_table_map:
#         selected_table = line_to_table_map[closest_renderer]
#         print(f"Selected experiment: {selected_table}")

#         # Update the second graph with data from the selected experiment
#         source2.data = dict(
#             time_step=data_map[selected_table]['time_step'],
#             unique_expressions=data_map[selected_table]['unique_expressions']
#         )
#     else:
#         print("No line was selected or the dataset is empty.")

# # Attach TapTool event
# p1.on_event('tap', update_second_plot)

# # Add dynamic downsampling on zoom
# def dynamic_downsampling(attr, old, new):
#     start = p1.x_range.start
#     end = p1.x_range.end

#     # Check for valid range values
#     if start is None or end is None or np.isnan(start) or np.isnan(end):
#         print("Invalid zoom range")
#         return

#     print(f"Zoom range: start={start}, end={end}")

#     for renderer in line_renderers:
#         table_name = line_to_table_map[renderer]
#         df = experiment_tables[table_name]

#         # Filter data within the zoom range
#         zoomed_data = df[(df['time_step'] >= start) & (df['time_step'] <= end)]

#         # Check if zoomed data is non-empty
#         if zoomed_data.empty:
#             print(f"No data in range for {table_name}")
#             continue

#         # Adjust nth_point for finer detail in zoomed range
#         nth_point = max(len(zoomed_data) // 1000, 1)  # Show ~1,000 points in zoomed range
#         downsampled_data = zoomed_data.iloc[::nth_point]

#         # Update the renderer's data source
#         renderer.data_source.data = dict(
#             time_step=downsampled_data['time_step'],
#             unique_entropy=downsampled_data['unique_entropy']
#         )

# # Attach zoom callback
# p1.x_range.on_change('start', dynamic_downsampling)
# p1.x_range.on_change('end', dynamic_downsampling)

# # Layout (Stack both plots vertically)
# layout = column(p1, p2, sizing_mode="stretch_width")  # Full width layout

# curdoc().add_root(layout)
# curdoc().title = "Full-Screen Dynamic Downsampling"



from bokeh.models import ColumnDataSource, Legend, LegendItem, TapTool
from bokeh.plotting import figure, curdoc
from bokeh.layouts import column
import pandas as pd
import numpy as np

# Globals
data_map = {}  # Store data for each experiment for dynamic updates
source2 = ColumnDataSource(data=dict(time_step=[], unique_expressions=[]))  # For second graph

# Generate synthetic data for testing with more randomness
def generate_synthetic_data(points, experiment_name):
    # Generate random time steps and unique entropy
    time_step = np.sort(np.random.uniform(0, points, size=points))  # Random, sorted x-axis values
    unique_entropy = np.random.uniform(0, 100, size=points)  # Random y-axis values
    unique_expressions = np.random.randint(1, 10, size=points)  # Random unique expressions
    return pd.DataFrame({
        'time_step': time_step,
        'unique_entropy': unique_entropy,
        'unique_expressions': unique_expressions,
        'experiment': experiment_name
    })

# Generate synthetic data for three large experiments
experiment_tables = {
    "experiment_10M": generate_synthetic_data(10_000_000, "experiment_10M"),
    "experiment_100M": generate_synthetic_data(100_000_000, "experiment_100M"),
    # "experiment_1B": generate_synthetic_data(1_000_000_000, "experiment_1B")
}

# Plot 1 (Unique Entropy Over Time)
p1 = figure(
    title="Unique Entropy Over Time (All Experiments)",
    x_axis_label="Time",
    y_axis_label="Unique Entropy",
    width=1920,  # Full width
    height=800,  # Larger height
    tools="tap,pan,box_zoom,wheel_zoom,reset"
)

# Plot 2 (Number of Unique Expressions Over Time)
p2 = figure(
    title="Number of Unique Expressions Over Time (Selected Experiment)",
    x_axis_label="Time",
    y_axis_label="Number of Unique Expressions",
    width=1920,  # Full width
    height=800,  # Larger height
    tools="pan,box_zoom,wheel_zoom,reset"
)
p2.line('time_step', 'unique_expressions', source=source2, line_width=2, color="green")  # Add a blank line initially

# Add lines and legends for all experiments in Plot 1
legend_items1 = []
colors = ['blue', 'green', 'red']  # Enough colors for 3 ex p    eriments
line_renderers = []  # Store renderers for matching taps
line_to_table_map = {}  # Map renderers to experiment tables

for idx, (table_name, df) in enumerate(experiment_tables.items()):
    # Ensure data is not empty
    if df.empty:
        print(f"Data for {table_name} is empty.")
        continue

    # Downsample the initial data (uniform nth-point sampling)
    nth_point = max(len(df) // 10000, 1)  # Keep ~10,000 points visible initially
    downsampled_df = df.iloc[::nth_point]

    # Check if downsampled data is not empty
    if downsampled_df.empty:
        print(f"Downsampled data for {table_name} is empty.")
        continue

    # Data for Plot 1
    source1 = ColumnDataSource(data=dict(
        time_step=downsampled_df['time_step'],
        unique_entropy=downsampled_df['unique_entropy']
    ))

    # Store unique_expressions data for dynamic updates
    data_map[table_name] = dict(
        time_step=df['time_step'],
        unique_expressions=df['unique_expressions']
    )

    # Add line to Plot 1
    color = colors[idx % len(colors)]
    line1 = p1.line('time_step', 'unique_entropy', source=source1, line_width=2, color=color, name=table_name)
    line_renderers.append(line1)
    line_to_table_map[line1] = table_name  # Map renderer to its experiment table
    legend_items1.append(LegendItem(label=table_name, renderers=[line1]))

# Add legend to Plot 1
legend1 = Legend(items=legend_items1)
p1.add_layout(legend1, 'right')
p1.legend.click_policy = "hide"

# Tap tool callback to update Plot 2
def update_second_plot(event):
    tap_x = event.x
    tap_y = event.y

    # Check for NaN values
    if np.isnan(tap_x) or np.isnan(tap_y):
        print("Invalid tap coordinates: x or y is NaN")
        return

    closest_renderer = None
    min_distance = float('inf')

    # Find the closest renderer (line) to the tap point
    for renderer in line_renderers:
        line_source = renderer.data_source
        x_vals = np.array(line_source.data['time_step'])
        y_vals = np.array(line_source.data['unique_entropy'])

        # Check if the line is visible
        if renderer.visible and len(x_vals) > 0 and len(y_vals) > 0:
            distances = np.sqrt((x_vals - tap_x) ** 2 + (y_vals - tap_y) ** 2)
            closest_point_distance = distances.min()

            if closest_point_distance < min_distance:
                min_distance = closest_point_distance
                closest_renderer = renderer

    # If a renderer is selected, update the second graph
    if closest_renderer and closest_renderer in line_to_table_map:
        selected_table = line_to_table_map[closest_renderer]
        print(f"Selected experiment: {selected_table}")

        # Update the second graph with data from the selected experiment
        source2.data = dict(
            time_step=data_map[selected_table]['time_step'],
            unique_expressions=data_map[selected_table]['unique_expressions']
        )
    else:
        print("No line was selected or the dataset is empty.")

# Attach TapTool event
p1.on_event('tap', update_second_plot)

# Add dynamic downsampling on zoom
def dynamic_downsampling(attr, old, new):
    start = p1.x_range.start
    end = p1.x_range.end

    # Check for valid range values
    if start is None or end is None or np.isnan(start) or np.isnan(end):
        print("Invalid zoom range")
        return

    print(f"Zoom range: start={start}, end={end}")

    for renderer in line_renderers:
        table_name = line_to_table_map[renderer]
        df = experiment_tables[table_name]

        # Filter data within the zoom range
        zoomed_data = df[(df['time_step'] >= start) & (df['time_step'] <= end)]

        # Check if zoomed data is non-empty
        if zoomed_data.empty:
            print(f"No data in range for {table_name}")
            continue

        # Adjust nth_point for finer detail in zoomed range
        nth_point = max(len(zoomed_data) // 1000, 1)  # Show ~1,000 points in zoomed range
        downsampled_data = zoomed_data.iloc[::nth_point]

        # Update the renderer's data source
        renderer.data_source.data = dict(
            time_step=downsampled_data['time_step'],
            unique_entropy=downsampled_data['unique_entropy']
        )

# Attach zoom callback
p1.x_range.on_change('start', dynamic_downsampling)
p1.x_range.on_change('end', dynamic_downsampling)

# Layout (Stack both plots vertically)
layout = column(p1, p2, sizing_mode="stretch_width")  # Full width layout

curdoc().add_root(layout)
curdoc().title = "Dynamic Downsampling for Large Datasets"
