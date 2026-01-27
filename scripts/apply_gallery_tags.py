#!/usr/bin/env python3
import csv
import re
from pathlib import Path

root = Path('/home/bergsving/Documents/GitHub/All-In-Bali-Website')
html_path = root / 'gallery.html'
csv_path = root / 'gallery-tags.csv'

if not csv_path.exists():
    raise SystemExit('gallery-tags.csv not found')

rows = []
with csv_path.open(newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    if 'filename' not in reader.fieldnames or 'tag' not in reader.fieldnames:
        raise SystemExit('CSV must have headers: filename, tag')
    for row in reader:
        filename = row['filename'].strip()
        tag = row['tag'].strip()
        if not filename:
            continue
        rows.append((filename, tag))

if not rows:
    raise SystemExit('No rows found in CSV')

missing_tags = [name for name, tag in rows if not tag]
if missing_tags:
    print('Missing tags for these files:')
    for name in missing_tags:
        print(f' - {name}')
    raise SystemExit('Please fill all tags before applying.')


def title_from_name(name: str) -> str:
    base = name.rsplit('.', 1)[0]
    words = base.replace('_', ' ').split()
    return ' '.join(w.capitalize() for w in words)

cards = []
for filename, tag in rows:
    title = title_from_name(filename)
    card = f"""
            <div class=\"gallery-card group\" data-category=\"{tag}\">
                <div class=\"relative overflow-hidden rounded-3xl\">
                    <img src=\"photos/{filename}\" class=\"w-full object-cover\" alt=\"{title}\" onclick=\"openLightbox(this.src)\" loading=\"lazy\">
                </div>
            </div>"""
    cards.append(card)

cards_html = "\n".join(cards) + "\n"

html = html_path.read_text(encoding='utf-8')
pattern = re.compile(r'(<div class="max-w-7xl mx-auto masonry-grid" id="masonryGrid">)([\s\S]*?)(\n\s*</div>\n\s*</main>)')
match = pattern.search(html)
if not match:
    raise SystemExit('Could not find masonryGrid container in gallery.html')

new_block = match.group(1) + "\n" + cards_html + match.group(3)
html = html[:match.start()] + new_block + html[match.end():]

html_path.write_text(html, encoding='utf-8')
print(f'Updated gallery.html with {len(rows)} tagged photos')
