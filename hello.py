import json

file_path = "example.json"
file_path="/Users/suryap/git/pythonDev/output/jsonResponse_July-06-2023.json"
def read_json():
    with open(file_path, 'r') as file:
        json_response = json.load(file)
        key_count=len(json_response.keys()) #counting keys No of keys: 3 for example totalCount, filteredTotalCount, scans
        print(f"No of keys: {key_count}")
        for key, value in json_response.items():
            print(key)
            #print(f"Key: {key}, Value: {value}")
            #print(key, value)
    #return json_response

print(read_json())

# import json

# file_path = "/Users/suryap/git/pythonDev/output/jsonResponse_July-06-2023.json"

# def count_nested_keys(data):
#     key_count = 0
#     for key, value in data.items():
#         if isinstance(value, dict):
#             key_count += count_nested_keys(value)
#         else:
#             key_count += 1
#     return key_count

# def read_json():
#     with open(file_path, 'r') as file:
#         json_response = json.load(file)
#         key_count = len(json_response.keys())
#         output = f"No of keys: {key_count}\n"
#         scans = json_response.get("scans", [])
        
#         for scan in scans:
#             key_count = count_nested_keys(scan)
#             output += f"Nested key count: {key_count}\n"
            
#     with open("out.txt", "w") as output_file:
#         output_file.write(output)

# read_json()




# import json

# file_path = "/Users/suryap/git/pythonDev/output/jsonResponse_July-06-2023.json"

# def read_json():
#     with open(file_path, 'r') as file:
#         json_response = json.load(file)
#         key_count = len(json_response.keys())
#         output = f"No of keys: {key_count}\n"
#         scans = json_response.get("scans", [])
#         second_key = []
#         for scan in scans:
#             for key, value in scan.items():
#                 if isinstance(value, dict):
#                     for second_key in value.keys():
#                         output += second_key + "\n"

#     with open("out.txt", "w") as output_file:
#         output_file.write(output)

# read_json()


# import json

# file_path = "/Users/suryap/git/pythonDev/output/jsonResponse_July-06-2023.json"

# def read_json():
#     with open(file_path, 'r') as file:
#         json_response = json.load(file)
#         key_count = len(json_response.keys())
#         output = f"No of keys: {key_count}\n"
#         scans = json_response.get("scans", [])
#         scandetails = json_response.get("statusDetails", [])

#         for scan in scans:
#             keys_to_read = ["id", "status", "branch", "createdAt", "updatedAt", "projectId", "projectName", "userAgent", "initiator"]  # Example: Specify the keys you want to read
#             for key, value in scan.items():
#                 if key in keys_to_read:
#                     output += f"{key}: {value}\n"

#         for scanDetails in scandetails:
#             keys_to_read2 = ["name", "status"]
#             output2 = ""
#             for key, value in scanDetails.items():
#                 if key in keys_to_read2:
#                     output2 += f"{key}: {value}\n\n"
#                     print(output2)

#     with open("out.txt", "w") as output_file:
#         output_file.write(f"{output}\n")
#     with open("out2.txt", "w") as output_file2:
#         output_file2.write(output2)
        

# read_json()



# import json

# file_path = "/Users/suryap/git/pythonDev/output/jsonResponse_July-06-2023.json"

# def process_scans(scans):
#     output = ""
#     for scan in scans:
#         for key, value in scan.items():
#             if key == "statusDetails":
#                 output += process_status_details(value)
#             else:
#                 output += f"{key}: {value}\n"
#     return output

# def process_status_details(statusDetails):
#     output = ""
#     if isinstance(statusDetails, list):
#         for detail in statusDetails:
#             if isinstance(detail, dict):
#                 name = detail.get("name", "")
#                 status = detail.get("status", "")
#                 output += f"Name: {name}, Status: {status}\n"
#     return output

# def read_json():
#     with open(file_path, 'r') as file:
#         json_response = json.load(file)
#         key_count = len(json_response.keys())
#         output = f"No of keys: {key_count}\n"
#         scans = json_response.get("scans", [])
#         statusDetails = json_response.get("statusDetails", [])

#         output += process_scans(scans)

#     with open("out.txt", "w") as output_file:
#         output_file.write(output)

# read_json()


# import json

# file_path = "/Users/suryap/git/pythonDev/output/jsonResponse_July-06-2023.json"

# def read_json():
#     with open(file_path, 'r') as file:
#         json_response = json.load(file)
#         key_count = len(json_response.keys())
#         output = f"No of keys: {key_count}\n"
#         scans = json_response.get("scans", [])
#         scandetails = json_response.get("statusDetails", [])

#         for scan in scans:
#             keys_to_read = ["id", "status", "branch", "createdAt", "updatedAt", "projectId", "projectName", "userAgent", "initiator"]  # Example: Specify the keys you want to read
#             for key, value in scan.items():
#                 if key in keys_to_read:
#                     output += f"{key}: {value}\n"

#         for scanDetails in scandetails:
#             keys_to_read2 = ["name", "status", "loc"]
#             output2 = ""
#             for key, value in scanDetails.items():
#                 if key in keys_to_read2:
#                     output2 += f"{key}: {value}\n"
#             print(output2)

#             with open("out2.txt", "a") as output_file:
#                 output_file.write(output2)

# read_json()


