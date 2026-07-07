import os
import re
import sys
import json
import webbrowser
import threading
import time
import tkinter as tk
from tkinter import messagebox
from flask import Flask, render_template, request, jsonify

# Détermination du dossier de base
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
    if os.path.exists(os.path.join(BASE_DIR, '_internal')):
        BASE_DIR = os.path.join(BASE_DIR, '_internal')
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_DIR = os.path.join(BASE_DIR, 'data')
if DATA_DIR not in sys.path:
    sys.path.insert(0, DATA_DIR)

app = Flask(__name__,
    template_folder=os.path.join(BASE_DIR, 'templates'),
    static_folder=os.path.join(BASE_DIR, 'static'),
    static_url_path='/static')

@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    return response

def get_token():
    path = os.path.join(DATA_DIR, 'github_token.txt')
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return f.read().strip()
    return None

def get_restaurant_config_path():
    return os.path.join(DATA_DIR, 'restaurant_config.json')

def get_restaurant_name():
    config_file = get_restaurant_config_path()
    if os.path.exists(config_file):
        with open(config_file, 'r', encoding='utf-8') as f:
            return json.load(f).get('restaurant_name', '')
    return ''

def get_restaurant_slug():
    config_file = get_restaurant_config_path()
    if os.path.exists(config_file):
        with open(config_file, 'r', encoding='utf-8') as f:
            name = json.load(f).get('restaurant_name', 'menu')
    else:
        name = 'menu'

    slug = name.lower()
    slug = slug.replace('é', 'e').replace('è', 'e').replace('ê', 'e').replace('ë', 'e')
    slug = slug.replace('à', 'a').replace('â', 'a').replace('ä', 'a')
    slug = slug.replace('ù', 'u').replace('û', 'u').replace('ü', 'u')
    slug = slug.replace('ô', 'o').replace('ö', 'o')
    slug = slug.replace('î', 'i').replace('ï', 'i')
    slug = slug.replace('ç', 'c').replace('œ', 'oe')
    slug = re.sub(r'[^a-z0-9]+', '-', slug).strip('-')
    return slug if slug else 'menu'

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('saisie.html', restaurant_name=get_restaurant_name())

@app.route('/api/process', methods=['POST'])
def process_menu():
    try:
        data = request.json
        menu_fr = data.get('menu', {})
        
        from core.translator import translate_menu
        from core.github_uploader import upload_to_github
        from core.html_generator import generate_html
        from core.qr_generator import generate_qr_base64

        translations = {}
        item_id_counter = 0
        
        for section, items in menu_fr.items():
            for item in items:
                text = item.get('nom', '')
                if text.strip():
                    item_id = 'item_' + str(item_id_counter)
                    item['id'] = item_id
                    tr = translate_menu(text)
                    translations[item_id] = tr
                    item_id_counter += 1

        html_content = generate_html(menu_fr, translations)
        
        token = get_token()
        slug = get_restaurant_slug()
        target_path = slug + '.html'
        
        ok, url_or_err = upload_to_github(token, html_content, target_path=target_path)
        
        if ok:
            github_url = 'https://tramb2026.github.io/ardoise-digitale/' + target_path + '?v=' + str(int(time.time()))
        else:
            github_url = url_or_err

        qr_b64 = generate_qr_base64(github_url)
        
        return jsonify({
            'success': True,
            'qr_code': qr_b64,
            'github_url': github_url
        })
    except Exception as e:
        import traceback
        print('ERREUR:', traceback.format_exc())
        return jsonify({'success': False, 'error': str(e)}), 500

def open_browser():
    time.sleep(1.5)
    webbrowser.open('http://127.0.0.1:5001')

# --- EXTINCTION AUTOMATIQUE APRÈS 30 MIN D'INACTIVITÉ ---
last_request_time = time.time()
TIMEOUT_SECONDS = 1800

@app.before_request
def update_activity():
    global last_request_time
    last_request_time = time.time()

def auto_shutdown_monitor():
    while True:
        time.sleep(60)
        if time.time() - last_request_time > TIMEOUT_SECONDS:
            print('Inactivité détectée (30 min). Arrêt automatique du serveur...')
            os._exit(0)

def ensure_restaurant_config():
    config_dir = DATA_DIR
    os.makedirs(config_dir, exist_ok=True)
    config_file = os.path.join(config_dir, 'restaurant_config.json')

    if not os.path.exists(config_file):
        root = tk.Tk()
        root.title("Configuration Initiale")
        root.geometry("300x150")
        root.attributes('-topmost', True)

        tk.Label(root, text="Nom du restaurant :").pack(pady=10)
        entry = tk.Entry(root, width=30)
        entry.pack(pady=5)
        entry.focus()

        def save_config():
            name = entry.get().strip()
            if not name:
                messagebox.showwarning("Attention", "Le nom est obligatoire.")
                return

            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump({"restaurant_name": name}, f, ensure_ascii=False, indent=2)

            root.destroy()

        tk.Button(root, text="Valider", command=save_config).pack(pady=10)
        root.protocol("WM_DELETE_WINDOW", lambda: None)
        root.mainloop()

@app.route('/api/restaurant_name')
def get_restaurant_name_api():
    config_file = get_restaurant_config_path()
    if os.path.exists(config_file):
        with open(config_file, 'r', encoding='utf-8') as f:
            return jsonify(json.load(f))
    return jsonify({'restaurant_name': ''})

if __name__ == '__main__':
    ensure_restaurant_config()
    threading.Thread(target=open_browser, daemon=True).start()
    threading.Thread(target=auto_shutdown_monitor, daemon=True).start()
    app.run(host='127.0.0.1', port=5001, debug=False)