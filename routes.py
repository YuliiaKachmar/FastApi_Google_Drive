from authlib.integrations.starlette_client import OAuth, OAuthError
from fastapi import APIRouter
from starlette.requests import Request
from starlette.responses import RedirectResponse
from starlette.templating import Jinja2Templates

# Import configuration and utility functions
from config import CLIENT_ID, CLIENT_SECRET, SCOPES
from drive_manager import get_drive_service, get_folder_structure, create_new_element, delete_element

# Create an APIRouter instance
router = APIRouter()

# Initialize OAuth and configure Google authentication
oauth = OAuth()
oauth.register(
    name='google',
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': ' '.join(SCOPES), 'redirect_uri': 'http://localhost:8000/auth'}
)

# Configure Jinja2 templates
templates = Jinja2Templates(directory="templates")

# In-memory session storage
session = dict()

@router.get("/")
def index(request: Request):
    """
    Route for the home page.

    If the user is authenticated, redirects to the welcome page.
    Otherwise, renders the home page.

    Args:
        request (Request): The incoming request.

    Returns:
        RedirectResponse or TemplateResponse: Depending on the user's authentication status.
    """
    user = request.session.get('user')
    if user:
        return RedirectResponse('/welcome')
    return templates.TemplateResponse(name="home.html", context={"request": request})


@router.get('/welcome')
def welcome(request: Request):
    """
    Route for the welcome page.

    If the user is not authenticated, redirects to the home page.
    Otherwise, renders the welcome page.

    Args:
        request (Request): The incoming request.

    Returns:
        RedirectResponse or TemplateResponse: Depending on the user's authentication status.
    """
    user = request.session.get('user')
    if not user:
        return RedirectResponse('/')
    return templates.TemplateResponse(name='welcome.html', context={'request': request, 'user': user})


@router.get("/login")
async def login(request: Request):
    """
    Route for initiating the OAuth login process.

    Redirects the user to the Google OAuth authorization URL.

    Args:
        request (Request): The incoming request.

    Returns:
        HTTPResponse: Redirects to the Google OAuth authorization URL.
    """
    url = request.url_for('auth')
    return await oauth.google.authorize_redirect(request, url)


@router.get('/auth')
async def auth(request: Request):
    """
    Route for handling the OAuth authentication callback.

    Retrieves the access token and stores user information in the session.

    Args:
        request (Request): The incoming request.

    Returns:
        RedirectResponse: Redirects to the file listing page.
        TemplateResponse: Renders an error page if OAuth authentication fails.
    """
    try:
        token = await oauth.google.authorize_access_token(request)
    except OAuthError as e:
        return templates.TemplateResponse(name='error.html', context={'request': request, 'error': e.error})

    session['user'] = {'access_token': token['access_token'], 'refresh_token': token['refresh_token']}
    return RedirectResponse('/files')


@router.route('/files', methods=['GET', 'DELETE', 'POST', 'PUT'])
def list_files(request: Request):
    """
    Route for listing files.

    If the user is not authenticated, redirects to the home page.
    Otherwise, renders the file listing page.

    Args:
        request (Request): The incoming request.

    Returns:
        RedirectResponse or TemplateResponse: Depending on the user's authentication status.
    """
    user = session.get('user')

    if not user:
        return RedirectResponse('/')

    return templates.TemplateResponse(
        name='files.html',
        context={
            'request': request,
            'user': user,
            'folder_structure': get_folder_structure('root', get_drive_service(user))})


@router.post("/create_element")
def create_element(request: Request, formData: dict):
    """
    Route for creating a new file element.

    If the user is not authenticated, redirects to the home page.
    Otherwise, creates a new file element and redirects to the file listing page.

    Args:
        request (Request): The incoming request.
        formData (dict): Form data containing information about the new file element.

    Returns:
        RedirectResponse or TemplateResponse: Depending on the success of the file creation.
    """
    user = session.get('user')
    if not user:
        return RedirectResponse('/')

    new_file = create_new_element(user, formData['element_name'], formData['element_type'], formData['parent_id'])

    if not new_file:
        return templates.TemplateResponse(
            name='error.html',
            context={
                'request': request,
                'error': "Can not create new element!"})
    return RedirectResponse('/files')


@router.delete('/delete_file/{file_id}')
def delete_file(request: Request, file_id: str):
    """
    Route for deleting a file.

    If the user is not authenticated, redirects to the home page.
    Otherwise, deletes the specified file and redirects to the file listing page.

    Args:
        request (Request): The incoming request.
        file_id (str): The ID of the file to be deleted.

    Returns:
        RedirectResponse or TemplateResponse: Depending on the success of the file deletion.
    """
    user = session.get('user')

    if not user:
        return RedirectResponse('/')

    try:
        delete_element(user, file_id)
        return RedirectResponse('/files')

    except Exception:
        return templates.TemplateResponse(
            name='error.html',
            context={
                'request': request,
                'error': "Unable to delete file!"
            }
        )


@router.get('/logout')
def logout(request: Request):
    """
    Route for user logout.

    Clears the user session and redirects to the home page.

    Args:
        request (Request): The incoming request.

    Returns:
        RedirectResponse: Redirects to the home page.
    """
    request.session.pop('user')
    return RedirectResponse('/')
