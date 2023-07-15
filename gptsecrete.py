# import pandas as pd
# import json
# from datetime import datetime

# # Load JSON file
# with open('example.json') as f:
#     data = json.load(f)

# # Convert JSON data to DataFrame
# df = pd.json_normalize(data, 'scans', errors='ignore')

# # Convert 'createdAt' and 'updatedAt' to datetime format
# df['createdAt'] = pd.to_datetime(df['createdAt'])
# df['updatedAt'] = pd.to_datetime(df['updatedAt'])

# # Calculate Scan Duration
# df['scanDuration'] = (df['updatedAt'] - df['createdAt']).dt.total_seconds()

# # Flatten the nested 'statusDetails' column
# df_statusDetails = pd.json_normalize(df['statusDetails'].explode(), errors='ignore')

# # Filter rows where 'statusDetails.name' is 'sast'
# df_statusDetails_sast = df_statusDetails[df_statusDetails['name'] == 'sast']

# # Rename 'status' in 'df_statusDetails_sast' to 'statusDetails_status' to avoid confusion
# df_statusDetails_sast.rename(columns={'status': 'statusDetails_status'}, inplace=True)

# # Merge the 'sast' statusDetails back into the main dataframe
# df_sast = pd.concat([df, df_statusDetails_sast], axis=1)

# # Select only the specified columns
# selected_columns = ['id', 'branch', 'projectName', 'initiator', 'statusDetails_status', 'details', 'scanDuration']
# df_selected = df_sast[selected_columns]

# # Save DataFrame to CSV
# df_selected.to_csv('selected_scans_data.csv', index=False)

# # Save DataFrame to Excel
# df_selected.to_excel('selected_scans_data.xlsx', index=False)

import argparse
import datetime
import glob
import json
import logging
import os
import re
import requests
import sys
import pandas as pd
import xlsxwriter

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        handlers=[
            logging.FileHandler("api_logs.log"),
            logging.StreamHandler()
        ]
    )

def get_refresh_token():
    with open('secrets.txt', 'r') as file:
        refresh_token = file.read().strip()
    return refresh_token

def get_access_token(refresh_token):
    url = "https://fmdev.cxone.cloud/auth/realms/fmdev/protocol/openid-connect/token"
    payload = {
        'grant_type': 'refresh_token',
        'client_id': 'ast-app',
        'refresh_token': refresh_token
    }
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    response = requests.post(url, headers=headers, data=payload)
    if response.status_code == 200:
        access_token = response.json().get('access_token')
        return access_token
    logging.error(f"Failed to retrieve access token: {response.text}")
    return None

def make_get_request(url, access_token):
    headers = {
        'Accept': 'application/json;version=1.0',
        'Authorization': access_token
    }
    response = requests.get(url, headers=headers)
    return response

def flatten_dict(data, parent_key='', sep='_'):
    flattened_dict = {}
    for key, value in data.items():
        new_key = parent_key + sep + key if parent_key else key
        if isinstance(value, dict):
            flattened_dict.update(flatten_dict(value, new_key, sep))
        elif isinstance(value, list):
            for i, item in enumerate(value):
                if isinstance(item, dict):
                    flattened_dict.update(flatten_dict(item, new_key + sep + str(i)))
        else:
            flattened_dict[new_key] = value
    return flattened_dict

def get_scan_ids_from_file(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return [item['scanId'] for item in data]

def get_scan_data(access_token, scan_id):
    url = f"https://fmdev.cxone.cloud/api/scans/{scan_id}"
    response = make_get_request(url, access_token)
    if response.status_code == 200:
        return flatten_dict(response.json())
    logging.error(f"Failed to retrieve data for scan {scan_id}: {response.text}")
    return None

def fetch_status_details(scan_data):
    keys = [k for k in scan_data.keys() if 'statusDetails' in k]
    for key in keys:
        if 'name' in key and scan_data[key] == 'SAST':
            return {k.replace(key.split('_name')[0] + '_', ''): v for k, v in scan_data.items() if key.split('_name')[0] in k}
    return None

def main():
    setup_logging()

    refresh_token = get_refresh_token()
    if not refresh_token:
        logging.error("Failed to read refresh token from secrets.txt.")
        return

    access_token = get_access_token(refresh_token)
    if not access_token:
        logging.error("Failed to retrieve access token.")
        return

    directory_path = "/Users/suryap/git/pythonDev/input"
    json_files = glob.glob(os.path.join(directory_path, "*.json"))

    all_status_details = []
    for json_file in json_files:
        scan_ids = get_scan_ids_from_file(json_file)
        for scan_id in scan_ids:
            scan_data = get_scan_data(access_token, scan_id)
            status_details = fetch_status_details(scan_data)
            if status_details:
                all_status_details.append(status_details)

    df = pd.DataFrame(all_status_details)
    df.to_excel("output.xlsx", index=False)

if __name__ == "__main__":
    main()
