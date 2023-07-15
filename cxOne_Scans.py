import argparse
import json
import logging
import os
import re
import requests
import sys
from openpyxl import Workbook
from datetime import datetime
import pandas as pd

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        handlers=[
            logging.FileHandler("api_logs.log"),
            logging.StreamHandler()
        ]
    )

def is_valid_date(date):
    date_regex = r"^\d{4}-\d{2}-\d{2}$"
    return re.match(date_regex, date) is not None

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
    payload = {}
    headers = {
        'Accept': 'application/json;version=1.0',
        'Authorization': access_token
    }
    response = requests.get(url, headers=headers, data=payload)
    return response

def make_get_request_with_pagination(url, access_token, offset, limit):
    url += f"&offset={offset}&limit={limit}"
    return make_get_request(url, access_token)

def flatten_dict(data, parent_key='', sep='_'):
    flattened_dict = {}
    for key, value in data.items():
        new_key = parent_key + sep + key if parent_key else key
        if key == 'id':
            new_key = 'Scan ID'
        elif key == 'status':
            new_key = 'Scan Status'
        elif key == 'statusDetails_0_details':
            new_key = 'Scan Type'
        elif key == 'statusDetails_0_1_name':
            new_key = 'Scan Type Status'
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

def create_results_sheet(workbook, data):
    sheet = workbook.create_sheet(title='results')
    headers = ['Scan ID', 'Scan Status', 'Scan Type', 'Scan Type Status', 'Scan Type Status Details']
    sheet.append(headers)
    for item in data:
        row = [
            item.get('id'),
            item.get('status'),
            item.get('statusDetails_0_details'),
            item.get('statusDetails_0_1_name'),
            item.get('statusDetails_0_1_status'),
            item.get('statusDetails_0_1_details'),
        ]
        sheet.append(row)

def main():
    setup_logging()

    # Create an ArgumentParser object
    parser = argparse.ArgumentParser(description="Script for API data retrieval")

    # Add the start_date argument
    parser.add_argument("start_date", type=str, help="Start date (YYYY-MM-DD)")

    # Add the end_date argument
    parser.add_argument("end_date", type=str, help="End date (YYYY-MM-DD)")

    # Parse the command-line arguments
    args = parser.parse_args()

    # Validate start_date
    if not is_valid_date(args.start_date):
        logging.error("Error: Invalid start date format. Please use YYYY-MM-DD.")
        sys.exit(1)

    # Validate end_date
    if not is_valid_date(args.end_date):
        logging.error("Error: Invalid end date format. Please use YYYY-MM-DD.")
        sys.exit(1)

    start_date = args.start_date
    end_date = args.end_date

    refresh_token = get_refresh_token()
    if not refresh_token:
        logging.error("Failed to read refresh token from secrets.txt.")
        return

    access_token = get_access_token(refresh_token)
    if not access_token:
        logging.error("Failed to retrieve access token.")
        return

    url = f"https://fmdev.cxone.cloud/api/scans?start_date={start_date}&end_date={end_date}"
    response = make_get_request_with_pagination(url, access_token, offset=0, limit=2000)

    if response.status_code != 200:
        logging.error(f"Failed to retrieve data. Status code: {response.status_code}, Response: {response.text}")
        return

    current_date = datetime.now().strftime("%B-%d-%Y")
    file_name = f"jsonResponse_{current_date}.json"

    output_directory = "output"
    os.makedirs(output_directory, exist_ok=True)

    json_file_path = os.path.join(output_directory, file_name)

    try:
        with open(json_file_path, "w") as file:
            file.write(response.text)
        logging.info(f"JSON response saved in {json_file_path}")

        normalized_scans = []
        for scan in extract_scans_from_file(json_file_path):
            flattened_scan = flatten_dict(scan)
            normalized_scans.append(flattened_scan)

        modified_file_name = f"CxOne_Scans_Data_{current_date}.xlsx"

        excel_file_path = os.path.join(output_directory, modified_file_name)

        with pd.ExcelWriter(excel_file_path, engine='openpyxl') as writer:
            df = pd.DataFrame(normalized_scans)
            df.to_excel(writer, sheet_name='jsondump', index=False)
            create_results_sheet(writer.book, normalized_scans)

        logging.info(f"Excel file saved in {excel_file_path}")
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
