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

st.set_page_config(page_title="SPC AI Monitor", layout="wide")
st.title("SPC AI Monitor")

def load_demo_data():
    process = "CVD for silicon oxide"
    # simulate some data with a clear violation
    process_metadata = {"Parameter": "Film Thickness",
    "Units": "nm",
    "Target": 500,
    "Process": "PECVD SiO2",
    "RF_Power": "120 W",
    "Pressure": "900 mTorr",
    "SiH4_Flow": "100 sccm",
    "N2O_Flow": "50 sccm",
    "Temperature": "400 C",
    "Deposition_Time": "60 s",
    "Tool": "PECVD Tool A",
    "Last_Maintenance": "2024-01-01"
       
    }

    data = {datetime.datetime(2024, 1, 1, 8, 0) + datetime.timedelta(minutes=i*15): 100 + i*0.5 for i in range(30)}
    spc_chart = generate_spc_chart(data, usl=120, lsl=80)

    violations = detect_violations(spc_chart)
    status = spc_status(violations)

    return process, process_metadata, spc_chart, violations, status


process, process_metadata, spc_chart, violations, status = load_demo_data()

def plot(spc_chart, violations, process_metadata):
    fig = go.Figure()

    fig.add_trace(go.Scatter(x=spc_chart["Time"], y=spc_chart["Data"], mode="lines", name="Value"))

    fig.add_hline(y=spc_chart["UCL"], line_dash="dash", line_color="red", annotation_text="UCL")
    fig.add_hline(y=spc_chart["LCL"], line_dash="dash", line_color="red", annotation_text="LCL")
    fig.add_hline(y=spc_chart["Mean"], line_dash="dash", line_color="green", annotation_text="Mean")

    col1, col2 = st.columns(2)
    col1.metric("Cpk", round(spc_chart["Cpk"], 2))
    col2.metric("Violations", len(violations))
    st.plotly_chart(fig)

    if st.button("🤖 Analyze with AI"):
        with st.spinner("Analyzing..."):
            analysis = get_ai_analysis(process, spc_chart, violations, process_metadata)
            st.markdown(analysis)

attention_count = 1 if status == "Attention" else 0
with st.expander(f"⚠️ Attention ({attention_count})"):
    if status == "Attention":
        plot(spc_chart, violations, process_metadata)

attention_count = 1 if status == "Monitor" else 0
with st.expander("💻 Monitor"):
    if status == "Monitor":
        plot(spc_chart, violations, process_metadata)

attention_count = 1 if status == "Stable" else 0
with st.expander("✅ Stable"):
    if status == "Stable":
        plot(spc_chart, violations, process_metadata)

