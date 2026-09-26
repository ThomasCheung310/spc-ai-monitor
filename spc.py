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

import numpy as np
import pandas as pd

def generate_spc_chart(spc_data, usl, lsl):  #spc_data is a dictionary
    df = pd.Series(spc_data)
    values = df.values
    timestamps = df.index

    mean = np.mean(values)
    standard_deviation = np.std(values)
    ucl = mean + 3 * standard_deviation
    lcl = mean - 3 * standard_deviation
    cpl = (mean - lsl) / (3 * standard_deviation)
    cpu = (usl - mean) / (3 * standard_deviation)
    cpk = min(cpl, cpu)

    spc_chart = {"Time": timestamps, "Data": values, "Mean": mean, "Standard_deviation": standard_deviation, "UCL": ucl, "LCL": lcl, "Cpl": cpl, "Cpu": cpu, "Cpk": cpk}
    return spc_chart

def detect_violations(spc_chart): #check spc chart base on Western Electric rule
    #zone_a: 2 sigma < y < 3 sigma
    #zone_b: 1 sigma < y < 2 sigma
    #sone_c: mean < y < 1 sigma
    df = pd.DataFrame({"Timestamp": spc_chart["Time"], "Value": spc_chart["Data"]})

    #rule 1
    rule1 = []
    violation_r1 = df[(df["Value"] > spc_chart["UCL"]) | (df["Value"] < spc_chart["LCL"])]
    for _, j in violation_r1.iterrows():
        rule1.append({
    "Timestamp": j["Timestamp"],
    "Value": j["Value"],
    "Rule": "Rule 1: Point outside control limits"
})

    #rule 2
    rule2 = []
    upper_bound2 = spc_chart["Mean"] + 2 * spc_chart["Standard_deviation"] 
    lower_bound2 = spc_chart["Mean"] - 2 * spc_chart["Standard_deviation"] 
    for i in range(2, len(df)):
        window = df.iloc[i-2:i+1]
        if ((window["Value"] > upper_bound2).sum() >= 2) or ((window["Value"] < lower_bound2).sum() >= 2):
            violation_r2 = df.iloc[i]
            rule2.append({
                "Timestamp": violation_r2["Timestamp"],
                "Value": violation_r2["Value"],
                "Rule": "Rule 2: 2 out of 3 points beyond 2σ on same side"
            })
        
    #rule 3
    rule3 = []
    upper_bound3 = spc_chart["Mean"] + spc_chart["Standard_deviation"] 
    lower_bound3 = spc_chart["Mean"] - spc_chart["Standard_deviation"] 
    for i in range(4, len(df)):
        window = df.iloc[i-4:i+1]
        if ((window["Value"] > upper_bound3).sum() >= 4) or ((window["Value"] < lower_bound3).sum() >= 4):
            violation_r3 = df.iloc[i]
            rule3.append({
                "Timestamp": violation_r3["Timestamp"],
                "Value": violation_r3["Value"],
                "Rule": "Rule 3: 4 out of 5 points beyond 1σ on same side"
            })

    #rule 4
    rule4 = []
    mean = spc_chart["Mean"]
    for i in range(7, len(df)):
        window = df.iloc[i-7:i+1]
        if ((window["Value"] > mean).sum() == 8) or ((window["Value"] < mean).sum() == 8):
            violation_r4 = df.iloc[i]
            rule4.append({
    "Timestamp": violation_r4["Timestamp"],
    "Value": violation_r4["Value"],
    "Rule": "Rule 4: 8 consecutive points on the same side"
})
    return rule1 + rule2 + rule3 + rule4

def spc_status(violations):
    if (len(violations) == 1):
        return "Monitor"
    elif (len(violations) >= 2):
        return "Attention"
    else:
        return "Stable"