# panel serve --show --autoreload offline_dashboard_panel.py

from base_setup import sample, reference, binned, normalized, get_sample_plot
import plotly.graph_objects as go
import panel as pn
pn.extension()

start_button = pn.widgets.Button(name='Resume Refreshing')
def start_stop(_):
    if start_button.clicks % 2 == 1:
        start_button.name = "Stop Refreshing"
        button_row[1] = pn.pane.GIF('assets/processing.gif', width=25)
    else:
        start_button.name = "Resume Refreshing"
        button_row[1] = "stop!"
start_button.on_click(start_stop)

button_row = pn.Row(start_button, "stop!")
row1 = pn.Column('<h1>Offline Divergent data reduction for Amor</h1>', 
                 button_row,
                 width=2000)

col1 = pn.Column("<h2>Reduction Result</h2>",
                      pn.pane.Plotly(go.Figure(get_sample_plot())), # I had to convert FigureWidget to Figure.
                      binned.bins.sum().plot().fig,
                      binned._repr_html_(), 
                      "<h2>Offline Data</h2>",
                      sample.hist(tof=40).plot().fig,
                      sample._repr_html_(),
                      reference._repr_html_(),
                      width=1000)

col2 = pn.Column("<h2>Workflow</h2>",
                 pn.pane.PNG('assets/workflow_graph.png'),
                 "<h2>Reference Calibration Result</h2>",
                 pn.pane.PNG('assets/calibration_result.png'),
                 "<h2>Normalization Result</h2>",
                 normalized.plot(norm='log').fig,
                 normalized.mean('detector_id').plot(norm='log').fig
                 )

row2 = pn.Row(col1, col2)
first_app = pn.Column(row1, row2)
first_app.servable()
