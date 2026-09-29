# spc-ai-monitor
# Copyright (C) 2026  Thomas Cheung

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import streamlit as st
import pandas as pd
import json
from spc import generate_spc_chart, detect_violations, spc_status
from ai import get_ai_analysis
import datetime
import plotly.graph_objects as go
import plotly.express as px
import os
from data_loader import read_csv


st.set_page_config(page_title="SPC AI Monitor", layout="wide")
st.title("SPC AI Monitor")
st.info("📊 This demo is running on simulated process data. In a production deployment, this app would connect to live fab data exports.")
if st.button("🔄 Refresh"):
    st.rerun()

def load_charts():
    data_folder = os.path.join(os.path.dirname(__file__), "data")
    charts = []

    for i in os.listdir(data_folder):
        if i.endswith(".csv"):
            file_path = os.path.join(data_folder, i)
            spc_data, usl, lsl, process_metadata = read_csv(file_path)
            process_name = process_metadata.get("Process", "Unknown Process")
            
            spc_chart = generate_spc_chart(spc_data, usl, lsl)

            violations = detect_violations(spc_chart)
            status = spc_status(violations)
            charts.append({
                    "Process Name": process_name,
                    "Process Metadata": process_metadata,
                    "SPC Chart": spc_chart,
                    "Violations": violations,
                    "Status": status
                        })

    return charts

def plot(process_name, spc_chart, violations, process_metadata):
    fig = go.Figure()

    fig.add_trace(go.Scatter(x=spc_chart["Timestamp"], y=spc_chart["Value"], mode="lines", name="Value"))

    fig.add_hline(y=spc_chart["USL"], line_dash="dash", line_color="blue", annotation_text="USL")
    fig.add_hline(y=spc_chart["LSL"], line_dash="dash", line_color="blue", annotation_text="LSL")
    fig.add_hline(y=spc_chart["UCL"], line_dash="dash", line_color="red", annotation_text="UCL")
    fig.add_hline(y=spc_chart["LCL"], line_dash="dash", line_color="red", annotation_text="LCL")
    fig.add_hline(y=spc_chart["Mean"], line_dash="dash", line_color="green", annotation_text="Mean")

    col1, col2 = st.columns(2)
    col1.metric("Cpk", round(spc_chart["Cpk"], 2))
    col2.metric("Violations", len(violations))
    st.plotly_chart(fig)

    button_key = f"ai_btn_{process_name}"
    result_key = f"ai_result_{process_name}"

    if len(violations) > 0:
        if st.button("🤖 Analyze with AI", key=button_key):
            with st.spinner("Analyzing..."):
                analysis = get_ai_analysis(process_name, spc_chart, violations, process_metadata)
                st.session_state[result_key] = analysis
        
            
        if result_key in st.session_state:
            st.info("⚠️ AI analysis is based on detected violations and process metadata. Validate with a process engineer before taking action.")
            st.markdown(st.session_state[result_key])


charts = load_charts()
attention_count = sum(1 for i in charts if i["Status"] == "Attention")
monitor_count = sum(1 for i in charts if i["Status"] == "Monitor")
stable_count = sum(1 for i in charts if i["Status"] == "Stable")

with st.expander(f"⚠️ Attention ({attention_count})"):
    for c in charts:
        if c["Status"] == "Attention":
            st.subheader(c["Process Name"])
            plot(c["Process Name"], c["SPC Chart"], c["Violations"], c["Process Metadata"])

with st.expander(f"💻 Monitor ({monitor_count})"):
    for c in charts:
        if c["Status"] == "Monitor":
            st.subheader(c["Process Name"])
            plot(c["Process Name"], c["SPC Chart"], c["Violations"], c["Process Metadata"])

with st.expander(f"✅ Stable ({stable_count})"):
    for c in charts:
        if c["Status"] == "Stable":
            st.subheader(c["Process Name"])
            plot(c["Process Name"], c["SPC Chart"], c["Violations"], c["Process Metadata"])
            
