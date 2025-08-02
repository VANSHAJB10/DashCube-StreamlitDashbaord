import streamlit as st
import random       
import duckdb       
import pandas as pd 

import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(page_title="ST Sales Dashboard", page_icon=":bar_chart:" , layout="wide")

st.title("ST Sales Dashboard")
st.markdown("_Excel to Dashboard-v0.1_")

##################################### // Upload File // ########################################
with st.sidebar:
    st.header("Configuration")
    uploaded_excel_file = st.file_uploader("Upload your Excel file", type=["xlsx", "xls"])

if uploaded_excel_file is None:
    st.info("Please upload an Excel file to proceed.", icon ="ℹ️")
    st.stop() #it stops the execution of the script if no file is uploaded

##################################### // Load Data // ########################################
@st.cache_data
def load_data(uploaded_file):
    df = pd.read_excel(uploaded_file)
    return df


df = load_data(uploaded_excel_file)
all_months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

with st.expander("View Data", expanded=False):
    st.dataframe(df, 
                 column_config={"Year": st.column_config.NumberColumn(format="%d")},
    )

def plot_metric(label, value, prefix="", suffix="", show_graph=False, color_graph=""):
    fig = go.Figure()

    fig.add_trace(
        go.Indicator(
            value=value,
            gauge={
                "axis": {"range": [0, 100]}, 
                "bar": {"color": color_graph}
            },
            number={
                "prefix": prefix, 
                "suffix": suffix, 
                "font.size": 26,
            },
            title={
                "text": label, 
                "font":{"size": 26},
            },
        )
    )

    if show_graph:
        fig.add_trace(
            go.Scatter(
                x=all_months, 
                y=[random.randint(0, 100) for _ in all_months],
                mode="lines+markers",
                line={"color": color_graph},
            )
        )
    
    fig.update_xaxes(visible=False, fixedrange=True)
    fig.update_yaxes(visible=False, fixedrange=True)
    fig.update_layout(
        # paper_bgcolor="lightgrey",
        margin=dict(t=30, b=0),
        showlegend=False,
        plot_bgcolor="white",
        height=100,
    )

    st.plotly_chart(fig, use_container_width=True)
