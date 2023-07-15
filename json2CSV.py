import pandas as pd
import json
import datetime

def flatten_dict(data, parent_key='', sep='_'):
    flattened_dict = {}
    for key, value in data.items():
        new_key = parent_key + sep + key if parent_key else key
        if isinstance(value, dict):
            flattened_dict.update(flatten_dict(value, new_key, sep))
        elif isinstance(value, list):
            for i, item in enumerate(value):
                new_key = new_key + sep + str(i)
                if isinstance(item, dict):
                    flattened_dict.update(flatten_dict(item, new_key, sep))
                else:
                    flattened_dict[new_key] = item
        else:
            flattened_dict[new_key] = value
    return flattened_dict

def extract_scans_from_file(file_path):
    with open(file_path, 'r') as file:
        json_response = file.read()

    response_data = json.loads(json_response)
    scans = response_data.get("scans", [])
    

    return scans

# Example usage:
#json_file_path = "/Users/suryap/git/pythonDev/jsonResponse.json"
json_file_path = "/Users/suryap/git/pythonDev/example.json"
scans = extract_scans_from_file(json_file_path)

# Flatten nested dictionaries and lists
normalized_scans = []
for scan in scans:
    flattened_scan = flatten_dict(scan)
    normalized_scans.append(flattened_scan)

# Create DataFrame from normalized scans
df = pd.DataFrame(normalized_scans)


# Get the current date
current_date = datetime.datetime.now().strftime("%B-%d-%Y")

# Specify the output CSV file path
print("PRINTING CSV........")
# Generate the modified file name with the current date
modified_file_name = f"CxOne_Scans_Data_{current_date}.csv"

# Specify the output CSV file path with the modified file name
csv_file_path = f"/Users/suryap/git/pythonDev/{modified_file_name}"

# Export DataFrame to CSV file
df.to_csv(csv_file_path, index=False)
