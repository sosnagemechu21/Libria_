import os
import PyPDF2
import re

def extract_chapters(pdf_path, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    print(f"Processing {pdf_path}...")
    
    try:
        with open(pdf_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            
            current_chapter = 0
            chapter_text = []
            
            # Simple heuristic: Look for "Unit 1" or "Chapter 1" on a line
            pattern = re.compile(r'^(Unit|Chapter)\s+(\d+)', re.IGNORECASE)
            
            for i in range(len(reader.pages)):
                page = reader.pages[i]
                text = page.extract_text()
                if not text:
                    continue
                
                lines = text.split('\n')
                for line in lines:
                    match = pattern.search(line.strip())
                    if match:
                        chapter_num = int(match.group(2))
                        
                        # Save previous chapter if we moved to a new one
                        if current_chapter > 0 and chapter_num > current_chapter:
                            save_chapter(output_dir, current_chapter, chapter_text)
                            chapter_text = []
                            
                        current_chapter = chapter_num
                        
                    if current_chapter > 0:
                        chapter_text.append(line)
            
            # Save the last chapter
            if current_chapter > 0 and chapter_text:
                save_chapter(output_dir, current_chapter, chapter_text)
                
            print(f"Finished {pdf_path}. Extracted {current_chapter} chapters.")
            
    except Exception as e:
        print(f"Error processing {pdf_path}: {e}")

def save_chapter(output_dir, chapter_num, text_lines):
    filename = os.path.join(output_dir, f"Chapter_{chapter_num}.txt")
    with open(filename, 'w', encoding='utf-8') as f:
        f.write('\n'.join(text_lines))
    print(f"Saved {filename}")

if __name__ == "__main__":
    books = [
        ("Books/grade_9_biology.pdf", "Books/Notes/Biology_Grade_9"),
        ("Books/grade_9_chemistry.pdf", "Books/Notes/Chemistry_Grade_9")
    ]
    
    for pdf, out_dir in books:
        if os.path.exists(pdf):
            extract_chapters(pdf, out_dir)
        else:
            print(f"File not found: {pdf}")
