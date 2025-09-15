import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output

# Load data
sheet_name = 'ClickBD_Data'
sheet_id = '1_TWU8G6FDjEhRaFxoAwo3jD93Ccmn6zGRuphyrqww2k'
url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
df = pd.read_csv(url)

# Clean Month column
df['Month'] = df['Month'].astype(str).str.strip()
valid_months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
df = df[df['Month'].isin(valid_months)]

# Add month number for sorting
df['Month_Num'] = pd.to_datetime(df['Month'], format='%b').dt.month

# Build dashboard
app = Dash(__name__)

app.layout = html.Div([
    html.H1("Sales Dashboard", style={'textAlign': 'center', 'color': '#333'}),

    # Dropdown filter
    html.Label("Select Month:", style={'fontWeight': 'bold'}),
    dcc.Dropdown(
    id='month-filter',
    options=[{'label': 'All', 'value': 'All'}] + 
            [{'label': m, 'value': m} for m in df['Month'].unique()],
    value='All',
    clearable=False,
    style={'width': '300px'}
    ),

    # KPI text for Total QTY
    html.Div(id='qty-kpi', style={
        'font-family' : 'Arial',
        'fontSize': '42px',
        'fontWeight': 'bold',
        'color': "#ffffff",
        'background': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        'padding': '25px',
        'borderRadius': '15px',
        'textAlign': 'center',
        'boxShadow': '0px 4px 15px rgba(0,0,0,0.2)',
        'margin': '25px auto',
        'width': '60%'
    }),

    # Graphs
    html.Div([
        dcc.Graph(id='month-sales', style={'width': '90%', 'display': 'inline-block'})
    ]),

    html.Div([
        dcc.Graph(id='salesperson-sales', style={'width': '48%', 'display': 'inline-block'}),
        dcc.Graph(id='delivery-status', style={'width': '48%', 'display': 'inline-block'})
    ]),

    html.Div([
        dcc.Graph(id='order-set-sales', style={'width': '48%', 'display': 'inline-block'}),
        dcc.Graph(id='country-sales', style={'width': '48%', 'display': 'inline-block'})
    ]),

    html.Div([
        dcc.Graph(id='district-sales', style={'width': '48%', 'display': 'inline-block'}),
        dcc.Graph(id='category-sales', style={'width': '48%', 'display': 'inline-block'})
    ]),

    html.Div([
        dcc.Graph(id='subcategory-sales', style={'width': '48%', 'display': 'inline-block'})
    ])
])

# Callbacks
@app.callback(
    [Output('qty-kpi', 'children'),
     Output('month-sales', 'figure'),
     Output('salesperson-sales', 'figure'),
     Output('delivery-status', 'figure'),
     Output('order-set-sales', 'figure'),
     Output('country-sales', 'figure'),
     Output('district-sales', 'figure'),
     Output('category-sales', 'figure'),
     Output('subcategory-sales', 'figure')],
    [Input('month-filter', 'value')]
)
def update_charts(selected_month):
    if selected_month == "All":
        dff = df.copy()
    else:
        dff = df[df['Month'] == selected_month]

    # 1. KPI text
    if selected_month == "All":
        kpi_text = f"📦 Total QTY (Overall): {dff['QTY'].sum()}"
        
        
    else:
        kpi_text = f"📦 Total QTY in {selected_month}: {dff['QTY'].sum()}"
    # 1. Month QTY
    month_df = df.groupby(['Month','Month_Num'])['QTY'].sum().reset_index().sort_values('Month_Num')
    fig1 = px.line(month_df, x='Month', y='QTY',
                   title="Monthly Sales Trend (QTY)",
                   markers=True,
                   text='QTY')
    fig1.update_traces(line=dict(color="#b92959", width=3), textposition="top center")
    fig1.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family="Arial", size=14, color="#2c3e50"),
        xaxis=dict(showgrid=False),
        yaxis=dict(gridcolor='lightgrey'),
        margin=dict(l=40, r=40, t=60, b=40)
    )
    
    # 2. Sales Person QTY
    fig2 = px.bar(dff.groupby('Sales Person')['QTY'].sum().reset_index(),
                  x='Sales Person', y='QTY', title="Sales Person Sales (QTY)",
                  color='Sales Person', color_discrete_sequence=px.colors.qualitative.Bold)

    # 3. Delivery Status (Pie)
    fig3 = px.pie(dff, names='Order Status', values='QTY',
                  title="Delivery Status",
                  color_discrete_sequence=px.colors.sequential.Sunsetdark)

    # 4. Order Set Sales
    fig4 = px.bar(dff.groupby('Order Set')['QTY'].sum().reset_index(),
                  x='Order Set', y='QTY', title="Order Set Sold (QTY)",
                  color='QTY', color_continuous_scale='Turbo')

    # 5. Country wise QTY
    fig5 = px.bar(dff.groupby('Order Country')['QTY'].sum().reset_index(),
                  x='Order Country', y='QTY', title="Country-wise Sales (QTY)",
                  color='Order Country', color_discrete_sequence=px.colors.qualitative.Pastel)

    # 6. District wise QTY
    fig6 = px.bar(dff.groupby('District')['QTY'].sum().reset_index(),
                  x='District', y='QTY', title="District-wise Sales (QTY)",
                  color='District', color_discrete_sequence=px.colors.qualitative.Vivid)

    # 7. Category wise QTY (remove null)
    cat_df = dff[dff['Category'].notna() & (dff['Category'].str.lower() != 'null')]
    fig7 = px.bar(cat_df.groupby('Category')['QTY'].sum().reset_index(),
                x='Category', y='QTY', title="Category-wise Sales (QTY)",
              color='Category', color_discrete_sequence=px.colors.qualitative.Safe)

    # 8. Sub-Category wise QTY (remove null)
    subcat_df = dff[dff['Sub-Category'].notna() & (dff['Sub-Category'].str.lower() != 'null')]
    fig8 = px.bar(subcat_df.groupby('Sub-Category')['QTY'].sum().reset_index(),
              x='Sub-Category', y='QTY', title="Sub-Category-wise Sales (QTY)",
              color='Sub-Category', color_discrete_sequence=px.colors.qualitative.Set2)

    return kpi_text, fig1, fig2, fig3, fig4, fig5, fig6, fig7, fig8

if __name__ == '__main__':
    app.run(debug=True)
