import os
import re
import time
import urllib.request
import urllib.error

# We will parse the LIBRARY_DATA from the seed file
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'libria.settings')
import django
django.setup()

from library.management.commands.seed_library import LIBRARY_DATA

# Create media directory
MEDIA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'media', 'textbooks')
os.makedirs(MEDIA_DIR, exist_ok=True)

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

def get_html(url):
    req = urllib.request.Request(url, headers={'User-Agent': USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            return response.read().decode('utf-8')
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return ""

def download_file(url, filepath):
    req = urllib.request.Request(url, headers={'User-Agent': USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=120) as response, open(filepath, 'wb') as out_file:
            data = response.read()
            out_file.write(data)
            return True
    except Exception as e:
        print(f"Error downloading {url}: {e}")
        if os.path.exists(filepath):
            os.remove(filepath)
        return False

print("Starting textbook downloads...")
for grade, grade_data in LIBRARY_DATA.items():
    for subject in grade_data['subjects']:
        for book in subject['books']:
            url = book['kehulum']
            title = book['title']
            filename = f"grade_{grade}_{subject['name'].lower().replace(' ', '_')}_{'new' if 'New' in title else 'old'}.pdf"
            filepath = os.path.join(MEDIA_DIR, filename)
            
            if os.path.exists(filepath):
                print(f"[{grade}] {subject['name']} already exists, skipping.")
                continue
                
            print(f"[{grade}] Fetching page for {subject['name']}...")
            html = get_html(url)
            
            # Find PDF link
            match = re.search(r'href="([^"]+\.pdf)"', html)
            if match:
                pdf_url = match.group(1)
                import urllib.parse
                parsed = urllib.parse.urlparse(pdf_url)
                pdf_url = urllib.parse.urlunparse((parsed.scheme, parsed.netloc, urllib.parse.quote(parsed.path), parsed.params, parsed.query, parsed.fragment))
                print(f"  Found PDF: {pdf_url.split('/')[-1]}")
                print(f"  Downloading (this may take a minute)...")
                if download_file(pdf_url, filepath):
                    print(f"  [OK] Saved to {filename}")
                time.sleep(1) # Be nice to the server
            else:
                print(f"  [ERROR] No PDF link found on {url}")

print("Done downloading textbooks.")
