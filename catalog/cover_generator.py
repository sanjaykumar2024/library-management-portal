"""
Publisher-Grade Book Cover Generator for LibrarySphere.
Synthesizes high-resolution (600x900), luxury hardcover book cover artwork
featuring authentic physical book anatomy (spine crease, cloth/leather spotlight,
embossed gold/silver foil framing, ornamental heraldic crests, and serif typography).
"""

import math
import io
import uuid
from PIL import Image, ImageDraw, ImageFont
from django.core.files.base import ContentFile


class BookCoverGenerator:
    """Generates publisher-grade 600x900 hardcover book covers with category-tailored themes."""

    WIDTH = 600
    HEIGHT = 900

    THEMES = {
        'literature': {
            'bg_top': (74, 14, 26),      # Deep Vintage Oxblood / Burgundy
            'bg_bot': (26, 4, 9),
            'foil': (228, 192, 108),     # Radiant Antique Gold
            'foil_dim': (160, 130, 70),
            'text': (255, 252, 245),
            'sub': (225, 200, 150),
        },
        'tech': {
            'bg_top': (11, 28, 54),      # Midnight Scholar Sapphire
            'bg_bot': (4, 10, 20),
            'foil': (224, 196, 128),     # Gilded Gold with Azure Subtext
            'foil_dim': (60, 150, 200),
            'text': (248, 252, 255),
            'sub': (180, 220, 245),
        },
        'science': {
            'bg_top': (10, 48, 34),      # British Racing Green / Deep Pine
            'bg_bot': (3, 18, 12),
            'foil': (232, 205, 125),     # Champagne Gold
            'foil_dim': (155, 135, 75),
            'text': (255, 252, 240),
            'sub': (215, 200, 145),
        },
        'philosophy': {
            'bg_top': (38, 18, 62),      # Imperial Byzantine Plum
            'bg_bot': (14, 6, 25),
            'foil': (230, 198, 120),     # Roman Gold
            'foil_dim': (160, 130, 80),
            'text': (255, 250, 245),
            'sub': (225, 200, 150),
        },
        'history': {
            'bg_top': (62, 32, 14),      # Antique Tuscan Leather
            'bg_bot': (24, 10, 4),
            'foil': (232, 180, 90),      # Burnished Bronze
            'foil_dim': (165, 120, 60),
            'text': (255, 250, 240),
            'sub': (225, 190, 130),
        },
        'business': {
            'bg_top': (18, 26, 42),      # Regimental Oxford Navy
            'bg_bot': (7, 11, 18),
            'foil': (235, 190, 95),      # Gilded Amber
            'foil_dim': (150, 125, 70),
            'text': (255, 252, 245),
            'sub': (220, 195, 140),
        },
        'scifi': {
            'bg_top': (20, 14, 46),      # Deep Astral Violet
            'bg_bot': (6, 4, 16),
            'foil': (210, 175, 245),     # Starlight Orchid & Platinum
            'foil_dim': (130, 95, 170),
            'text': (250, 248, 255),
            'sub': (195, 175, 230),
        },
    }

    @classmethod
    def detect_genre(cls, title: str, category_name: str) -> str:
        """Classifies book into a visual design genre based on category and title keywords."""
        text = f"{title} {category_name}".lower()

        if any(k in text for k in ['computer', 'software', 'programming', 'python', 'java', 'code', 'data',
                                  'algorithm', 'machine learning', 'network', 'microservice', 'engineering',
                                  'developer', 'operating system', 'design patterns', 'agile']):
            return 'tech'
        if any(k in text for k in ['physics', 'cosmos', 'math', 'quantum', 'space', 'biology', 'chemistry',
                                  'astronomy', 'nature', 'spring', 'earth', 'universe', 'relativity']):
            return 'science'
        if any(k in text for k in ['philosophy', 'meditations', 'psychology', 'thinking', 'mind', 'ethics',
                                  'republic', 'justice', 'plato', 'marcus', 'nietzsche', 'habit', 'grit',
                                  'meaning', 'flow']):
            return 'philosophy'
        if any(k in text for k in ['history', 'sapiens', 'war', 'antiquity', 'empire', 'silk roads',
                                  'revolution', 'century', 'civilization', 'lessons of history']):
            return 'history'
        if any(k in text for k in ['business', 'money', 'economics', 'startup', 'lean', 'principles',
                                  'invest', 'capital', 'finance', 'zero to one', 'management']):
            return 'business'
        if any(k in text for k in ['dune', 'scifi', 'sci-fi', 'space odyssey', 'solaris', 'robot',
                                  'android', 'galaxy', 'hitchhiker', 'three-body', 'foundation', 'neuromancer']):
            return 'scifi'

        return 'literature'

    @classmethod
    def _get_font(cls, name_or_path: str, size: int):
        """Loads TTF font with fallback to system fonts or default."""
        system_candidates = [
            name_or_path,
            f"/System/Library/Fonts/Supplemental/{name_or_path}",
            f"/System/Library/Fonts/{name_or_path}",
            "/System/Library/Fonts/Supplemental/Georgia Bold.ttf",
            "/System/Library/Fonts/Supplemental/Georgia.ttf",
            "/System/Library/Fonts/Supplemental/Times New Roman.ttf",
            "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        ]
        for path in system_candidates:
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
        return ImageFont.load_default()

    @classmethod
    def _draw_diamond(cls, draw, cx, cy, size, fill, outline=None):
        pts = [(cx, cy - size), (cx + size, cy), (cx, cy + size), (cx - size, cy)]
        draw.polygon(pts, fill=fill, outline=outline)

    @classmethod
    def _draw_crest(cls, draw, cx, cy, t, genre='literature'):
        """Renders an intricate gilded medallion with laurel leaves and genre insignia."""
        # Outer double circle
        draw.ellipse([cx - 55, cy - 55, cx + 55, cy + 55], outline=t['foil'], width=2)
        draw.ellipse([cx - 48, cy - 48, cx + 48, cy + 48], outline=t['foil_dim'], width=1)

        # Decorative perimeter beads
        for i in range(12):
            angle = i * math.pi / 6
            bx = cx + 51.5 * math.cos(angle)
            by = cy + 51.5 * math.sin(angle)
            draw.ellipse([bx - 1.5, by - 1.5, bx + 1.5, by + 1.5], fill=t['foil'])

        # Laurel leaves
        for side in (-1, 1):
            for step in range(5):
                la = -math.pi / 2 + (step + 1) * 0.32
                lx = cx + side * (38 * math.cos(la))
                ly = cy + 38 * math.sin(la)
                draw.polygon([
                    (lx, ly),
                    (lx + side * 6, ly - 4),
                    (lx + side * 10, ly),
                    (lx + side * 5, ly + 3)
                ], fill=t['foil'])

        # Genre Center Emblem
        if genre == 'tech':
            # Isometric data cube
            draw.polygon([(cx, cy - 18), (cx + 16, cy - 8), (cx, cy + 2), (cx - 16, cy - 8)], outline=t['foil'], width=2)
            draw.polygon([(cx - 16, cy - 8), (cx, cy + 2), (cx, cy + 20), (cx - 16, cy + 10)], outline=t['foil'], width=2)
            draw.polygon([(cx + 16, cy - 8), (cx, cy + 2), (cx, cy + 20), (cx + 16, cy + 10)], outline=t['foil'], width=2)
            draw.ellipse([cx - 3, cy - 9, cx + 3, cy - 3], fill=t['foil'])
        elif genre == 'science':
            # Atomic planetary orbits
            draw.ellipse([cx - 20, cy - 8, cx + 20, cy + 8], outline=t['foil'], width=2)
            draw.ellipse([cx - 8, cy - 20, cx + 8, cy + 20], outline=t['foil'], width=2)
            draw.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=t['foil'])
        elif genre == 'philosophy':
            # Classical pediment & pillars
            draw.polygon([(cx, cy - 16), (cx - 20, cy - 6), (cx + 20, cy - 6)], outline=t['foil'], width=2, fill=t['foil_dim'])
            draw.line([(cx - 20, cy - 4), (cx + 20, cy - 4)], fill=t['foil'], width=2)
            for px in (-14, -5, 5, 14):
                draw.line([(cx + px, cy - 2), (cx + px, cy + 14)], fill=t['foil'], width=2)
            draw.rectangle([cx - 22, cy + 14, cx + 22, cy + 18], fill=t['foil'])
        elif genre == 'scifi':
            # Starlight compass rose
            for i in range(8):
                angle = i * math.pi / 4 - math.pi / 2
                r = 20 if i % 2 == 0 else 8
                pts = [(cx, cy),
                       (cx + r * math.cos(angle - 0.2), cy + r * math.sin(angle - 0.2)),
                       (cx + r * 1.3 * math.cos(angle), cy + r * 1.3 * math.sin(angle)),
                       (cx + r * math.cos(angle + 0.2), cy + r * math.sin(angle + 0.2))]
                draw.polygon(pts, fill=t['foil'])
        else:
            # Radiant open book of knowledge
            for ra in (-0.5, -0.25, 0, 0.25, 0.5):
                rx1 = cx + 18 * math.sin(ra)
                ry1 = cy - 14 - 18 * math.cos(ra)
                rx2 = cx + 25 * math.sin(ra)
                ry2 = cy - 14 - 25 * math.cos(ra)
                draw.line([(rx1, ry1), (rx2, ry2)], fill=t['foil'], width=1)
            draw.polygon([(cx, cy - 8), (cx - 22, cy + 4), (cx - 22, cy + 18), (cx, cy + 10)], outline=t['foil'], width=2)
            draw.polygon([(cx, cy - 8), (cx + 22, cy + 4), (cx + 22, cy + 18), (cx, cy + 10)], outline=t['foil'], width=2)
            draw.line([(cx, cy - 8), (cx, cy + 10)], fill=t['foil'], width=2)

    @classmethod
    def generate_cover(cls, title: str, author: str = "", category: str = "", isbn: str = "") -> ContentFile:
        """
        Synthesizes a 600x900 publisher-grade hardcover book cover.
        Returns a Django ContentFile with PNG bytes.
        """
        W, H = cls.WIDTH, cls.HEIGHT
        genre = cls.detect_genre(title, category)
        t = cls.THEMES.get(genre, cls.THEMES['literature'])

        # 1. Background gradient with soft library overhead spotlight
        img = Image.new('RGB', (W, H), t['bg_bot'])
        spot_cx, spot_cy = W / 2, H * 0.35

        for y in range(H):
            ratio_y = y / H
            for x in range(0, W, 2):
                dist = math.hypot(x - spot_cx, (y - spot_cy) * 1.2) / (W * 0.75)
                spot = max(0.0, 1.0 - dist) * 0.22

                r = int(t['bg_top'][0] * (1 - ratio_y) + t['bg_bot'][0] * ratio_y)
                g = int(t['bg_top'][1] * (1 - ratio_y) + t['bg_bot'][1] * ratio_y)
                b = int(t['bg_top'][2] * (1 - ratio_y) + t['bg_bot'][2] * ratio_y)

                r = min(255, int(r + (255 - r) * spot))
                g = min(255, int(g + (255 - g) * spot * 0.8))
                b = min(255, int(b + (255 - b) * spot * 0.6))

                img.putpixel((x, y), (r, g, b))
                if x + 1 < W:
                    img.putpixel((x + 1, y), (r, g, b))

        # 2. Hardcover physical anatomy: 3D Spine hinge on the left
        for x in range(32):
            if x < 10:
                alpha = (10 - x) / 10.0 * 0.50
                col = (0, 0, 0)
            elif x < 15:
                alpha = (1.0 - abs(x - 12.5) / 2.5) * 0.28
                col = (255, 255, 255)
            else:
                alpha = (32 - x) / 17.0 * 0.25
                col = (0, 0, 0)

            for y in range(H):
                curr = img.getpixel((x, y))
                new_r = int(curr[0] * (1 - alpha) + col[0] * alpha)
                new_g = int(curr[1] * (1 - alpha) + col[1] * alpha)
                new_b = int(curr[2] * (1 - alpha) + col[2] * alpha)
                img.putpixel((x, y), (new_r, new_g, new_b))

        # Right edge hardcover board bevel highlight
        for y in range(H):
            curr = img.getpixel((W - 2, y))
            img.putpixel((W - 2, y), (min(255, curr[0] + 35), min(255, curr[1] + 35), min(255, curr[2] + 35)))

        draw = ImageDraw.Draw(img)
        margin = 38

        # 3. Outer & Inner embossed foil frame
        draw.rectangle([margin, margin, W - margin, H - margin], outline=t['foil'], width=2)
        draw.rectangle([margin + 6, margin + 6, W - margin - 6, H - margin - 6], outline=t['foil_dim'], width=1)

        # Ornate corner florets
        for cx, cy, dx, dy in [(margin, margin, 1, 1),
                              (W - margin, margin, -1, 1),
                              (margin, H - margin, 1, -1),
                              (W - margin, H - margin, -1, -1)]:
            draw.line([(cx + dx * 16, cy), (cx + dx * 16, cy + dy * 16)], fill=t['foil'], width=2)
            draw.line([(cx, cy + dy * 16), (cx + dx * 16, cy + dy * 16)], fill=t['foil'], width=2)
            cls._draw_diamond(draw, cx + dx * 8, cy + dy * 8, 4, fill=t['foil'])

        # Fonts
        font_cat = cls._get_font("Georgia Bold.ttf", 12)
        font_by = cls._get_font("Georgia Bold.ttf", 11)
        font_author = cls._get_font("Georgia.ttf", 19)
        font_imprint = cls._get_font("Georgia Bold.ttf", 11)

        # 4. Top Category Cartouche / Series Header
        display_category = (category or genre).upper()
        if len(display_category) > 28:
            display_category = display_category[:26] + "..."

        c_box = draw.textbbox((0, 0), display_category, font=font_cat)
        c_w = c_box[2] - c_box[0]

        badge_w = min(W - margin * 2 - 40, c_w + 50)
        badge_x1 = (W - badge_w) // 2
        badge_y1 = margin + 24
        badge_x2 = badge_x1 + badge_w

        draw.line([(badge_x1 - 30, badge_y1 + 12), (badge_x1, badge_y1 + 12)], fill=t['foil_dim'], width=1)
        cls._draw_diamond(draw, badge_x1 - 15, badge_y1 + 12, 3, fill=t['foil'])
        draw.line([(badge_x2, badge_y1 + 12), (badge_x2 + 30, badge_y1 + 12)], fill=t['foil_dim'], width=1)
        cls._draw_diamond(draw, badge_x2 + 15, badge_y1 + 12, 3, fill=t['foil'])

        draw.text(((W - c_w) // 2, badge_y1 + 5), display_category, font=font_cat, fill=t['sub'])

        # 5. Book Title Layout
        words = title.split()
        lines = []
        curr = []
        max_line_len = 16 if len(title) > 30 else 20
        for w in words:
            curr.append(w)
            if len(' '.join(curr)) > max_line_len:
                lines.append(' '.join(curr[:-1]))
                curr = [w]
        if curr:
            lines.append(' '.join(curr))

        # Adaptive typography scale
        if len(lines) <= 2:
            font_size = 40
        elif len(lines) == 3:
            font_size = 33
        elif len(lines) == 4:
            font_size = 28
        else:
            font_size = 24
            lines = lines[:5]

        font_title = cls._get_font("Georgia Bold.ttf", font_size)

        total_title_h = len(lines) * (font_size + 12)
        start_y = 195 + (150 - total_title_h) // 2
        for line in lines:
            l_box = draw.textbbox((0, 0), line, font=font_title)
            l_w = l_box[2] - l_box[0]
            # Deep letterpress deboss drop shadow
            draw.text(((W - l_w) // 2 + 1, start_y + 2), line, font=font_title, fill=(5, 5, 5))
            draw.text(((W - l_w) // 2, start_y), line, font=font_title, fill=t['text'])
            start_y += font_size + 12

        # 6. Gilded Filigree Divider with Vector Diamonds
        div_y = start_y + 24
        draw.line([(W // 2 - 95, div_y), (W // 2 - 25, div_y)], fill=t['foil_dim'], width=1)
        draw.line([(W // 2 + 25, div_y), (W // 2 + 95, div_y)], fill=t['foil_dim'], width=1)
        cls._draw_diamond(draw, W // 2, div_y, 6, fill=t['foil'])
        cls._draw_diamond(draw, W // 2 - 24, div_y, 3, fill=t['foil_dim'])
        cls._draw_diamond(draw, W // 2 + 24, div_y, 3, fill=t['foil_dim'])

        # 7. Author Display
        if author:
            by_text = 'BY'
            b_box = draw.textbbox((0, 0), by_text, font=font_by)
            b_w = b_box[2] - b_box[0]
            draw.text(((W - b_w) // 2, div_y + 22), by_text, font=font_by, fill=t['foil_dim'])

            clean_author = author.upper()
            if len(clean_author) > 36:
                clean_author = clean_author[:33] + "..."
            a_box = draw.textbbox((0, 0), clean_author, font=font_author)
            a_w = a_box[2] - a_box[0]
            draw.text(((W - a_w) // 2, div_y + 40), clean_author, font=font_author, fill=t['foil'])
        else:
            default_author = 'LIBRARYSPHERE EDITION'
            a_box = draw.textbbox((0, 0), default_author, font=font_author)
            a_w = a_box[2] - a_box[0]
            draw.text(((W - a_w) // 2, div_y + 30), default_author, font=font_author, fill=t['foil'])

        # 8. Heraldic Central Medallion Seal
        seal_y = 600
        cls._draw_crest(draw, W // 2, seal_y, t, genre=genre)

        # 9. Bottom Imprint & Lower Accent
        imp_y = H - margin - 35
        draw.line([(margin + 50, imp_y - 12), (W - margin - 50, imp_y - 12)], fill=t['foil_dim'], width=1)
        cls._draw_diamond(draw, W // 2, imp_y - 12, 3, fill=t['foil'])

        imprint_text = 'LIBRARYSPHERE HERITAGE COLLECTION'
        i_box = draw.textbbox((0, 0), imprint_text, font=font_imprint)
        i_w = i_box[2] - i_box[0]
        draw.text(((W - i_w) // 2, imp_y), imprint_text, font=font_imprint, fill=t['sub'])

        buffer = io.BytesIO()
        img.save(buffer, format='PNG', quality=95)
        file_name = f"{isbn or uuid.uuid4().hex}.png"
        return ContentFile(buffer.getvalue(), name=file_name)
