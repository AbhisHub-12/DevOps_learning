#!/bin/bash
#
# Smart Learning Assistant v3.0 - Easy Runner
# Usage: ./run.sh [options]
#

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SCRIPT="$SCRIPT_DIR/smart_learn_v3.py"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# V3 Sections in DevOps_Notes.html
declare -a SECTIONS=("git-advanced" "github-actions" "linux" "cicd" "docker" "kubernetes" "ingress" "observability")
declare -a SECTION_NAMES=("Git & GitHub Advanced" "GitHub Actions" "Linux for DevOps" "CI/CD Pipelines" "Docker Deep Dive" "Kubernetes" "Ingress & Cert Manager" "Observability")

show_banner() {
    echo -e "${BLUE}"
    echo "╔═══════════════════════════════════════════════════════════╗"
    echo "║         🚀 Smart Learning Assistant v3.0                  ║"
    echo "║         Adds to DevOps_Notes.html sections                ║"
    echo "╚═══════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

show_menu() {
    echo -e "${GREEN}Choose an option:${NC}"
    echo ""
    echo "  1) 📄 Add from file (auto-detect section)"
    echo "  2) 📄 Add from file → specific section"
    echo "  3) 📋 Paste content (auto-detect section)"
    echo "  4) 📋 Paste content → specific section"
    echo "  5) 🔍 Search existing notes"
    echo "  6) 📚 List all sections"
    echo "  7) 🗑️  Remove content"
    echo "  8) 🧪 Dry run (preview without saving)"
    echo "  9) ❓ Help"
    echo "  0) 🚪 Exit"
    echo ""
}

select_section() {
    SELECTED_SECTION=""

    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${CYAN}📚 Select Section (from DevOps_Notes.html):${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

    count=1
    for i in "${!SECTIONS[@]}"; do
        echo -e "  ${GREEN}$count)${NC} ${SECTIONS[$i]} - ${SECTION_NAMES[$i]}"
        ((count++))
    done

    echo -e "  ${YELLOW}$count)${NC} ➕ Create NEW section"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo -e "${YELLOW}Enter number or type section name directly:${NC}"
    read -r selection

    if [[ "$selection" =~ ^[0-9]+$ ]]; then
        if [ "$selection" -eq "$count" ]; then
            echo -e "${YELLOW}Enter new section name (e.g., terraform, aws, ansible):${NC}"
            read -r SELECTED_SECTION
        elif [ "$selection" -ge 1 ] && [ "$selection" -lt "$count" ]; then
            SELECTED_SECTION="${SECTIONS[$((selection-1))]}"
        fi
    else
        SELECTED_SECTION="$selection"
    fi
}

add_file() {
    echo -e "${YELLOW}Enter file path (drag & drop works):${NC}"
    read -r filepath
    # Remove quotes if present (from drag & drop)
    filepath="${filepath%\'}"
    filepath="${filepath#\'}"
    filepath="${filepath%\"}"
    filepath="${filepath#\"}"
    # Remove trailing spaces
    filepath="${filepath%% }"

    if [ -f "$filepath" ]; then
        python3 "$PYTHON_SCRIPT" -f "$filepath"
    else
        echo -e "${RED}File not found: $filepath${NC}"
    fi
}

add_file_with_section() {
    echo -e "${YELLOW}Enter file path (drag & drop works):${NC}"
    read -r filepath
    # Remove quotes if present (from drag & drop)
    filepath="${filepath%\'}"
    filepath="${filepath#\'}"
    filepath="${filepath%\"}"
    filepath="${filepath#\"}"
    filepath="${filepath%% }"

    if [ ! -f "$filepath" ]; then
        echo -e "${RED}File not found: $filepath${NC}"
        return
    fi

    echo ""
    select_section

    if [ -n "$SELECTED_SECTION" ]; then
        echo ""
        echo -e "${GREEN}📁 Adding to section: $SELECTED_SECTION${NC}"
        python3 "$PYTHON_SCRIPT" -f "$filepath" -t "$SELECTED_SECTION"
    else
        echo -e "${RED}No section specified${NC}"
    fi
}

paste_content() {
    echo -e "${YELLOW}Paste your content (Ctrl+D when done):${NC}"
    python3 "$PYTHON_SCRIPT" -i
}

paste_content_with_section() {
    select_section

    if [ -n "$SELECTED_SECTION" ]; then
        echo ""
        echo -e "${GREEN}📁 Adding to section: $SELECTED_SECTION${NC}"
        echo -e "${YELLOW}Now paste your content (Ctrl+D when done):${NC}"
        python3 "$PYTHON_SCRIPT" -i -t "$SELECTED_SECTION"
    else
        echo -e "${RED}No section specified${NC}"
    fi
}

search_notes() {
    echo -e "${YELLOW}Enter search term:${NC}"
    read -r query
    if [ -n "$query" ]; then
        python3 "$PYTHON_SCRIPT" --search "$query"
    fi
}

list_sections() {
    python3 "$PYTHON_SCRIPT" --list
}

dry_run() {
    echo -e "${YELLOW}Choose input method:${NC}"
    echo "  1) File (auto-detect)"
    echo "  2) File → specific section"
    echo "  3) Paste (auto-detect)"
    echo "  4) Paste → specific section"
    read -r method

    case $method in
        1)
            echo -e "${YELLOW}Enter file path:${NC}"
            read -r filepath
            filepath="${filepath%\'}"
            filepath="${filepath#\'}"
            filepath="${filepath%\"}"
            filepath="${filepath#\"}"
            if [ -f "$filepath" ]; then
                python3 "$PYTHON_SCRIPT" --dry-run -f "$filepath"
            else
                echo -e "${RED}File not found${NC}"
            fi
            ;;
        2)
            echo -e "${YELLOW}Enter file path:${NC}"
            read -r filepath
            filepath="${filepath%\'}"
            filepath="${filepath#\'}"
            filepath="${filepath%\"}"
            filepath="${filepath#\"}"
            if [ -f "$filepath" ]; then
                select_section
                if [ -n "$SELECTED_SECTION" ]; then
                    python3 "$PYTHON_SCRIPT" --dry-run -f "$filepath" -t "$SELECTED_SECTION"
                fi
            else
                echo -e "${RED}File not found${NC}"
            fi
            ;;
        3)
            echo -e "${YELLOW}Paste content (Ctrl+D when done):${NC}"
            content=$(cat)
            if [ -n "$content" ]; then
                echo "$content" | python3 "$PYTHON_SCRIPT" --dry-run -i
            fi
            ;;
        4)
            select_section
            if [ -n "$SELECTED_SECTION" ]; then
                echo -e "${YELLOW}Paste content (Ctrl+D when done):${NC}"
                content=$(cat)
                if [ -n "$content" ]; then
                    echo "$content" | python3 "$PYTHON_SCRIPT" --dry-run -i -t "$SELECTED_SECTION"
                fi
            fi
            ;;
        *)
            echo -e "${RED}Invalid option${NC}"
            ;;
    esac
}

show_help() {
    python3 "$PYTHON_SCRIPT" --help
    echo ""
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}Quick Commands:${NC}"
    echo ""
    echo -e "  ${CYAN}Auto-detect section:${NC}"
    echo "    learn3 -f /path/to/file.pdf"
    echo "    learn3 -i"
    echo ""
    echo -e "  ${CYAN}Specify section:${NC}"
    echo "    learn3 -f file.pdf -t kubernetes"
    echo "    learn3 -f file.pdf -t docker"
    echo "    learn3 -f file.pdf -t git-advanced"
    echo ""
    echo -e "  ${CYAN}Available sections:${NC}"
    echo "    git-advanced, github-actions, linux, cicd"
    echo "    docker, kubernetes, ingress, observability"
    echo ""
    echo -e "  ${CYAN}Other:${NC}"
    echo "    learn3 --list                    - List all sections"
    echo "    learn3 --search \"keyword\"        - Search notes"
    echo "    learn3 --dry-run -f file.pdf     - Preview"
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

remove_content() {
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${RED}🗑️  Remove Content${NC}"
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo -e "${YELLOW}Paste the content you want to remove (Ctrl+D when done):${NC}"
    echo -e "${CYAN}(Paste a unique portion of text - like a heading or code block)${NC}"
    echo ""

    content_to_remove=$(cat)

    if [ -n "$content_to_remove" ]; then
        echo ""
        echo -e "${YELLOW}Preview what will be removed...${NC}"
        python3 "$PYTHON_SCRIPT" --remove --dry-run <<< "$content_to_remove"

        echo ""
        echo -e "${RED}Are you sure you want to remove this content? (y/n):${NC}"
        read -r confirm

        if [ "$confirm" = "y" ] || [ "$confirm" = "Y" ]; then
            python3 "$PYTHON_SCRIPT" --remove <<< "$content_to_remove"
        else
            echo -e "${YELLOW}Cancelled.${NC}"
        fi
    else
        echo -e "${RED}No content provided${NC}"
    fi
}

# Check for command line arguments
if [ $# -gt 0 ]; then
    # Pass all arguments to Python script
    python3 "$PYTHON_SCRIPT" "$@"
    exit $?
fi

# Interactive mode
show_banner

while true; do
    show_menu
    echo -e "${BLUE}Enter choice [0-9]:${NC} "
    read -r choice
    echo ""

    case $choice in
        1) add_file ;;
        2) add_file_with_section ;;
        3) paste_content ;;
        4) paste_content_with_section ;;
        5) search_notes ;;
        6) list_sections ;;
        7) remove_content ;;
        8) dry_run ;;
        9) show_help ;;
        0) echo -e "${GREEN}Goodbye! Happy Learning! 🎓${NC}"; exit 0 ;;
        *) echo -e "${RED}Invalid option. Please try again.${NC}" ;;
    esac

    echo ""
    echo -e "${YELLOW}Press Enter to continue...${NC}"
    read -r
    clear
    show_banner
done
