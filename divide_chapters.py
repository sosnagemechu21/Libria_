"""
divide_chapters.py

Splits Ethiopian textbooks into individual chapters:
1. Extracts chapter text notes into Books/Notes/<Structure>/Chapter_<N>.txt for manual editing.
2. Optionally splits the PDF into individual chapter PDF files (--split-pdf).
"""

import os
import re
import sys
import argparse
import PyPDF2

ROMAN_MAP = {
    'I': 1, 'II': 2, 'III': 3, 'IV': 4, 'V': 5,
    'VI': 6, 'VII': 7, 'VIII': 8, 'IX': 9, 'X': 10,
    'XI': 11, 'XII': 12, 'XIII': 13, 'XIV': 14, 'XV': 15,
    'XVI': 16, 'XVII': 17, 'XVIII': 18, 'XIX': 19, 'XX': 20
}

def parse_unit_number(text_val):
    text_val = text_val.strip().upper()
    if text_val.isdigit():
        return int(text_val)
    if text_val in ROMAN_MAP:
        return ROMAN_MAP[text_val]
    return None

def detect_chapters_from_toc(reader):
    """
    Parses the Table of Contents (TOC) typically present in the first 20 pages.
    Returns list of dicts: {'unit': int, 'title': str, 'start_page': int, 'end_page': int, 'start_idx': int, 'end_idx': int}
    """
    total_pages = len(reader.pages)
    toc_entries = []
    last_toc_page = 0

    for p_idx in range(min(20, total_pages)):
        try:
            text = reader.pages[p_idx].extract_text() or ""
        except Exception:
            continue

        for line in text.split('\n'):
            line_s = line.strip()
            # Match: Unit 1: Title ... 1 or Chapter 1 Title 12
            m = re.match(r'^(?:Unit|Chapter)\s+([0-9]{1,2}|[IVXLCDM]{1,6})\s*[:\.\-]?\s*(.+?)\s+([0-9]{1,4})\s*$', line_s, re.IGNORECASE)
            if m:
                u_num = parse_unit_number(m.group(1))
                if u_num and 1 <= u_num <= 35:
                    u_title = m.group(2).strip()
                    book_p = int(m.group(3))
                    # Avoid duplicates or sub-sections
                    if not any(e['unit'] == u_num for e in toc_entries):
                        toc_entries.append({
                            'unit': u_num,
                            'title': u_title,
                            'book_page': book_p
                        })
                        last_toc_page = p_idx

    if len(toc_entries) < 2:
        return []

    # Sort TOC entries by unit number
    toc_entries.sort(key=lambda x: x['unit'])

    # Find PDF page offset by matching book page 1 / Unit 1 opener after TOC
    target_u1_page = toc_entries[0]['book_page']
    offset = None

    for p_idx in range(last_toc_page + 1, min(last_toc_page + 20, total_pages)):
        try:
            p_text = reader.pages[p_idx].extract_text() or ""
            lines = [l.strip() for l in p_text.split('\n') if l.strip()]
            # Match page number or unit opener
            if any(l == str(target_u1_page) or l.endswith(f" {target_u1_page}") or l.startswith(f"{target_u1_page} ") for l in lines[-3:] + lines[:3]):
                offset = p_idx - target_u1_page + 1
                break
            if re.search(r'\bunit\b', p_text, re.IGNORECASE) and (str(target_u1_page) in p_text or "outcomes" in p_text.lower() or "introduction" in p_text.lower()):
                offset = p_idx - target_u1_page + 1
                break
        except Exception:
            continue

    if offset is None:
        offset = last_toc_page + 1

    chapters = []
    for i, entry in enumerate(toc_entries):
        start_idx = max(0, min(entry['book_page'] + offset - 1, total_pages - 1))
        if i + 1 < len(toc_entries):
            next_start = toc_entries[i+1]['book_page'] + offset - 1
            end_idx = max(start_idx, min(next_start - 1, total_pages - 1))
        else:
            end_idx = total_pages - 1

        chapters.append({
            'unit': entry['unit'],
            'title': entry['title'],
            'start_page': start_idx + 1,
            'end_page': end_idx + 1,
            'start_idx': start_idx,
            'end_idx': end_idx
        })

    return chapters

def detect_chapters_from_page_scan(reader):
    """
    Fallback method: scans every page line-by-line for Unit / Chapter headings.
    """
    total_pages = len(reader.pages)
    unit_pattern = re.compile(
        r'^\s*(?:Unit|Chapter)\s+([0-9]{1,2}|[IVXLCDM]{1,6})\b[:\s\-]*(.*)',
        re.IGNORECASE
    )

    chapters = {}
    current_chapter = 0

    for p_idx in range(min(10, total_pages), total_pages):
        try:
            page = reader.pages[p_idx]
            page_text = page.extract_text() or ""
        except Exception:
            continue

        lines = [l.strip() for l in page_text.split('\n') if l.strip()]
        for line_idx, line in enumerate(lines[:8]):
            m = unit_pattern.match(line)
            if m:
                unit_num = parse_unit_number(m.group(1))
                if unit_num is not None and 1 <= unit_num <= 35:
                    if (current_chapter == 0 and unit_num == 1) or (current_chapter > 0 and unit_num == current_chapter + 1):
                        title = m.group(2).strip()
                        if not title and line_idx + 1 < len(lines):
                            title = lines[line_idx + 1]

                        if current_chapter > 0:
                            chapters[current_chapter]['end_page'] = p_idx
                            chapters[current_chapter]['end_idx'] = p_idx - 1

                        current_chapter = unit_num
                        chapters[current_chapter] = {
                            'unit': unit_num,
                            'title': title,
                            'start_page': p_idx + 1,
                            'end_page': total_pages,
                            'start_idx': p_idx,
                            'end_idx': total_pages - 1
                        }
                        break

    return list(chapters.values())

def extract_chapters_from_pdf(pdf_path, output_dir, split_pdf=False, force=False):
    if not os.path.exists(pdf_path):
        print(f"[ERROR] PDF not found: {pdf_path}")
        return False

    os.makedirs(output_dir, exist_ok=True)
    existing_notes = [f for f in os.listdir(output_dir) if f.startswith("Chapter_") and f.endswith(".txt")]
    if existing_notes and not force:
        print(f"[SKIP] Chapters already extracted in {os.path.basename(output_dir)} ({len(existing_notes)} chapters found).")
        return True

    print(f"\n[PROCESSING] {os.path.basename(pdf_path)}")
    print(f"  Target Notes Folder: {output_dir}")

    try:
        with open(pdf_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            num_pages = len(reader.pages)
            print(f"  Total Pages: {num_pages}")

            # Strategy 1: TOC parser
            chapters = detect_chapters_from_toc(reader)
            method_used = "Table of Contents"

            # Strategy 2: Fallback page-by-page header scan
            if not chapters:
                chapters = detect_chapters_from_page_scan(reader)
                method_used = "Page Header Scan"

            if not chapters:
                print(f"  [WARN] No chapter markers detected. Extracting first 60 pages as reference note.")
                chapters = [{
                    'unit': 1,
                    'title': 'General Content',
                    'start_page': 1,
                    'end_page': min(num_pages, 60),
                    'start_idx': 0,
                    'end_idx': min(num_pages, 60) - 1
                }]
                method_used = "Single Reference"

            print(f"  Detected {len(chapters)} chapters using {method_used}.")

            # Save note files
            for ch in chapters:
                note_file = os.path.join(output_dir, f"Chapter_{ch['unit']}.txt")
                
                # Extract text for this chapter's pages
                ch_text = []
                for p in range(ch['start_idx'], ch['end_idx'] + 1):
                    try:
                        p_t = reader.pages[p].extract_text()
                        if p_t:
                            ch_text.append(p_t)
                    except Exception:
                        pass

                with open(note_file, 'w', encoding='utf-8') as out_f:
                    out_f.write("=" * 65 + "\n")
                    out_f.write(f"Book: {os.path.basename(pdf_path)}\n")
                    out_f.write(f"Chapter {ch['unit']}: {ch['title'] or 'Unit ' + str(ch['unit'])}\n")
                    out_f.write(f"Pages: {ch['start_page']} to {ch['end_page']}\n")
                    out_f.write("=" * 65 + "\n\n")
                    out_f.write("\n\n--- [PAGE BREAK] ---\n\n".join(ch_text))
                
                print(f"  -> Saved Note: Chapter_{ch['unit']}.txt (pp. {ch['start_page']}-{ch['end_page']})")

            # Optional: Split PDF
            if split_pdf and len(chapters) > 1:
                print(f"  [EXPORTING CHAPTER PDFs]")
                for ch in chapters:
                    pdf_writer = PyPDF2.PdfWriter()
                    for p in range(ch['start_idx'], ch['end_idx'] + 1):
                        pdf_writer.add_page(reader.pages[p])

                    ch_pdf_path = os.path.join(output_dir, f"Chapter_{ch['unit']}.pdf")
                    with open(ch_pdf_path, 'wb') as ch_out:
                        pdf_writer.write(ch_out)
                    print(f"  -> Saved PDF: Chapter_{ch['unit']}.pdf")

            print(f"[DONE] Successfully extracted {len(chapters)} chapters for {os.path.basename(pdf_path)}.\n")
            return True

    except Exception as e:
        print(f"[ERROR] Failed to process {pdf_path}: {e}\n")
        return False

def process_directory(books_dir, notes_dir, split_pdf=False, force=False):
    books_dir = os.path.abspath(books_dir)
    notes_dir = os.path.abspath(notes_dir)
    print(f"Scanning for textbooks in: {books_dir}")
    print(f"Notes destination: {notes_dir}\n")

    pdf_files = []
    for root, _, files in os.walk(books_dir):
        if 'Notes' in root.split(os.sep):
            continue
        for f in files:
            if f.lower().endswith('.pdf'):
                pdf_files.append(os.path.join(root, f))

    if not pdf_files:
        print(f"No PDF files found in {books_dir}.")
        return

    print(f"Found {len(pdf_files)} PDF textbook(s) to process.\n")

    for pdf_path in pdf_files:
        rel_path = os.path.relpath(pdf_path, books_dir)
        rel_dir = os.path.splitext(rel_path)[0]
        subject_notes_dir = os.path.join(notes_dir, rel_dir)
        extract_chapters_from_pdf(pdf_path, subject_notes_dir, split_pdf=split_pdf, force=force)

def main():
    parser = argparse.ArgumentParser(description="Divide Ethiopian textbooks into chapters and notes.")
    parser.add_argument('--input', type=str, default='Books', help="Path to a PDF file or directory containing PDFs")
    parser.add_argument('--output', type=str, default='Books/Notes', help="Directory to save chapter notes")
    parser.add_argument('--split-pdf', action='store_true', help="Also split and save chapter PDF files")
    parser.add_argument('--force', action='store_true', help="Force re-extraction of chapters if already present")
    args = parser.parse_args()

    input_path = os.path.abspath(args.input)
    output_path = os.path.abspath(args.output)

    if os.path.isfile(input_path):
        extract_chapters_from_pdf(input_path, output_path, split_pdf=args.split_pdf, force=args.force)
    elif os.path.isdir(input_path):
        process_directory(input_path, output_path, split_pdf=args.split_pdf, force=args.force)
    else:
        print(f"[ERROR] Path does not exist: {input_path}")

if __name__ == '__main__':
    main()
