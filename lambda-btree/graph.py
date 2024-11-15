from bokeh.models import ColumnDataSource, Select, Div, CustomJS
from bokeh.plotting import figure, show
from bokeh.layouts import row, column, Spacer
import numpy as np

# Sample data generation for unique entropy over time
time_steps = np.arange(0, 100)
unique_entropies = np.random.rand(100)  # Replace with your computed entropies for N simulations

# Data source for the first plot (Unique Entropy Over Time)
source1 = ColumnDataSource(data=dict(time=time_steps, entropy=unique_entropies))

# Data source for selected simulation (dummy data for lambda analysis)
lambda_x = np.linspace(0, 10, 100)
lambda_y = np.sin(lambda_x)  # Replace with your lambda expression data

source2 = ColumnDataSource(data=dict(x=lambda_x, y=lambda_y))

# Div element for the title
title_div = Div(text="<h1 style='margin-bottom: 20px;'><b>Lambda Expression Analysis Tool</b></h1>", width=400)

# Div element for displaying selected point info
info_div = Div(text="<p style='margin-top: 20px;'>Select a point on the green graph to see its data here.</p>", width=250)

# Simulation selection widget
simulation_select = Select(title="Select Simulation", value="1", options=[str(i) for i in range(1, 6)], width=200)

# Plot 1: Unique entropy over time (set width)
p1 = figure(title="Unique Entropy Over Time", x_axis_label="Time", y_axis_label="Unique Entropy", tools="tap", width=700, height=400)
p1.line('time', 'entropy', source=source1, line_width=2)

# Plot 2: Detailed lambda expression analysis (set the same width)
p2 = figure(title="Lambda Expression Analysis", x_axis_label="Expression Part", y_axis_label="Fluctuation", tools="tap", width=700, height=400)
p2.line('x', 'y', source=source2, line_width=2, line_color="green")
p2.scatter('x', 'y', source=source2, size=6, color="green", alpha=0.6)

# CustomJS callback for showing data when selecting a single point on the green graph
green_graph_callback = CustomJS(args=dict(source=source2, info_div=info_div), code="""
    var selected_indices = source.selected.indices;
    if (selected_indices.length > 0) {
        // Keep only the last selected point
        var last_selected_index = selected_indices[selected_indices.length - 1];
        source.selected.indices = [last_selected_index];  // Clear old points and keep the last one only
        
        var x_value = source.data['x'][last_selected_index];
        var y_value = source.data['y'][last_selected_index];
        var info_text = '<p style="margin-top: 20px;"><b>Selected Point Info:</b><br>';
        info_text += 'X: ' + x_value.toFixed(2) + ', Y: ' + y_value.toFixed(2) + '</p>';
        info_div.text = info_text;
    } else {
        info_div.text = '<p style="margin-top: 20px;">Select a point on the green graph to see its data here.</p>';
    }
    source.change.emit();  // Emit change to update the visualization
""")
source2.selected.js_on_change('indices', green_graph_callback)

# Layout: Align the select widget and info div to the left of the green graph
layout = column(
    title_div,
    row(p1, Spacer(width=100)),  # Center align by adding space
    Spacer(height=20),
    row(column(simulation_select, Spacer(height=10), info_div, width=250), p2)
)

# Show the result
show(layout)
