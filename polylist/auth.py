from fasthtml.common import *
from fasthtml.oauth import GitHubAppClient
import os

# Set up the GitHub OAuth client
client = GitHubAppClient(
    os.getenv("AUTH_CLIENT_ID"),
    os.getenv("AUTH_CLIENT_SECRET"),
    redirect_uri="http://localhost:8000/auth_redirect"
)

app, rtr = fast_app()

@app.get('/login')
def login():
    login_link = client.login_link_with_state(state='current_prompt: add a unicorn')
    return Div(
        H1("Login"),
        P("Please log in to continue."),
        A('Login with GitHub', href=login_link)
    )

@app.get('/auth_redirect')
def auth_redirect(code: str, session, state: str = None):
    print(f"state: {state}")  # Use as needed
    token = client.exchange_code_for_token(code)
    user_info = client.get_user_info(token)
    user_id = user_info['id']
    session['user_id'] = user_id
    return RedirectResponse('/', status_code=303)

# Beforeware for authentication
def before(req, session):
    auth = req.scope['auth'] = session.get('user_id', None)
    if not auth:
        return RedirectResponse('/login', status_code=303)
    # You can add user-specific logic here, like updating user counts
    
bware = Beforeware(before, skip=['/login', '/auth_redirect'])

# Apply the Beforeware to the app
app.before = bware

@app.get('/')
def home(auth):
    return Div(
        H1("Welcome"),
        P(f"You are logged in with user ID: {auth}"),
        A("Logout", href="/logout")
    )

@app.get('/logout')
def logout(session):
    session.clear()
    return RedirectResponse('/login', status_code=303)

if __name__ == "__main__":
    serve(app)
