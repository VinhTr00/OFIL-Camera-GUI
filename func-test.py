import requests
import os
import getpass

# Get the name of the current Linux user
username = getpass.getuser()

print(f"Current Linux user: {username}")
# IP address and path to the picture file
ip_address = '192.168.0.100'
picture_path = '/Pictures/vinhtran.jpg'

# URL of the picture
url = f'http://{ip_address}{picture_path}'

# Destination file path to save the picture
destination_path = f"/home/{username}/Downloads/OFIL/vinhtran.jpg"

# Send an HTTP GET request to the URL
response = requests.get(url)

# Specify the path and name of the folder you want to create
folder_path = f"/home/{username}/Downloads/OFIL/"

# Create the folder
if not os.path.exists(folder_path):
    # Create the folder
    os.makedirs(folder_path)
    print(f"Folder '{folder_path}' created successfully.")
else:
    print(f"Folder '{folder_path}' already exists.")

# Check if the request was successful (status code 200)
if response.status_code == 200:
    # Save the picture to a file
    with open(destination_path, 'wb') as file:
        file.write(response.content)
    print('Picture downloaded successfully.')
else:
    print(f'Error downloading picture. Status code: {response.status_code}')