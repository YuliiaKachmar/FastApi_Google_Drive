from googleapiclient.discovery import build
from google.oauth2 import credentials


from config import CLIENT_ID, CLIENT_SECRET


def get_drive_service(user):
    """
    Creates and returns a Google Drive service using the user's credentials.

    Args:
        user (dict): User information containing access and refresh tokens.

    Returns:
        googleapiclient.discovery.Resource: Google Drive service instance.
    """
    creds = credentials.Credentials(
        token=user['access_token'],
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        refresh_token=user['refresh_token']
    )
    return build('drive', 'v3', credentials=creds)


def get_folder_structure(folder_id, drive_service):
    """
    Recursively retrieves the folder structure of the specified folder in Google Drive.

    Args:
        folder_id (str): ID of the folder in Google Drive.
        drive_service (googleapiclient.discovery.Resource): Google Drive service instance.

    Returns:
        list: List of dictionaries representing files and folders in the specified folder.
    """
    files = []
    page_token = None

    while True:
        results = drive_service.files().list(q=f"'{folder_id}' in parents",
                                             fields='files(id, name, mimeType)',
                                             pageToken=page_token).execute()
        print(results)
        files.extend(results.get('files', []))
        page_token = results.get('nextPageToken')
        if not page_token:
            break

    for file in files:
        if file['mimeType'] == 'application/vnd.google-apps.folder':
            file['children'] = get_folder_structure(file['id'], drive_service)

    return files


def create_new_element(user, element_name: str, element_type: str, element_parent_id: str):
    """
    Creates a new file or folder in Google Drive.

    Args:
        user (dict): User information containing access and refresh tokens.
        element_name (str): Name of the new file or folder.
        element_type (str): Type of the new element ('file' or 'folder').
        element_parent_id (str): ID of the parent folder.

    Returns:
        dict or None: Information about the newly created file or folder, or None if creation fails.
    """
    drive_service = get_drive_service(user)
    new_file = None
    if element_type == 'file':
        file_metadata = {
            'name': element_name,
            'parents': [element_parent_id]
        }
        new_file = drive_service.files().create(body=file_metadata).execute()

    elif element_type == 'folder':
        folder_metadata = {
            'name': element_name,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [element_parent_id]
        }
        new_file = drive_service.files().create(body=folder_metadata).execute()

    return new_file


def delete_element(user, file_id: str):
    """
    Deletes a file or folder in Google Drive.

    Args:
        user (dict): User information containing access and refresh tokens.
        file_id (str): ID of the file or folder to be deleted.
    """
    get_drive_service(user).files().delete(fileId=file_id).execute()
