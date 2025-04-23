import pandas as pd
import dash
from dash import dcc, html, Input, Output
import plotly.express as px

# Load Data
df = pd.read_excel('shark tank.xlsx', sheet_name='table')

# Clean column names
df.columns = df.columns.str.strip()

# Replace Deal values for clarity
df['Deal'] = df['Deal'].replace({'Y': 'Deal Closed', 'N': 'No Deal'})

# List of Shark Names (adjust based on actual column headers)
sharks = ['Aman Gupta', 'Ashneer Grover', 'Vineeta Singh',
          'Peyush Bansal', 'Namita Thapar', 'Anupam Mittal', 'Ghazal Alagh']

# Initialize the Dash app
app = dash.Dash(__name__)
app.title = "SHARK TANK"

# App Layout
app.layout = html.Div([
    html.H1("SHARK TANK", style={"textAlign": "center"}),

    # Filters
    html.Div([
        html.Div([
            html.Label("Select Sector:"),
            dcc.Dropdown(
                options=[{'label': sec, 'value': sec} for sec in sorted(df['Sector'].dropna().unique())],
                id='sector-filter',
                placeholder="All Sectors"
            )
        ], style={'width': '48%', 'display': 'inline-block'}),

        html.Div([
            html.Label("Select Deal Status:"),
            dcc.Dropdown(
                options=[{'label': status, 'value': status} for status in df['Deal'].unique()],
                id='deal-filter',
                placeholder="All Deals"
            )
        ], style={'width': '48%', 'display': 'inline-block'})
    ], style={'padding': 10}),

    # KPIs
    html.Div([
        html.Div(id='total-pitches', style={'width': '32%', 'display': 'inline-block'}),
        html.Div(id='total-deals', style={'width': '32%', 'display': 'inline-block'}),
        html.Div(id='total-investment', style={'width': '32%', 'display': 'inline-block'})
    ], style={'textAlign': 'center', 'padding': 20}),

    # Graphs
    html.Div([
        dcc.Graph(id='deal-status-pie'),
        dcc.Graph(id='top-sharks-bar'),
        dcc.Graph(id='top-sectors-bar')
    ])
])

# Callback to update dashboard based on filters
@app.callback(
    [Output('total-pitches', 'children'),
     Output('total-deals', 'children'),
     Output('total-investment', 'children'),
     Output('deal-status-pie', 'figure'),
     Output('top-sharks-bar', 'figure'),
     Output('top-sectors-bar', 'figure')],
    [Input('sector-filter', 'value'),
     Input('deal-filter', 'value')]
)
def update_dashboard(selected_sector, selected_deal):
    # Filter data
    filtered_df = df.copy()
    if selected_sector:
        filtered_df = filtered_df[filtered_df['Sector'] == selected_sector]
    if selected_deal:
        filtered_df = filtered_df[filtered_df['Deal'] == selected_deal]

    # KPIs
    total_pitches = f"Total Pitches: {filtered_df.shape[0]}"
    total_deals = f"Total Deals: {(filtered_df['Deal'] == 'Deal Closed').sum()}"
    total_investment = f"Total Investment: {filtered_df[sharks].fillna(0).sum().sum():.2f} Lakhs"

    # Deal Status Pie Chart
    deal_status_fig = px.pie(
        filtered_df,
        names='Deal',
        title='Deal Status Distribution'
    )

    # Top Sharks Bar Chart
    shark_investments = filtered_df[sharks].fillna(0).sum().sort_values(ascending=False)
    shark_fig = px.bar(
        x=shark_investments.index,
        y=shark_investments.values,
        title='Top Sharks by Investment',
        labels={'x': 'Sharks', 'y': 'Investment (Lakhs)'}
    )

    # Top Sectors Bar Chart
    top_sectors = filtered_df['Sector'].value_counts().nlargest(10)
    sectors_fig = px.bar(
        x=top_sectors.index,
        y=top_sectors.values,
        title='Top Sectors by Number of Pitches',
        labels={'x': 'Sector', 'y': 'Number of Pitches'}
    )

    return total_pitches, total_deals, total_investment, deal_status_fig, shark_fig, sectors_fig

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
