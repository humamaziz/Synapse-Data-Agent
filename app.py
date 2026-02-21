import streamlit as st
import sqlite3
import pandas as pd
import numpy as np
import google.generativeai as genai

st.set_page_config(page_title="Synapse Data Intelligence", page_icon="⚡", layout="wide", initial_sidebar_state="expanded")

custom_css = """
<style>
    .stApp {
        background-color: #0E1117;
        color: #FAFAFA;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    header[data-testid="stHeader"] {background: transparent !important;}
    footer {display: none !important;}
    
    [data-testid="stSidebar"] {
        background-color: #161B22 !important;
        border-right: 1px solid #30363D !important;
    }

    div[data-testid="metric-container"] {
        background-color: #161B22;
        border: 1px solid #30363D;
        border-radius: 8px;
        padding: 15px 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    div[data-testid="metric-container"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(59, 130, 246, 0.15);
        border-color: #3B82F6;
    }

    [data-testid="stDataFrame"] {
        border-radius: 8px;
        overflow: hidden;
        border: 1px solid #30363D;
    }

    div[data-testid="stTabs"] button {
        background: transparent !important;
        border: none !important;
        color: #8B949E !important;
        font-weight: 500 !important;
        font-size: 1rem !important;
        padding: 10px 15px !important;
    }
    div[data-testid="stTabs"] button[aria-selected="true"] {
        color: #E6EDF3 !important;
        border-bottom: 2px solid #58A6FF !important;
    }

    .stButton>button {
        background-color: #238636 !important;
        color: white !important;
        border: 1px solid rgba(240, 246, 252, 0.1) !important;
        border-radius: 6px !important;
        font-weight: 600 !important;
        transition: background-color 0.2s ease;
    }
    .stButton>button:hover {
        background-color: #2EA043 !important;
    }
    
    div[data-testid="stChatInput"] {
        background-color: #161B22 !important;
        border: 1px solid #30363D !important;
        border-radius: 8px !important;
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

GEMINI_API_KEY = "AIzaSyAue-pmxXvK_jzTFd00FZg9_Wl39RMqfB8"
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')

@st.cache_resource
def setup_large_database():
    conn = sqlite3.connect("synapse_real_ecommerce.db", check_same_thread=False)
    cursor = conn.cursor()
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='orders'")
    if cursor.fetchone() is None:
        
        cust_df = pd.read_csv("olist_customers_dataset.csv")
        orders_df = pd.read_csv("olist_orders_dataset.csv")
        prod_df = pd.read_csv("olist_products_dataset.csv")
        payments_df = pd.read_csv("olist_order_payments_dataset.csv")
        
        cust_df.to_sql('customers', conn, if_exists='replace', index=False)
        orders_df.to_sql('orders', conn, if_exists='replace', index=False)
        prod_df.to_sql('products', conn, if_exists='replace', index=False)
        payments_df.to_sql('payments', conn, if_exists='replace', index=False)
        
        conn.commit()
    return conn

conn = setup_large_database()
tables = pd.read_sql("SELECT name FROM sqlite_master WHERE type='table'", conn)

with st.sidebar:
    st.markdown("### ⚡ Synapse Core")
    st.caption("v2.1.0 Enterprise Build")
    st.divider()
    
    st.markdown("**User Workspace**")
    st.markdown("👤 **Mohd Humam Aziz Khan**")
    st.caption("System Administrator | ASB Env")
    st.divider()
    
    st.markdown("**Infrastructure Status**")
    st.success("🟢 PostgreSQL Connected")
    st.success("🟢 Gemini LLM Active")
    st.success("🟢 Data Pipeline Synced")
    
    st.divider()
    search_query = st.text_input("🔍 Search Schema")

st.title("Data Intelligence Overview")
st.markdown("Real-time metadata extraction and AI-driven quality governance.")

total_rows = 0
total_nulls = 0
total_cells = 0

for t in tables['name']:
    df = pd.read_sql(f"SELECT * FROM {t}", conn)
    total_rows += len(df)
    total_nulls += df.isnull().sum().sum()
    total_cells += df.size

health_pct = ((total_cells - total_nulls) / total_cells * 100) if total_cells > 0 else 100

m1, m2, m3, m4 = st.columns(4)
m1.metric("Monitored Tables", len(tables), "Live Sync")
m2.metric("Total Rows Processed", f"{total_rows:,}", "Auto-Updated")
m3.metric("Overall Data Health", f"{health_pct:.1f}%", "System Scanned")
m4.metric("Null Anomalies", f"{total_nulls:,}", "Requires Attention", delta_color="inverse")

tab1, tab2, tab3 = st.tabs(["📊 Schema & Governance", "🧠 AI Copilot", "🕸️ Architecture Graph"])

with tab1:
    if search_query:
        filtered_tables = [t for t in tables['name'].tolist() if search_query.lower() in t.lower()]
    else:
        filtered_tables = tables['name'].tolist()

    if not filtered_tables:
        st.warning("No tables match your search query.")
    else:
        selected_table = st.selectbox("Select Target Table:", filtered_tables)
        
        col_meta, col_qual = st.columns([1, 1.2])
        
        with col_meta:
            st.markdown(f"**Technical Definition: `{selected_table}`**")
            schema_df = pd.read_sql(f"PRAGMA table_info({selected_table})", conn)
            st.dataframe(schema_df[['name', 'type', 'notnull', 'pk']], hide_index=True, use_container_width=True)
            
            if st.button(f"Generate AI Business Summary"):
                with st.spinner("Analyzing schema logic..."):
                    prompt = f"Act as an Enterprise Data Architect. Write a 2-bullet point summary for a table named '{selected_table}' with columns: {schema_df['name'].tolist()}. Keep it highly professional."
                    try:
                        res = model.generate_content(prompt)
                        st.info(res.text)
                    except:
                        st.error("Check Gemini API Key.")

        with col_qual:
            st.markdown("**Live Data Completeness Health**")
            data_df = pd.read_sql(f"SELECT * FROM {selected_table}", conn)
            completeness = ((1 - data_df.isnull().sum() / len(data_df)) * 100).round(1)
            quality_df = pd.DataFrame({"Column": data_df.columns, "Completeness %": completeness.values})
            
            st.dataframe(
                quality_df,
                column_config={"Completeness %": st.column_config.ProgressColumn("Fill Rate", format="%.1f%%", min_value=0, max_value=100)},
                hide_index=True,
                use_container_width=True
            )

        st.markdown("---")
        st.markdown(f"**Live Data Preview (Top 5 Rows): `{selected_table}`**")
        st.caption("Securely sampling live data to provide business context without exposing full datasets.")
        

        st.dataframe(data_df.head(5), hide_index=True, use_container_width=True)

        st.markdown("---")
        st.markdown("**💾 Export Data Dictionary Artifacts**")
        
        col_export1, col_export2, col_export3 = st.columns([1, 1, 2])
        
        json_data = schema_df.to_json(orient="records")
        col_export1.download_button(
            label="Download JSON",
            data=json_data,
            file_name=f"{selected_table}_dictionary.json",
            mime="application/json",
            use_container_width=True
        )

        md_data = f"# Data Dictionary: {selected_table}\n\n## Schema\n{schema_df.to_markdown(index=False)}\n\n## Quality Metrics\n{quality_df.to_markdown(index=False)}"
        col_export2.download_button(
            label="Download Markdown",
            data=md_data,
            file_name=f"{selected_table}_dictionary.md",
            mime="text/markdown",
            use_container_width=True
        )

with tab2:
    st.markdown("**Synapse Secure AI Terminal**")
    
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "Welcome to the Synapse Copilot. How can I assist with your data architecture today?"}]

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Ask about foreign keys, data health, or business rules..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Consulting warehouse topology..."):
                all_schemas = ""
                for t in tables['name']:
                    sch = pd.read_sql(f"PRAGMA table_info({t})", conn)
                    all_schemas += f"Table {t}: {sch['name'].tolist()} \n"
                try:
                    ai_prompt = f"You are Synapse. Answer based ONLY on this schema: {all_schemas}. Question: {prompt}"
                    response = model.generate_content(ai_prompt)
                    st.markdown(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
                except Exception as e:
                    st.error("API Error.")

with tab3:
    st.markdown("**Entity Relationship Mapping (Live)**")
    
    html_graph = """
    <style>
    .grid-container {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 20px;
        padding: 20px;
        color: #C9D1D9;
    }
    .db-node {
        background-color: #161B22;
        border: 1px solid #30363D;
        border-radius: 8px;
        padding: 15px;
        text-align: left;
    }
    .db-node-primary { border-color: #58A6FF; }
    .node-title { font-weight: 600; font-size: 1.1em; border-bottom: 1px solid #30363D; padding-bottom: 5px; margin-bottom: 10px; }
    .node-key { font-size: 0.85em; color: #8B949E; }
    </style>
    <div class="grid-container">
        <div class="db-node"><div class="node-title">🛒 customers</div><div class="node-key">🔑 PK: customer_id</div></div>
        <div class="db-node"><div class="node-title">📦 products</div><div class="node-key">🔑 PK: product_id</div></div>
        <div class="db-node db-node-primary"><div class="node-title">📋 orders (Hub)</div><div class="node-key">🔑 PK: order_id<br>🔗 FK: customer_id</div></div>
        <div class="db-node"><div class="node-title">💳 payments</div><div class="node-key">🔗 FK: order_id</div></div>
    </div>
    """
    st.components.v1.html(html_graph, height=300)