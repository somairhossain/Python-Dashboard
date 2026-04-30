import time, os, json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output, callback_context
import dash_bootstrap_components as dbc

# ─── Data Loading ─────────────────────────────────────────────────────────────
SHEET_ID     = '1_TWU8G6FDjEhRaFxoAwo3jD93Ccmn6zGRuphyrqww2k'
SHEET_NAME   = 'ClickBD_Data'
CACHE_TTL    = 300
_cache       = {"df": None, "ts": 0}
VALID_MONTHS = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']

def load_data(force=False):
    now = time.time()
    if not force and _cache["df"] is not None and (now - _cache["ts"]) < CACHE_TTL:
        return _cache["df"]

    df = None

    # ── Method 1: Google Sheets API via service account (most reliable) ───
    creds_json = os.environ.get("GOOGLE_CREDENTIALS")
    if creds_json:
        try:
            import gspread
            from google.oauth2.service_account import Credentials
            scopes = ['https://www.googleapis.com/auth/spreadsheets.readonly']
            creds  = Credentials.from_service_account_info(json.loads(creds_json), scopes=scopes)
            gc     = gspread.authorize(creds)
            ws     = gc.open_by_key(SHEET_ID).worksheet(SHEET_NAME)
            rows   = ws.get_all_values()
            df     = pd.DataFrame(rows[1:], columns=rows[0])
            print("✅ Loaded via Google Sheets API")
        except Exception as e:
            print(f"⚠️  Sheets API failed: {e}")

    # ── Method 2: Direct CSV fallback ─────────────────────────────────────
    if df is None:
        try:
            import requests, io
            url = (f"https://docs.google.com/spreadsheets/d/{SHEET_ID}"
                   f"/gviz/tq?tqx=out:csv&sheet={SHEET_NAME}")
            r   = requests.get(url, timeout=15)
            r.raise_for_status()
            df  = pd.read_csv(io.StringIO(r.text))
            print("✅ Loaded via CSV URL")
        except Exception as e:
            print(f"⚠️  CSV URL failed: {e}")

    if df is None or df.empty:
        print("❌ All data sources failed — returning empty DataFrame")
        return _cache["df"] or pd.DataFrame()

    # ── Clean ─────────────────────────────────────────────────────────────
    df['Month'] = df['Month'].astype(str).str.strip()
    df = df[df['Month'].isin(VALID_MONTHS)]
    df['Month_Num'] = pd.to_datetime(df['Month'], format='%b').dt.month
    df['Year'] = df['Year'].astype(str).str.extract(r'(\d{4})').astype(float).astype('Int64')
    if 'QTY' in df.columns:
        df['QTY'] = pd.to_numeric(df['QTY'], errors='coerce').fillna(0).astype(int)

    _cache["df"] = df
    _cache["ts"] = now
    return df

load_data()

# ─── Theme ────────────────────────────────────────────────────────────────────
BG      = '#0a0e1a'
SURFACE = '#111827'
CARD    = '#161d2e'
BORDER  = '#1e2d45'
CYAN    = '#00e5ff'
CORAL   = '#ff4d6d'
GOLD    = '#ffd166'
GREEN   = '#06d6a0'
TEXT    = '#e2e8f0'
MUTED   = '#64748b'

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
app    = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

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
                    html.Span(id='last-updated', children='Loading...'),
                ], className='live-badge'),
                html.Button('Refresh', id='refresh-btn', n_clicks=0,
                            className='refresh-btn'),
            ], className='header-actions'),
        ], className='header-inner'),
    ], className='header-bar'),

    html.Div([
        html.Span('Filter by:', className='filter-label'),
        dcc.Dropdown(id='year-filter',        value='All', clearable=False,
                     placeholder='Year',         className='dash-dropdown',
                     style={'minWidth': '130px'}),
        dcc.Dropdown(id='month-filter',       value='All', clearable=False,
                     placeholder='Month',        className='dash-dropdown',
                     style={'minWidth': '130px'}),
        dcc.Dropdown(id='salesperson-filter', value='All', clearable=False,
                     placeholder='Sales Person', className='dash-dropdown',
                     style={'minWidth': '160px'}),
        dcc.Dropdown(id='status-filter',      value='All', clearable=False,
                     placeholder='Order Status', className='dash-dropdown',
                     style={'minWidth': '160px'}),
    ], className='filter-bar'),

    html.Div([
        html.Div([html.Div('📦', className='kpi-icon'),
                  html.Div(id='kpi-qty',     className='kpi-value cyan'),
                  html.Div('TOTAL QTY SOLD', className='kpi-label'),
                  html.Div(id='kpi-qty-sub', className='kpi-sub')],
                 className='kpi-card cyan'),
        html.Div([html.Div('🛒', className='kpi-icon'),
                  html.Div(id='kpi-orders',     className='kpi-value coral'),
                  html.Div('TOTAL ORDERS',      className='kpi-label'),
                  html.Div(id='kpi-orders-sub', className='kpi-sub')],
                 className='kpi-card coral'),
        html.Div([html.Div('📍', className='kpi-icon'),
                  html.Div(id='kpi-districts',     className='kpi-value gold'),
                  html.Div('DISTRICTS REACHED',    className='kpi-label'),
                  html.Div(id='kpi-districts-sub', className='kpi-sub')],
                 className='kpi-card gold'),
        html.Div([html.Div('🏆', className='kpi-icon'),
                  html.Div(id='kpi-top-sp',     className='kpi-value green'),
                  html.Div('TOP SALES PERSON',  className='kpi-label'),
                  html.Div(id='kpi-top-sp-sub', className='kpi-sub')],
                 className='kpi-card green'),
    ], className='kpi-row'),

    section('SALES TREND'),
    html.Div([make_chart_card('month-sales', '380px')], className='chart-grid cols-1'),

    section('PERFORMANCE BREAKDOWN'),
    html.Div([make_chart_card('salesperson-sales', '360px'),
              make_chart_card('delivery-status',   '360px')],
             className='chart-grid cols-2'),

    section('GEOGRAPHIC DISTRIBUTION'),
    html.Div([make_chart_card('country-sales',  '360px'),
              make_chart_card('district-sales', '360px')],
             className='chart-grid cols-2'),

    section('PRODUCT INSIGHTS'),
    html.Div([make_chart_card('order-set-sales', '360px'),
              make_chart_card('category-sales',  '360px')],
             className='chart-grid cols-2'),
    html.Div([make_chart_card('subcategory-sales', '400px')], className='chart-grid cols-1'),

    html.Footer([
        html.Span('CLICKBD Sales Intelligence Dashboard', className='footer-text'),
        html.Span(id='footer-record-count', className='footer-text'),
    ], className='footer'),

], style={'minHeight': '100vh', 'position': 'relative', 'zIndex': '1'})


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
    forced = bool(ctx.triggered and ctx.triggered[0]['prop_id'] == 'refresh-btn.n_clicks')
    df     = load_data(force=forced)

    if df is None or df.empty:
        empty = {'label': 'No data', 'value': 'All'}
        empty_fig = go.Figure().update_layout(**PLOTLY_LAYOUT,
            title='No data available — check Google Sheets connection')
        return ([empty],[empty],[empty],[empty],
                'No data loaded', '—','—','—','—','—','—','—','—',
                *[empty_fig]*8, 'No records')

    all_opt     = [{'label': '— All —', 'value': 'All'}]
    year_opts   = all_opt + [{'label': int(y), 'value': y}
                             for y in sorted(df['Year'].dropna().unique())]
    month_opts  = all_opt + [{'label': m, 'value': m}
                             for m in VALID_MONTHS if m in df['Month'].unique()]
    sp_opts     = all_opt + [{'label': s, 'value': s}
                             for s in sorted(df['Sales Person'].dropna().unique())]
    status_opts = all_opt + [{'label': s, 'value': s}
                             for s in sorted(df['Order Status'].dropna().unique())]

    last_upd = time.strftime('Updated %H:%M:%S', time.localtime(_cache['ts']))

    dff = df.copy()
    if sel_year   and sel_year   != 'All': dff = dff[dff['Year']         == sel_year]
    if sel_month  and sel_month  != 'All': dff = dff[dff['Month']        == sel_month]
    if sel_sp     and sel_sp     != 'All': dff = dff[dff['Sales Person'] == sel_sp]
    if sel_status and sel_status != 'All': dff = dff[dff['Order Status'] == sel_status]

    total_qty    = dff['QTY'].sum()
    total_orders = len(dff)
    districts    = dff['District'].nunique()
    sp_series    = dff.groupby('Sales Person')['QTY'].sum()
    top_sp       = sp_series.idxmax() if len(sp_series) else '-'
    top_sp_qty   = int(sp_series.max()) if len(sp_series) else 0

    ctx_parts = []
    if sel_year  and sel_year  != 'All': ctx_parts.append(str(int(sel_year)))
    if sel_month and sel_month != 'All': ctx_parts.append(sel_month)
    ctx_label = ' - '.join(ctx_parts) if ctx_parts else 'All time'

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

    sp_df = (dff.groupby('Sales Person')['QTY'].sum()
               .reset_index().sort_values('QTY', ascending=True))
    fig2 = px.bar(sp_df, x='QTY', y='Sales Person', orientation='h',
                  title='Sales Person Performance (QTY)',
                  color='QTY', color_continuous_scale=[[0,CORAL+'44'],[1,CORAL]],
                  text_auto=True)
    fig2.update_traces(textfont_color=TEXT, textposition='outside')
    fig2.update_layout(**PLOTLY_LAYOUT)

    vc = dff['Order Status'].value_counts()
    fig3 = go.Figure(go.Pie(labels=vc.index, values=vc.values, hole=0.55,
        marker=dict(colors=CHART_COLORS, line=dict(color=BG, width=2)),
        textfont=dict(color=TEXT)))
    fig3.update_layout(**PLOTLY_LAYOUT, title='Order Status Distribution', showlegend=True)

    os_df = (dff.groupby('Order Set')['QTY'].sum()
               .reset_index().sort_values('QTY', ascending=False))
    fig4 = px.bar(os_df, x='Order Set', y='QTY', title='Order Set Breakdown',
                  color='QTY', color_continuous_scale=[[0,GOLD+'44'],[1,GOLD]],
                  text_auto=True)
    fig4.update_traces(textfont_color=TEXT)
    fig4.update_layout(**PLOTLY_LAYOUT)

    c_df = (dff.groupby('Order Country')['QTY'].sum()
              .reset_index().sort_values('QTY', ascending=False))
    fig5 = px.bar(c_df, x='Order Country', y='QTY', title='Country-wise Sales',
                  color='Order Country', text_auto=True,
                  color_discrete_sequence=CHART_COLORS)
    fig5.update_traces(textfont_color=TEXT)
    fig5.update_layout(**PLOTLY_LAYOUT, showlegend=False)

    d_df = (dff.groupby('District')['QTY'].sum()
              .reset_index().sort_values('QTY', ascending=False).head(20))
    fig6 = px.bar(d_df, x='District', y='QTY', title='Top 20 Districts by QTY',
                  color='QTY', color_continuous_scale=[[0,GREEN+'33'],[1,GREEN]],
                  text_auto=True)
    fig6.update_traces(textfont_color=TEXT)
    fig6.update_layout(**PLOTLY_LAYOUT)

    cat_df = dff[dff['Category'].notna() & (dff['Category'].str.lower() != 'null')]
    cat_df = cat_df.groupby('Category')['QTY'].sum().reset_index().sort_values('QTY', ascending=False)
    fig7 = px.bar(cat_df, x='Category', y='QTY', title='Category Performance',
                  color='Category', text_auto=True,
                  color_discrete_sequence=CHART_COLORS)
    fig7.update_traces(textfont_color=TEXT)
    fig7.update_layout(**PLOTLY_LAYOUT, showlegend=False)

    sub_df = dff[dff['Sub-Category'].notna() & (dff['Sub-Category'].str.lower() != 'null')]
    sub_df = sub_df.groupby('Sub-Category')['QTY'].sum().reset_index().sort_values('QTY', ascending=False)
    fig8 = px.bar(sub_df, x='Sub-Category', y='QTY', title='Sub-Category Performance',
                  color='QTY', color_continuous_scale=[[0,CYAN+'33'],[1,CYAN]],
                  text_auto=True)
    fig8.update_traces(textfont_color=TEXT)
    fig8.update_layout(**PLOTLY_LAYOUT)

    return (
        year_opts, month_opts, sp_opts, status_opts,
        last_upd,
        f"{total_qty:,}",    ctx_label,
        f"{total_orders:,}", ctx_label,
        f"{districts}",      f"across {dff['Order Country'].nunique()} countries",
        top_sp,              f"{top_sp_qty:,} units sold",
        fig1, fig2, fig3, fig4, fig5, fig6, fig7, fig8,
        f"{len(dff):,} records in view",
    )


if __name__ == "__main__":
    app.run_server(host="0.0.0.0", port=8050, debug=False)
