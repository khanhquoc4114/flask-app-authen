from flask import Flask, render_template, url_for, session, redirect, request, jsonify
from authlib.integrations.flask_client import OAuth
import os
from functools import wraps
from dotenv import load_dotenv
from models import db, User

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = (
    f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}"
    f"@{os.getenv('POSTGRES_HOST')}/{os.getenv('POSTGRES_DB')}"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

oauth = OAuth(app)

github = oauth.register(
    name='github',
    client_id=os.getenv('GITHUB_CLIENT_ID'),
    client_secret=os.getenv('GITHUB_CLIENT_SECRET'),
    authorize_url='https://github.com/login/oauth/authorize',
    access_token_url='https://github.com/login/oauth/access_token',
    userinfo_url='https://api.github.com/user',
    client_kwargs={
        'scope': 'user:email'
    }
)

google = oauth.register(
    name='google',
    client_id=os.getenv('GOOGLE_CLIENT_ID'),
    client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    access_token_url='https://oauth2.googleapis.com/token',
    userinfo_url='https://www.googleapis.com/oauth2/v2/userinfo',
    client_kwargs={
        'scope': 'openid email profile'
    },
    redirect_uri='http://localhost:5000/auth/google/callback',
    jwks_uri = "https://www.googleapis.com/oauth2/v3/certs"
)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login')
def login():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/auth/google')
def google_auth():
    # Cách 1: Sử dụng redirect_uri cố định
    # redirect_uri = 'http://localhost:5000/auth/google/callback'
    
    # Cách 2: Sử dụng url_for với _external=True và _scheme='http'
    redirect_uri = url_for('google_callback', _external=True, _scheme='http')
    
    return google.authorize_redirect(redirect_uri)

@app.route('/auth/google/callback')
def google_callback():
    try:
        # 1. Exchange authorization code for access token
        token = google.authorize_access_token()
        
        # 2. Call Google API to get user info
        resp = google.get('https://www.googleapis.com/oauth2/v2/userinfo')
        user_info = resp.json()

        print(f"[DEBUG] User info: {user_info}")

        # 3. Validate required fields
        if not user_info or 'id' not in user_info:
            print("[ERROR] No user info found or missing 'id'")
            return redirect(url_for('login'))

        # 4. Extract user information
        email = user_info.get("email", "")

        # 5. Store session
        session['user'] = {
            'id': user_info['id'],
            'name': user_info.get('name', ''),
            'email': email,
            'picture': user_info.get('picture', '')
        }

        return redirect(url_for('dashboard'))

    except Exception as e:
        print(f"[ERROR] Exception in Google callback: {e}")
        return redirect(url_for('login'))

@app.route('/auth/github')
def github_auth():
    # redirect_uri = 'http://localhost:5000/auth/github/callback'
    
    # Cách 2: Sử dụng url_for với _external=True và _scheme='http'
    redirect_uri = url_for('github_callback', _external=True, _scheme='http')
    
    return github.authorize_redirect(redirect_uri)

@app.route('/auth/github/callback')
def github_callback():
    try:
        print("GitHub callback được gọi")
        
        token = github.authorize_access_token()
        print(f"GitHub Token: {token}")
        
        resp = github.get('https://api.github.com/user')
        user_info = resp.json()
        print(f"GitHub User info: {user_info}")
        
        email = user_info.get('https://api.github.com/user/emails')
        if not email:
            email_resp = github.get('https://api.github.com/user/emails')
            emails = email_resp.json()
            for email_obj in emails:
                if email_obj.get('primary'):
                    email = email_obj.get('email')
                    break
        
        if user_info and 'id' in user_info:
            session['user'] = {
                'id': str(user_info['id']),
                'name': user_info.get('name') or user_info.get('login', ''),
                'email': email or '',
                'picture': user_info.get('avatar_url', ''),
                'provider': 'github',
                'username': user_info.get('login', '')
            }
            return redirect(url_for('dashboard'))
        else:
            print("No GitHub user info found")
            return redirect(url_for('login'))
            
    except Exception as e:
        print(f"Error in GitHub callback: {e}")
        import traceback
        traceback.print_exc()
        return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', user=session['user'])

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

@app.route('/api/user')
@login_required
def get_user():
    return jsonify(session['user'])

@app.cli.command("init-db")
def init_db():
    db.create_all()
    print("Initialized the database.")

if __name__ == '__main__':
    app.run(debug=True)