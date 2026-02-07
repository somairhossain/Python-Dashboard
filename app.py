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
df['Year'] = df['Year'].astype(str).str.extract(r'(\d{4})').astype(float).astype('Int64')
# Build dashboard
app = Dash(__name__)
server = app.server  # 👈 Render needs this

app.layout = html.Div([
    html.H1("CLICKBD Online Shop\n Monthly Sales Report", 
            style={
        'textAlign': 'center',
        'color': 'white',
        'fontSize': '48px',
        'fontWeight': 'bold',
        'padding': '20px',
        'marginBottom': '30px',
        'borderRadius': '12px',
        'background': 'linear-gradient(135deg, #ffdb00, #ff0053)',
        'boxShadow': '0px 4px 20px rgba(0,0,0,0.2)',
        'fontFamily': 'Segoe UI, sans-serif'
            }),

    # Dropdown filter
    html.Label("Select Year:", style={'fontWeight': 'bold'}),
dcc.Dropdown(
    id='year-filter',
    options=[{'label': 'All', 'value': 'All'}] + 
            [{'label': y, 'value': y} for y in sorted(df['Year'].unique())],
    value='All',
    clearable=False,
    style={'width': '300px'}
),
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
        'background': 'linear-gradient(135deg, #8E2DE2, #FF6B6B)',
        'padding': '25px',
        'borderRadius': '15px',
        'textAlign': 'center',
        'boxShadow': '0px 4px 15px rgba(0,0,0,0.2)',
        'margin': '25px auto',
        'width': '60%'
    }),

    # Graphs
    html.Div([
        dcc.Graph(id='month-sales', style={'width': '90%', 'height' : '80vh' , 'display': 'inline-block'})
    ]),

    html.Div([
        dcc.Graph(id='salesperson-sales', style={'width': '95%', 'height' : '80vh' , 'display': 'inline-block'}),
        dcc.Graph(id='delivery-status', style={'width': '95%', 'height' : '80vh', 'display': 'inline-block'})
    ]),

    html.Div([
        dcc.Graph(id='order-set-sales', style={'width': '95%', 'height' : '80vh', 'display': 'inline-block'}),
        dcc.Graph(id='country-sales', style={'width': '95%', 'height' : '80vh', 'display': 'inline-block'})
    ]),

    html.Div([
        dcc.Graph(id='district-sales', style={'width': '95%', 'height' : '80vh', 'display': 'inline-block'}),
        dcc.Graph(id='category-sales', style={'width': '95%', 'height' : '80vh', 'display': 'inline-block'})
    ]),

    html.Div([
        dcc.Graph(id='subcategory-sales', style={'width': '95%', 'height' : '80vh', 'display': 'inline-block'})
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
    [Input('year-filter', 'value'),
     Input('month-filter', 'value')]
)
def update_charts(selected_year, selected_month):
    dff = df.copy()
    
    #Apply Year filter
    if selected_year != 'All':
        dff = dff[dff['Year'] == selected_year]

    #Apply Month Filter
    if selected_month != "All":
        dff = dff[dff['Month'] == selected_month]

    # 1. KPI text
    if selected_year == "All":
        kpi_text = f"📦 Total QTY (Overall): {dff['QTY'].sum()}"
    elif selected_year != "All" and selected_month == "All":
        kpi_text = f"📦 Total QTY in {selected_year}: {dff['QTY'].sum()}"
    elif selected_year != "All" and selected_month != "All":
        kpi_text = f"📦 Total QTY in {selected_month} {selected_year}: {dff['QTY'].sum()}"    
    else:
        kpi_text = f"📦 Total QTY in {selected_month}: {dff['QTY'].sum()}"
    # 2. Month QTY
    # month_df = df.groupby(['Month','Month_Num'])['QTY'].sum().reset_index().sort_values('Month_Num')
    trend_df = df.groupby(
    ['Year', 'Month', 'Month_Num'], as_index=False
)['QTY'].sum()

# trend_df = trend_df.sort_values('Month_Num')

# fig1 = px.line(
#     trend_df,
#     x='Month',
#     y='QTY',
#     color='Year',          # separate line per year
#     markers=True,
#     title="Monthly Sales Trend by Year (QTY)",
#     category_orders={
#         'Month': valid_months
#     }
# )
#     fig1.update_traces(line=dict(color="#b92959", width=3), textposition="top center")
#     )

# fig1.update_layout(
#     plot_bgcolor='white',
#     paper_bgcolor='white',
#     font=dict(family="Arial", size=14, color="#2c3e50"),
#     xaxis=dict(showgrid=False),
#     yaxis=dict(gridcolor='lightgrey'),
#     legend_title_text='Year',
#     margin=dict(l=40, r=40, t=60, b=40)
# )

    # 2. Monthly Sales Trend (ALL Years – Ignore Filters)

trend_df = df.groupby(
    ['Year', 'Month', 'Month_Num'], as_index=False
)['QTY'].sum()

trend_df = trend_df.sort_values('Month_Num')

# 🔑 CRITICAL FIX: convert Year to string for categorical coloring
trend_df['Year'] = trend_df['Year'].astype(str)

fig1 = px.line(
    trend_df,
    x='Month',
    y='QTY',
    color='Year',                 # now treated as categorical
    markers=True,
    title="Monthly Sales Trend by Year (QTY)",
    category_orders={'Month': valid_months}
)

fig1.update_layout(
    plot_bgcolor='white',
    paper_bgcolor='white',
    font=dict(family="Arial", size=14, color="#2c3e50"),
    xaxis=dict(showgrid=False),
    yaxis=dict(gridcolor='lightgrey'),
    legend_title_text='Year',
    margin=dict(l=40, r=40, t=60, b=40)
)
    
    # 4. Sales Person QTY
    fig2 = px.bar(dff.groupby('Sales Person')['QTY'].sum().reset_index(),
                  x='Sales Person', y='QTY', title="Sales Person Sales (QTY)",
                  color='Sales Person', text_auto = True, color_discrete_sequence=px.colors.qualitative.Bold)

    # 5. Delivery Status (Pie)
    fig3 = px.pie(dff, names='Order Status', values='QTY',
                  title="Delivery Status",
                  color_discrete_sequence=px.colors.sequential.Sunsetdark)

    # 6. Order Set Sales
    fig4 = px.bar(dff.groupby('Order Set')['QTY'].sum().reset_index(),
                  x='Order Set', y='QTY', title="Order Set Sold (QTY)",
                  color='QTY', text_auto = True, color_continuous_scale='Turbo')

    # 7. Country wise QTY
    fig5 = px.bar(dff.groupby('Order Country')['QTY'].sum().reset_index(),
                  x='Order Country', y='QTY', title="Country-wise Sales (QTY)",
                  color='Order Country', text_auto = True, color_discrete_sequence=px.colors.qualitative.Pastel)

    # 8. District wise QTY
    fig6 = px.bar(dff.groupby('District')['QTY'].sum().reset_index(),
                  x='District', y='QTY', title="District-wise Sales (QTY)",
                  color='District', text_auto = True, color_discrete_sequence=px.colors.qualitative.Vivid)

    # 9. Category wise QTY (remove null)
    cat_df = dff[dff['Category'].notna() & (dff['Category'].str.lower() != 'null')]
    fig7 = px.bar(cat_df.groupby('Category')['QTY'].sum().reset_index(),
                x='Category', y='QTY', title="Category-wise Sales (QTY)",
              color='Category', text_auto = True, color_discrete_sequence=px.colors.qualitative.Safe)

    # 10. Sub-Category wise QTY (remove null)
    subcat_df = dff[dff['Sub-Category'].notna() & (dff['Sub-Category'].str.lower() != 'null')]
    fig8 = px.bar(subcat_df.groupby('Sub-Category')['QTY'].sum().reset_index(),
              x='Sub-Category', y='QTY', title="Sub-Category-wise Sales (QTY)",
              color='Sub-Category', text_auto = True, color_discrete_sequence=px.colors.qualitative.Set2)

    return kpi_text, fig1, fig2, fig3, fig4, fig5, fig6, fig7, fig8

if __name__ == "__main__":
    app.run_server(host="0.0.0.0", port=8050)













