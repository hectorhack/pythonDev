import requests
import datetime


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

    return None


def make_get_request(url, access_token):
    payload = {}
    headers = {
        'Accept': 'application/json;version=1.0',
        'Authorization': access_token
    }
    response = requests.get(url, headers=headers, data=payload)
    return response


def main():
    refresh_token = get_refresh_token()
    if refresh_token:
        access_token = get_access_token(refresh_token)
        if access_token:
            url = "https://fmdev.cxone.cloud/api/scans?offset=0&limit=200"
            response = make_get_request(url, access_token)
            if response.status_code == 200:
                current_date = datetime.datetime.now().strftime("%B-%d-%Y")
                #file_name = f"jsonResponse_{current_date}.json"
                file_name = f"jsonResponse.json"

                with open(file_name, "w") as file:
                    file.write(response.text)
                print(f"JSON response saved in {file_name}")
            else:
                print("Failed to retrieve data.")
        else:
            print("Failed to retrieve access token.")
    else:
        print("Failed to read refresh token from secrets.txt.")


if __name__ == "__main__":
    main()
