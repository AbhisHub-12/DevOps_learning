#!/usr/bin/env python3
"""
Smart Learning Assistant v2.0 - Unlimited File Size & Multi-Topic Support
Author: Abhisht

Features:
- No file size limit (chunked processing)
- Auto-detects multiple topics in content
- Creates separate topic folders/files
- Updates index.html dynamically
- Supports PDF, text, code files, images (OCR)

Usage:
    learn "paste your text here"           - Add text content
    learn -f /path/to/file.pdf            - Add from PDF (any size)
    learn -f /path/to/large-doc.txt       - Add from text file
    learn -i                               - Interactive mode
    learn --list                           - List all topics
    learn --search "kubernetes"            - Search existing notes
"""

import os
import sys
import argparse
import yaml
import json
import re
import subprocess
import base64
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Tuple
from concurrent.futures import ThreadPoolExecutor
import hashlib

# Third-party imports
try:
    from openai import OpenAI
except ImportError:
    subprocess.run([sys.executable, "-m", "pip", "install", "openai", "--break-system-packages", "-q"])
    from openai import OpenAI

try:
    import PyPDF2
except ImportError:
    subprocess.run([sys.executable, "-m", "pip", "install", "PyPDF2", "--break-system-packages", "-q"])
    import PyPDF2

try:
    import fitz  # PyMuPDF for better PDF handling
except ImportError:
    subprocess.run([sys.executable, "-m", "pip", "install", "PyMuPDF", "--break-system-packages", "-q"])
    import fitz

# Configuration
CONFIG_PATH = "/Users/abhishtbagewadi/Documents/Scripts/RCA-SCRIPT-2/abhisht_script_github_ready/config/config.yaml"
REPO_PATH = Path.home() / "DevOps_learning_v2"
INDEX_FILE = REPO_PATH / "index.html"
TOPICS_DIR = REPO_PATH / "topics"

# Chunk size for processing large content (characters)
CHUNK_SIZE = 6000
MAX_CHUNKS_PER_BATCH = 5

# DevOps Topics for categorization (can be extended dynamically)
DEVOPS_TOPICS = {
    "git": {"name": "Git & GitHub", "icon": "🔀", "color": "#f05032"},
    "github-actions": {"name": "GitHub Actions", "icon": "⚡", "color": "#2088ff"},
    "linux": {"name": "Linux", "icon": "🐧", "color": "#fcc624"},
    "docker": {"name": "Docker", "icon": "🐳", "color": "#2496ed"},
    "kubernetes": {"name": "Kubernetes", "icon": "☸️", "color": "#326ce5"},
    "terraform": {"name": "Terraform", "icon": "🏗️", "color": "#7b42bc"},
    "ansible": {"name": "Ansible", "icon": "🔧", "color": "#ee0000"},
    "jenkins": {"name": "Jenkins", "icon": "🔨", "color": "#d24939"},
    "cicd": {"name": "CI/CD Pipelines", "icon": "🔄", "color": "#43a047"},
    "aws": {"name": "AWS Cloud", "icon": "☁️", "color": "#ff9900"},
    "azure": {"name": "Azure Cloud", "icon": "🌐", "color": "#0078d4"},
    "gcp": {"name": "Google Cloud", "icon": "🌩️", "color": "#4285f4"},
    "monitoring": {"name": "Monitoring & Observability", "icon": "📊", "color": "#e65100"},
    "prometheus": {"name": "Prometheus & Grafana", "icon": "📈", "color": "#e6522c"},
    "security": {"name": "DevSecOps", "icon": "🔐", "color": "#d32f2f"},
    "networking": {"name": "Networking", "icon": "🌐", "color": "#00796b"},
    "helm": {"name": "Helm Charts", "icon": "⎈", "color": "#0f1689"},
    "argocd": {"name": "ArgoCD & GitOps", "icon": "🔶", "color": "#ef7b4d"},
    "scripting": {"name": "Shell Scripting", "icon": "📜", "color": "#4eaa25"},
    "python": {"name": "Python for DevOps", "icon": "🐍", "color": "#3776ab"},
    "yaml": {"name": "YAML & Configuration", "icon": "📝", "color": "#cb171e"},
    "nginx": {"name": "Nginx & Web Servers", "icon": "🌐", "color": "#009639"},
    "databases": {"name": "Databases", "icon": "🗄️", "color": "#336791"},
    "misc": {"name": "Miscellaneous", "icon": "📚", "color": "#607d8b"}
}


# Random colors for new topics
NEW_TOPIC_COLORS = [
    "#e91e63", "#9c27b0", "#673ab7", "#3f51b5", "#03a9f4",
    "#00bcd4", "#009688", "#4caf50", "#8bc34a", "#cddc39",
    "#ffeb3b", "#ffc107", "#ff9800", "#ff5722", "#795548"
]

# Icons for new topics (will cycle through)
NEW_TOPIC_ICONS = ["📖", "💡", "🔧", "⚙️", "🛠️", "📦", "🎯", "✨", "🔥", "💻"]


def find_or_create_topic(topic_input: str) -> str:
    """
    Find matching existing topic or create new one.
    Returns the topic key to use.
    """
    topic_input = topic_input.lower().strip().replace(" ", "-")

    # Check for exact match
    if topic_input in DEVOPS_TOPICS:
        print(f"   ✅ Found existing topic: {DEVOPS_TOPICS[topic_input]['name']}")
        return topic_input

    # Check for partial match (topic contains input or input contains topic)
    for key, info in DEVOPS_TOPICS.items():
        if topic_input in key or key in topic_input:
            print(f"   ✅ Matched to existing topic: {info['name']}")
            return key
        # Also check against the name
        if topic_input in info['name'].lower().replace(" ", "-"):
            print(f"   ✅ Matched to existing topic: {info['name']}")
            return key

    # No match found - create new topic
    print(f"   🆕 Creating new topic: {topic_input}")

    # Generate display name (capitalize words)
    display_name = " ".join(word.capitalize() for word in topic_input.replace("-", " ").split())

    # Pick random color and icon
    import random
    color = random.choice(NEW_TOPIC_COLORS)
    icon = random.choice(NEW_TOPIC_ICONS)

    # Add to DEVOPS_TOPICS
    DEVOPS_TOPICS[topic_input] = {
        "name": display_name,
        "icon": icon,
        "color": color
    }

    print(f"   {icon} New topic created: {display_name}")
    return topic_input


def process_for_specific_topic(client: OpenAI, content: str, topic: str) -> Dict[str, List[dict]]:
    """Process content for a specific topic (skip auto-detection)"""

    print(f"\n📊 Content size: {len(content):,} characters")

    topic_info = DEVOPS_TOPICS.get(topic, DEVOPS_TOPICS["misc"])
    print(f"🎯 Target topic: {topic_info['icon']} {topic_info['name']}")

    # Chunk the content
    chunks = chunk_content(content)
    print(f"📦 Split into {len(chunks)} chunks")

    # Process all chunks for this specific topic
    results = {topic: []}

    print(f"\n🔄 Processing all content for {topic_info['name']}...")

    for i, chunk in enumerate(chunks):
        print(f"   Analyzing chunk {i+1}/{len(chunks)}...", end="\r")
        analysis = analyze_chunk_for_topic(client, chunk, topic)
        if analysis:
            results[topic].append(analysis)

    print(f"   ✅ Extracted {len(results[topic])} sections for {topic_info['name']}")

    return results


def analyze_chunk_for_topic(client: OpenAI, chunk: str, target_topic: str) -> Optional[dict]:
    """Analyze chunk and extract content for specific topic (always relevant)"""

    topic_info = DEVOPS_TOPICS.get(target_topic, {"name": target_topic.replace("-", " ").title()})

    prompt = f"""Extract learning content from this text and format it for a {topic_info['name']} knowledge base.

CONTENT:
{chunk}

RESPOND IN JSON FORMAT:
{{
    "title": "Clear section title",
    "summary": "2-3 sentence summary of the content",
    "key_points": ["point 1", "point 2", "point 3"],
    "code_examples": [
        {{"description": "what it does", "language": "bash/yaml/python", "code": "the code"}}
    ],
    "commands": [
        {{"command": "the command", "description": "what it does"}}
    ],
    "tips": ["practical tip 1", "practical tip 2"],
    "best_practices": ["practice 1", "practice 2"]
}}

Extract all useful information. If no code/commands exist, use empty arrays."""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You extract learning content and format it as JSON. Always respond with valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )

        response_text = response.choices[0].message.content.strip()
        response_text = re.sub(r'^```json?\n?', '', response_text)
        response_text = re.sub(r'\n?```$', '', response_text)

        result = json.loads(response_text)
        # Always return result for specific topic mode (no relevance check)
        if result.get("title") or result.get("summary") or result.get("key_points"):
            return result
    except Exception as e:
        print(f"   ⚠️ Chunk analysis error: {e}")

    return None


def load_config() -> dict:
    """Load configuration from YAML file"""
    with open(CONFIG_PATH, 'r') as f:
        return yaml.safe_load(f)


def get_openai_client() -> OpenAI:
    """Initialize OpenAI client"""
    config = load_config()
    return OpenAI(api_key=config['openai']['api_key'])


def extract_pdf_content(file_path: str) -> str:
    """Extract text from PDF using PyMuPDF (handles large files better)"""
    content = []
    try:
        doc = fitz.open(file_path)
        total_pages = len(doc)
        print(f"   📄 Processing {total_pages} pages...")

        for i, page in enumerate(doc):
            text = page.get_text()
            if text:
                content.append(f"\n--- Page {i+1} ---\n{text}")

            # Progress indicator for large files
            if total_pages > 10 and (i + 1) % 10 == 0:
                print(f"   📖 Processed {i+1}/{total_pages} pages...")

        doc.close()
    except Exception as e:
        print(f"   ⚠️ PyMuPDF failed, trying PyPDF2: {e}")
        # Fallback to PyPDF2
        try:
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                for i, page in enumerate(reader.pages):
                    text = page.extract_text()
                    if text:
                        content.append(text)
        except Exception as e2:
            print(f"   ❌ PDF extraction failed: {e2}")
            return ""

    return "\n".join(content)


def read_file_content(file_path: str) -> Tuple[str, str]:
    """Read content from various file types. Returns (content, file_type)"""
    path = Path(file_path)

    if not path.exists():
        print(f"❌ Error: File not found: {file_path}")
        sys.exit(1)

    suffix = path.suffix.lower()
    file_size = path.stat().st_size

    print(f"   📁 File size: {file_size / 1024 / 1024:.2f} MB")

    if suffix == '.pdf':
        return extract_pdf_content(file_path), 'pdf'
    elif suffix in ['.png', '.jpg', '.jpeg', '.gif', '.webp']:
        # For images, we'll use vision API
        return read_image_content(file_path), 'image'
    else:
        # Text-based files - handle large files
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read(), 'text'
        except UnicodeDecodeError:
            with open(file_path, 'r', encoding='latin-1') as f:
                return f.read(), 'text'


def read_image_content(file_path: str) -> str:
    """Extract text from image using OpenAI Vision"""
    client = get_openai_client()

    with open(file_path, 'rb') as f:
        image_data = base64.b64encode(f.read()).decode('utf-8')

    # Determine image type
    suffix = Path(file_path).suffix.lower()
    mime_type = {
        '.png': 'image/png',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.gif': 'image/gif',
        '.webp': 'image/webp'
    }.get(suffix, 'image/png')

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Extract all text and technical information from this image. If it's a diagram, describe the architecture and components. If it contains code, extract the code. Provide detailed technical content."
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{mime_type};base64,{image_data}"
                        }
                    }
                ]
            }
        ],
        max_tokens=4096
    )

    return response.choices[0].message.content


def chunk_content(content: str, chunk_size: int = CHUNK_SIZE) -> List[str]:
    """Split large content into manageable chunks"""
    if len(content) <= chunk_size:
        return [content]

    chunks = []
    # Try to split on paragraph boundaries
    paragraphs = content.split('\n\n')
    current_chunk = ""

    for para in paragraphs:
        if len(current_chunk) + len(para) < chunk_size:
            current_chunk += para + "\n\n"
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = para + "\n\n"

    if current_chunk:
        chunks.append(current_chunk.strip())

    # If paragraphs are too long, force split
    final_chunks = []
    for chunk in chunks:
        if len(chunk) > chunk_size:
            for i in range(0, len(chunk), chunk_size):
                final_chunks.append(chunk[i:i+chunk_size])
        else:
            final_chunks.append(chunk)

    return final_chunks


def analyze_content_for_topics(client: OpenAI, content: str) -> List[str]:
    """First pass: Identify all topics present in the content"""

    topics_list = ", ".join(DEVOPS_TOPICS.keys())

    # Use a sample of content for topic detection
    sample = content[:10000] if len(content) > 10000 else content

    response = client.chat.completions.create(
        model="gpt-4o-mini",  # Faster for topic detection
        messages=[
            {
                "role": "system",
                "content": "You identify DevOps topics in content. Respond with ONLY a JSON array of topic keys."
            },
            {
                "role": "user",
                "content": f"""Identify ALL DevOps topics present in this content.

AVAILABLE TOPICS: {topics_list}

CONTENT:
{sample}

Respond with ONLY a JSON array of matching topic keys, e.g.: ["kubernetes", "docker", "helm"]
If content doesn't match any specific topic, use ["misc"]"""
            }
        ],
        temperature=0.1
    )

    response_text = response.choices[0].message.content.strip()

    # Clean and parse
    response_text = re.sub(r'^```json?\n?', '', response_text)
    response_text = re.sub(r'\n?```$', '', response_text)

    try:
        topics = json.loads(response_text)
        # Validate topics
        valid_topics = [t for t in topics if t in DEVOPS_TOPICS]
        return valid_topics if valid_topics else ["misc"]
    except:
        return ["misc"]


def analyze_chunk(client: OpenAI, chunk: str, target_topic: str) -> Optional[dict]:
    """Analyze a single chunk of content for a specific topic"""

    topic_info = DEVOPS_TOPICS.get(target_topic, DEVOPS_TOPICS["misc"])

    prompt = f"""Analyze this content and extract information related to {topic_info['name']}.

CONTENT:
{chunk}

RESPOND IN JSON FORMAT:
{{
    "relevant": true/false,
    "title": "Section title if relevant",
    "summary": "2-3 sentence summary",
    "key_points": ["point 1", "point 2"],
    "code_examples": [
        {{"description": "what it does", "language": "bash/yaml/python", "code": "the code"}}
    ],
    "commands": [
        {{"command": "the command", "description": "what it does"}}
    ],
    "tips": ["tip 1", "tip 2"],
    "best_practices": ["practice 1"]
}}

If content is not relevant to {topic_info['name']}, set "relevant": false and leave other fields empty."""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You extract DevOps learning content. Respond with valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )

        response_text = response.choices[0].message.content.strip()
        response_text = re.sub(r'^```json?\n?', '', response_text)
        response_text = re.sub(r'\n?```$', '', response_text)

        result = json.loads(response_text)
        if result.get("relevant", False):
            return result
    except Exception as e:
        print(f"   ⚠️ Chunk analysis error: {e}")

    return None


def process_large_content(client: OpenAI, content: str) -> Dict[str, List[dict]]:
    """Process large content, identify topics, and extract structured data"""

    print(f"\n📊 Content size: {len(content):,} characters")

    # Step 1: Identify all topics in the content
    print("🔍 Detecting topics...")
    topics = analyze_content_for_topics(client, content)
    print(f"   Found topics: {', '.join(topics)}")

    # Step 2: Chunk the content
    chunks = chunk_content(content)
    print(f"📦 Split into {len(chunks)} chunks")

    # Step 3: Process chunks for each topic
    results = {topic: [] for topic in topics}

    for topic in topics:
        topic_name = DEVOPS_TOPICS[topic]['name']
        print(f"\n🔄 Processing for {topic_name}...")

        for i, chunk in enumerate(chunks):
            print(f"   Analyzing chunk {i+1}/{len(chunks)}...", end="\r")
            analysis = analyze_chunk(client, chunk, topic)
            if analysis:
                results[topic].append(analysis)

        print(f"   ✅ Found {len(results[topic])} relevant sections for {topic_name}")

    return results


def ensure_topic_file(topic: str) -> Path:
    """Ensure topic directory and file exist, return file path"""

    # Create topics directory
    TOPICS_DIR.mkdir(exist_ok=True)

    topic_info = DEVOPS_TOPICS.get(topic, DEVOPS_TOPICS["misc"])
    topic_file = TOPICS_DIR / f"{topic}.html"

    if not topic_file.exists():
        # Create new topic file with template
        template = generate_topic_template(topic, topic_info)
        with open(topic_file, 'w', encoding='utf-8') as f:
            f.write(template)
        print(f"   📁 Created new topic file: {topic}.html")

    return topic_file


def generate_topic_template(topic: str, topic_info: dict) -> str:
    """Generate HTML template for a new topic file"""

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{topic_info['icon']} {topic_info['name']} - DevOps Learning</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/themes/prism-tomorrow.min.css" rel="stylesheet" />
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        :root {{
            --primary: {topic_info['color']};
            --dark: #2d3748;
            --light: #f7fafc;
            --code-bg: #1e1e1e;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: var(--dark);
            background: var(--light);
        }}
        .header {{
            background: linear-gradient(135deg, var(--primary) 0%, #333 100%);
            color: white;
            padding: 2rem;
            text-align: center;
        }}
        .header h1 {{ font-size: 2.5rem; margin-bottom: 0.5rem; }}
        .container {{ max-width: 1000px; margin: 0 auto; padding: 2rem; }}
        .section {{
            background: white;
            border-radius: 10px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            border-left: 4px solid var(--primary);
        }}
        .section h2 {{ color: var(--primary); margin-bottom: 1rem; }}
        .section h3 {{ color: var(--dark); margin: 1rem 0 0.5rem; }}
        .section-meta {{ font-size: 0.85rem; color: #666; margin-bottom: 1rem; }}
        pre {{
            background: var(--code-bg);
            border-radius: 8px;
            padding: 1rem;
            overflow-x: auto;
            margin: 1rem 0;
        }}
        code {{ font-family: 'Fira Code', monospace; font-size: 0.9rem; }}
        .tip {{
            background: #e6f7ff;
            border-left: 4px solid #1890ff;
            padding: 1rem;
            margin: 1rem 0;
            border-radius: 5px;
        }}
        .tip::before {{ content: '💡 TIP: '; font-weight: bold; color: #1890ff; }}
        .best-practice {{
            background: #f0f9ff;
            border: 2px solid var(--primary);
            padding: 1rem;
            margin: 1rem 0;
            border-radius: 8px;
        }}
        .best-practice::before {{
            content: '✅ BEST PRACTICE';
            display: block;
            font-weight: bold;
            color: var(--primary);
            margin-bottom: 0.5rem;
        }}
        table {{ width: 100%; border-collapse: collapse; margin: 1rem 0; }}
        th {{ background: var(--primary); color: white; padding: 0.75rem; text-align: left; }}
        td {{ padding: 0.75rem; border-bottom: 1px solid #e2e8f0; }}
        tr:hover {{ background: var(--light); }}
        ul {{ margin: 0.5rem 0 0.5rem 1.5rem; }}
        .back-link {{
            display: inline-block;
            margin: 1rem 0;
            color: var(--primary);
            text-decoration: none;
        }}
        .back-link:hover {{ text-decoration: underline; }}
        @media (max-width: 768px) {{
            .header h1 {{ font-size: 1.8rem; }}
            .container {{ padding: 1rem; }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{topic_info['icon']} {topic_info['name']}</h1>
        <p>DevOps Learning Notes</p>
    </div>

    <div class="container">
        <a href="../index.html" class="back-link">← Back to Topics</a>

        <main id="content">
        <!-- CONTENT_MARKER -->
        </main>
    </div>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/prism.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-bash.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-yaml.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-python.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-json.min.js"></script>
</body>
</html>
'''


def generate_section_html(analysis: dict, topic: str) -> str:
    """Generate HTML section from analysis"""

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    section_id = hashlib.md5(f"{analysis.get('title', '')}{timestamp}".encode()).hexdigest()[:8]

    title = analysis.get('title', 'New Learning')
    summary = analysis.get('summary', '')
    key_points = analysis.get('key_points', [])
    code_examples = analysis.get('code_examples', [])
    tips = analysis.get('tips', [])
    commands = analysis.get('commands', [])
    best_practices = analysis.get('best_practices', [])

    html = f'''
        <section id="section-{section_id}" class="section">
            <h2>{title}</h2>
            <p class="section-meta">Added: {timestamp}</p>
            <p>{summary}</p>
'''

    if key_points:
        html += '            <h3>Key Points</h3>\n            <ul>\n'
        for point in key_points:
            html += f'                <li>{point}</li>\n'
        html += '            </ul>\n'

    if code_examples:
        html += '            <h3>Code Examples</h3>\n'
        for example in code_examples:
            lang = example.get('language', 'bash')
            code = example.get('code', '').replace('<', '&lt;').replace('>', '&gt;')
            desc = example.get('description', '')
            html += f'''            <p><strong>{desc}</strong></p>
            <pre><code class="language-{lang}">{code}</code></pre>
'''

    if commands:
        html += '''            <h3>Commands</h3>
            <table>
                <tr><th>Command</th><th>Description</th></tr>
'''
        for cmd in commands:
            cmd_text = cmd.get('command', '').replace('<', '&lt;').replace('>', '&gt;')
            html += f'''                <tr>
                    <td><code>{cmd_text}</code></td>
                    <td>{cmd.get('description', '')}</td>
                </tr>
'''
        html += '            </table>\n'

    if tips:
        for tip in tips:
            html += f'            <div class="tip">{tip}</div>\n'

    if best_practices:
        html += '            <div class="best-practice">\n'
        for practice in best_practices:
            html += f'                <p>• {practice}</p>\n'
        html += '            </div>\n'

    html += '        </section>\n'
    return html


def update_topic_file(topic: str, sections: List[dict]) -> Path:
    """Update topic file with new sections"""

    topic_file = ensure_topic_file(topic)

    with open(topic_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Generate HTML for all sections
    new_content = ""
    for section in sections:
        new_content += generate_section_html(section, topic)

    # Insert before marker
    marker = "<!-- CONTENT_MARKER -->"
    if marker in content:
        content = content.replace(marker, f"{new_content}\n        {marker}")
    else:
        # Fallback: insert before </main>
        content = content.replace("</main>", f"{new_content}\n        </main>")

    with open(topic_file, 'w', encoding='utf-8') as f:
        f.write(content)

    return topic_file


def update_index_html():
    """Update index.html with links to all topic files"""

    # Find all topic files
    topic_files = list(TOPICS_DIR.glob("*.html")) if TOPICS_DIR.exists() else []

    # Generate topic cards
    topic_cards = ""
    for topic_file in sorted(topic_files):
        topic_key = topic_file.stem
        if topic_key in DEVOPS_TOPICS:
            info = DEVOPS_TOPICS[topic_key]
            topic_cards += f'''
            <a href="topics/{topic_key}.html" class="topic-card" style="border-color: {info['color']}">
                <span class="topic-icon">{info['icon']}</span>
                <span class="topic-name">{info['name']}</span>
            </a>
'''

    # Also include existing HTML files in root
    existing_files = ""
    for html_file in REPO_PATH.glob("*.html"):
        if html_file.name not in ["index.html"]:
            name = html_file.stem.replace("_", " ").replace("-", " ").title()
            existing_files += f'''
            <a href="{html_file.name}" class="file-link">📄 {name}</a>
'''

    # Generate new index.html
    index_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🚀 DevOps Learning Hub - AbhisHub</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 2rem;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        .header {{
            text-align: center;
            color: white;
            margin-bottom: 2rem;
        }}
        .header h1 {{ font-size: 3rem; margin-bottom: 0.5rem; }}
        .header p {{ font-size: 1.2rem; opacity: 0.9; }}
        .topics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 1rem;
            margin-bottom: 2rem;
        }}
        .topic-card {{
            background: white;
            border-radius: 12px;
            padding: 1.5rem;
            text-decoration: none;
            color: #333;
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 0.5rem;
            transition: transform 0.2s, box-shadow 0.2s;
            border-left: 4px solid;
        }}
        .topic-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }}
        .topic-icon {{ font-size: 2.5rem; }}
        .topic-name {{ font-weight: 600; text-align: center; }}
        .legacy-section {{
            background: white;
            border-radius: 12px;
            padding: 1.5rem;
            margin-top: 2rem;
        }}
        .legacy-section h2 {{ color: #333; margin-bottom: 1rem; }}
        .file-link {{
            display: block;
            padding: 0.75rem 1rem;
            background: #f7fafc;
            color: #333;
            text-decoration: none;
            border-radius: 8px;
            margin-bottom: 0.5rem;
            transition: background 0.2s;
        }}
        .file-link:hover {{ background: #edf2f7; }}
        .footer {{
            text-align: center;
            color: white;
            margin-top: 2rem;
            opacity: 0.8;
        }}
        .stats {{
            display: flex;
            justify-content: center;
            gap: 2rem;
            margin: 1rem 0;
        }}
        .stat {{
            background: rgba(255,255,255,0.2);
            padding: 0.5rem 1rem;
            border-radius: 20px;
            color: white;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 DevOps Learning Hub</h1>
            <p>Personal knowledge base for DevOps, Cloud & Automation</p>
            <div class="stats">
                <span class="stat">📚 {len(topic_files)} Topics</span>
                <span class="stat">📅 Updated: {datetime.now().strftime("%Y-%m-%d")}</span>
            </div>
        </div>

        <div class="topics-grid">
{topic_cards}
        </div>

        <div class="legacy-section">
            <h2>📁 Original Notes</h2>
{existing_files}
        </div>

        <div class="footer">
            <p>Created by AbhisHub-12 | Powered by AI Learning Assistant</p>
        </div>
    </div>
</body>
</html>
'''

    with open(INDEX_FILE, 'w', encoding='utf-8') as f:
        f.write(index_content)


def git_commit_and_push(message: str) -> bool:
    """Commit changes and push to GitHub"""
    try:
        os.chdir(REPO_PATH)
        subprocess.run(['git', 'add', '-A'], check=True, capture_output=True)
        subprocess.run(['git', 'commit', '-m', message], check=True, capture_output=True)
        result = subprocess.run(['git', 'push'], capture_output=True, text=True)
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        return False


def list_topics():
    """List all available topics"""
    print("\n📚 Available DevOps Topics:\n")
    for key, info in DEVOPS_TOPICS.items():
        print(f"  {info['icon']} {key}: {info['name']}")
    print()


def search_notes(query: str):
    """Search all topic files for a term"""
    print(f"\n🔍 Searching for '{query}'...\n")

    matches = []
    search_files = list(REPO_PATH.glob("**/*.html"))

    for file_path in search_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            if query.lower() in content.lower():
                # Extract context
                clean = re.sub(r'<[^>]+>', '', content)
                idx = clean.lower().find(query.lower())
                if idx >= 0:
                    start = max(0, idx - 50)
                    end = min(len(clean), idx + len(query) + 100)
                    context = clean[start:end].strip()
                    matches.append((file_path.name, context))
        except:
            continue

    if matches:
        print(f"Found {len(matches)} matches:\n")
        for filename, context in matches[:10]:
            print(f"📄 {filename}")
            print(f"   ...{context}...")
            print()
    else:
        print("No matches found.")


def interactive_input() -> str:
    """Get multi-line input from user"""
    print("\n📝 Paste your content (press Ctrl+D or Ctrl+Z when done):\n")
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
        description='Smart Learning Assistant v2.0 - Unlimited File Size Support',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  learn2 -f file.pdf                    # Auto-detect topics
  learn2 -f file.pdf -t kubernetes      # Force add to kubernetes topic
  learn2 -f file.pdf -t "service mesh"  # Create new topic if not exists
  learn2 -i -t docker                   # Paste content, add to docker
        '''
    )

    parser.add_argument('content', nargs='?', help='Text content to add')
    parser.add_argument('-f', '--file', help='Path to file (PDF, txt, images, code - any size)')
    parser.add_argument('-t', '--topic', help='Specify topic name (matches existing or creates new)')
    parser.add_argument('-i', '--interactive', action='store_true', help='Interactive input')
    parser.add_argument('--list', action='store_true', help='List all topics')
    parser.add_argument('--search', help='Search existing notes')
    parser.add_argument('--no-push', action='store_true', help='Do not push to GitHub')
    parser.add_argument('--dry-run', action='store_true', help='Analyze only')

    args = parser.parse_args()

    if args.list:
        list_topics()
        return

    if args.search:
        search_notes(args.search)
        return

    # Get content
    content = None
    source = "direct input"

    if args.file:
        print(f"\n📄 Reading file: {args.file}")
        content, file_type = read_file_content(args.file)
        source = Path(args.file).name
        print(f"   ✅ Extracted {len(content):,} characters")
    elif args.interactive:
        content = interactive_input()
        source = "interactive"
    elif args.content:
        content = args.content
    else:
        parser.print_help()
        print("\n❌ Please provide content, file, or use -i for interactive mode")
        sys.exit(1)

    if not content or len(content.strip()) < 10:
        print("❌ Content too short")
        sys.exit(1)

    # Initialize OpenAI
    print(f"\n🤖 Initializing AI analysis...")
    client = get_openai_client()

    # Check if specific topic is specified
    if args.topic:
        print(f"\n🎯 Topic specified: {args.topic}")
        # Find matching topic or create new one
        topic_key = find_or_create_topic(args.topic)
        # Process content for this specific topic
        results = process_for_specific_topic(client, content, topic_key)
    else:
        # Auto-detect topics (original behavior)
        results = process_large_content(client, content)

    if args.dry_run:
        print("\n🔍 Dry run - results:")
        for topic, sections in results.items():
            if sections:
                topic_info = DEVOPS_TOPICS.get(topic, {"icon": "📚", "name": topic})
                print(f"\n  {topic_info['icon']} {topic}: {len(sections)} sections")
        return

    # Update topic files
    print(f"\n📝 Updating topic files...")
    updated_topics = []

    for topic, sections in results.items():
        if sections:
            topic_file = update_topic_file(topic, sections)
            updated_topics.append(topic)
            print(f"   ✅ Updated {topic}.html with {len(sections)} sections")

    # Update index
    print(f"📋 Updating index.html...")
    update_index_html()

    # Git commit and push
    topics_str = ", ".join(updated_topics)
    commit_msg = f"📚 Add learning content: {topics_str} (from {source})"

    if not args.no_push:
        print(f"\n📤 Pushing to GitHub...")
        if git_commit_and_push(commit_msg):
            print(f"\n✅ Successfully updated your learning repo!")
            print(f"   🌐 View at: https://abhishub-12.github.io/DevOps_learning/")
        else:
            print(f"\n⚠️ Saved locally. Manual push may be needed.")
    else:
        subprocess.run(['git', 'add', '-A'], cwd=REPO_PATH, capture_output=True)
        subprocess.run(['git', 'commit', '-m', commit_msg], cwd=REPO_PATH, capture_output=True)
        print(f"\n✅ Committed locally (--no-push specified)")


if __name__ == '__main__':
    main()
