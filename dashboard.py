import streamlit as st
import random       
import duckdb       
import pandas as pd       

st.set_page_config(page_title="Sales Dashboard", page_icon=":bar_chart:", layout="wide")

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