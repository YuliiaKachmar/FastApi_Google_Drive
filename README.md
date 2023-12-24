# FastApi_Google_Drive
Welcome to FastApi_Google_Drive! This is a FastAPI-based web application designed to interact with Google Drive through the Google Drive API. The application allows users to authenticate via OAuth 2.0, view their Google Drive folder structure, create new files and folders, delete existing files, and manage their Google Drive content seamlessly.

## Instalation:
 - git clone https://github.com/YuliiaKachmar/FastApi_Google_Drive.git
 - cd {projectName}
 - pip install -r requirements.txt
 - python app.py

## Endpoints:
- /: Home page
- /welcome: Welcome page
- /login: Initiates OAuth login process
- /auth: OAuth authentication callback
- /files: File listing page
- /create_element: Creates a new file element
- /delete_file/{file_id}: Deletes a file
- /logout: User logout
