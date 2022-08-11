import google.auth

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


def fetch_start_page_token(creds):
    """Retrieve page token for the current state of the account.
    Returns & prints : start page token
    """
    try:
        # create drive api client
        service = build('drive', 'v3', credentials=creds)
        # pylint: disable=maybe-no-member
        response = service.changes().getStartPageToken().execute()
        print(f'Start token: {response.get("startPageToken")}')
    except HttpError as error:
        print(f'An error occurred: {error}')
        response = None
    return response.get('startPageToken')

def fetch_changes(saved_start_page_token, creds):
    """Retrieve the list of changes for the currently authenticated user.
        prints changed file's ID
    Args:
        saved_start_page_token : StartPageToken for the current state of the
        account.
    Returns: saved start page token.
    """
    try:
        # create drive api client
        service = build('drive', 'v3', credentials=creds)

        # Begin with our last saved start token for this user or the
        # current token from getStartPageToken()
        page_token = saved_start_page_token
        # pylint: disable=maybe-no-member

        changed_files = []
        while page_token is not None:
            print(page_token)
            response = service.changes().list(pageToken=page_token,
                                              spaces='drive',
                                              fields='*').execute()
            file_id = ''
            for change in response.get('changes'):
                # Process change
                print(f'Change found for file: {change.get("fileId")}')
                file_id = change.get('fileId')
                changed_files.append(file_id)
            page_token = response.get('nextPageToken')
    except HttpError as error:
        print(f'An error occurred: {error}')
    return changed_files

