import time
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output, callback_context, State
import dash_bootstrap_components as dbc

# ─── Data Loading (TTL cache) ────────────────────────────────────────────────
SHEET_NAME = 'ClickBD_Data'
SHEET_ID   = '1_TWU8G6FDjEhRaFxoAwo3jD93Ccmn6zGRuphyrqww2k'
URL        = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={SHEET_NAME}"
CACHE_TTL  = 300
_cache     = {"df": None, "ts": 0}

VALID_MONTHS = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']

def load_data(force=False):
    now = time.time()
    if force or _cache["df"] is None or (now - _cache["ts"]) > CACHE_TTL:
        df = pd.read_csv(URL)
        df['Month'] = df['Month'].astype(str).str.strip()
        df = df[df['Month'].isin(VALID_MONTHS)]
        df['Month_Num'] = pd.to_datetime(df['Month'], format='%b').dt.month
        df['Year'] = df['Year'].astype(str).str.extract(r'(\d{4})').astype(float).astype('Int64')
        _cache["df"] = df
        _cache["ts"] = now
    return _cache["df"]

load_data()

# ─── Theme ────────────────────────────────────────────────────────────────────
BG       = '#0a0e1a'
SURFACE  = '#111827'
CARD     = '#161d2e'
BORDER   = '#1e2d45'
CYAN     = '#00e5ff'
CORAL    = '#ff4d6d'
GOLD     = '#ffd166'
GREEN    = '#06d6a0'
TEXT     = '#e2e8f0'
MUTED    = '#64748b'

PLOTLY_LAYOUT = dict(
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    font=dict(family="'JetBrains Mono', monospace", size=12, color=TEXT),
    margin=dict(l=16, r=16, t=48, b=16),
    legend=dict(bgcolor='rgba(0,0,0,0)', font=dict(color=TEXT)),
    xaxis=dict(gridcolor=BORDER, linecolor=BORDER, tickfont=dict(color=MUTED)),
    yaxis=dict(gridcolor=BORDER, linecolor=BORDER, tickfont=dict(color=MUTED)),
    coloraxis_colorbar=dict(tickfont=dict(color=TEXT)),
    title=dict(font=dict(family="'Syne', sans-serif", size=15, color=TEXT), x=0.02),
    hoverlabel=dict(bgcolor=SURFACE, font_color=TEXT, bordercolor=BORDER),
)

CHART_COLORS = [CYAN, CORAL, GOLD, GREEN, '#c77dff', '#ff9f1c', '#4cc9f0', '#f72585']

# ─── App ──────────────────────────────────────────────────────────────────────
app    = Dash(__name__, external_stylesheets=[
    dbc.themes.BOOTSTRAP,
    "https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=JetBrains+Mono:wght@300;400;500&display=swap"
])

server = app.server

# ─── Custom CSS ───────────────────────────────────────────────────────────────
CUSTOM_CSS = f"""
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body, html {{
    background: {BG};
    color: {TEXT};
    font-family: 'JetBrains Mono', monospace;
    min-height: 100vh;
    overflow-x: hidden;
}}
::-webkit-scrollbar {{ width: 6px; }}
::-webkit-scrollbar-track {{ background: {BG}; }}
::-webkit-scrollbar-thumb {{ background: {BORDER}; border-radius: 3px; }}

/* Grain overlay */
body::before {{
    content: '';
    position: fixed;
    inset: 0;
    background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)' opacity='0.04'/%3E%3C/svg%3E");
    pointer-events: none;
    z-index: 0;
    opacity: 0.5;
}}

.dash-graph {{ border-radius: 0 !important; }}

/* Header */
.header-bar {{
    background: linear-gradient(135deg, {SURFACE} 0%, #0d1526 100%);
    border-bottom: 1px solid {BORDER};
    padding: 0;
    position: sticky;
    top: 0;
    z-index: 100;
    backdrop-filter: blur(12px);
}}
.header-inner {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 14px 24px;
    flex-wrap: wrap;
    gap: 12px;
}}
.brand {{
    display: flex;
    align-items: center;
    gap: 14px;
}}
.brand-icon {{
    width: 42px; height: 42px;
    background: linear-gradient(135deg, {CYAN}, {CORAL});
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 20px;
    flex-shrink: 0;
}}
.brand-title {{
    font-family: 'Syne', sans-serif;
    font-weight: 800;
    font-size: 20px;
    color: {TEXT};
    line-height: 1.1;
    letter-spacing: -0.5px;
}}
.brand-sub {{
    font-size: 10px;
    color: {MUTED};
    letter-spacing: 2px;
    text-transform: uppercase;
    font-weight: 300;
}}
.header-actions {{
    display: flex;
    align-items: center;
    gap: 12px;
    flex-wrap: wrap;
}}
.live-badge {{
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 5px 12px;
    border-radius: 20px;
    border: 1px solid {BORDER};
    font-size: 11px;
    color: {MUTED};
    background: {BG};
    white-space: nowrap;
}}
.live-dot {{
    width: 6px; height: 6px;
    border-radius: 50%;
    background: {GREEN};
    animation: pulse-dot 2s infinite;
}}
@keyframes pulse-dot {{
    0%, 100% {{ opacity: 1; transform: scale(1); }}
    50% {{ opacity: 0.5; transform: scale(0.8); }}
}}
.refresh-btn {{
    background: linear-gradient(135deg, {CYAN}22, {CYAN}11) !important;
    border: 1px solid {CYAN}55 !important;
    color: {CYAN} !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 12px !important;
    padding: 7px 16px !important;
    border-radius: 8px !important;
    cursor: pointer !important;
    transition: all 0.2s !important;
    white-space: nowrap;
}}
.refresh-btn:hover {{
    background: {CYAN}22 !important;
    border-color: {CYAN} !important;
    box-shadow: 0 0 16px {CYAN}33 !important;
}}

/* Filter bar */
.filter-bar {{
    background: {SURFACE};
    border-bottom: 1px solid {BORDER};
    padding: 14px 24px;
    display: flex;
    align-items: center;
    gap: 16px;
    flex-wrap: wrap;
}}
.filter-label {{
    font-size: 10px;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: {MUTED};
    white-space: nowrap;
}}
.Select-control, .Select-menu-outer {{
    background: {CARD} !important;
    border-color: {BORDER} !important;
    color: {TEXT} !important;
    border-radius: 8px !important;
}}
.Select-value-label, .Select-placeholder {{ color: {TEXT} !important; }}
.Select-option {{ background: {CARD} !important; color: {TEXT} !important; }}
.Select-option:hover {{ background: {BORDER} !important; }}
.VirtualizedSelectOption {{ background: {CARD} !important; color: {TEXT} !important; }}

/* KPI row */
.kpi-row {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 16px;
    padding: 20px 24px;
}}
.kpi-card {{
    background: {CARD};
    border: 1px solid {BORDER};
    border-radius: 12px;
    padding: 20px;
    position: relative;
    overflow: hidden;
    transition: transform 0.2s, box-shadow 0.2s;
}}
.kpi-card:hover {{
    transform: translateY(-2px);
    box-shadow: 0 8px 32px rgba(0,0,0,0.4);
}}
.kpi-card::before {{
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
}}
.kpi-card.cyan::before  {{ background: linear-gradient(90deg, {CYAN}, transparent); }}
.kpi-card.coral::before {{ background: linear-gradient(90deg, {CORAL}, transparent); }}
.kpi-card.gold::before  {{ background: linear-gradient(90deg, {GOLD}, transparent); }}
.kpi-card.green::before {{ background: linear-gradient(90deg, {GREEN}, transparent); }}
.kpi-icon {{
    font-size: 24px;
    margin-bottom: 10px;
}}
.kpi-value {{
    font-family: 'Syne', sans-serif;
    font-size: 32px;
    font-weight: 800;
    line-height: 1;
    margin-bottom: 4px;
}}
.kpi-value.cyan  {{ color: {CYAN}; }}
.kpi-value.coral {{ color: {CORAL}; }}
.kpi-value.gold  {{ color: {GOLD}; }}
.kpi-value.green {{ color: {GREEN}; }}
.kpi-label {{
    font-size: 10px;
    color: {MUTED};
    letter-spacing: 1.5px;
    text-transform: uppercase;
}}
.kpi-sub {{
    font-size: 11px;
    color: {MUTED};
    margin-top: 6px;
}}

/* Section */
.section-header {{
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 20px 24px 8px;
}}
.section-label {{
    font-family: 'Syne', sans-serif;
    font-size: 13px;
    font-weight: 700;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: {MUTED};
}}
.section-line {{
    flex: 1;
    height: 1px;
    background: {BORDER};
}}

/* Chart grid */
.chart-grid {{
    display: grid;
    gap: 16px;
    padding: 0 24px 16px;
}}
.chart-grid.cols-1 {{ grid-template-columns: 1fr; }}
.chart-grid.cols-2 {{ grid-template-columns: repeat(2, 1fr); }}
.chart-card {{
    background: {CARD};
    border: 1px solid {BORDER};
    border-radius: 12px;
    overflow: hidden;
    transition: box-shadow 0.2s;
}}
.chart-card:hover {{
    box-shadow: 0 4px 24px rgba(0,0,0,0.5);
}}

/* Footer */
.footer {{
    border-top: 1px solid {BORDER};
    padding: 20px 24px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 10px;
}}
.footer-text {{
    font-size: 11px;
    color: {MUTED};
}}

/* Mobile */
@media (max-width: 768px) {{
    .header-inner {{ padding: 12px 16px; }}
    .brand-title {{ font-size: 16px; }}
    .filter-bar {{ padding: 12px 16px; flex-direction: column; align-items: flex-start; }}
    .kpi-row {{ padding: 12px 16px; grid-template-columns: repeat(2, 1fr); gap: 10px; }}
    .kpi-value {{ font-size: 24px; }}
    .chart-grid {{ padding: 0 16px 12px; }}
    .chart-grid.cols-2 {{ grid-template-columns: 1fr; }}
    .section-header {{ padding: 14px 16px 6px; }}
    .footer {{ padding: 16px; }}
}}
@media (max-width: 480px) {{
    .kpi-row {{ grid-template-columns: 1fr 1fr; }}
    .kpi-value {{ font-size: 20px; }}
    .kpi-card {{ padding: 14px; }}
    .brand-sub {{ display: none; }}
}}

/* Dropdown override for Dash */
.dash-dropdown .Select-control {{
    background: {CARD} !important;
    border: 1px solid {BORDER} !important;
    border-radius: 8px !important;
    min-height: 36px !important;
}}
.dash-dropdown .Select-value-label {{ color: {TEXT} !important; font-size: 13px !important; }}
.dash-dropdown .Select-placeholder {{ color: {MUTED} !important; font-size: 13px !important; }}
.dash-dropdown .Select-arrow {{ border-top-color: {MUTED} !important; }}
.dash-dropdown .Select-menu-outer {{
    background: {SURFACE} !important;
    border: 1px solid {BORDER} !important;
    border-radius: 8px !important;
    margin-top: 2px !important;
    box-shadow: 0 8px 32px rgba(0,0,0,0.5) !important;
}}
.dash-dropdown .Select-option {{
    background: {SURFACE} !important;
    color: {TEXT} !important;
    font-size: 13px !important;
    padding: 8px 12px !important;
}}
.dash-dropdown .Select-option.is-focused {{
    background: {BORDER} !important;
}}
.dash-dropdown .Select-option.is-selected {{
    background: {CYAN}22 !important;
    color: {CYAN} !important;
}}
.dash-dropdown .Select-input input {{
    color: {TEXT} !important;
}}
"""
# 2. Inject your CUSTOM_CSS variable into the HTML template
# Note: We use double curly braces {{ }} for Dash placeholders so Python doesn't get confused
app.index_string = f'''
<!DOCTYPE html>
<html>
    <head>
        {{%metas%}}
        <title>ClickBD Sales Intelligence</title>
        {{%favicon%}}
        {{%css%}}
        <style>
            {CUSTOM_CSS}
        </style>
    </head>
    <body>
        {{%app_entry%}}
        <footer>
            {{%config%}}
            {{%scripts%}}
            {{%renderer%}}
        </footer>
    </body>
</html>
'''

def make_chart_card(graph_id, height='420px'):
    return html.Div(
        dcc.Graph(id=graph_id, config={'displayModeBar': False},
                  style={'height': height}),
        className='chart-card'
    )

def section(label):
    return html.Div([
        html.Span(label, className='section-label'),
        html.Div(className='section-line'),
    ], className='section-header')

app.layout = html.Div([
    # Inject CSS
    # html.Style(CUSTOM_CSS),

    # ── Header ──────────────────────────────────────────────────────────────
    html.Header([
        html.Div([
            html.Div([
                html.Div('📦', className='brand-icon'),
                html.Div([
                    html.Div('CLICKBD', className='brand-title'),
                    html.Div('SALES INTELLIGENCE', className='brand-sub'),
                ]),
            ], className='brand'),
            html.Div([
                html.Div([
                    html.Div(className='live-dot'),
                    html.Span(id='last-updated', children='Loading…'),
                ], className='live-badge'),
                html.Button('⟳ Refresh', id='refresh-btn', n_clicks=0, className='refresh-btn'),
            ], className='header-actions'),
        ], className='header-inner'),
    ], className='header-bar'),

    # ── Filter bar ──────────────────────────────────────────────────────────
    html.Div([
        html.Span('Filter by:', className='filter-label'),
        dcc.Dropdown(id='year-filter',  value='All', clearable=False,
                     placeholder='Year', className='dash-dropdown',
                     style={'minWidth': '130px'}),
        dcc.Dropdown(id='month-filter', value='All', clearable=False,
                     placeholder='Month', className='dash-dropdown',
                     style={'minWidth': '130px'}),
        dcc.Dropdown(id='salesperson-filter', value='All', clearable=False,
                     placeholder='Sales Person', className='dash-dropdown',
                     style={'minWidth': '160px'}),
        dcc.Dropdown(id='status-filter', value='All', clearable=False,
                     placeholder='Order Status', className='dash-dropdown',
                     style={'minWidth': '160px'}),
    ], className='filter-bar'),

    # ── KPI cards ───────────────────────────────────────────────────────────
    html.Div([
        html.Div([html.Div('📦', className='kpi-icon'),
                  html.Div(id='kpi-qty',      className='kpi-value cyan'),
                  html.Div('TOTAL QTY SOLD',  className='kpi-label'),
                  html.Div(id='kpi-qty-sub',  className='kpi-sub')],
                 className='kpi-card cyan'),
        html.Div([html.Div('🛒', className='kpi-icon'),
                  html.Div(id='kpi-orders',      className='kpi-value coral'),
                  html.Div('TOTAL ORDERS',        className='kpi-label'),
                  html.Div(id='kpi-orders-sub',   className='kpi-sub')],
                 className='kpi-card coral'),
        html.Div([html.Div('📍', className='kpi-icon'),
                  html.Div(id='kpi-districts',    className='kpi-value gold'),
                  html.Div('DISTRICTS REACHED',   className='kpi-label'),
                  html.Div(id='kpi-districts-sub',className='kpi-sub')],
                 className='kpi-card gold'),
        html.Div([html.Div('🏆', className='kpi-icon'),
                  html.Div(id='kpi-top-sp',       className='kpi-value green'),
                  html.Div('TOP SALES PERSON',     className='kpi-label'),
                  html.Div(id='kpi-top-sp-sub',   className='kpi-sub')],
                 className='kpi-card green'),
    ], className='kpi-row'),

    # ── Trend ───────────────────────────────────────────────────────────────
    section('SALES TREND'),
    html.Div([make_chart_card('month-sales', '380px')], className='chart-grid cols-1'),

    # ── Performance ─────────────────────────────────────────────────────────
    section('PERFORMANCE BREAKDOWN'),
    html.Div([
        make_chart_card('salesperson-sales', '360px'),
        make_chart_card('delivery-status',   '360px'),
    ], className='chart-grid cols-2'),

    # ── Geography ───────────────────────────────────────────────────────────
    section('GEOGRAPHIC DISTRIBUTION'),
    html.Div([
        make_chart_card('country-sales',  '360px'),
        make_chart_card('district-sales', '360px'),
    ], className='chart-grid cols-2'),

    # ── Products ────────────────────────────────────────────────────────────
    section('PRODUCT INSIGHTS'),
    html.Div([
        make_chart_card('order-set-sales',    '360px'),
        make_chart_card('category-sales',     '360px'),
    ], className='chart-grid cols-2'),
    html.Div([make_chart_card('subcategory-sales', '400px')], className='chart-grid cols-1'),

    # ── Footer ──────────────────────────────────────────────────────────────
    html.Footer([
        html.Span('CLICKBD Sales Intelligence Dashboard', className='footer-text'),
        html.Span(id='footer-record-count', className='footer-text'),
    ], className='footer'),

], style={'minHeight': '100vh', 'position': 'relative', 'zIndex': '1'})


# ─── Callback ─────────────────────────────────────────────────────────────────
@app.callback(
    [Output('year-filter',        'options'),
     Output('month-filter',       'options'),
     Output('salesperson-filter', 'options'),
     Output('status-filter',      'options'),
     Output('last-updated',       'children'),
     Output('kpi-qty',            'children'),
     Output('kpi-qty-sub',        'children'),
     Output('kpi-orders',         'children'),
     Output('kpi-orders-sub',     'children'),
     Output('kpi-districts',      'children'),
     Output('kpi-districts-sub',  'children'),
     Output('kpi-top-sp',         'children'),
     Output('kpi-top-sp-sub',     'children'),
     Output('month-sales',        'figure'),
     Output('salesperson-sales',  'figure'),
     Output('delivery-status',    'figure'),
     Output('order-set-sales',    'figure'),
     Output('country-sales',      'figure'),
     Output('district-sales',     'figure'),
     Output('category-sales',     'figure'),
     Output('subcategory-sales',  'figure'),
     Output('footer-record-count','children')],
    [Input('refresh-btn',        'n_clicks'),
     Input('year-filter',        'value'),
     Input('month-filter',       'value'),
     Input('salesperson-filter', 'value'),
     Input('status-filter',      'value')],
)
def update_dashboard(n_clicks, sel_year, sel_month, sel_sp, sel_status):
    ctx    = callback_context
    forced = ctx.triggered and ctx.triggered[0]['prop_id'] == 'refresh-btn.n_clicks'
    df     = load_data(force=bool(forced))

    # ── Dropdown options ──────────────────────────────────────────────────
    all_opt = [{'label': '— All —', 'value': 'All'}]
    year_opts = all_opt + [{'label': int(y), 'value': y}
                           for y in sorted(df['Year'].dropna().unique())]
    month_opts = all_opt + [{'label': m, 'value': m}
                            for m in VALID_MONTHS if m in df['Month'].unique()]
    sp_opts    = all_opt + [{'label': s, 'value': s}
                            for s in sorted(df['Sales Person'].dropna().unique())]
    status_opts = all_opt + [{'label': s, 'value': s}
                             for s in sorted(df['Order Status'].dropna().unique())]

    last_upd = time.strftime('Updated %H:%M:%S', time.localtime(_cache['ts']))

    # ── Filter ────────────────────────────────────────────────────────────
    dff = df.copy()
    if sel_year   and sel_year   != 'All': dff = dff[dff['Year']         == sel_year]
    if sel_month  and sel_month  != 'All': dff = dff[dff['Month']        == sel_month]
    if sel_sp     and sel_sp     != 'All': dff = dff[dff['Sales Person'] == sel_sp]
    if sel_status and sel_status != 'All': dff = dff[dff['Order Status'] == sel_status]

    # ── KPIs ──────────────────────────────────────────────────────────────
    total_qty     = dff['QTY'].sum()
    total_orders  = len(dff)
    districts     = dff['District'].nunique()
    sp_series     = dff.groupby('Sales Person')['QTY'].sum()
    top_sp        = sp_series.idxmax() if len(sp_series) else '—'
    top_sp_qty    = int(sp_series.max()) if len(sp_series) else 0

    # Context subtitle
    ctx_parts = []
    if sel_year  and sel_year  != 'All': ctx_parts.append(str(int(sel_year)))
    if sel_month and sel_month != 'All': ctx_parts.append(sel_month)
    ctx_label = ' · '.join(ctx_parts) if ctx_parts else 'All time'

    # ── Chart 1 – Monthly trend (full df, no filter) ──────────────────────
    month_df = (df.groupby(['Year','Month','Month_Num'])['QTY']
                  .sum().reset_index().sort_values('Month_Num'))
    fig1 = px.line(month_df, x='Month', y='QTY', color='Year',
                   markers=True, title='Monthly QTY Trend by Year',
                   color_discrete_sequence=CHART_COLORS)
    fig1.update_traces(line_width=2.5, marker_size=7)
    fig1.update_layout(**PLOTLY_LAYOUT,
        xaxis=dict(categoryorder='array', categoryarray=VALID_MONTHS,
                   gridcolor=BORDER, linecolor=BORDER, tickfont=dict(color=MUTED)),
        yaxis=dict(gridcolor=BORDER, linecolor=BORDER, tickfont=dict(color=MUTED)))

    # ── Chart 2 – Sales person ────────────────────────────────────────────
    sp_df = dff.groupby('Sales Person')['QTY'].sum().reset_index().sort_values('QTY', ascending=True)
    fig2  = px.bar(sp_df, x='QTY', y='Sales Person', orientation='h',
                   title='Sales Person Performance (QTY)',
                   color='QTY', color_continuous_scale=[[0, CORAL+'44'], [1, CORAL]],
                   text_auto=True)
    fig2.update_traces(textfont_color=TEXT, textposition='outside')
    fig2.update_layout(**PLOTLY_LAYOUT)

    # ── Chart 3 – Delivery status (donut) ────────────────────────────────
    fig3 = go.Figure(go.Pie(
        labels=dff['Order Status'].value_counts().index,
        values=dff['Order Status'].value_counts().values,
        hole=0.55,
        marker=dict(colors=CHART_COLORS, line=dict(color=BG, width=2)),
        textfont=dict(color=TEXT),
    ))
    fig3.update_layout(**PLOTLY_LAYOUT, title='Order Status Distribution',
                       showlegend=True)

    # ── Chart 4 – Order set ───────────────────────────────────────────────
    os_df = dff.groupby('Order Set')['QTY'].sum().reset_index().sort_values('QTY', ascending=False)
    fig4  = px.bar(os_df, x='Order Set', y='QTY', title='Order Set Breakdown',
                   color='QTY', color_continuous_scale=[[0, GOLD+'44'], [1, GOLD]],
                   text_auto=True)
    fig4.update_traces(textfont_color=TEXT)
    fig4.update_layout(**PLOTLY_LAYOUT)

    # ── Chart 5 – Country ─────────────────────────────────────────────────
    c_df = dff.groupby('Order Country')['QTY'].sum().reset_index().sort_values('QTY', ascending=False)
    fig5  = px.bar(c_df, x='Order Country', y='QTY', title='Country-wise Sales',
                   color='Order Country', text_auto=True,
                   color_discrete_sequence=CHART_COLORS)
    fig5.update_traces(textfont_color=TEXT)
    fig5.update_layout(**PLOTLY_LAYOUT, showlegend=False)

    # ── Chart 6 – District (top 20) ───────────────────────────────────────
    d_df = (dff.groupby('District')['QTY'].sum().reset_index()
               .sort_values('QTY', ascending=False).head(20))
    fig6  = px.bar(d_df, x='District', y='QTY', title='Top 20 Districts by QTY',
                   color='QTY', color_continuous_scale=[[0, GREEN+'33'], [1, GREEN]],
                   text_auto=True)
    fig6.update_traces(textfont_color=TEXT)
    fig6.update_layout(**PLOTLY_LAYOUT)

    # ── Chart 7 – Category ───────────────────────────────────────────────
    cat_df = dff[dff['Category'].notna() & (dff['Category'].str.lower() != 'null')]
    cat_df = cat_df.groupby('Category')['QTY'].sum().reset_index().sort_values('QTY', ascending=False)
    fig7   = px.bar(cat_df, x='Category', y='QTY', title='Category Performance',
                    color='Category', text_auto=True,
                    color_discrete_sequence=CHART_COLORS)
    fig7.update_traces(textfont_color=TEXT)
    fig7.update_layout(**PLOTLY_LAYOUT, showlegend=False)

    # ── Chart 8 – Sub-category ────────────────────────────────────────────
    sub_df = dff[dff['Sub-Category'].notna() & (dff['Sub-Category'].str.lower() != 'null')]
    sub_df = sub_df.groupby('Sub-Category')['QTY'].sum().reset_index().sort_values('QTY', ascending=False)
    fig8   = px.bar(sub_df, x='Sub-Category', y='QTY', title='Sub-Category Performance',
                    color='QTY', color_continuous_scale=[[0, CYAN+'33'], [1, CYAN]],
                    text_auto=True)
    fig8.update_traces(textfont_color=TEXT)
    fig8.update_layout(**PLOTLY_LAYOUT)

    return (
        year_opts, month_opts, sp_opts, status_opts,
        last_upd,
        f"{total_qty:,}",      ctx_label,
        f"{total_orders:,}",   ctx_label,
        f"{districts}",        f"across {dff['Order Country'].nunique()} countries",
        top_sp,                f"{top_sp_qty:,} units sold",
        fig1, fig2, fig3, fig4, fig5, fig6, fig7, fig8,
        f"{len(dff):,} records in view",
    )


if __name__ == "__main__":
    app.run_server(host="0.0.0.0", port=8050, debug=False)
