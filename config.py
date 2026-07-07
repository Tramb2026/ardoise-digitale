import os

BASE = os.path.dirname(os.path.abspath(__file__))

TOKEN_FILE = os.path.join(BASE, 'data', 'github_token.txt')
GITHUB_USER = 'tramb2026'
GITHUB_REPO = 'ardoise-digitale'
GITHUB_BRANCH = 'main'

QR_URL = f'https://{GITHUB_USER}.github.io/{GITHUB_REPO}/menu_public.html'
GITHUB_API = f'https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/contents'
