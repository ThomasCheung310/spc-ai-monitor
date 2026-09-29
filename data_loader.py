import pandas as pd

def read_csv(file_path):
    df = pd.read_csv(file_path)
    spc_data = dict(zip(df["Timestamp"], df["Value"]))
    usl = df["USL"].iloc[0]
    lsl = df["LSL"].iloc[0]

    required_columns = ["Timestamp", "Value", "USL", "LSL"]
    metadata_columns = [i for i in df.columns if i not in required_columns]
    process_metadata = df[metadata_columns].iloc[0].to_dict()

    return spc_data, usl, lsl, process_metadata