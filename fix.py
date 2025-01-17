from bokeh.models import ColumnDataSource, Select, Div
from bokeh.plotting import figure, show
from bokeh.layouts import column

source = ColumnDataSource(data=dict(x=[1, 2, 3], y=[4, 5, 6]))

p = figure(title="Test Plot")
p.line('x', 'y', source=source)

layout = column(Div(text="<h1>Test</h1>"), p)
show(layout)
