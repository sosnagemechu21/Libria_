"""
download_and_organize_books.py

Automated script to download Ethiopian New Curriculum student textbooks from Kehulum.com,
filter excluded subjects (Amharic, HPE/Sports, PVA), and organize Grade 11 & 12 into
Natural Science and Social Science streams.
"""

import os
import re
import sys
import time
import shutil
import argparse
import urllib.request
import urllib.parse
from bs4 import BeautifulSoup

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

# Subjects to exclude
EXCLUDED_SUBJECTS = {
    'amharic',
    'health-and-physical-education-hpe',
    'performing-and-visual-art-pva',
    'performance-and-visual-arts',
    'sport',
}

# Stream mappings for Grades 11 and 12
NATURAL_SCIENCE_SUBJECTS = {
    'biology',
    'chemistry',
    'physics',
    'mathematics',
    'information-technology',
    'agriculture',
    'agriculure', # kehulum spelling for grade 12
    'english-for-ethiopia',
}

SOCIAL_SCIENCE_SUBJECTS = {
    'economics',
    'geography',
    'history',
    'mathematics',
    'information-technology',
    'english-for-ethiopia',
}

def get_html(url, retries=5):
    headers = {'User-Agent': USER_AGENT}
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=25) as resp:
                return resp.read().decode('utf-8', errors='ignore')
        except Exception as e:
            if attempt < retries - 1:
                wait_time = (attempt + 1) * 3
                print(f"  [RETRY] Error fetching {url} ({e}), retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                print(f"  [ERROR] Failed to fetch {url}: {e}")
                return None

def download_file(url, target_path, retries=4):
    os.makedirs(os.path.dirname(target_path), exist_ok=True)
    
    # Check if already downloaded and valid (> 500 KB)
    if os.path.exists(target_path) and os.path.getsize(target_path) > 500 * 1024:
        print(f"  [SKIP] {os.path.basename(target_path)} already exists ({os.path.getsize(target_path) // (1024*1024)} MB).")
        return True

    temp_path = target_path + ".tmp"
    headers = {'User-Agent': USER_AGENT}
    
    # Encode URL properly if needed
    parsed = urllib.parse.urlparse(url)
    encoded_url = urllib.parse.urlunparse((
        parsed.scheme,
        parsed.netloc,
        urllib.parse.quote(parsed.path),
        parsed.params,
        parsed.query,
        parsed.fragment
    ))

    for attempt in range(retries):
        try:
            req = urllib.request.Request(encoded_url, headers=headers)
            with urllib.request.urlopen(req, timeout=180) as response, open(temp_path, 'wb') as out_file:
                total_size = int(response.headers.get('content-length', 0))
                downloaded = 0
                block_size = 64 * 1024
                
                while True:
                    buffer = response.read(block_size)
                    if not buffer:
                        break
                    downloaded += len(buffer)
                    out_file.write(buffer)
                    
                    if total_size > 0:
                        percent = downloaded * 100 / total_size
                        mb_down = downloaded / (1024 * 1024)
                        mb_total = total_size / (1024 * 1024)
                        sys.stdout.write(f"\r  [DOWNLOADING] {mb_down:.1f}MB / {mb_total:.1f}MB ({percent:.1f}%)")
                        sys.stdout.flush()
                
                sys.stdout.write("\n")

            if os.path.exists(temp_path) and os.path.getsize(temp_path) > 500 * 1024:
                if os.path.exists(target_path):
                    os.remove(target_path)
                os.rename(temp_path, target_path)
                print(f"  [SUCCESS] Saved {os.path.basename(target_path)}")
                return True
            else:
                print(f"  [ERROR] Downloaded file seems corrupt or empty (< 500 KB).")
                if os.path.exists(temp_path):
                    os.remove(temp_path)

        except Exception as e:
            print(f"\n  [WARN] Attempt {attempt+1}/{retries} failed for {url}: {e}")
            if os.path.exists(temp_path):
                os.remove(temp_path)
            if attempt < retries - 1:
                wait_t = (attempt + 1) * 4
                print(f"  Retrying in {wait_t}s...")
                time.sleep(wait_t)

    print(f"  [ERROR] Failed to download after {retries} attempts: {url}")
    return False

def scrape_grade_books(grade_num):
    url = f"https://kehulum.com/student-textbook/new/grade-{grade_num}"
    html = get_html(url)
    if not html:
        return []

    soup = BeautifulSoup(html, 'html.parser')
    books = []
    seen = set()

    for a in soup.find_all('a', href=True):
        href = a['href']
        m = re.match(rf'^https://kehulum\.com/student-textbook/new/grade-{grade_num}/([^/]+)$', href)
        if m:
            slug = m.group(1).lower().strip()
            if slug in seen or slug in EXCLUDED_SUBJECTS:
                continue
            seen.add(slug)
            books.append({'slug': slug, 'detail_url': href})
    
    return books

def get_pdf_download_url(detail_url):
    html = get_html(detail_url)
    if not html:
        return None
    
    match = re.search(r'href="([^"]+\.pdf)"', html)
    if match:
        return match.group(1)
    return None

def normalize_subject_name(slug):
    # Normalize common slugs into clean filenames
    mapping = {
        'english-for-ethiopia': 'english',
        'agriculure': 'agriculture',
        'information-technology': 'information_technology',
        'citizenship-education': 'citizenship_education',
        'citizen-education': 'citizenship_education',
        'career-and-technical-education-cte': 'cte',
        'general-science': 'general_science',
        'social-studies': 'social_studies',
    }
    return mapping.get(slug, slug.replace('-', '_'))

def main():
    parser = argparse.ArgumentParser(description="Download and organize Ethiopian textbooks.")
    parser.add_argument('--grades', type=str, default='9,10,11,12', help="Comma-separated grades (e.g. 9,10,11,12 or all)")
    parser.add_argument('--output', type=str, default='Books', help="Destination books directory")
    parser.add_argument('--dry-run', action='store_true', help="List books without downloading")
    args = parser.parse_args()

    if args.grades.lower() == 'all':
        grades = list(range(1, 13))
    else:
        grades = [int(g.strip()) for g in args.grades.split(',') if g.strip().isdigit()]

    base_dir = os.path.abspath(args.output)
    print(f"Textbook Downloader & Organizer")
    print(f"Target Directory: {base_dir}")
    print(f"Grades: {grades}")
    print(f"Excluded Subjects: {', '.join(EXCLUDED_SUBJECTS)}\n")

    # Keep a cache of already downloaded files to easily duplicate shared subjects across streams
    download_cache = {}

    for grade in grades:
        print(f"--- Processing Grade {grade} ---")
        books = scrape_grade_books(grade)
        print(f"Found {len(books)} relevant books (excluding Amharic, HPE/Sports, etc.)")

        for book in books:
            slug = book['slug']
            sub_name = normalize_subject_name(slug)
            filename = f"{sub_name}.pdf"

            # Determine destination folder(s)
            target_dirs = []
            if grade in [11, 12]:
                is_nat = slug in NATURAL_SCIENCE_SUBJECTS
                is_soc = slug in SOCIAL_SCIENCE_SUBJECTS
                if is_nat:
                    target_dirs.append(os.path.join(base_dir, f"Grade_{grade}", "Natural_Science"))
                if is_soc:
                    target_dirs.append(os.path.join(base_dir, f"Grade_{grade}", "Social_Science"))
                if not is_nat and not is_soc:
                    target_dirs.append(os.path.join(base_dir, f"Grade_{grade}"))
            else:
                target_dirs.append(os.path.join(base_dir, f"Grade_{grade}"))

            print(f"\n[Grade {grade}] Subject: {sub_name}")
            for td in target_dirs:
                rel_path = os.path.relpath(os.path.join(td, filename), base_dir)
                print(f"  Target: Books/{rel_path}")

            if args.dry_run:
                continue

            # Check if all destination files already exist
            all_exist = all(
                os.path.exists(os.path.join(td, filename)) and os.path.getsize(os.path.join(td, filename)) > 500 * 1024
                for td in target_dirs
            )
            if all_exist:
                print(f"  [SKIP] All destination copies already exist.")
                continue

            # Look up or fetch download URL
            pdf_url = get_pdf_download_url(book['detail_url'])
            if not pdf_url:
                print(f"  [ERROR] No PDF link found on {book['detail_url']}")
                continue

            # First download to the first destination
            first_target = os.path.join(target_dirs[0], filename)
            success = download_file(pdf_url, first_target)
            
            # If successful and book belongs to multiple streams, copy to second destination
            if success:
                for additional_dir in target_dirs[1:]:
                    add_target = os.path.join(additional_dir, filename)
                    os.makedirs(additional_dir, exist_ok=True)
                    if not os.path.exists(add_target) or os.path.getsize(add_target) < 500 * 1024:
                        shutil.copy2(first_target, add_target)
                        print(f"  [COPIED] Shared subject mirrored to {os.path.relpath(add_target, base_dir)}")

            time.sleep(1) # Gentle delay between books

    print("\nAll downloads and organization completed successfully!")

if __name__ == '__main__':
    main()
