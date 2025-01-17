# # # # #bokeh serve --show bokeh.py

# # # # from bokeh.io import curdoc
# # # # from bokeh.models import ColumnDataSource, Select, Div
# # # # from bokeh.plotting import figure
# # # # from bokeh.layouts import row, column, Spacer
# # # # import sqlite3
# # # # import pandas as pd


# # # # def list_experiment_tables(db_name='src/alchemy_data.db'):
# # # #     conn = sqlite3.connect(db_name)
# # # #     cursor = conn.cursor()
# # # #     cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
# # # #     tables = [row[0] for row in cursor.fetchall()]
# # # #     conn.close()
# # # #     return [table for table in tables if table.startswith('experiment_')]


# # # # def load_data_from_sqlite(db_name, table_name):
# # # #     conn = sqlite3.connect(db_name)
# # # #     query = f"""
# # # #     SELECT series_number AS time_series_number, lambda_expression, 
# # # #            ROW_NUMBER() OVER(PARTITION BY series_number ORDER BY id) AS time_step
# # # #     FROM {table_name}
# # # #     """
# # # #     df = pd.read_sql_query(query, conn)
# # # #     conn.close()
# # # # df['unique_entropy'] = df.groupby('time_series_number')['lambda_expression'].transform(
# # # #     lambda x: pd.Series([len(set(x[:i + 1])) for i in range(len(x))])
# # # # )



# # # # db_name = 'src/alchemy_data.db'
# # # # experiment_tables = list_experiment_tables(db_name)
# # # # if not experiment_tables:
# # # #     raise ValueError(f"No experiment tables found in the database: {db_name}")

# # # # current_table = experiment_tables[0]
# # # # df = load_data_from_sqlite(db_name, current_table)

# # # # data_sources = {}
# # # # for series_num, series_df in df.groupby('time_series_number'):
# # # #     data_sources[f"Series {series_num}"] = ColumnDataSource(data=dict(
# # # #         time_step=series_df['time_step'],
# # # #         unique_entropy=series_df['unique_entropy']
# # # #     ))

# # # # csv_options = list(data_sources.keys())
# # # # source1 = data_sources[csv_options[0]]

# # # # p1 = figure(title="Unique Entropy Over Time", x_axis_label="Time", y_axis_label="Unique Entropy", width=700, height=400)
# # # # p1.line('time_step', 'unique_entropy', source=source1, line_width=2, color='blue')

# # # # table_select = Select(title="Select Experiment Table", value=current_table, options=experiment_tables)
# # # # series_select = Select(title="Select Series", value=csv_options[0], options=csv_options)


# # # # def update_table(attr, old, new):
# # # #     global current_table
# # # #     current_table = table_select.value
# # # #     new_df = load_data_from_sqlite(db_name, current_table)
# # # #     new_sources = {}
# # # #     for series_num, series_df in new_df.groupby('time_series_number'):
# # # #         new_sources[f"Series {series_num}"] = ColumnDataSource(data=dict(
# # # #             time_step=series_df['time_step'],
# # # #             unique_entropy=series_df['unique_entropy']
# # # #         ))
# # # #     global data_sources
# # # #     data_sources = new_sources
# # # #     series_select.options = list(new_sources.keys())
# # # #     series_select.value = list(new_sources.keys())[0]
# # # #     update_series(None, None, None)


# # # # def update_series(attr, old, new):
# # # #     selected_series = series_select.value
# # # #     source1.data = data_sources[selected_series].data


# # # # table_select.on_change('value', update_table)
# # # # series_select.on_change('value', update_series)

# # # # layout = column(
# # # #     Div(text="<h1>Lambda Expression Analysis Tool</h1>", width=400),
# # # #     row(table_select, series_select),
# # # #     p1,
# # # # )


# # # # curdoc().add_root(layout)







# # # # from bokeh.models import ColumnDataSource, Select
# # # # from bokeh.plotting import figure, curdoc
# # # # from bokeh.layouts import column, row
# # # # import sqlite3
# # # # import pandas as pd

# # # # # Globals
# # # # db_name = 'src/alchemy_data.db'
# # # # source1 = ColumnDataSource(data=dict(time_step=[], unique_entropy=[]))

# # # # def list_experiment_tables(db_name):
# # # #     conn = sqlite3.connect(db_name)
# # # #     try:
# # # #         query = "SELECT name FROM sqlite_master WHERE type='table'"
# # # #         tables = pd.read_sql_query(query, conn)['name'].tolist()
# # # #         experiment_tables = [table for table in tables if table.startswith('experiment_')]
# # # #     finally:
# # # #         conn.close()
# # # #     return experiment_tables

# # # # def load_data_from_sqlite(db_name, table_name):
# # # #     conn = sqlite3.connect(db_name)
# # # #     try:
# # # #         query = f"""
# # # #         SELECT id, lambda_expression 
# # # #         FROM {table_name}
# # # #         ORDER BY id
# # # #         """
# # # #         print(f"Loading data from {table_name}")
# # # #         df = pd.read_sql_query(query, conn)
# # # #         print(f"Loaded {len(df)} rows")
# # # #         df['unique_entropy'] = [len(set(df['lambda_expression'].iloc[:i+1])) 
# # # #                               for i in range(len(df))]
# # # #         return df
# # # #     except Exception as e:
# # # #         print(f"Database error: {e}")
# # # #         return pd.DataFrame()
# # # #     finally:
# # # #         conn.close()


# # # # # Get experiment tables
# # # # experiment_tables = list_experiment_tables(db_name)
# # # # if not experiment_tables:
# # # #     raise ValueError(f"No experiment tables found in the database '{db_name}'")

# # # # # Initial setup
# # # # initial_table = experiment_tables[0]
# # # # def load_data_from_sqlite(db_name, table_name):
# # # #     conn = sqlite3.connect(db_name)
# # # #     try:
# # # #         query = f"""
# # # #         SELECT id, lambda_expression
# # # #         FROM {table_name}
# # # #         WHERE series_number = (
# # # #             SELECT MIN(series_number) 
# # # #             FROM {table_name}
# # # #         )
# # # #         ORDER BY id
# # # #         """
# # # #         print(f"Loading data from {table_name}")
# # # #         df = pd.read_sql_query(query, conn)
# # # #         print(f"Loaded {len(df)} rows from series {df['id'].min()} to {df['id'].max()}")
# # # #         df['unique_entropy'] = [len(set(df['lambda_expression'].iloc[:i+1])) 
# # # #                               for i in range(len(df))]
# # # #         return df
# # # #     finally:
# # # #         conn.close()

# # # # def update_data(attr, old, new):
# # # #     print(f"Updating to table: {experiment_select.value}")
# # # #     df = load_data_from_sqlite(db_name, experiment_select.value)
# # # #     if not df.empty:
# # # #         new_data = dict(
# # # #             time_step=df['id'].tolist(),
# # # #             unique_entropy=df['unique_entropy'].tolist()
# # # #         )
# # # #         source1.data.clear()  # Clear existing data
# # # #         source1.data = new_data  # Set new data
# # # #         print(f"Updated with {len(new_data['time_step'])} points")
# # # # # Plot
# # # # p1 = figure(
# # # #     title="Unique Entropy Over Time",
# # # #     x_axis_label="Time",
# # # #     y_axis_label="Unique Entropy",
# # # #     width=800,
# # # #     height=400
# # # # )
# # # # p1.line('time_step', 'unique_entropy', source=source1, line_width=2, line_color="blue")

# # # # # Experiment table selector
# # # # experiment_select = Select(title="Select Experiment Table", value=initial_table, options=experiment_tables)
# # # # experiment_select.on_change('value', update_data)  # Make sure it's 'value' not "value"

# # # # # Layout
# # # # layout = column(
# # # #     row(experiment_select),
# # # #     p1
# # # # )
# # # # curdoc().add_root(layout)
# # # # curdoc().title = "Lambda Expression Analysis Tool"










# # # # from bokeh.models import ColumnDataSource, Select
# # # # from bokeh.plotting import figure, curdoc
# # # # from bokeh.layouts import column, row
# # # # import sqlite3
# # # # import pandas as pd

# # # # # Globals
# # # # db_name = 'src/alchemy_data.db'
# # # # source1 = ColumnDataSource(data=dict(time_step=[], unique_entropy=[]))

# # # # def list_experiment_tables(db_name):
# # # #     conn = sqlite3.connect(db_name)
# # # #     try:
# # # #         query = "SELECT name FROM sqlite_master WHERE type='table'"
# # # #         tables = pd.read_sql_query(query, conn)['name'].tolist()
# # # #         experiment_tables = [table for table in tables if table.startswith('experiment_')]
# # # #     finally:
# # # #         conn.close()
# # # #     return experiment_tables

# # # # def load_data_from_sqlite(db_name, table_name):
# # # #     conn = sqlite3.connect(db_name)
# # # #     try:
# # # #         query = f"""
# # # #         SELECT id, lambda_expression 
# # # #         FROM {table_name}
# # # #         ORDER BY id
# # # #         """
# # # #         df = pd.read_sql_query(query, conn)
# # # #         df['unique_entropy'] = [len(set(df['lambda_expression'].iloc[:i+1])) 
# # # #                               for i in range(len(df))]
# # # #         return df
# # # #     except Exception as e:
# # # #         print(f"Database error: {e}")
# # # #         return pd.DataFrame()
# # # #     finally:
# # # #         conn.close()

# # # # # Get experiment tables
# # # # experiment_tables = list_experiment_tables(db_name)
# # # # if not experiment_tables:
# # # #     raise ValueError(f"No experiment tables found in the database '{db_name}'")

# # # # # Initial setup
# # # # initial_table = experiment_tables[0]
# # # # df = load_data_from_sqlite(db_name, initial_table)
# # # # source1.data = dict(
# # # #     time_step=df['id'].tolist(),
# # # #     unique_entropy=df['unique_entropy'].tolist()
# # # # )

# # # # def update_data(attr, old, new):
# # # #     print(f"Updating to table: {experiment_select.value}")
# # # #     df = load_data_from_sqlite(db_name, experiment_select.value)
# # # #     print(f"Retrieved {len(df)} rows")
# # # #     if not df.empty:
# # # #         source1.data = dict(
# # # #             time_step=df['id'].tolist(),
# # # #             unique_entropy=df['unique_entropy'].tolist()
# # # #         )
# # # #         print(f"Source updated: {source1.data}")
# # # #     else:
# # # #         source1.data = dict(time_step=[], unique_entropy=[])
# # # #         print("No data available for this table.")
# # # #     print("Update complete")

# # # # # Plot
# # # # p1 = figure(
# # # #     title="Unique Entropy Over Time",
# # # #     x_axis_label="Time",
# # # #     y_axis_label="Unique Entropy",
# # # #     width=800,
# # # #     height=400
# # # # )
# # # # p1.line('time_step', 'unique_entropy', source=source1, line_width=2, line_color="blue")

# # # # # Experiment table selector
# # # # experiment_select = Select(title="Select Experiment Table", value=initial_table, options=experiment_tables)
# # # # experiment_select.on_change('value', update_data)

# # # # # Layout
# # # # layout = column(
# # # #     row(experiment_select),
# # # #     p1
# # # # )
# # # # curdoc().add_root(layout)
# # # # curdoc().title = "Lambda Expression Analysis Tool"






# # from bokeh.models import ColumnDataSource, Select
# # from bokeh.plotting import figure, curdoc
# # from bokeh.layouts import column, row
# # import sqlite3
# # import pandas as pd

# # # Globals
# # db_name = 'src/alchemy_data.db'
# # source1 = ColumnDataSource(data=dict(time_step=[], unique_entropy=[]))
# # source2 = ColumnDataSource(data=dict(time_step=[], unique_expressions=[]))

# # def list_experiment_tables(db_name):
# #     conn = sqlite3.connect(db_name)
# #     try:
# #         query = "SELECT name FROM sqlite_master WHERE type='table'"
# #         tables = pd.read_sql_query(query, conn)['name'].tolist()
# #         experiment_tables = [table for table in tables if table.startswith('experiment_')]
# #     finally:
# #         conn.close()
# #     return experiment_tables

# # def load_data_from_sqlite(db_name, table_name):
# #     conn = sqlite3.connect(db_name)
# #     try:
# #         query = f"""
# #         SELECT id, lambda_expression 
# #         FROM {table_name}
# #         ORDER BY id
# #         """
# #         df = pd.read_sql_query(query, conn)
# #         # Calculate unique entropy
# #         df['unique_entropy'] = [len(set(df['lambda_expression'].iloc[:i+1])) 
# #                               for i in range(len(df))]
# #         # Calculate number of unique expressions
# #         df['unique_expressions'] = df['lambda_expression'].apply(lambda x: len(set(x.split())))  # Adjust as needed
# #         return df
# #     except Exception as e:
# #         print(f"Database error: {e}")
# #         return pd.DataFrame()
# #     finally:
# #         conn.close()

# # # Get experiment tables
# # experiment_tables = list_experiment_tables(db_name)
# # if not experiment_tables:
# #     raise ValueError(f"No experiment tables found in the database '{db_name}'")

# # # Initial setup
# # initial_table = experiment_tables[0]
# # df = load_data_from_sqlite(db_name, initial_table)
# # source1.data = dict(
# #     time_step=df['id'].tolist(),
# #     unique_entropy=df['unique_entropy'].tolist()
# # )
# # source2.data = dict(
# #     time_step=df['id'].tolist(),
# #     unique_expressions=df['unique_expressions'].tolist()
# # )

# # def update_data(attr, old, new):
# #     print(f"Updating to table: {experiment_select.value}")
# #     df = load_data_from_sqlite(db_name, experiment_select.value)
# #     print(f"Retrieved {len(df)} rows")
# #     if not df.empty:
# #         source1.data = dict(
# #             time_step=df['id'].tolist(),
# #             unique_entropy=df['unique_entropy'].tolist()
# #         )
# #         source2.data = dict(
# #             time_step=df['id'].tolist(),
# #             unique_expressions=df['unique_expressions'].tolist()
# #         )
# #         print(f"Source updated: {source1.data}")
# #     else:
# #         source1.data = dict(time_step=[], unique_entropy=[])
# #         source2.data = dict(time_step=[], unique_expressions=[])
# #         print("No data available for this table.")
# #     print("Update complete")

# # # Plot 1 (Unique Entropy Over Time)
# # p1 = figure(
# #     title="Unique Entropy Over Time",
# #     x_axis_label="Time",
# #     y_axis_label="Unique Entropy",
# #     width=800,
# #     height=400
# # )
# # p1.line('time_step', 'unique_entropy', source=source1, line_width=2, line_color="blue")

# # # Plot 2 (Number of Unique Expressions Over Time)
# # p2 = figure(
# #     title="Number of Unique Expressions Over Time",
# #     x_axis_label="Time",
# #     y_axis_label="Number of Unique Expressions",
# #     width=800,
# #     height=400
# # )
# # p2.line('time_step', 'unique_expressions', source=source2, line_width=2, line_color="green")

# # # Experiment table selector
# # experiment_select = Select(title="Select Experiment Table", value=initial_table, options=experiment_tables)
# # experiment_select.on_change('value', update_data)

# # # Layout (Stack both plots vertically)
# # layout = column(
# #     row(experiment_select),
# #     p1,
# #     p2
# # )

# # curdoc().add_root(layout)
# # curdoc().title = "Lambda Expression Analysis Tool"


# # from bokeh.io import curdoc
# # from bokeh.models import ColumnDataSource, Select
# # from bokeh.plotting import figure
# # from bokeh.layouts import column, row
# # import sqlite3
# # import pandas as pd
# # import datashader as ds
# # import datashader.transfer_functions as tf
# # from datashader import reductions as rd

# # # Globals
# # db_name = 'src/alchemy_data.db'
# # source1 = ColumnDataSource(data=dict(time_step=[], unique_entropy=[]))

# # def list_experiment_tables(db_name):
# #     conn = sqlite3.connect(db_name)
# #     try:
# #         query = "SELECT name FROM sqlite_master WHERE type='table'"
# #         tables = pd.read_sql_query(query, conn)['name'].tolist()
# #         experiment_tables = [table for table in tables if table.startswith('experiment_')]
# #     finally:
# #         conn.close()
# #     return experiment_tables

# # def load_data_from_sqlite(db_name, table_name):
# #     conn = sqlite3.connect(db_name)
# #     try:
# #         query = f"""
# #         SELECT id, lambda_expression 
# #         FROM {table_name}
# #         ORDER BY id
# #         """
# #         df = pd.read_sql_query(query, conn)
# #         df['unique_entropy'] = [len(set(df['lambda_expression'].iloc[:i+1])) 
# #                               for i in range(len(df))]
# #         return df
# #     except Exception as e:
# #         print(f"Database error: {e}")
# #         return pd.DataFrame()
# #     finally:
# #         conn.close()

# # # Get experiment tables
# # experiment_tables = list_experiment_tables(db_name)
# # if not experiment_tables:
# #     raise ValueError(f"No experiment tables found in the database '{db_name}'")

# # # Initial setup
# # initial_table = experiment_tables[0]

# # import colorcet as cc
# # import datashader.transfer_functions as tf
# # from datashader import reductions as rd
# # import numpy as np
# # from PIL import Image
# # import io

# # def update_data(attr, old, new):
# #     print(f"Updating to table: {experiment_select.value}")
# #     df = load_data_from_sqlite(db_name, experiment_select.value)
# #     print(f"Retrieved {len(df)} rows")
    
# #     if not df.empty:
# #         # Use Datashader to render large datasets efficiently
# #         canvas = ds.Canvas(plot_width=800, plot_height=400)
# #         agg = canvas.points(df, 'id', 'unique_entropy', agg=rd.count())
        
# #         # Apply color mapping
# #         img = tf.shade(agg, cmap=cc.fire)  # Use colorcet's fire colormap
# #         img_bokeh = tf.dynspread(img)  # Dynamically spread the image to avoid empty space
        
# #         # Convert the Datashader image to a format Bokeh can handle
# #         with io.BytesIO() as output:
# #             img_bokeh.to_pil().save(output, format="PNG")
# #             img_bokeh_url = output.getvalue()

# #         # Update the source for Bokeh
# #         source1.data = dict(time_step=df['id'].tolist(), unique_entropy=df['unique_entropy'].tolist())
        
# #         # Now render the image using Bokeh's image_url
# #         p1.image_url(url=[img_bokeh_url], x=0, y=0, w=800, h=400)

# #         print(f"Source updated with {len(source1.data['time_step'])} points")
# #     else:
# #         source1.data = dict(time_step=[], unique_entropy=[])
# #         print("No data available for this table.")
    
# #     print("Update complete")


# # # Plot using Datashader output (not directly Bokeh plot)
# # p1 = figure(
# #     title="Unique Entropy Over Time",
# #     x_axis_label="Time",
# #     y_axis_label="Unique Entropy",
# #     width=800,
# #     height=400
# # )

# # # Experiment table selector
# # experiment_select = Select(title="Select Experiment Table", value=initial_table, options=experiment_tables)
# # experiment_select.on_change('value', update_data)

# # # Layout
# # layout = column(
# #     row(experiment_select),
# #     p1
# # )
# # curdoc().add_root(layout)
# # curdoc().title = "Lambda Expression Analysis Tool"



# # import colorcet as cc
# # import datashader as ds
# # import datashader.transfer_functions as tf
# # from datashader import reductions as rd
# # import io
# # from bokeh.io import curdoc
# # from bokeh.models import ColumnDataSource, Select, Div
# # from bokeh.plotting import figure
# # from bokeh.layouts import column
# # import sqlite3
# # import pandas as pd


# # def list_experiment_tables(db_name='src/alchemy_data.db'):
# #     conn = sqlite3.connect(db_name)
# #     cursor = conn.cursor()
# #     cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
# #     tables = [row[0] for row in cursor.fetchall()]
# #     conn.close()
# #     return [table for table in tables if table.startswith('experiment_')]


# # def load_data_from_sqlite(db_name, table_name):
# #     conn = sqlite3.connect(db_name)
# #     query = f"""
# #     SELECT series_number AS time_series_number, lambda_expression, 
# #            ROW_NUMBER() OVER(PARTITION BY series_number ORDER BY id) AS time_step
# #     FROM {table_name}
# #     """
# #     df = pd.read_sql_query(query, conn)
# #     conn.close()
# #     df['unique_entropy'] = df.groupby('time_series_number')['lambda_expression'].transform(
# #         lambda x: pd.Series([len(set(x[:i + 1])) for i in range(len(x))])
# #     )
    
# #     # Count unique expressions (distinct lambda expressions) over time for Plot 2
# #     df['unique_expressions'] = df.groupby('time_series_number')['lambda_expression'].transform(lambda x: x.nunique())
    
# #     return df


# # # Globals
# # db_name = 'src/alchemy_data.db'
# # experiment_tables = list_experiment_tables(db_name)
# # if not experiment_tables:
# #     raise ValueError(f"No experiment tables found in the database: {db_name}")

# # current_table = experiment_tables[0]
# # df = load_data_from_sqlite(db_name, current_table)

# # # Data Sources
# # data_sources = {}
# # for series_num, series_df in df.groupby('time_series_number'):
# #     data_sources[f"Series {series_num}"] = ColumnDataSource(data=dict(
# #         time_step=series_df['time_step'],
# #         unique_entropy=series_df['unique_entropy'],
# #         unique_expressions=series_df['unique_expressions']  # For Plot 2
# #     ))

# # # Create initial data source
# # csv_options = list(data_sources.keys())
# # source1 = data_sources[csv_options[0]]
# # source2 = data_sources[csv_options[0]]  # You can customize this for the second plot

# # # Create Plot 1 (Unique Entropy - Datashader)
# # p1 = figure(title="Unique Entropy Over Time - Plot 1", x_axis_label="Time", y_axis_label="Unique Entropy", width=700, height=400)

# # # Create Plot 2 (Number of Unique Expressions - Datashader)
# # p2 = figure(title="Number of Unique Expressions Over Time - Plot 2", x_axis_label="Time", y_axis_label="Number of Unique Expressions", width=700, height=400)


# # # Experiment table selector
# # experiment_select = Select(title="Select Experiment Table", value=current_table, options=experiment_tables)

# # # Layout (Stacks the plots vertically)
# # layout = column(
# #     Div(text="<h1>Lambda Expression Analysis Tool</h1>", width=400),
# #     experiment_select,
# #     p1,
# #     p2  # Plots will be displayed one below the other
# # )

# # experiment_select.on_change('value', update_data)

# # curdoc().add_root(layout)







from bokeh.models import ColumnDataSource, Select
from bokeh.plotting import figure, curdoc
from bokeh.layouts import column, row
import sqlite3
import pandas as pd

# Globals
db_name = 'src/alchemy_data.db'
source1 = ColumnDataSource(data=dict(time_step=[], unique_entropy=[]))
source2 = ColumnDataSource(data=dict(time_step=[], unique_expressions=[]))

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

# Initial setup
initial_table = experiment_tables[0]
df = load_data_from_sqlite(db_name, initial_table)
source1.data = dict(
    time_step=df['id'].tolist(),
    unique_entropy=df['unique_entropy'].tolist()
)
source2.data = dict(
    time_step=df['id'].tolist(),
    unique_expressions=df['unique_expressions'].tolist()
)

def update_data(attr, old, new):
    print(f"Updating to table: {experiment_select.value}")
    df = load_data_from_sqlite(db_name, experiment_select.value)
    print(f"Retrieved {len(df)} rows")
    if not df.empty:
        source1.data = dict(
            time_step=df['id'].tolist(),
            unique_entropy=df['unique_entropy'].tolist()
        )
        source2.data = dict(
            time_step=df['id'].tolist(),
            unique_expressions=df['unique_expressions'].tolist()
        )
        print(f"Source updated: {source1.data}")
    else:
        source1.data = dict(time_step=[], unique_entropy=[])
        source2.data = dict(time_step=[], unique_expressions=[])
        print("No data available for this table.")
    print("Update complete")

# Plot 1 (Unique Entropy Over Time)
p1 = figure(
    title="Unique Entropy Over Time",
    x_axis_label="Time",
    y_axis_label="Unique Entropy",
    width=800,
    height=400
)
p1.line('time_step', 'unique_entropy', source=source1, line_width=2, line_color="blue")

# Plot 2 (Number of Unique Expressions Over Time)
p2 = figure(
    title="Number of Unique Expressions Over Time",
    x_axis_label="Time",
    y_axis_label="Number of Unique Expressions",
    width=800,
    height=400
)
p2.line('time_step', 'unique_expressions', source=source2, line_width=2, line_color="green")

# Experiment table selector
experiment_select = Select(title="Select Experiment Table", value=initial_table, options=experiment_tables)
experiment_select.on_change('value', update_data)

# Layout (Stack both plots vertically)
layout = column(
    row(experiment_select),
    p1,
    p2
)

curdoc().add_root(layout)
curdoc().title = "Lambda Expression Analysis Tool"




# from bokeh.models import ColumnDataSource, Select
# from bokeh.plotting import figure, curdoc
# from bokeh.layouts import column, row
# import sqlite3
# import pandas as pd

# # Globals
# db_name = 'src/alchemy_data.db'
# source1 = ColumnDataSource(data=dict(time_step=[], unique_entropy=[]))
# source2 = ColumnDataSource(data=dict(time_step=[], unique_expressions=[]))

# def list_experiment_tables(db_name):
#     conn = sqlite3.connect(db_name)
#     try:
#         query = "SELECT name FROM sqlite_master WHERE type='table'"
#         tables = pd.read_sql_query(query, conn)['name'].tolist()
#         experiment_tables = [table for table in tables if table.startswith('experiment_')]
#     finally:
#         conn.close()
#     return experiment_tables

# def load_data_from_sqlite(db_name, table_name):
#     conn = sqlite3.connect(db_name)
#     try:
#         query = f"""
#         SELECT id, lambda_expression 
#         FROM {table_name}
#         ORDER BY id
#         """
#         df = pd.read_sql_query(query, conn)
#         # Calculate unique entropy
#         df['unique_entropy'] = [len(set(df['lambda_expression'].iloc[:i+1])) 
#                               for i in range(len(df))]
#         # Calculate number of unique expressions
#         df['unique_expressions'] = df['lambda_expression'].apply(lambda x: len(set(x.split())))  # Adjust as needed
#         return df
#     except Exception as e:
#         print(f"Database error: {e}")
#         return pd.DataFrame()
#     finally:
#         conn.close()

# # Get experiment tables
# experiment_tables = list_experiment_tables(db_name)
# if not experiment_tables:
#     raise ValueError(f"No experiment tables found in the database '{db_name}'")

# # Initial setup
# initial_table = experiment_tables[0]
# df = load_data_from_sqlite(db_name, initial_table)
# source1.data = dict(
#     time_step=df['id'].tolist(),
#     unique_entropy=df['unique_entropy'].tolist()
# )
# source2.data = dict(
#     time_step=df['id'].tolist(),
#     unique_expressions=df['unique_expressions'].tolist()
# )

# def update_data(attr, old, new):
#     print(f"Updating to table: {experiment_select.value}")
#     df = load_data_from_sqlite(db_name, experiment_select.value)
#     print(f"Retrieved {len(df)} rows")
#     if not df.empty:
#         source1.data = dict(
#             time_step=df['id'].tolist(),
#             unique_entropy=df['unique_entropy'].tolist()
#         )
#         source2.data = dict(
#             time_step=df['id'].tolist(),
#             unique_expressions=df['unique_expressions'].tolist()
#         )
#         print(f"Source updated: {source1.data}")
#     else:
#         source1.data = dict(time_step=[], unique_entropy=[])
#         source2.data = dict(time_step=[], unique_expressions=[])
#         print("No data available for this table.")
#     print("Update complete")

# # Plot 1 (Unique Entropy Over Time)
# p1 = figure(
#     title="Unique Entropy Over Time",
#     x_axis_label="Time",
#     y_axis_label="Unique Entropy",
#     width=800,
#     height=400
# )
# p1.line('time_step', 'unique_entropy', source=source1, line_width=2, line_color="blue")

# # Plot 2 (Number of Unique Expressions Over Time)
# p2 = figure(
#     title="Number of Unique Expressions Over Time",
#     x_axis_label="Time",
#     y_axis_label="Number of Unique Expressions",
#     width=800,
#     height=400
# )
# p2.line('time_step', 'unique_expressions', source=source2, line_width=2, line_color="green")

# # Experiment table selector
# experiment_select = Select(title="Select Experiment Table", value=initial_table, options=experiment_tables)
# experiment_select.on_change('value', update_data)

# # Layout (Stack both plots vertically)
# layout = column(
#     row(experiment_select),
#     p1,
#     p2
# )

# curdoc().add_root(layout)
# curdoc().title = "Lambda Expression Analysis Tool"


# from bokeh.io import curdoc
# from bokeh.models import ColumnDataSource, Select
# from bokeh.plotting import figure
# from bokeh.layouts import column, row
# import sqlite3
# import pandas as pd
# import datashader as ds
# import datashader.transfer_functions as tf
# from datashader import reductions as rd

# # Globals
# db_name = 'src/alchemy_data.db'
# source1 = ColumnDataSource(data=dict(time_step=[], unique_entropy=[]))

# def list_experiment_tables(db_name):
#     conn = sqlite3.connect(db_name)
#     try:
#         query = "SELECT name FROM sqlite_master WHERE type='table'"
#         tables = pd.read_sql_query(query, conn)['name'].tolist()
#         experiment_tables = [table for table in tables if table.startswith('experiment_')]
#     finally:
#         conn.close()
#     return experiment_tables

# def load_data_from_sqlite(db_name, table_name):
#     conn = sqlite3.connect(db_name)
#     try:
#         query = f"""
#         SELECT id, lambda_expression 
#         FROM {table_name}
#         ORDER BY id
#         """
#         df = pd.read_sql_query(query, conn)
#         df['unique_entropy'] = [len(set(df['lambda_expression'].iloc[:i+1])) 
#                               for i in range(len(df))]
#         return df
#     except Exception as e:
#         print(f"Database error: {e}")
#         return pd.DataFrame()
#     finally:
#         conn.close()

# # Get experiment tables
# experiment_tables = list_experiment_tables(db_name)
# if not experiment_tables:
#     raise ValueError(f"No experiment tables found in the database '{db_name}'")

# # Initial setup
# initial_table = experiment_tables[0]

# import colorcet as cc
# import datashader.transfer_functions as tf
# from datashader import reductions as rd
# import numpy as np
# from PIL import Image
# import io

# def update_data(attr, old, new):
#     print(f"Updating to table: {experiment_select.value}")
#     df = load_data_from_sqlite(db_name, experiment_select.value)
#     print(f"Retrieved {len(df)} rows")
    
#     if not df.empty:
#         # Use Datashader to render large datasets efficiently
#         canvas = ds.Canvas(plot_width=800, plot_height=400)
#         agg = canvas.points(df, 'id', 'unique_entropy', agg=rd.count())
        
#         # Apply color mapping
#         img = tf.shade(agg, cmap=cc.fire)  # Use colorcet's fire colormap
#         img_bokeh = tf.dynspread(img)  # Dynamically spread the image to avoid empty space
        
#         # Convert the Datashader image to a format Bokeh can handle
#         with io.BytesIO() as output:
#             img_bokeh.to_pil().save(output, format="PNG")
#             img_bokeh_url = output.getvalue()

#         # Update the source for Bokeh
#         source1.data = dict(time_step=df['id'].tolist(), unique_entropy=df['unique_entropy'].tolist())
        
#         # Now render the image using Bokeh's image_url
#         p1.image_url(url=[img_bokeh_url], x=0, y=0, w=800, h=400)

#         print(f"Source updated with {len(source1.data['time_step'])} points")
#     else:
#         source1.data = dict(time_step=[], unique_entropy=[])
#         print("No data available for this table.")
    
#     print("Update complete")


# # Plot using Datashader output (not directly Bokeh plot)
# p1 = figure(
#     title="Unique Entropy Over Time",
#     x_axis_label="Time",
#     y_axis_label="Unique Entropy",
#     width=800,
#     height=400
# )

# # Experiment table selector
# experiment_select = Select(title="Select Experiment Table", value=initial_table, options=experiment_tables)
# experiment_select.on_change('value', update_data)

# # Layout
# layout = column(
#     row(experiment_select),
#     p1
# )
# curdoc().add_root(layout)
# curdoc().title = "Lambda Expression Analysis Tool"
