# DevOps Learning Notes

A personal knowledge base for DevOps, Cloud, and Automation - powered by AI.

[![GitHub Pages](https://img.shields.io/badge/View-GitHub%20Pages-blue?style=for-the-badge&logo=github)](https://abhishub-12.github.io/DevOps_learning/)

## Features

- **AI-Powered Analysis**: Automatically extracts key points, code examples, and best practices
- **Smart Topic Detection**: Analyzes content and adds to the appropriate section
- **Unlimited File Size**: Handles large PDFs, documents, and code files
- **Image Support**: Extracts text from screenshots and diagrams using AI vision
- **Git Integration**: Auto-commits and pushes changes to GitHub

## Repository Structure

```
DevOps_learning/
├── index.html                 # Main landing page
├── DevOps_Notes.html          # All notes organized by topic sections
├── Devops_flow_chart.html     # DevOps flow visualization
├── scripts/
│   ├── smart_learn.py         # V2 - Creates separate topic files
│   ├── smart_learn_v3.py      # V3 - Adds to DevOps_Notes.html (Recommended)
│   ├── run.sh                 # Interactive menu
│   └── requirements.txt       # Python dependencies
└── README.md
```

## Quick Start

### Prerequisites

- Python 3.8+
- OpenAI API key

### Installation

```bash
# Clone the repository
git clone https://github.com/AbhisHub-12/DevOps_learning.git
cd DevOps_learning

# Install dependencies
pip3 install -r scripts/requirements.txt

# Make scripts executable
chmod +x scripts/run.sh scripts/smart_learn.py scripts/smart_learn_v3.py

# Add alias to your shell (recommended)
echo 'alias learn="python3 ~/DevOps_learning/scripts/smart_learn_v3.py"' >> ~/.zshrc
source ~/.zshrc
```

## Usage

### Method 1: Interactive Menu

```bash
./scripts/run.sh
```

### Method 2: Command Line

```bash
# Add from a PDF file
learn -f ~/Downloads/kubernetes-guide.pdf

# Add to a specific section
learn -f ~/Downloads/docker-notes.pdf -t docker

# Interactive paste mode
learn -i

# Search your notes
learn --search "deployment"

# List all sections
learn --list

# Preview without saving
learn --dry-run -f ~/Downloads/file.pdf
```

### Method 3: Direct Script

```bash
python3 ~/DevOps_learning/scripts/smart_learn_v3.py -f /path/to/file.pdf
```

## Supported Sections

Content is automatically categorized into these sections in DevOps_Notes.html:

| Section | Description |
|---------|-------------|
| git-advanced | Git & GitHub Advanced |
| github-actions | GitHub Actions & Workflows |
| linux | Linux for DevOps |
| cicd | CI/CD Pipelines |
| docker | Docker Deep Dive |
| kubernetes | Kubernetes Orchestration |
| ingress | Ingress & Cert Manager |
| observability | Observability & Monitoring |

## Supported File Types

| Type | Extensions |
|------|------------|
| PDF | `.pdf` |
| Text | `.txt`, `.md` |
| Code | `.py`, `.sh`, `.yaml`, `.json`, `.js`, `.go` |
| Images | `.png`, `.jpg`, `.jpeg`, `.gif`, `.webp` |

## View Your Notes

Visit: **https://abhishub-12.github.io/DevOps_learning/**

---

**Created by AbhisHub-12** | Powered by OpenAI GPT-4
