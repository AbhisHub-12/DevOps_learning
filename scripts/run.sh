#!/bin/bash
#
# Smart Learning Assistant v2.0 - Easy Runner
# Usage: ./run.sh [options]
#

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SCRIPT="$SCRIPT_DIR/smart_learn.py"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

show_banner() {
    echo -e "${BLUE}"
    echo "╔═══════════════════════════════════════════════════════════╗"
    echo "║         🚀 Smart Learning Assistant v2.0                  ║"
    echo "║         Add knowledge to your DevOps repo easily          ║"
    echo "╚═══════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

show_menu() {
    echo -e "${GREEN}Choose an option:${NC}"
    echo ""
    echo "  1) 📄 Add from file (auto-detect topics)"
    echo "  2) 📄 Add from file → specific topic"
    echo "  3) 📋 Paste content (auto-detect topics)"
    echo "  4) 📋 Paste content → specific topic"
    echo "  5) 🔍 Search existing notes"
    echo "  6) 📚 List all topics"
    echo "  7) 🧪 Dry run (preview without saving)"
    echo "  8) ❓ Help"
    echo "  9) 🚪 Exit"
    echo ""
}

select_topic() {
    # This function sets the global SELECTED_TOPIC variable
    SELECTED_TOPIC=""

    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${CYAN}📚 Select Topic:${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

    # Check if topics directory exists and has files
    TOPICS_DIR="$SCRIPT_DIR/../topics"
    declare -a topic_list=()

    if [ -d "$TOPICS_DIR" ] && [ "$(ls -A "$TOPICS_DIR" 2>/dev/null)" ]; then
        count=1
        for file in "$TOPICS_DIR"/*.html; do
            if [ -f "$file" ]; then
                topic_name=$(basename "$file" .html)
                topic_list+=("$topic_name")
                echo -e "  ${GREEN}$count)${NC} $topic_name"
                ((count++))
            fi
        done
        echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo -e "  ${YELLOW}$count)${NC} ➕ Create NEW topic"
        echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo ""
        echo -e "${YELLOW}Enter number or type topic name directly:${NC}"
        read -r selection

        if [[ "$selection" =~ ^[0-9]+$ ]]; then
            if [ "$selection" -eq "$count" ]; then
                echo -e "${YELLOW}Enter new topic name:${NC}"
                read -r SELECTED_TOPIC
            elif [ "$selection" -ge 1 ] && [ "$selection" -lt "$count" ]; then
                SELECTED_TOPIC="${topic_list[$((selection-1))]}"
            fi
        else
            SELECTED_TOPIC="$selection"
        fi
    else
        echo -e "  ${YELLOW}No topics created yet. Common topics:${NC}"
        echo ""
        echo "  1) docker          2) kubernetes       3) terraform"
        echo "  4) aws             5) linux            6) git"
        echo "  7) jenkins         8) ansible          9) helm"
        echo "  10) prometheus     11) argocd          12) ➕ NEW topic"
        echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

        declare -a defaults=("docker" "kubernetes" "terraform" "aws" "linux" "git" "jenkins" "ansible" "helm" "prometheus" "argocd")

        echo ""
        echo -e "${YELLOW}Enter number or type topic name directly:${NC}"
        read -r selection

        if [[ "$selection" =~ ^[0-9]+$ ]]; then
            if [ "$selection" -eq 12 ]; then
                echo -e "${YELLOW}Enter new topic name:${NC}"
                read -r SELECTED_TOPIC
            elif [ "$selection" -ge 1 ] && [ "$selection" -le 11 ]; then
                SELECTED_TOPIC="${defaults[$((selection-1))]}"
            fi
        else
            SELECTED_TOPIC="$selection"
        fi
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

add_file_with_topic() {
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
    select_topic

    if [ -n "$SELECTED_TOPIC" ]; then
        echo ""
        echo -e "${GREEN}📁 Adding to topic: $SELECTED_TOPIC${NC}"
        python3 "$PYTHON_SCRIPT" -f "$filepath" -t "$SELECTED_TOPIC"
    else
        echo -e "${RED}No topic specified${NC}"
    fi
}

paste_content() {
    python3 "$PYTHON_SCRIPT" -i
}

paste_content_with_topic() {
    select_topic

    if [ -n "$SELECTED_TOPIC" ]; then
        echo ""
        echo -e "${GREEN}📁 Adding to topic: $SELECTED_TOPIC${NC}"
        echo -e "${YELLOW}Now paste your content (Ctrl+D when done):${NC}"
        python3 "$PYTHON_SCRIPT" -i -t "$SELECTED_TOPIC"
    else
        echo -e "${RED}No topic specified${NC}"
    fi
}

search_notes() {
    echo -e "${YELLOW}Enter search term:${NC}"
    read -r query
    if [ -n "$query" ]; then
        python3 "$PYTHON_SCRIPT" --search "$query"
    fi
}

list_topics() {
    python3 "$PYTHON_SCRIPT" --list
}

dry_run() {
    echo -e "${YELLOW}Choose input method:${NC}"
    echo "  1) File (auto-detect)"
    echo "  2) File → specific topic"
    echo "  3) Paste (auto-detect)"
    echo "  4) Paste → specific topic"
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
                select_topic
                if [ -n "$SELECTED_TOPIC" ]; then
                    python3 "$PYTHON_SCRIPT" --dry-run -f "$filepath" -t "$SELECTED_TOPIC"
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
            select_topic
            if [ -n "$SELECTED_TOPIC" ]; then
                echo -e "${YELLOW}Paste content (Ctrl+D when done):${NC}"
                content=$(cat)
                if [ -n "$content" ]; then
                    echo "$content" | python3 "$PYTHON_SCRIPT" --dry-run -i -t "$SELECTED_TOPIC"
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
    echo -e "  ${CYAN}Auto-detect topics:${NC}"
    echo "    learn2 -f /path/to/file.pdf"
    echo "    learn2 -i"
    echo ""
    echo -e "  ${CYAN}Specify topic (existing):${NC}"
    echo "    learn2 -f file.pdf -t kubernetes"
    echo "    learn2 -f file.pdf -t docker"
    echo ""
    echo -e "  ${CYAN}Create new topic:${NC}"
    echo "    learn2 -f file.pdf -t \"service-mesh\""
    echo "    learn2 -f file.pdf -t \"my-custom-notes\""
    echo ""
    echo -e "  ${CYAN}Other:${NC}"
    echo "    learn2 --list                    - List all topics"
    echo "    learn2 --search \"keyword\"        - Search notes"
    echo "    learn2 --dry-run -f file.pdf     - Preview"
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
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
    echo -e "${BLUE}Enter choice [1-9]:${NC} "
    read -r choice
    echo ""

    case $choice in
        1) add_file ;;
        2) add_file_with_topic ;;
        3) paste_content ;;
        4) paste_content_with_topic ;;
        5) search_notes ;;
        6) list_topics ;;
        7) dry_run ;;
        8) show_help ;;
        9) echo -e "${GREEN}Goodbye! Happy Learning! 🎓${NC}"; exit 0 ;;
        *) echo -e "${RED}Invalid option. Please try again.${NC}" ;;
    esac

    echo ""
    echo -e "${YELLOW}Press Enter to continue...${NC}"
    read -r
    clear
    show_banner
done
