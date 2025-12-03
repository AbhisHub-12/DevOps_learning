# 🚀 DevOps Learning Hub

A personal knowledge base for DevOps, Cloud, and Automation - powered by AI.

[![GitHub Pages](https://img.shields.io/badge/View-GitHub%20Pages-blue?style=for-the-badge&logo=github)](https://abhishub-12.github.io/DevOps_learning/)

## ✨ Features

- **AI-Powered Analysis**: Automatically extracts key points, code examples, and best practices
- **Multi-Topic Detection**: Analyzes content and splits into relevant topic categories
- **Unlimited File Size**: Handles large PDFs, documents, and code files
- **Auto-Organization**: Creates separate topic files and updates the index automatically
- **Image Support**: Extracts text from screenshots and diagrams using AI vision
- **Git Integration**: Auto-commits and pushes changes to GitHub

## 📁 Repository Structure

```
DevOps_learning/
├── index.html                 # Main hub with topic cards
├── topics/                    # Auto-generated topic files
│   ├── docker.html
│   ├── kubernetes.html
│   ├── terraform.html
│   ├── aws.html
│   └── ...
├── DevOps_Notes.html          # Original comprehensive notes
├── Devops_flow_chart.html     # DevOps flow visualization
├── scripts/
│   ├── smart_learn.py         # Main AI learning script
│   ├── run.sh                 # Easy runner script
│   └── requirements.txt       # Python dependencies
└── README.md
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- OpenAI API key (configured in config.yaml)

### Installation

```bash
# Clone the repository
git clone https://github.com/AbhisHub-12/DevOps_learning.git
cd DevOps_learning

# Install dependencies
pip3 install -r scripts/requirements.txt

# Make scripts executable
chmod +x scripts/run.sh scripts/smart_learn.py

# Add alias to your shell (optional but recommended)
echo 'alias learn="python3 ~/DevOps_learning/scripts/smart_learn.py"' >> ~/.zshrc
source ~/.zshrc
```

## 📖 Usage

### Method 1: Interactive Menu (Easiest)

```bash
./scripts/run.sh
```

This opens an interactive menu:
```
╔═══════════════════════════════════════════════════════════╗
║         🚀 Smart Learning Assistant v2.0                  ║
╚═══════════════════════════════════════════════════════════╝

Choose an option:

  1) 📝 Add text content
  2) 📄 Add from file (PDF, txt, code, image)
  3) 📋 Paste multi-line content
  4) 🔍 Search existing notes
  5) 📚 List all topics
  6) 🧪 Dry run (preview without saving)
  7) ❓ Help
  8) 🚪 Exit
```

### Method 2: Command Line (Quick)

```bash
# Add text directly
learn "Kubernetes uses pods as the smallest deployable unit"

# Add from a PDF file (any size)
learn -f ~/Downloads/docker-guide.pdf

# Add from an image/screenshot
learn -f ~/Desktop/architecture-diagram.png

# Add from any text file
learn -f ~/notes/terraform-notes.txt

# Interactive paste mode (for multi-line content)
learn -i

# Search your notes
learn --search "deployment"

# List all available topics
learn --list

# Preview without saving (dry run)
learn --dry-run "your content here"
learn --dry-run -f ~/Downloads/large-file.pdf
```

### Method 3: Direct Script

```bash
python3 ~/DevOps_learning/scripts/smart_learn.py "your content"
python3 ~/DevOps_learning/scripts/smart_learn.py -f /path/to/file.pdf
```

## 📚 Supported Topics

The AI automatically categorizes content into these topics:

| Icon | Topic | Description |
|------|-------|-------------|
| 🔀 | git | Git & GitHub |
| ⚡ | github-actions | GitHub Actions & Workflows |
| 🐧 | linux | Linux Administration |
| 🐳 | docker | Docker & Containerization |
| ☸️ | kubernetes | Kubernetes Orchestration |
| 🏗️ | terraform | Terraform & IaC |
| 🔧 | ansible | Ansible & Config Management |
| 🔨 | jenkins | Jenkins CI/CD |
| 🔄 | cicd | CI/CD Pipelines |
| ☁️ | aws | AWS Cloud Services |
| 🌐 | azure | Azure Cloud |
| 🌩️ | gcp | Google Cloud Platform |
| 📊 | monitoring | Monitoring & Observability |
| 📈 | prometheus | Prometheus & Grafana |
| 🔐 | security | DevSecOps & Security |
| 🌐 | networking | Networking & DNS |
| ⎈ | helm | Helm Charts |
| 🔶 | argocd | ArgoCD & GitOps |
| 📜 | scripting | Shell Scripting |
| 🐍 | python | Python for DevOps |
| 📝 | yaml | YAML & Configuration |
| 🌐 | nginx | Nginx & Web Servers |
| 🗄️ | databases | Databases |
| 📚 | misc | Miscellaneous |

## 📄 Supported File Types

| Type | Extensions | Notes |
|------|------------|-------|
| PDF | `.pdf` | Any size, multi-page support |
| Text | `.txt`, `.md` | Plain text files |
| Code | `.py`, `.sh`, `.yaml`, `.json`, `.js`, `.go` | Code files |
| Images | `.png`, `.jpg`, `.jpeg`, `.gif`, `.webp` | Uses AI vision to extract text |

## 🔧 Configuration

The script uses the OpenAI API key from:
```
/Users/abhishtbagewadi/Documents/Scripts/RCA-SCRIPT-2/abhisht_script_github_ready/config/config.yaml
```

Config structure:
```yaml
openai:
  api_key: "your-api-key-here"
  model: "gpt-4o-2024-11-20"
```

## 🎯 Examples

### Example 1: Add from a Kubernetes book PDF

```bash
learn -f ~/Downloads/kubernetes-in-action.pdf
```

Output:
```
📄 Reading file: kubernetes-in-action.pdf
   📁 File size: 15.32 MB
   📄 Processing 450 pages...
   ✅ Extracted 2,500,000 characters

🤖 Initializing AI analysis...
📊 Content size: 2,500,000 characters
🔍 Detecting topics...
   Found topics: kubernetes, docker, helm, networking
📦 Split into 420 chunks

🔄 Processing for Kubernetes...
   ✅ Found 85 relevant sections for Kubernetes

📝 Updating topic files...
   📁 Created new topic file: kubernetes.html
   ✅ Updated kubernetes.html with 85 sections

📤 Pushing to GitHub...
✅ Successfully updated your learning repo!
   🌐 View at: https://abhishub-12.github.io/DevOps_learning/
```

### Example 2: Add from a screenshot

```bash
learn -f ~/Desktop/aws-architecture.png
```

The AI will analyze the image, extract all text and diagram information, and add it to your notes.

### Example 3: Quick text addition

```bash
learn "Docker Compose uses a YAML file to define multi-container applications. Use 'docker-compose up -d' to start services in detached mode."
```

## 🌐 View Your Notes

Visit: **https://abhishub-12.github.io/DevOps_learning/**

The site features:
- Topic cards with icons
- Searchable content
- Code syntax highlighting
- Responsive design

## 🤝 Contributing

Feel free to fork and customize for your own learning journey!

## 📝 License

MIT License - Feel free to use and modify.

---

**Created by AbhisHub-12** | Powered by OpenAI GPT-4
