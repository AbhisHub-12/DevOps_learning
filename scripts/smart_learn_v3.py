#!/usr/bin/env python3
"""
Smart Learning Assistant v3.0 - Add to Existing DevOps_Notes.html
Author: Abhisht

This version:
- Does NOT change index.html
- Does NOT create topics/ folder
- ADDS new sections to existing DevOps_Notes.html
- Matches the original format exactly

Usage:
    learn3 -f /path/to/file.pdf              # Add from PDF
    learn3 -f /path/to/file.pdf -t git       # Add to specific section
    learn3 -i                                 # Paste content
    learn3 --list                             # List sections
"""

import os
import sys
import argparse
import yaml
import json
import re
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Tuple

# Third-party imports
try:
    from openai import OpenAI
except ImportError:
    subprocess.run([sys.executable, "-m", "pip", "install", "openai", "--break-system-packages", "-q"])
    from openai import OpenAI

try:
    import fitz  # PyMuPDF
except ImportError:
    subprocess.run([sys.executable, "-m", "pip", "install", "PyMuPDF", "--break-system-packages", "-q"])
    import fitz

# Configuration
CONFIG_PATH = "/Users/abhishtbagewadi/Documents/Scripts/RCA-SCRIPT-2/abhisht_script_github_ready/config/config.yaml"
REPO_PATH = Path.home() / "DevOps_learning"
NOTES_FILE = REPO_PATH / "DevOps_Notes.html"

# Chunk size for large content
CHUNK_SIZE = 6000

# Existing sections in DevOps_Notes.html (id -> display name)
EXISTING_SECTIONS = {
    "git-advanced": "Git & GitHub Advanced",
    "github-actions": "GitHub Actions",
    "linux": "Linux for DevOps",
    "cicd": "CI/CD Pipelines",
    "docker": "Docker Deep Dive",
    "kubernetes": "Kubernetes",
    "ingress": "Ingress & Cert Manager",
    "observability": "Observability"
}


def load_config() -> dict:
    with open(CONFIG_PATH, 'r') as f:
        return yaml.safe_load(f)


def get_openai_client() -> OpenAI:
    config = load_config()
    return OpenAI(api_key=config['openai']['api_key'])


def extract_pdf_content(file_path: str) -> str:
    """Extract text from PDF - tries text first, then OCR via Vision API"""
    content = []
    try:
        doc = fitz.open(file_path)
        total_pages = len(doc)
        print(f"   📄 Processing {total_pages} pages...")

        # First try text extraction
        for i, page in enumerate(doc):
            text = page.get_text()
            if text and text.strip():
                content.append(text)
            if total_pages > 10 and (i + 1) % 10 == 0:
                print(f"   📖 Processed {i+1}/{total_pages} pages...")

        text_content = "\n".join(content)

        # If no text found, use Vision API for image-based PDFs
        if len(text_content.strip()) < 100:
            print(f"   📷 PDF appears to be image-based. Using AI Vision...")
            content = []
            client = get_openai_client()

            # Process pages as images (limit to first 20 pages for large PDFs)
            pages_to_process = min(total_pages, 20)

            for i in range(pages_to_process):
                page = doc[i]
                # Render page to image
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x zoom for better quality
                img_bytes = pix.tobytes("png")

                # Convert to base64
                import base64
                img_base64 = base64.b64encode(img_bytes).decode('utf-8')

                try:
                    response = client.chat.completions.create(
                        model="gpt-4o",
                        messages=[
                            {
                                "role": "user",
                                "content": [
                                    {
                                        "type": "text",
                                        "text": "Extract ALL text from this page. Include all headings, paragraphs, code blocks, lists, and any other text content. Return only the extracted text, nothing else."
                                    },
                                    {
                                        "type": "image_url",
                                        "image_url": {
                                            "url": f"data:image/png;base64,{img_base64}"
                                        }
                                    }
                                ]
                            }
                        ],
                        max_tokens=4000
                    )
                    page_text = response.choices[0].message.content
                    if page_text:
                        content.append(page_text)

                    if (i + 1) % 5 == 0:
                        print(f"   🔍 OCR processed {i+1}/{pages_to_process} pages...")

                except Exception as e:
                    print(f"   ⚠️ Page {i+1} OCR failed: {e}")

            if total_pages > 20:
                print(f"   ℹ️ Processed first 20 of {total_pages} pages")

            text_content = "\n\n".join(content)

        doc.close()
        return text_content

    except Exception as e:
        print(f"   ❌ PDF extraction failed: {e}")
        return ""


def read_file_content(file_path: str) -> str:
    """Read content from file"""
    path = Path(file_path)
    if not path.exists():
        print(f"❌ File not found: {file_path}")
        sys.exit(1)

    suffix = path.suffix.lower()
    file_size = path.stat().st_size
    print(f"   📁 File size: {file_size / 1024 / 1024:.2f} MB")

    if suffix == '.pdf':
        return extract_pdf_content(file_path)
    else:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            with open(file_path, 'r', encoding='latin-1') as f:
                return f.read()


def chunk_content(content: str) -> List[str]:
    """Split large content into chunks"""
    if len(content) <= CHUNK_SIZE:
        return [content]

    chunks = []
    paragraphs = content.split('\n\n')
    current_chunk = ""

    for para in paragraphs:
        if len(current_chunk) + len(para) < CHUNK_SIZE:
            current_chunk += para + "\n\n"
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = para + "\n\n"

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks


def analyze_and_format_content(client: OpenAI, content: str, section_name: str) -> str:
    """Analyze content and format it in the existing HTML style"""

    chunks = chunk_content(content)
    print(f"📦 Split into {len(chunks)} chunks")

    all_html = ""

    for i, chunk in enumerate(chunks):
        print(f"   Analyzing chunk {i+1}/{len(chunks)}...", end="\r")

        prompt = f"""Extract learning content from this text about {section_name} and format as HTML.

CONTENT:
{chunk}

FORMAT THE OUTPUT AS HTML using these exact styles (no <html>, <head>, <body> tags - just the content):

For subsection titles:
<h3>Subsection Title</h3>

For code blocks:
<div class="command-box">
# Comment
command here
</div>

For tips:
<div class="tip">Tip text here</div>

For warnings:
<div class="warning">Warning text here</div>

For best practices:
<div class="best-practice">Best practice text here</div>

For command tables:
<table class="command-table">
    <tr><th>Command</th><th>Description</th></tr>
    <tr><td><code>command</code></td><td>description</td></tr>
</table>

For regular paragraphs:
<p>Text here</p>

For lists:
<ul>
    <li>Item 1</li>
    <li>Item 2</li>
</ul>

Extract all useful information. Use appropriate formatting for the content type."""

        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You format technical content as HTML. Return only HTML content, no markdown, no code blocks."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2
            )

            html_content = response.choices[0].message.content.strip()

            # Clean up any markdown code blocks if present
            html_content = re.sub(r'^```html?\n?', '', html_content)
            html_content = re.sub(r'\n?```$', '', html_content)

            all_html += html_content + "\n\n"

        except Exception as e:
            print(f"   ⚠️ Error: {e}")

    print(f"   ✅ Processed {len(chunks)} chunks")
    return all_html


def find_section_in_file(section_id: str) -> bool:
    """Check if section exists in the file"""
    with open(NOTES_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    return f'id="{section_id}"' in content


def add_content_to_section(section_id: str, new_content: str) -> bool:
    """Add new content to existing section"""

    with open(NOTES_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find the section and add content before the closing </section> tag
    section_pattern = f'(<section id="{section_id}"[^>]*>.*?)(</section>)'

    def replace_section(match):
        section_content = match.group(1)
        section_end = match.group(2)

        # Add timestamp comment and new content
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        addition = f'\n                <!-- Added on {timestamp} -->\n{new_content}\n                '

        return section_content + addition + section_end

    new_file_content, count = re.subn(section_pattern, replace_section, content, flags=re.DOTALL)

    if count > 0:
        with open(NOTES_FILE, 'w', encoding='utf-8') as f:
            f.write(new_file_content)
        return True
    return False


def create_new_section(section_id: str, section_title: str, new_content: str) -> bool:
    """Create a new section and add to TOC"""

    with open(NOTES_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    # Count existing sections to get the number
    section_count = len(re.findall(r'<section id="[^"]*" class="section">', content))
    section_num = section_count + 1

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    # Create new section HTML
    new_section = f'''
            <!-- New Section Added on {timestamp} -->
            <section id="{section_id}" class="section">
                <h2>{section_num}. {section_title}</h2>

{new_content}
            </section>
'''

    # Add to TOC
    toc_entry = f'                <li><a href="#{section_id}">{section_title}</a></li>\n'

    # Find TOC and add entry
    toc_pattern = r'(</ul>\s*</nav>)'
    content = re.sub(toc_pattern, toc_entry + r'            \1', content)

    # Add section before closing </main>
    content = content.replace('</main>', new_section + '        </main>')

    with open(NOTES_FILE, 'w', encoding='utf-8') as f:
        f.write(content)

    return True


def detect_best_section(client: OpenAI, content: str) -> str:
    """Detect which section the content belongs to"""

    sections_list = ", ".join([f"{k}: {v}" for k, v in EXISTING_SECTIONS.items()])

    sample = content[:5000] if len(content) > 5000 else content

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You identify which DevOps section content belongs to. Respond with only the section ID."},
            {"role": "user", "content": f"""Which section does this content belong to?

AVAILABLE SECTIONS:
{sections_list}

CONTENT:
{sample}

Respond with ONLY the section ID (e.g., "git-advanced", "docker", "kubernetes").
If it doesn't fit any section, suggest a new section ID in kebab-case."""}
        ],
        temperature=0.1
    )

    return response.choices[0].message.content.strip().lower().replace('"', '')


def git_commit_and_push(message: str) -> bool:
    """Commit and push changes"""
    try:
        os.chdir(REPO_PATH)
        subprocess.run(['git', 'add', 'DevOps_Notes.html'], check=True, capture_output=True)
        subprocess.run(['git', 'commit', '-m', message], check=True, capture_output=True)
        result = subprocess.run(['git', 'push'], capture_output=True, text=True)
        return result.returncode == 0
    except subprocess.CalledProcessError:
        return False


def list_sections():
    """List all sections"""
    print("\n📚 Existing Sections in DevOps_Notes.html:\n")
    for key, name in EXISTING_SECTIONS.items():
        print(f"  • {key}: {name}")
    print("\n💡 Use -t <section-id> to add content to a specific section")
    print("   Example: learn3 -f file.pdf -t docker")
    print()


def interactive_input() -> str:
    """Get multi-line input"""
    print("\n📝 Paste your content (Ctrl+D when done):\n")
    lines = []
    try:
        while True:
            line = input()
            lines.append(line)
    except EOFError:
        pass
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(
        description='Smart Learning v3 - Add to existing DevOps_Notes.html',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  learn3 -f notes.pdf                  # Auto-detect section
  learn3 -f notes.pdf -t docker        # Add to Docker section
  learn3 -f notes.pdf -t "new-topic"   # Create new section
  learn3 -i -t kubernetes              # Paste content to K8s section
        '''
    )

    parser.add_argument('content', nargs='?', help='Text content')
    parser.add_argument('-f', '--file', help='File path')
    parser.add_argument('-t', '--topic', help='Target section ID')
    parser.add_argument('-i', '--interactive', action='store_true', help='Paste mode')
    parser.add_argument('--list', action='store_true', help='List sections')
    parser.add_argument('--dry-run', action='store_true', help='Preview only')
    parser.add_argument('--no-push', action='store_true', help='No git push')

    args = parser.parse_args()

    if args.list:
        list_sections()
        return

    # Get content
    content = None
    source = "input"

    if args.file:
        print(f"\n📄 Reading: {args.file}")
        content = read_file_content(args.file)
        source = Path(args.file).name
        print(f"   ✅ Extracted {len(content):,} characters")
    elif args.interactive:
        content = interactive_input()
        source = "paste"
    elif args.content:
        content = args.content
    else:
        parser.print_help()
        sys.exit(1)

    if not content or len(content.strip()) < 10:
        print("❌ Content too short")
        sys.exit(1)

    print(f"\n🤖 Initializing AI...")
    client = get_openai_client()

    # Determine section
    if args.topic:
        section_id = args.topic.lower().replace(" ", "-")
        print(f"🎯 Target section: {section_id}")
    else:
        print("🔍 Auto-detecting section...")
        section_id = detect_best_section(client, content)
        print(f"   Detected: {section_id}")

    # Check if section exists
    section_exists = section_id in EXISTING_SECTIONS or find_section_in_file(section_id)
    section_name = EXISTING_SECTIONS.get(section_id, section_id.replace("-", " ").title())

    print(f"\n📝 Formatting content for: {section_name}")
    formatted_html = analyze_and_format_content(client, content, section_name)

    if args.dry_run:
        print("\n🔍 Dry run - preview:")
        print("-" * 50)
        print(formatted_html[:1000])
        print("-" * 50)
        print(f"\n{'Would update' if section_exists else 'Would create'} section: {section_id}")
        return

    # Add content
    if section_exists:
        print(f"📥 Adding to existing section: {section_id}")
        success = add_content_to_section(section_id, formatted_html)
    else:
        print(f"📁 Creating new section: {section_id}")
        success = create_new_section(section_id, section_name, formatted_html)
        # Add to EXISTING_SECTIONS for future reference
        EXISTING_SECTIONS[section_id] = section_name

    if success:
        print(f"   ✅ Content added successfully!")

        # Git commit and push
        commit_msg = f"📚 Add to {section_name} (from {source})"

        if not args.no_push:
            print(f"\n📤 Pushing to GitHub...")
            if git_commit_and_push(commit_msg):
                print(f"\n✅ Updated DevOps_Notes.html!")
                print(f"   🌐 View: https://abhishub-12.github.io/DevOps_learning/DevOps_Notes.html")
            else:
                print(f"\n⚠️ Saved locally. Push manually if needed.")
        else:
            subprocess.run(['git', 'add', 'DevOps_Notes.html'], cwd=REPO_PATH, capture_output=True)
            subprocess.run(['git', 'commit', '-m', commit_msg], cwd=REPO_PATH, capture_output=True)
            print(f"\n✅ Committed locally (--no-push)")
    else:
        print(f"   ❌ Failed to add content")


if __name__ == '__main__':
    main()
