import re
import time
from deep_translator import GoogleTranslator

def translate_menu(text):
    targets = {"en": "en", "es": "es", "de": "de", "it": "it", "ru": "ru"}
    results = {k: "" for k in targets}
    
    # Extraire les textes protégés [[...]]
    protected = {}
    counter = [0]
    
    def replace_protected(match):
        placeholder = f"__PROT{counter[0]}__"
        protected[placeholder] = match.group(1)
        counter[0] += 1
        return placeholder
    
    text_clean = re.sub(r'\[\[(.*?)\]\]', replace_protected, text)
    parts = re.split(r'(".*?")', text_clean)
    
    for lang, code in targets.items():
        trans_parts = []
        try:
            translator = GoogleTranslator(source='fr', target=code)
        except Exception:
            results[lang] = text
            continue
        
        for part in parts:
            if part.startswith('"') and part.endswith('"'):
                trans_parts.append(part)
            elif part.strip():
                try:
                    # Traduction avec gestion d'erreur
                    translated = translator.translate(part.strip())
                    for placeholder, original in protected.items():
                        translated = translated.replace(placeholder, original)
                    trans_parts.append(translated)
                except Exception:
                    # Si Google bloque ou timeout, on garde le texte original (fallback)
                    restored = part
                    for placeholder, original in protected.items():
                        restored = restored.replace(placeholder, original)
                    trans_parts.append(restored)
            else:
                trans_parts.append(part)
        
        result = "".join(trans_parts)
        for placeholder, original in protected.items():
            result = result.replace(placeholder, original)
        results[lang] = result
    
    return results
