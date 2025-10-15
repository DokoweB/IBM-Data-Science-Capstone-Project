import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px

# Load your data
URL = 'https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBM-DS0321EN-SkillsNetwork/datasets/spacex_launch_geo.csv'
spacex_df = pd.read_csv(URL)

# Calculate min and max payload values
min_payload = spacex_df['Payload Mass (kg)'].min()
max_payload = spacex_df['Payload Mass (kg)'].max()

# Get unique launch sites
launch_sites = spacex_df['Launch Site'].unique()

# Create dropdown options
dropdown_options = [{'label': 'All Sites', 'value': 'ALL'}]
dropdown_options.extend([{'label': site, 'value': site} for site in launch_sites])

# Initialize the Dash app
app = dash.Dash(__name__)

# App layout
app.layout = html.Div([
    html.H1("SpaceX Launch Success Dashboard", style={'textAlign': 'center'}),
    
    # Dropdown for launch sites
    dcc.Dropdown(
        id='site-dropdown',
        options=dropdown_options,
        value='ALL',
        placeholder="Select a Launch Site here",
        searchable=True
    ),
    
    html.Br(),
    
    # Range slider for payload
    html.Div([
        html.Label("Select Payload Range (kg):", style={'fontSize': 16}),
        dcc.RangeSlider(
            id='payload-slider',
            min=0,
            max=10000,
            step=1000,
            marks={
                0: '0 kg',
                2500: '2500',
                5000: '5000',
                7500: '7500',
                10000: '10000 kg'
            },
            value=[min_payload, max_payload]
        )
    ]),
    
    html.Br(),
    
    # Pie chart
    dcc.Graph(id='success-pie-chart'),
    
    html.Br(),
    
    # Scatter chart
    dcc.Graph(id='success-payload-scatter-chart')
])

# Callback for pie chart
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        success_count = spacex_df[spacex_df['class'] == 1].shape[0]
        failure_count = spacex_df[spacex_df['class'] == 0].shape[0]
        
        fig = px.pie(
            values=[success_count, failure_count],
            names=['Success', 'Failure'],
            title='Total Success Launches for All Sites'
        )
        return fig
    else:
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        success_count = filtered_df[filtered_df['class'] == 1].shape[0]
        failure_count = filtered_df[filtered_df['class'] == 0].shape[0]
        
        fig = px.pie(
            values=[success_count, failure_count],
            names=['Success', 'Failure'],
            title=f'Success vs Failure Launches for {entered_site}'
        )
        return fig

# Callback for scatter plot
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
     Input(component_id="payload-slider", component_property="value")]
)
def update_scatter_chart(selected_site, payload_range):
    low, high = payload_range
    filtered_df = spacex_df[(spacex_df['Payload Mass (kg)'] >= low) & 
                           (spacex_df['Payload Mass (kg)'] <= high)]
    
    if selected_site == 'ALL':
        fig = px.scatter(
            filtered_df,
            x='Payload Mass (kg)',
            y='class',
            color='Booster Version',
            title='Correlation between Payload and Success for All Sites',
            labels={'class': 'Launch Outcome', 'Payload Mass (kg)': 'Payload Mass (kg)'},
            hover_data=['Launch Site', 'Booster Version']
        )
    else:
        site_filtered_df = filtered_df[filtered_df['Launch Site'] == selected_site]
        fig = px.scatter(
            site_filtered_df,
            x='Payload Mass (kg)',
            y='class',
            color='Booster Version',
            title=f'Correlation between Payload and Success for {selected_site}',
            labels={'class': 'Launch Outcome', 'Payload Mass (kg)': 'Payload Mass (kg)'},
            hover_data=['Booster Version']
        )
    
    fig.update_layout(
        yaxis=dict(
            tickmode='array',
            tickvals=[0, 1],
            ticktext=['Failure', 'Success']
        )
    )
    
    return fig

# Run the app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8056, debug=True)