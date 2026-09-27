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

import os
from dotenv import load_dotenv
from openai import OpenAI
import json

load_dotenv()
token = os.getenv("GROQ_API_KEY")
client = OpenAI(    
            base_url = "https://api.groq.com/openai/v1",   
            api_key = token,
        )

def get_ai_analysis(process, spc_chart, violations, process_metadata):
    #chart data
    process_name = process
    mean = spc_chart["Mean"]
    ucl = spc_chart["UCL"]
    lcl = spc_chart["LCL"]
    cpu = spc_chart["Cpu"]
    cpl = spc_chart["Cpl"]
    cpk = spc_chart["Cpk"]

    #violations
    #violations_str = json.dumps(violations, default=str, indent=2)
    violations_str = json.dumps(violations[:5], default=str, indent=2)
    process_metadata_str = json.dumps(process_metadata, indent=2)

    response = client.chat.completions.create(model="openai/gpt-oss-120b", 
                                              temperature= 0.2,
                                messages= [
                                        {"role": "system", "content": "You are a process engineer for a semiconductor fab. You will be given violations and process meta data. For each violation, respond in plain text in bullet points with organization, max 200 words and give: 1 sentence summary, 2 root causes, 2 action steps."},
                                        {"role": "user", "content": f"Process: {process_name} \n\n Chart Statistics: \n Mean: {mean}\n UCL: {ucl}\n LCL:\n{lcl}\n Cpu: {cpu}\n Cpl:\n{cpl}\n Cpk: {cpk}\n\n Detected Violations: {violations_str} \n\n Process Metadata: {process_metadata_str}"}]
    )

    return response.choices[0].message.content
    
    
if __name__ == "__main__":
    # dummy chart data
    process = "CVD for silicon oxide"
    spc_chart = {
        "Mean": "10nm",
        "UCL": "13nm",
        "LCL": "7nm",
        "Cpu": "1.3",
        "Cpl": "0.6",
        "Cpk": "0.6"
    }

    # dummy violations
    violations = [
        {"Timestamp": "2026-08-07, 06:30",
        "Value": "14nm",
        "Rule": "Rule 1: Point outside control limits"},
        {"Timestamp": "2026-08-07, 13:40",
        "Value": "11.2nm",
        "Rule": "Rule 3: 4 out of 5 points beyond 1σ on same side"}
    ]

    # dummy process metadata
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

    result = get_ai_analysis(process, spc_chart, violations, process_metadata)
    print(result)