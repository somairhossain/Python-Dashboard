import time
import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output, callback_context

# ─── Data Loading (with TTL cache) ──────────────────────────────────────────
SHEET_NAME = 'ClickBD_Data'
SHEET_ID   = '1_TWU8G6FDjEhRaFxoAwo3jD93Ccmn6zGRuphyrqww2k'
URL        = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={SHEET_NAME}"

CACHE_TTL  = 300          # seconds (5 minutes); lower this if you want faster auto-refresh
_cache     = {"df": None, "ts": 0}

def load_data(force: bool = False) -> pd.DataFrame:
    """Return cached DataFrame, or re-fetch if stale / forced."""
    now = time.time()
    if force or _cache["df"] is None or (now - _cache["ts"]) > CACHE_TTL:
        df = pd.read_csv(URL)

        # Clean Month column
        valid_months = ['Jan','Feb','Mar','Apr','May','Jun',
                        'Jul','Aug','Sep','Oct','Nov','Dec']
        df['Month'] = df['Month'].astype(str).str.strip()
        df = df[df['Month'].isin(valid_months)]

        # Month number for sorting; Year as nullable int
        df['Month_Num'] = pd.to_datetime(df['Month'], format='%b').dt.month
        df['Year'] = (
            df['Year'].astype(str)
                      .str.extract(r'(\d{4})')
                      .astype(float)
                      .astype('Int64')
        )

        _cache["df"] = df
        _cache["ts"] = now

    return _cache["df"]

# Initial load at startup
load_data()

# ─── App ─────────────────────────────────────────────────────────────────────
app    = Dash(__name__)
server = app.server   # Render needs this

TITLE_STYLE = {
    'textAlign': 'center',
    'color': 'white',
    'fontSize': '48px',
    'fontWeight': 'bold',
    'padding': '20px',
    'marginBottom': '30px',
    'borderRadius': '12px',
    'background': 'linear-gradient(135deg, #ffdb00, #ff0053)',
    'boxShadow': '0px 4px 20px rgba(0,0,0,0.2)',
    'fontFamily': 'Segoe UI, sans-serif',
}

app.layout = html.Div([
    html.H1("CLICKBD Online Shop\nMonthly Sales Report", style=TITLE_STYLE),

    # ── Refresh button ────────────────────────────────────────────────────
    html.Div([
        html.Button(
            "🔄 Refresh Data",
            id='refresh-btn',
            n_clicks=0,
            style={
                'fontSize': '16px',
                'fontWeight': 'bold',
                'padding': '10px 28px',
                'borderRadius': '8px',
                'border': 'none',
                'background': 'linear-gradient(135deg, #00c6ff, #0072ff)',
                'color': 'white',
                'cursor': 'pointer',
                'boxShadow': '0 4px 12px rgba(0,114,255,0.35)',
            }
        ),
        html.Span(
            id='last-updated',
            style={'marginLeft': '16px', 'color': '#555', 'fontSize': '14px'}
        ),
    ], style={'marginBottom': '18px'}),

    # ── Filters ──────────────────────────────────────────────────────────
    html.Label("Select Year:", style={'fontWeight': 'bold'}),
    dcc.Dropdown(id='year-filter',  value='All', clearable=False,
                 style={'width': '300px'}),

    html.Label("Select Month:", style={'fontWeight': 'bold', 'marginTop': '10px'}),
    dcc.Dropdown(id='month-filter', value='All', clearable=False,
                 style={'width': '300px'}),

    # ── KPI ──────────────────────────────────────────────────────────────
    html.Div(id='qty-kpi', style={
        'fontFamily': 'Arial',
        'fontSize': '42px',
        'fontWeight': 'bold',
        'color': '#ffffff',
        'background': 'linear-gradient(135deg, #8E2DE2, #FF6B6B)',
        'padding': '25px',
        'borderRadius': '15px',
        'textAlign': 'center',
        'boxShadow': '0px 4px 15px rgba(0,0,0,0.2)',
        'margin': '25px auto',
        'width': '60%',
    }),

    # ── Charts ───────────────────────────────────────────────────────────
    html.Div([
        dcc.Graph(id='month-sales',
                  style={'width': '90%', 'height': '80vh', 'display': 'inline-block'})
    ]),
    html.Div([
        dcc.Graph(id='salesperson-sales',
                  style={'width': '95%', 'height': '80vh', 'display': 'inline-block'}),
        dcc.Graph(id='delivery-status',
                  style={'width': '95%', 'height': '80vh', 'display': 'inline-block'}),
    ]),
    html.Div([
        dcc.Graph(id='order-set-sales',
                  style={'width': '95%', 'height': '80vh', 'display': 'inline-block'}),
        dcc.Graph(id='country-sales',
                  style={'width': '95%', 'height': '80vh', 'display': 'inline-block'}),
    ]),
    html.Div([
        dcc.Graph(id='district-sales',
                  style={'width': '95%', 'height': '80vh', 'display': 'inline-block'}),
        dcc.Graph(id='category-sales',
                  style={'width': '95%', 'height': '80vh', 'display': 'inline-block'}),
    ]),
    html.Div([
        dcc.Graph(id='subcategory-sales',
                  style={'width': '95%', 'height': '80vh', 'display': 'inline-block'})
    ]),
])

# ─── Callback ────────────────────────────────────────────────────────────────
@app.callback(
    [Output('year-filter',       'options'),
     Output('month-filter',      'options'),
     Output('last-updated',      'children'),
     Output('qty-kpi',           'children'),
     Output('month-sales',       'figure'),
     Output('salesperson-sales', 'figure'),
     Output('delivery-status',   'figure'),
     Output('order-set-sales',   'figure'),
     Output('country-sales',     'figure'),
     Output('district-sales',    'figure'),
     Output('category-sales',    'figure'),
     Output('subcategory-sales', 'figure')],
    [Input('refresh-btn',  'n_clicks'),
     Input('year-filter',  'value'),
     Input('month-filter', 'value')],
)
def update_dashboard(n_clicks, selected_year, selected_month):
    ctx     = callback_context
    # Force a fresh fetch only when the Refresh button triggered this callback
    forced  = ctx.triggered and ctx.triggered[0]['prop_id'] == 'refresh-btn.n_clicks'
    df      = load_data(force=bool(forced))

    # ── Rebuild dropdown options from fresh data ──────────────────────────
    year_opts  = ([{'label': 'All', 'value': 'All'}] +
                  [{'label': int(y), 'value': y}
                   for y in sorted(df['Year'].dropna().unique())])
    month_opts = ([{'label': 'All', 'value': 'All'}] +
                  [{'label': m, 'value': m}
                   for m in ['Jan','Feb','Mar','Apr','May','Jun',
                              'Jul','Aug','Sep','Oct','Nov','Dec']
                   if m in df['Month'].unique()])

    last_upd = f"Last fetched: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(_cache['ts']))}"

    # ── Filter ────────────────────────────────────────────────────────────
    dff = df.copy()
    if selected_year and selected_year != 'All':
        dff = dff[dff['Year'] == selected_year]
    if selected_month and selected_month != 'All':
        dff = dff[dff['Month'] == selected_month]

    # ── KPI ──────────────────────────────────────────────────────────────
    if selected_year == 'All':
        kpi_text = f"📦 Total QTY (Overall): {dff['QTY'].sum():,}"
    elif selected_month == 'All':
        kpi_text = f"📦 Total QTY in {selected_year}: {dff['QTY'].sum():,}"
    else:
        kpi_text = f"📦 Total QTY in {selected_month} {selected_year}: {dff['QTY'].sum():,}"

    # ── Chart 1 – Monthly trend (always uses full df for comparison) ──────
    month_df = (
        df.groupby(['Year', 'Month', 'Month_Num'])['QTY']
          .sum().reset_index().sort_values('Month_Num')
    )
    fig1 = px.line(month_df, x='Month', y='QTY', color='Year',
                   markers=True, text='QTY',
                   title="Monthly Sales Trend by Year (QTY)")
    fig1.update_layout(
        plot_bgcolor='white', paper_bgcolor='white',
        font=dict(family="Arial", size=14, color="#2c3e50"),
        xaxis=dict(categoryorder='array',
                   categoryarray=['Jan','Feb','Mar','Apr','May','Jun',
                                  'Jul','Aug','Sep','Oct','Nov','Dec'],
                   showgrid=False),
        yaxis=dict(gridcolor='lightgrey'),
        legend_title_text='Year',
        margin=dict(l=40, r=40, t=60, b=40),
    )

    # ── Chart 2 – Sales Person ────────────────────────────────────────────
    fig2 = px.bar(dff.groupby('Sales Person')['QTY'].sum().reset_index(),
                  x='Sales Person', y='QTY', title="Sales Person Sales (QTY)",
                  color='Sales Person', text_auto=True,
                  color_discrete_sequence=px.colors.qualitative.Bold)

    # ── Chart 3 – Delivery Status (Pie) ──────────────────────────────────
    fig3 = px.pie(dff, names='Order Status', values='QTY',
                  title="Delivery Status",
                  color_discrete_sequence=px.colors.sequential.Sunsetdark)

    # ── Chart 4 – Order Set ───────────────────────────────────────────────
    fig4 = px.bar(dff.groupby('Order Set')['QTY'].sum().reset_index(),
                  x='Order Set', y='QTY', title="Order Set Sold (QTY)",
                  color='QTY', text_auto=True, color_continuous_scale='Turbo')

    # ── Chart 5 – Country ─────────────────────────────────────────────────
    fig5 = px.bar(dff.groupby('Order Country')['QTY'].sum().reset_index(),
                  x='Order Country', y='QTY', title="Country-wise Sales (QTY)",
                  color='Order Country', text_auto=True,
                  color_discrete_sequence=px.colors.qualitative.Pastel)

    # ── Chart 6 – District ────────────────────────────────────────────────
    fig6 = px.bar(dff.groupby('District')['QTY'].sum().reset_index(),
                  x='District', y='QTY', title="District-wise Sales (QTY)",
                  color='District', text_auto=True,
                  color_discrete_sequence=px.colors.qualitative.Vivid)

    # ── Chart 7 – Category ───────────────────────────────────────────────
    cat_df = dff[dff['Category'].notna() & (dff['Category'].str.lower() != 'null')]
    fig7 = px.bar(cat_df.groupby('Category')['QTY'].sum().reset_index(),
                  x='Category', y='QTY', title="Category-wise Sales (QTY)",
                  color='Category', text_auto=True,
                  color_discrete_sequence=px.colors.qualitative.Safe)

    # ── Chart 8 – Sub-Category ───────────────────────────────────────────
    sub_df = dff[dff['Sub-Category'].notna() & (dff['Sub-Category'].str.lower() != 'null')]
    fig8 = px.bar(sub_df.groupby('Sub-Category')['QTY'].sum().reset_index(),
                  x='Sub-Category', y='QTY', title="Sub-Category-wise Sales (QTY)",
                  color='Sub-Category', text_auto=True,
                  color_discrete_sequence=px.colors.qualitative.Set2)

    return (year_opts, month_opts, last_upd,
            kpi_text, fig1, fig2, fig3, fig4, fig5, fig6, fig7, fig8)


if __name__ == "__main__":
    app.run_server(host="0.0.0.0", port=8050, debug=False)
