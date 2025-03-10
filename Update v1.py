import requests
import os
import sys

github_repo = "https://raw.githubusercontent.com/your-username/your-repo/main/"

def get_latest_version(exe_name):
    url = github_repo + exe_name
    try:
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            return exe_name
        else:
            print("No new update available.")
            return None
    except Exception as e:
        print(f"Error checking latest version: {e}")
        return None

def download_latest_exe(exe_name):
    url = github_repo + exe_name
    try:
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            exe_path = os.path.join(os.getcwd(), exe_name)
            with open(exe_path, "wb") as file:
                for chunk in response.iter_content(1024):
                    file.write(chunk)
            print("Update successful! Restarting...")
            os.startfile(exe_path)
            sys.exit()
        else:
            print("Failed to download the new version.")
    except Exception as e:
        print(f"Error downloading update: {e}")

if __name__ == "__main__":
    exe_name = os.path.basename(sys.argv[0])  # Get the current executable name
    latest_version = get_latest_version(exe_name)
    
    if latest_version:
        print(f"New version {latest_version} available! Updating...")
        download_latest_exe(exe_name)
    else:
        print("Up to date!")
