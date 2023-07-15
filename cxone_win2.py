import argparse
import datetime
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
    sheet = workbook.add_worksheet('results')
    headers = ['Scan ID', 'Scan Status', 'Scan Type', 'Scan Type Status', 'Scan Type Status Details', 'Scan Duration']
    sheet.write_row(0, 0, headers)
    for i, item in enumerate(data):
        row = [
            item.get('Scan ID'),
            item.get('Scan Status'),
            item.get('statusDetails_0_details'),
            item.get('statusDetails_0_1_name'),
            item.get('statusDetails_0_1_status'),
            item.get('statusDetails_0_1_details'),
            calc_scan_duration(item.get('created_at'), item.get('updated_at'))
        ]
        sheet.write_row(i + 1, 0, row)


def calc_scan_duration(createdAt, updatedAt):
    if not createdAt or not updatedAt:
        return "N/A"  # Return a default duration if the values are None or empty

    try:
        created_at = datetime.datetime.strptime(createdAt.split("T")[1].split(".")[0], "%H:%M:%S")
        updated_at = datetime.datetime.strptime(updatedAt.split("T")[1].split(".")[0], "%H:%M:%S")
        delta = updated_at - created_at
        return str(delta)
    except (ValueError, IndexError):
        return "Invalid Format"  # Return a message indicating invalid format if there's an error


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

    current_date = datetime.datetime.now().strftime("%B-%d-%Y")
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

        excel_file_path_jsondump = os.path.join(output_directory, modified_file_name)
        excel_file_path_results = os.path.join(output_directory, f"results_{current_date}.xlsx")

        # Create jsondump workbook
        workbook_jsondump = xlsxwriter.Workbook(excel_file_path_jsondump)
        worksheet_jsondump = workbook_jsondump.add_worksheet('jsondump')
        df = pd.DataFrame(normalized_scans)
        df.to_excel(excel_file_path_jsondump, sheet_name='jsondump', index=False)

        # Create results workbook
        workbook_results = xlsxwriter.Workbook(excel_file_path_results)
        create_results_sheet(workbook_results, normalized_scans)

        workbook_jsondump.close()
        workbook_results.close()

        logging.info(f"Excel files saved.")
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")


if __name__ == "__main__":
    main()
