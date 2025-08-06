import streamlit as st
import random       
import duckdb       
import pandas as pd 
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

st.set_page_config(page_title="ST Sales Dashboard", page_icon=":bar_chart:", layout="wide")

st.title("🏢 ST Sales Dashboard")
st.markdown("_Excel to Dashboard - Advanced Analytics v2.0_")

##################################### // Upload File // ########################################
with st.sidebar:
    st.header("📁 Configuration")
    uploaded_excel_file = st.file_uploader("Upload your Excel file", type=["xlsx", "xls"])

if uploaded_excel_file is None:
    st.info("Please upload an Excel file to proceed.", icon="ℹ️")
    st.stop()

##################################### // Load Data // ########################################
@st.cache_data
def load_data(uploaded_file):
    df = pd.read_excel(uploaded_file)
    return df

df = load_data(uploaded_excel_file)
all_months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

# Add sidebar filters
st.sidebar.header("Filters")
business_units = ['All'] + sorted(df['business_unit'].unique().tolist())
selected_business_unit = st.sidebar.selectbox("Business Unit", business_units)

years = ['All'] + sorted(df['Year'].unique().tolist())
selected_year = st.sidebar.selectbox("Year", years)

account_types = ['All', 'Sales', 'Expenses']
selected_account_type = st.sidebar.selectbox("Account Type", account_types)

# Filter data based on selections
filtered_df = df.copy()
if selected_business_unit != 'All':
    filtered_df = filtered_df[filtered_df['business_unit'] == selected_business_unit]
if selected_year != 'All':
    filtered_df = filtered_df[filtered_df['Year'] == selected_year]

with st.expander("View Raw Data", expanded=False):
    st.dataframe(filtered_df, 
                 column_config={"Year": st.column_config.NumberColumn(format="%d")})

##################################### // Helper Functions // ########################################
def calculate_total_for_account(df, account_name):
    """Calculate total for a specific account across all months"""
    account_df = df[df['Account'] == account_name]
    if account_df.empty:
        return 0
    total = account_df[all_months].sum().sum()
    return total

def calculate_kpis(df):
    """Calculate key performance indicators"""
    total_sales = calculate_total_for_account(df, 'Sales')
    total_cogs = abs(calculate_total_for_account(df, 'Cost of Goods Sold'))
    
    # Calculate total expenses (all non-sales, non-COGS accounts)
    expense_accounts = df[~df['Account'].isin(['Sales', 'Cost of Goods Sold'])]
    total_expenses = abs(expense_accounts[all_months].sum().sum())
    
    gross_profit = total_sales - total_cogs
    net_profit = gross_profit - total_expenses
    
    gross_margin = (gross_profit / total_sales * 100) if total_sales != 0 else 0
    net_margin = (net_profit / total_sales * 100) if total_sales != 0 else 0
    
    return {
        'total_sales': total_sales,
        'total_cogs': total_cogs,
        'total_expenses': total_expenses,
        'gross_profit': gross_profit,
        'net_profit': net_profit,
        'gross_margin': gross_margin,
        'net_margin': net_margin
    }

def plot_metric(label, value, prefix="", suffix="", show_graph=False, color_graph="", delta=None):
    """Enhanced metric display with optional delta"""
    fig = go.Figure()

    fig.add_trace(
        go.Indicator(
            value=value,
            gauge={"axis": {"visible": False}},
            number={
                "prefix": prefix,
                "suffix": suffix,
                "font.size": 28,
            },
            title={
                "text": label,
                "font": {"size": 20},
            },
        )
    )

    if show_graph:
        fig.add_trace(
            go.Scatter(
                y=random.sample(range(0, 101), 30),
                hoverinfo="skip",
                fill="tozeroy",
                fillcolor=color_graph,
                line={"color": color_graph},
            )
        )

    fig.update_xaxes(visible=False, fixedrange=True)
    fig.update_yaxes(visible=False, fixedrange=True)
    fig.update_layout(
        margin=dict(t=50, b=0),
        showlegend=False,
        #plot_bgcolor="white",
        plot_bgcolor="rgba(0,0,0,0)",   # Transparent plot background
        paper_bgcolor="rgba(0,0,0,0)",  # Transparent paper background
        height=120,
    )

    st.plotly_chart(fig, use_container_width=True)
    
    # Add delta information below if provided
    if delta:
        if delta > 0:
            st.markdown(f"<p style='text-align: center; color: green;'>📈 +{delta:.1f}%</p>", unsafe_allow_html=True)
        elif delta < 0:
            st.markdown(f"<p style='text-align: center; color: red;'>📉 {delta:.1f}%</p>", unsafe_allow_html=True)
        else:
            st.markdown(f"<p style='text-align: center; color: gray;'>➡️ {delta:.1f}%</p>", unsafe_allow_html=True)


def plot_gauge(indicator_number, indicator_color, indicator_suffix, indicator_title, max_bound):
    """Enhanced gauge chart"""
    fig = go.Figure(
        go.Indicator(
            value=indicator_number,
            mode="gauge+number+delta",
            domain={"x": [0, 1], "y": [0, 1]},
            number={
                "suffix": indicator_suffix,
                "font.size": 24,
            },
            gauge={
                "axis": {"range": [0, max_bound], "tickwidth": 1},
                "bar": {"color": indicator_color},
                "steps": [
                    {"range": [0, max_bound*0.5], "color": "lightgray"},
                    {"range": [max_bound*0.5, max_bound*0.8], "color": "gray"}
                ],
                "threshold": {
                    "line": {"color": "red", "width": 4},
                    "thickness": 0.75,
                    "value": max_bound*0.9
                }
            },
            title={
                "text": indicator_title,
                "font": {"size": 20},
            },
        )
    )
    fig.update_layout(
        height=200,
        margin=dict(l=10, r=10, t=40, b=10, pad=8),
    )
    st.plotly_chart(fig, use_container_width=True)

##################################### // Executive Summary Cards // ########################################
st.header("📊 Executive Summary")

kpis = calculate_kpis(filtered_df)

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    plot_metric(
        "💰 Total Revenue",
        kpis['total_sales'],
        prefix="$",
        suffix="",
        show_graph=True,
        color_graph="rgba(0, 104, 201, 0.2)",
        # delta=random.uniform(-5, 15)  # Simulated growth
    )


with col2:
    plot_metric(
        "💸 Total Expenses",
        kpis['total_expenses'],
        prefix="$",
        suffix="",
        show_graph=True,
        color_graph="rgba(255, 43, 43, 0.2)",
        # delta=random.uniform(-10, 5)
    )

with col3:
    profit_color = "rgba(0, 200, 0, 0.2)" if kpis['net_profit'] >= 0 else "rgba(255, 43, 43, 0.2)"
    plot_metric(
        "🏆 Net Profit",
        kpis['net_profit'],
        prefix="$",
        suffix="",
        show_graph=True,
        color_graph=profit_color,
        # delta=random.uniform(-8, 20)
    )

with col4:
    plot_metric(
        "📊 Gross Margin",
        kpis['gross_margin'],
        prefix="",
        suffix="%",
        show_graph=True,                
        color_graph="rgba(0, 104, 201, 0.2)" 
    
    )

with col5:
    plot_metric(
        "🎯 Net Margin",
        kpis['net_margin'],
        prefix="",
        suffix="%",
        show_graph=True,                
        color_graph="rgba(0, 203, 101, 0.2)"  
    
    )
st.markdown("---")
##################################### // Business Unit Performance Gauges // ########################################
st.subheader("🏢 Business Unit Performance")
# bu_cols = st.columns(3)
bu_cols = st.columns([0.7, 0.7, 0.7])


business_unit_names = filtered_df['business_unit'].unique()
colors = ["#0068C9", "#FF8700", "#FF2B2B", "#29B09D", "#6B46C1"]

for i, bu in enumerate(business_unit_names[:3]):  # Show top 3 business units
    bu_data = filtered_df[filtered_df['business_unit'] == bu] # filter means that we only get the data for the current business unit
    
    bu_sales = calculate_total_for_account(bu_data, 'Sales')
    
    bu_expenses = abs(bu_data[~bu_data['Account'].isin(['Sales'])][all_months].sum().sum())
    
    efficiency = (bu_sales - bu_expenses) / bu_sales * 100 if bu_sales != 0 else 0
    
    with bu_cols[i]:
        plot_gauge(
            efficiency,
            colors[i % len(colors)],
            "",
            f"{bu} Efficiency",
            30.0
        )
        # setting size of gauge chart
        st.markdown(
            f"<div style='text-align: center; color:{colors[i % len(colors)]}; font-size: 16px;'>{bu} Sales: ${bu_sales:,.0f}</div>",
            unsafe_allow_html=True
        )
        st.markdown(
            f"<div style='text-align: center; color:{colors[i % len(colors)]}; font-size: 16px;'>Expenses: ${bu_expenses:,.0f}</div>",
            unsafe_allow_html=True
        )

st.markdown("---")

##################################### // Revenue Analysis Charts // ########################################
st.header(" Revenue Analysis")

col1, col2 = st.columns([0.7, 0.3])

with col1:
    st.subheader(" Monthly Revenue Trends")
    # Melt the data for monthly trends
    sales_df = filtered_df[filtered_df['Account'] == 'Sales']
    melted_sales = sales_df.melt(
        id_vars=['business_unit', 'Year'],
        value_vars=all_months,
        var_name='Month',
        value_name='Revenue'
    )
    melted_sales['Month'] = pd.Categorical(melted_sales['Month'], categories=all_months, ordered=True)
    
    fig_line = px.line(
        melted_sales,
        x='Month',
        y='Revenue',
        color='business_unit',
        title="Monthly Revenue by Business Unit",
        markers=True
    )
    fig_line.update_layout(
    height=600,
    yaxis=dict(tick0=0, dtick=10_000_000) 
    )
    st.plotly_chart(fig_line, use_container_width=True)

with col2:
    st.subheader(" Revenue Distribution")
    revenue_by_bu = filtered_df[filtered_df['Account'] == 'Sales'].groupby('business_unit')[all_months].sum().sum(axis=1).reset_index()
    revenue_by_bu.columns = ['business_unit', 'total_revenue']
    
    fig_pie = px.pie(
        revenue_by_bu,
        values='total_revenue',
        names='business_unit',
        title="Revenue Share by Business Unit"
    )
    fig_pie.update_layout(height=600)
    st.plotly_chart(fig_pie, use_container_width=True)

# Revenue Heatmap
# st.subheader("🔥 Revenue Performance Heatmap")
# heatmap_data = filtered_df[filtered_df['Account'] == 'Sales'].set_index('business_unit')[all_months]
# fig_heatmap = px.imshow(
#     heatmap_data,
#     title="Revenue Heatmap: Business Unit vs Month",
#     color_continuous_scale="Viridis",
#     aspect="auto"
# )
# fig_heatmap.update_layout(height=400)
# st.plotly_chart(fig_heatmap, use_container_width=True)

st.markdown("---")

##################################### // Profitability Dashboard // ########################################
st.header(" Profitability Analysis")

col1, col2 = st.columns([0.5, 0.5])

with col1:
    st.subheader("Profit Components Bar Chart")
    categories = ['Revenue', 'COGS', 'Gross Profit', 'Expenses', 'Net Profit']
    revenue = kpis['total_sales']
    cogs = -kpis['total_cogs']
    gross_profit = revenue + cogs
    expenses = -kpis['total_expenses']
    net_profit = gross_profit + expenses

    values = [revenue, cogs, gross_profit, expenses, net_profit]
    colors = [
        "#1f77b4",  # Revenue
        "#d62728",  # COGS
        "#2ca02c",  # Gross Profit
        "#ff7f0e",  # Expenses
        "#9467bd"   # Net Profit
    ]

    fig_bar = go.Figure(
        go.Bar(
            x=categories,
            y=values,
            marker_color=colors,
            text=[f"${v:,.0f}" for v in values],
            textposition="outside"
        )
    )
    fig_bar.update_layout(
        title="Profit Components (Bar Chart)",
        height=800,
        yaxis=dict(
            zeroline=True,
            showline=True,
            rangemode="normal"
        )
    )
    st.plotly_chart(fig_bar, use_container_width=True) 
with col2:
    st.subheader("Expense Breakdown")
    # Get all expense accounts
    expense_df = filtered_df[~filtered_df['Account'].isin(['Sales', 'Cost of Goods Sold'])]
    expense_totals = expense_df.groupby('Account')[all_months].sum().sum(axis=1).reset_index()
    expense_totals.columns = ['Account', 'Total']
    expense_totals['Total'] = expense_totals['Total'].abs()
    
    fig_expense_pie = px.pie(
        expense_totals,
        values='Total',
        names='Account',
        title="Expense Categories"
    )
    fig_expense_pie.update_layout(height=700)
    st.plotly_chart(fig_expense_pie, use_container_width=True)

st.markdown("---")

##################################### // Business Unit Comparison // ########################################
st.header("Business Unit Comparison")

# Create comparison metrics
bu_comparison_data = []
for bu in filtered_df['business_unit'].unique():
    bu_data = filtered_df[filtered_df['business_unit'] == bu]
    bu_kpis = calculate_kpis(bu_data)
    bu_comparison_data.append({
        'Business Unit': bu,
        'Revenue': bu_kpis['total_sales'],
        'Expenses': bu_kpis['total_expenses'],
        'Net Profit': bu_kpis['net_profit'],
        'Net Margin (%)': bu_kpis['net_margin']
    })

comparison_df = pd.DataFrame(bu_comparison_data)

col1, col2 = st.columns(2)

with col1:
    st.subheader("Performance Comparison")
    fig_comparison = px.bar(
        comparison_df,
        x='Business Unit',
        y=['Revenue', 'Net Profit'],
        title="Revenue vs Net Profit by Business Unit",
        barmode='group'
    )
    fig_comparison.update_layout(height=400)
    st.plotly_chart(fig_comparison, use_container_width=True)

with col2:
    st.subheader("🏆 Profitability Ranking")
    sorted_df = comparison_df.sort_values('Net Profit', ascending=True)
    fig_ranking = px.bar(
        sorted_df,
        x='Net Profit',
        y='Business Unit',
        orientation='h',
        title="Net Profit Ranking",
        color='Net Profit',
        color_continuous_scale='RdYlGn'
    )
    fig_ranking.update_layout(height=400)
    st.plotly_chart(fig_ranking, use_container_width=True)

# Performance table
st.subheader("📋 Detailed Performance Metrics")
st.dataframe(comparison_df.style.format({
    'Revenue': '${:,.0f}',
    'Expenses': '${:,.0f}',
    'Net Profit': '${:,.0f}',
    'Net Margin (%)': '{:.1f}%'
}), use_container_width=True)

st.markdown("---")

##################################### // Expense Analysis // ########################################
st.header("Expense Analysis")


years_available = sorted(filtered_df['Year'].unique())
selected_years_expense = st.multiselect(
    "Select Year(s) for Expense Analysis", years_available, default=years_available, key="expense_years"
)

# Filter data for selected years
filtered_expense_df = filtered_df[filtered_df['Year'].isin(selected_years_expense)]


st.subheader(" Monthly Expense Trends")
expense_accounts = ['Payroll Expense', 'Marketing Expense', 'R&D Expense', 'Consulting Expense']
available_expense_accounts = [acc for acc in expense_accounts if acc in filtered_expense_df['Account'].values]

expense_monthly_data = []
for account in available_expense_accounts:
    account_data = filtered_expense_df[filtered_expense_df['Account'] == account]
    for year in selected_years_expense:
        year_data = account_data[account_data['Year'] == year]
        for month in all_months:
            total_expense = year_data[month].abs().sum()
            expense_monthly_data.append({
                'Year': year,
                'Month': month,
                'Account': account,
                'Expense': total_expense
            })

expense_monthly_df = pd.DataFrame(expense_monthly_data)
expense_monthly_df['Month'] = pd.Categorical(expense_monthly_df['Month'], categories=all_months, ordered=True)

if not expense_monthly_df.empty:
    fig_expense_trend = px.line(
        expense_monthly_df,
        x='Month',
        y='Expense',
        color='Account',
        line_group='Year',
        title="Monthly Expense Trends",
        markers=True,
        facet_col="Year" if len(selected_years_expense) > 1 else None
    )
    fig_expense_trend.update_layout(height=400)
    st.plotly_chart(fig_expense_trend, use_container_width=True)


st.subheader("📊 Expense Ratios")
total_revenue = calculate_total_for_account(filtered_expense_df, 'Sales')
expense_ratios = []

for account in available_expense_accounts:
    account_total = abs(calculate_total_for_account(filtered_expense_df, account))
    ratio = round((account_total / total_revenue * 100),2) if total_revenue != 0 else 0
    expense_ratios.append({
        'Account': account,
        'Expense Ratio (%)': ratio
    })

ratio_df = pd.DataFrame(expense_ratios)

if not ratio_df.empty:
    fig_ratio = px.bar(
        ratio_df,
        x='Account',
        y='Expense Ratio (%)',
        title="Expense as % of Revenue",
        color='Expense Ratio (%)',
        color_continuous_scale='Reds'
    )
    fig_ratio.update_layout(height=400, xaxis_tickangle=-45)
    st.plotly_chart(fig_ratio, use_container_width=True)

# Footer
st.markdown("🚀 **Enhanced Dashboard** | Comprehensive Business Analytics") 