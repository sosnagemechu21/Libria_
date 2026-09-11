import os
import re

EMOJI_MAP = {
    '📚': '<i data-lucide="book-open"></i>',
    '⏱': '<i data-lucide="clock"></i>',
    '☕': '<i data-lucide="coffee"></i>',
    '🏠': '<i data-lucide="home"></i>',
    '🤖': '<i data-lucide="bot"></i>',
    '👤': '<i data-lucide="user"></i>',
    '🎉': '<i data-lucide="party-popper"></i>',
    '📝': '<i data-lucide="notebook-pen"></i>',
    '💡': '<i data-lucide="lightbulb"></i>',
    '🚀': '<i data-lucide="rocket"></i>',
    '🔄': '<i data-lucide="refresh-cw"></i>',
    '📈': '<i data-lucide="trending-up"></i>',
    '🖤': '<i data-lucide="moon"></i>',
    '🌿': '<i data-lucide="leaf"></i>',
    '📜': '<i data-lucide="scroll"></i>',
    '🌌': '<i data-lucide="stars"></i>',
    '🌸': '<i data-lucide="flower"></i>',
    '🎥': '<i data-lucide="video"></i>',
    '🎬': '<i data-lucide="clapperboard"></i>',
    '🚫': '<i data-lucide="ban"></i>',
    '🔍': '<i data-lucide="search"></i>',
    '▶': '<i data-lucide="play"></i>',
    '⚡': '<i data-lucide="zap"></i>',
    '🎓': '<i data-lucide="graduation-cap"></i>',
    '🎨': '<i data-lucide="palette"></i>',
    '💾': '<i data-lucide="save"></i>',
    '✅': '<i data-lucide="check-circle"></i>',
    '🏆': '<i data-lucide="trophy"></i>',
    '🔥': '<i data-lucide="flame"></i>',
    '💬': '<i data-lucide="message-square"></i>',
    '👋': '<i data-lucide="hand"></i>',
    '📄': '<i data-lucide="file-text"></i>',
    '🎵': '<i data-lucide="music"></i>',
    '✓': '<i data-lucide="check"></i>'
}

def replace_in_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    for emoji, lucide in EMOJI_MAP.items():
        content = content.replace(emoji, lucide)
        
    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Updated {filepath}")

for root, _, files in os.walk('templates'):
    for file in files:
        if file.endswith('.html'):
            replace_in_file(os.path.join(root, file))

# Add script to base.html if not present
base_path = 'templates/base.html'
with open(base_path, 'r', encoding='utf-8') as f:
    base_content = f.read()

if 'lucide.min.js' not in base_content:
    base_content = base_content.replace('</body>', '  <script src="https://unpkg.com/lucide@latest"></script>\n  <script>lucide.createIcons();</script>\n</body>')
    with open(base_path, 'w', encoding='utf-8') as f:
        f.write(base_content)
    print("Added Lucide script to base.html")

print("Done replacing emojis in templates.")
