import requests
import base64

def upload_to_github(token, content, target_path="menu_public.html"):
    try:
        repo = "tramb2026/ardoise-digitale"
        path = target_path
        url = f"https://api.github.com/repos/{repo}/contents/{path}"
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }

        # 1. Récupérer le SHA actuel (Timeout 10s)
        r = requests.get(url, headers=headers, timeout=10)
        sha = None
        if r.status_code == 200:
            sha = r.json().get("sha")
        elif r.status_code != 404:
            return False, f"Erreur lecture GitHub (Code {r.status_code}). Vérifiez votre connexion."

        # 2. Uploader avec le SHA (Timeout 15s)
        content_b64 = base64.b64encode(content.encode("utf-8")).decode("utf-8")
        data = {"message": "Update menu via ArdoiseDigitale", "content": content_b64}
        if sha:
            data["sha"] = sha

        r = requests.put(url, json=data, headers=headers, timeout=15)
        if r.status_code in [200, 201]:
            return True, f"https://tramb2026.github.io/ardoise-digitale/{path}"
        elif r.status_code == 401:
            return False, "Token GitHub invalide ou expiré."
        elif r.status_code == 403:
            return False, "Quota GitHub dépassé ou Token sans droits d'écriture."
        else:
            return False, f"Erreur upload GitHub (Code {r.status_code})."
    except requests.exceptions.Timeout:
        return False, "Délai d'attente dépassé. Vérifiez votre connexion internet."
    except requests.exceptions.ConnectionError:
        return False, "Aucune connexion internet détectée."
    except Exception as e:
        return False, f"Erreur inattendue : {str(e)}"
