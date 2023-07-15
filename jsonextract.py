# import json


# def extract_status_details(file_path):
#     # Read the JSON from file
#     with open(file_path, "r") as file:
#         json_response = file.read()

#     # Parse the JSON
#     json_data = json.loads(json_response)

#     # Extract the "statusDetails"
#     status_details = []
#     if "scans" in json_data:
#         scans = json_data["scans"]
#         for scan in scans:
#             if "statusDetails" in scan:
#                 status_details.extend(scan["statusDetails"])

#     return status_details

# def main():
#     file_path = "/Users/suryap/git/pythonDev/example.json"
#     status_details = extract_status_details(file_path)
#     for detail in status_details:
#         print("Name:", detail["name"])
#         print("Status:", detail["status"])
#         print("Details:", detail["details"])
#         print("LOC:", detail.get("loc", "N/A"))  # Print "loc" if available, otherwise "N/A"
#         print()

# if __name__ == "__main__":
#     main()




import json

def extract_status_details(file_path):
    # Read the JSON from file
    with open(file_path, "r") as file:
        json_response = file.read()

    # Parse the JSON
    json_data = json.loads(json_response)

    # Extract the "statusDetails"
    status_details = []
    if "scans" in json_data:
        scans = json_data["scans"]
        for scan in scans:
            if "statusDetails" in scan:
                for detail in scan["statusDetails"]:
                    if detail["name"] in ["sast"]:
                        status_details.append((detail["name"], detail["status"]))

    return status_details

def main():
    file_path = "/Users/suryap/git/pythonDev/example.json"
    status_details = extract_status_details(file_path)
    for name, status in status_details:
        print(f"name: {name} \nstatus: {status}")

if __name__ == "__main__":
    main()




