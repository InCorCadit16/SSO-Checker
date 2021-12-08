from flask import Flask, render_template, redirect, request
import requests_oauthlib as oauth_req
import os
import requests_oauthlib.compliance_fixes as facebook_compliance_fix

app = Flask('SSO Checker')

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')

GOOGLE_AUTHORIZATION_URL = 'https://accounts.google.com/o/oauth2/auth'
GOOGLE_TOKEN_URL = 'https://accounts.google.com/o/oauth2/token'
GOOGLE_USER_INFO_URL = 'https://www.googleapis.com/oauth2/v3/userinfo'
GOOGLE_SCOPES = [
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile'
]


FACEBOOK_CLIENT_ID = os.environ.get('FACEBOOK_CLIENT_ID')
FACEBOOK_CLIENT_SECRET = os.environ.get('FACEBOOK_CLIENT_SECRET')

FACEBOOK_AUTHORIZATION_URL = 'https://www.facebook.com/dialog/oauth'
FACEBOOK_TOKEN_URL = 'https://graph.facebook.com/oauth/access_token'
FACEBOOK_SCOPES = [
    'email', 'public_profile'
]

@app.route('/')
def index():
    return render_template('login.html')


@app.route('/google-login')
def google_login():
    googlelogin = oauth_req.OAuth2Session(
        GOOGLE_CLIENT_ID, redirect_uri="http://localhost:5000/google-callback", scope=GOOGLE_SCOPES
    )

    auth_url = googlelogin.authorization_url(GOOGLE_AUTHORIZATION_URL)
    return redirect(auth_url[0])


@app.route('/google-callback')
def google_callback():
    googlelogin = oauth_req.OAuth2Session(GOOGLE_CLIENT_ID, redirect_uri="http://localhost:5000/google-callback")
    token = googlelogin.fetch_token(
        token_url=GOOGLE_TOKEN_URL, client_secret=GOOGLE_CLIENT_SECRET, authorization_response=request.url
    )

    googlelogin.token = token
    user_info = googlelogin.get(GOOGLE_USER_INFO_URL).json()
    return render_template("user-info.html", user_info=user_info, provider="Google")


@app.route('/fb-login')
def fb_login():
    facebook = oauth_req.OAuth2Session(
        FACEBOOK_CLIENT_ID, redirect_uri="http://localhost:5000/fb-callback", scope=FACEBOOK_SCOPES
    )
    authorization_url, _ = facebook.authorization_url(FACEBOOK_AUTHORIZATION_URL)

    return redirect(authorization_url)


@app.route('/fb-callback')
def fb_callback():
    facebook = oauth_req.OAuth2Session(
        FACEBOOK_CLIENT_ID, scope=FACEBOOK_SCOPES, redirect_uri="http://localhost:5000/fb-callback"
    )

    facebook.fetch_token(
        FACEBOOK_TOKEN_URL,
        client_secret=FACEBOOK_CLIENT_SECRET,
        authorization_response=request.full_path,
    )

    user_info = facebook.get(
        "https://graph.facebook.com/me?fields=id,name,email,picture{url}"
    ).json()

    return render_template("fb-user-info.html", user_info=user_info, provider="Facebook")


if __name__ == '__main__':
    app.run()

