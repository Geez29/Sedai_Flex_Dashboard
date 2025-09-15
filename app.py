
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

st.set_page_config(page_title="Sedai Cost Optimization Dashboard", layout="wide")

# ------------------------------
# THEME / COLORS (McKinsey-esque)
# ------------------------------
COLORS = {
    "primary": "#0033A0",   # Navy
    "accent": "#00A3E0",    # Light blue
    "teal": "#00B398",      # Teal
    "orange": "#FF6A13",    # Orange
    "gray": "#6D6E71",      # Gray
    "slate": "#2F3942",     # Slate
}

CATEGORY_COLORS = {
    "Achieved Savings": COLORS["primary"],
    "Unachieveable Savings": COLORS["gray"],
    "Delayed Savings": COLORS["orange"],
    "Initiated": COLORS["accent"],
}

# ------------------------------
# HELPERS
# ------------------------------
@st.cache_data(show_spinner=False)
def load_data(uploaded, default_path: str = "sedai_execution_report_sample_v4.xlsx"):
    """Load dataframe from uploaded file or default path."""
    if uploaded is not None:
        df = pd.read_excel(uploaded)
    else:
        p = Path(default_path)
        if p.exists():
            df = pd.read_excel(p)
        else:
            st.warning("Upload an XLSX file with an 'Execution report'-style schema.")
            return pd.DataFrame()
    # Standardize column names (trim and unify)
    df.columns = [c.strip() for c in df.columns]
    # Ensure key columns exist
    for col in [
        'Sprint','Start Date','End Date','Inference Type','Region','Cloud Provider',
        'Current Monthly Cost ($)','Est. Monthly Cost ($)','Cost Savings in $','Cost Savings in %',
        'Achieved Savings','Unachieveable Savings','Delayed Savings','Initiated'
    ]:
        if col not in df.columns:
            df[col] = np.nan

    # Parse dates
    for c in ['Start Date','End Date']:
        if c in df.columns:
            df[c] = pd.to_datetime(df[c], errors='coerce')

    # Derive Month/Year using Start Date (fallback to End Date)
    when = df['Start Date'].fillna(df['End Date'])
    when = when.fillna(pd.Timestamp.today().normalize())
    df['Month'] = when.dt.month_name()
    df['Year'] = when.dt.year

    # Fiscal Year and Quarter mapping (FY = Apr 1 to Mar 31, labeled by end-year)
    def fy(dt: pd.Timestamp):
        if pd.isna(dt):
            dt = pd.Timestamp.today()
        return dt.year + 1 if dt.month >= 4 else dt.year

    def fq(dt: pd.Timestamp):
        m = dt.month
        if m in (4,5,6):
            return 'Q1'  # Apr-Jun
        elif m in (7,8,9):
            return 'Q2'
        elif m in (10,11,12):
            return 'Q3'
        else:
            return 'Q4'  # Jan-Mar

    df['FY'] = when.apply(lambda d: f"FY{fy(d)}")
    df['Quarter'] = when.apply(fq)
    df['FY_Quarter'] = df['FY'] + ' ' + df['Quarter']

    # Numeric coercions
    for c in ['Current Monthly Cost ($)','Est. Monthly Cost ($)','Cost Savings in $','Cost Savings in %',
              'Achieved Savings','Unachieveable Savings','Delayed Savings','Initiated']:
        df[c] = pd.to_numeric(df[c], errors='coerce')

    return df


def money(x, zero_dash: bool=False):
    if pd.isna(x):
        return "—" if zero_dash else "$0"
    if abs(x) < 0.5 and zero_dash:
        return "—"
    return f"${x:,.0f}"


def weighted_savings_pct(df: pd.DataFrame) -> float:
    cur = df['Current Monthly Cost ($)'].sum()
    sav = df['Cost Savings in $'].sum()
    if cur and cur > 0:
        return sav / cur * 100.0
    return float(df['Cost Savings in %'].mean()) if not df['Cost Savings in %'].isna().all() else 0.0

# ------------------------------
# HEADER
# ------------------------------
left, right = st.columns([0.82, 0.18])
with left:
    st.markdown("""
    <div style='padding-top:6px'>
        <h2 style='margin-bottom:0'>Sedai Cost Optimization Dashboard</h2>
        <p style='margin-top:4px;color:#5f6c72'>One-page executive view – filtered by Month, Year, FY, Sprint</p>
    </div>
    """, unsafe_allow_html=True)
with right:
    st.image('assets/flex_logo.png', use_container_width=True)

# ------------------------------
# SIDEBAR – DATA
# ------------------------------
st.sidebar.header("Data")
upload = st.sidebar.file_uploader("Upload Sedai Execution Report (XLSX)", type=['xlsx'])
df = load_data(upload)

if df.empty:
    st.stop()

# ------------------------------
# FILTERS
# ------------------------------
st.sidebar.header("Filters")

def multi_filter(label, values):
    opts = sorted([v for v in pd.Series(values).dropna().unique()])
    sel = st.sidebar.multiselect(label, options=opts, default=opts)
    return sel

sel_month = multi_filter("Month", df['Month'])
sel_year = multi_filter("Year", df['Year'])
sel_fy = multi_filter("Fiscal Year (FY)", df['FY'])
sel_sprint = multi_filter("Sprint", df['Sprint'])

mask = (
    df['Month'].isin(sel_month) &
    df['Year'].isin(sel_year) &
    df['FY'].isin(sel_fy) &
    df['Sprint'].isin(sel_sprint)
)
flt = df[mask].copy()

# ------------------------------
# KPIs
# ------------------------------
k1, k2, k3, k4 = st.columns(4)
with k1:
    st.metric("Total Recommendations", f"{len(flt):,}")
with k2:
    st.metric("Total Savings ($)", money(flt['Cost Savings in $'].sum()))
with k3:
    st.metric("Total Savings (%)", f"{weighted_savings_pct(flt):.1f}%")
with k4:
    st.metric("Avg Savings / Rec ($)", money(flt['Cost Savings in $'].mean()))

# ------------------------------
# CHARTS ROW 1 – Funnel + Savings by Inference Type (Bar)
# ------------------------------
col1, col2 = st.columns([0.50, 0.50])

with col1:
    st.subheader("Savings Pipeline (Funnel)")
    pipe_vals = {
        'Initiated': flt['Initiated'].sum(),
        'Delayed Savings': flt['Delayed Savings'].sum(),
        'Unachieveable Savings': flt['Unachieveable Savings'].sum(),
        'Achieved Savings': flt['Achieved Savings'].sum(),
    }
    funnel_df = pd.DataFrame({'Stage': list(pipe_vals.keys()), 'Value': list(pipe_vals.values())})
    fig_funnel = px.funnel(
        funnel_df, x='Value', y='Stage', color='Stage',
        color_discrete_map=CATEGORY_COLORS,
    )
    fig_funnel.update_traces(textposition='inside', texttemplate='%{x:$,.0f}')
    fig_funnel.update_layout(margin=dict(l=10,r=10,t=10,b=10), showlegend=False)
    st.plotly_chart(fig_funnel, use_container_width=True, theme=None)

with col2:
    st.subheader("Savings by Inference Type ($)")
    by_inf = flt.groupby('Inference Type', dropna=False)['Cost Savings in $'].sum().sort_values(ascending=False).reset_index()
    if by_inf.empty:
        st.info("No data for selected filters.")
    else:
        fig_bar = px.bar(by_inf, x='Inference Type', y='Cost Savings in $', text='Cost Savings in $', color_discrete_sequence=[COLORS['primary']])
        fig_bar.update_traces(texttemplate='$%{y:,.0f}', textposition='outside', cliponaxis=False)
        fig_bar.update_layout(margin=dict(l=10,r=10,t=10,b=10), xaxis_title='', yaxis_title='Savings ($)')
        st.plotly_chart(fig_bar, use_container_width=True, theme=None)

# ------------------------------
# CHARTS ROW 2 – Mix Pie + Recommendations by Sprint (Bar+Line)
# ------------------------------
col3, col4 = st.columns([0.40, 0.60])

with col3:
    st.subheader("Savings Mix ($)")
    mix_df = pd.DataFrame({
        'Category': list(CATEGORY_COLORS.keys()),
        'Value': [
            flt['Achieved Savings'].sum(),
            flt['Unachieveable Savings'].sum(),
            flt['Delayed Savings'].sum(),
            flt['Initiated'].sum(),
        ]
    })
    fig_pie = px.pie(mix_df, names='Category', values='Value', color='Category', color_discrete_map=CATEGORY_COLORS, hole=0.35)
    fig_pie.update_traces(textposition='inside', textinfo='label+percent', hovertemplate='%{label}: $%{value:,.0f} (%{percent})')
    fig_pie.update_layout(margin=dict(l=10,r=10,t=10,b=10), showlegend=False)
    st.plotly_chart(fig_pie, use_container_width=True, theme=None)

with col4:
    st.subheader("Recommendations by Sprint & Savings ($)")
    s_grp = flt.groupby('Sprint', dropna=False).agg(Recommendations=('Sprint','count'), Savings_USD=('Cost Savings in $','sum')).sort_values('Savings_USD', ascending=False).reset_index()
    if s_grp.empty:
        st.info("No data for selected filters.")
    else:
        fig_sprint = go.Figure()
        fig_sprint.add_trace(go.Bar(x=s_grp['Sprint'], y=s_grp['Recommendations'], name='Recommendations', marker_color=COLORS['accent'], yaxis='y', text=s_grp['Recommendations'], textposition='outside'))
        fig_sprint.add_trace(go.Scatter(x=s_grp['Sprint'], y=s_grp['Savings_USD'], name='Savings ($)', mode='lines+markers+text', text=[f"${v:,.0f}" for v in s_grp['Savings_USD']], textposition='top center', marker_color=COLORS['primary'], yaxis='y2'))
        fig_sprint.update_layout(margin=dict(l=10,r=40,t=10,b=10), xaxis=dict(title=''), yaxis=dict(title='Recommendations'), yaxis2=dict(title='Savings ($)', overlaying='y', side='right', showgrid=False), legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1))
        st.plotly_chart(fig_sprint, use_container_width=True, theme=None)

# ------------------------------
# TABLE – Sprint Summary
# ------------------------------
st.subheader("Sprint Summary – Savings & Counts")
summary = flt.groupby('Sprint', dropna=False).agg(
    Total_Recommendations=('Sprint','count'),
    Current_Spend_USD=('Current Monthly Cost ($)','sum'),
    Est_Spend_USD=('Est. Monthly Cost ($)','sum'),
    Total_Savings_USD=('Cost Savings in $','sum'),
    Achieved_USD=('Achieved Savings','sum'),
    Unachievable_USD=('Unachieveable Savings','sum'),
    Delayed_USD=('Delayed Savings','sum'),
    Initiated_USD=('Initiated','sum'),
    Achieved_Count=('Achieved Savings', lambda s: (s>0).sum()),
    Unachievable_Count=('Unachieveable Savings', lambda s: (s>0).sum()),
    Delayed_Count=('Delayed Savings', lambda s: (s>0).sum()),
    Initiated_Count=('Initiated', lambda s: (s>0).sum()),
)
if not summary.empty:
    summary['Total_Savings_%'] = (summary['Total_Savings_USD'] / summary['Current_Spend_USD']).replace([np.inf, -np.inf], 0).fillna(0)*100
    disp = summary.reset_index().copy()
    money_cols = ['Current_Spend_USD','Est_Spend_USD','Total_Savings_USD','Achieved_USD','Unachievable_USD','Delayed_USD','Initiated_USD']
    for c in money_cols:
        disp[c] = disp[c].map(lambda v: f"${v:,.0f}")
    disp['Total_Savings_%'] = disp['Total_Savings_%'].map(lambda v: f"{v:,.1f}%")
    st.dataframe(disp, use_container_width=True)
else:
    st.info("No rows in current filter.")

st.caption("FY: Apr 1 to Mar 31 (end-year label, e.g., Apr 2024–Mar 2025 = FY2025). Q1=Apr–Jun, Q2=Jul–Sep, Q3=Oct–Dec, Q4=Jan–Mar.")
