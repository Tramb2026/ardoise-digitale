import qrcode
from PIL import Image, ImageDraw, ImageFont
import io
import base64

def draw_restaurant_icon(size=50):
    """Dessine une icône assiette + couverts (fourchette et couteau)"""
    icon = Image.new('RGBA', (size, size), (255, 255, 255, 0))
    draw = ImageDraw.Draw(icon)
    
    margin = 5
    draw.ellipse([margin, margin, size-margin, size-margin], outline='#10b981', width=3)
    
    fork_x = size // 2 - 8
    fork_top = margin + 5
    fork_bottom = size - margin - 5
    draw.line([(fork_x, fork_top + 10), (fork_x, fork_bottom)], fill='#10b981', width=2)
    for dx in [-3, 0, 3]:
        draw.line([(fork_x + dx, fork_top), (fork_x + dx, fork_top + 12)], fill='#10b981', width=2)
    
    knife_x = size // 2 + 8
    draw.line([(knife_x, fork_top + 15), (knife_x, fork_bottom)], fill='#10b981', width=2)
    draw.polygon([(knife_x - 3, fork_top), (knife_x + 3, fork_top), (knife_x, fork_top + 15)], fill='#10b981')
    
    return icon

def generate_qr_base64(url):
    # QR code carré avec correction d'erreur élevée
    qr = qrcode.QRCode(box_size=10, border=4, error_correction=qrcode.constants.ERROR_CORRECT_H)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white").convert('RGB')

    # QR code CARRÉ : 10cm x 10cm = 400 x 400 pixels
    qr_size = 400
    img = img.resize((qr_size, qr_size), Image.Resampling.LANCZOS)

    # Dimensions totales : largeur = QR + marges, hauteur = textes haut + QR + textes bas + contact
    WIDTH = 500
    HEIGHT = 580
    bg = Image.new('RGB', (WIDTH, HEIGHT), 'white')
    draw = ImageDraw.Draw(bg)

    # Polices
    try:
        font_menu = ImageFont.truetype("arial.ttf", 24)
        font_contact = ImageFont.truetype("arial.ttf", 14)
    except:
        font_menu = ImageFont.load_default()
        font_contact = ImageFont.load_default()

    # 4 langues SANS article, en NOIR
    menu_names_top = ['Menu', 'Menú']               # FR, EN
    menu_names_bottom = ['Speisekarte', 'Меню']     # DE, RU

    # --- TEXTES EN HAUT (2 mots centrés, collés au QR) ---
    top_y = 20
    top_spacing = WIDTH // 3
    for i, name in enumerate(menu_names_top):
        x = top_spacing * (i + 1)
        bbox = draw.textbbox((0, 0), name, font=font_menu)
        text_width = bbox[2] - bbox[0]
        draw.text((x - text_width // 2, top_y), name, fill='#000000', font=font_menu)

    # --- QR CODE CARRÉ (centré horizontalement) ---
    qr_x = (WIDTH - qr_size) // 2
    qr_y = 55
    bg.paste(img, (qr_x, qr_y))

    # --- LOGO AU CENTRE DU QR ---
    icon_size = 50
    icon = draw_restaurant_icon(icon_size)
    icon_x = qr_x + (qr_size - icon_size) // 2
    icon_y = qr_y + (qr_size - icon_size) // 2
    draw.rectangle([icon_x - 5, icon_y - 5, icon_x + icon_size + 5, icon_y + icon_size + 5], fill='white')
    bg.paste(icon, (icon_x, icon_y), icon)

    # --- TEXTES EN BAS (2 mots centrés, collés au QR) ---
    bottom_y = qr_y + qr_size + 10
    bottom_spacing = WIDTH // 3
    for i, name in enumerate(menu_names_bottom):
        x = bottom_spacing * (i + 1)
        bbox = draw.textbbox((0, 0), name, font=font_menu)
        text_width = bbox[2] - bbox[0]
        draw.text((x - text_width // 2, bottom_y), name, fill='#000000', font=font_menu)

    # --- CONTACT (tout en bas, bien séparé) ---
    contact_text = "contact@updatedman.com"
    contact_bbox = draw.textbbox((0, 0), contact_text, font=font_contact)
    contact_width = contact_bbox[2] - contact_bbox[0]
    draw.text(((WIDTH - contact_width) // 2, HEIGHT - 30), contact_text, fill='#6b7280', font=font_contact)

    # Convertir en base64
    buffered = io.BytesIO()
    bg.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8')