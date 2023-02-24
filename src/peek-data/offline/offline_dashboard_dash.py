# python offline_dashboard_dash.py

from dash import Dash, html, Input, Output, dcc
from base_setup import sample, reference, binned, get_sample_plot
import dash_gif_component as gif
app = Dash(__name__)


column1 = html.Div([
    html.H2(children='Interactive Plot'),
    dcc.Graph(figure=get_sample_plot()),
    html.H2(children='Reduction Result'),
    html.Img(src='assets/binned.png', width=600),
    html.Iframe(srcDoc=binned._repr_html_(), width=1000, height=450, style={'border': 0}),
    html.H2(children='Offline Data'),
    html.Img(src='assets/sample_raw_2d.png', width=600),
    html.Iframe(srcDoc=sample._repr_html_(), width=1000, height=450, style={'border': 0}),
    html.Iframe(srcDoc=reference._repr_html_(), width=1000, height=450, style={'border': 0})
], style={'display': 'flex', 'flex-direction': 'column', 'padding': '30px'})

column2 = html.Div([
    html.H2(children='Workflow'),
    html.Img(src='assets/workflow_graph.png', width=600),
    html.H2(children='Reference Calibration Result'),
    html.Img(src='assets/calibration_result.png', width=600),
    html.H2(children='Normalization Result'),
    html.Img(src='assets/normalized_2d_scatter.png', width=600),
    html.Img(src='assets/normalized_mean.png', width=600)
], style={'display': 'flex', 'flex-direction': 'column', 'padding': '30px'})

processing_gif = gif.GifPlayer(gif='assets/processing.gif', still='assets/processing.png', autoplay=True)

app.layout = html.Div([
    html.H1(children='Offline Divergent data reduction for Amor'),
    html.Div(children=[
        html.Button('Stop Refreshing', id='refreshing', n_clicks=0),
        html.Div(id='refreshing-status', children=processing_gif, style={'width': '25px', 'margin-left': '20px'})
    ], style={'display': 'flex', 'flex-direction': 'row'}),
    html.Div([column1, column2], style={'display': 'flex', 'flex-direction': 'row'})
])

@app.callback(
    Output('refreshing', 'children'),
    Output('refreshing-status', 'children'),
    Input('refreshing', 'n_clicks')
)
def update_refreshing_status(n_clicks):
    if n_clicks%2 == 1:
        return "Resume Refreshing", "stop!"
    return 'Stop Refreshing', processing_gif

if __name__ == '__main__':
    app.run_server(debug=True)