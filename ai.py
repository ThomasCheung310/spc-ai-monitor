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

def get_ai_analysis(process_name, spc_chart, violations, process_metadata):
    #chart data
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
    
    
