#!/bin/bash
# Mirror Office/PDF files into OneDrive, preserving source directory structure.
# PostToolUse hook — runs after Write or Bash, never blocks, exits 0 always.
#
# Example: ~/.openclaw/workspace/projects/financial/docs/reports/report.xlsx
#       -> OneDrive-Personal/.openclaw/workspace/projects/financial/docs/reports/report.xlsx
#
# Write-tool calls only ever touch one file, so we mirror that exact path.
# Bash calls (python scripts writing xlsx/docx/pptx via xlsxwriter/python-pptx/etc)
# don't tell us which file changed, so we sweep for recently-modified Office/PDF
# files instead and mirror any that are newer than their OneDrive copy.

ONEDRIVE_ROOT=~/Library/CloudStorage/OneDrive-Personal
HOME_DIR=$(eval echo ~)
SCAN_ROOT="$HOME_DIR/.openclaw/workspace/projects"

mirror_one() {
  local file_path="$1"
  [[ -f "$file_path" ]] || return

  local ext="${file_path##*.}"
  local ext_lower
  ext_lower=$(echo "$ext" | tr '[:upper:]' '[:lower:]')
  case "$ext_lower" in
    xlsx|docx|pptx|pdf) ;;
    *) return ;;
  esac

  local rel_path
  if [[ "$file_path" == "$HOME_DIR/"* ]]; then
    rel_path="${file_path#$HOME_DIR/}"
  else
    rel_path="_external${file_path}"
  fi

  local dest_dir="$ONEDRIVE_ROOT/${rel_path%/*}"
  local dest="$dest_dir/${file_path##*/}"

  # Skip if OneDrive copy is already up to date.
  if [[ -f "$dest" && "$dest" -nt "$file_path" ]]; then
    return
  fi

  mkdir -p "$dest_dir" 2>/dev/null
  cp -p "$file_path" "$dest" 2>/dev/null
}

input=$(cat)
tool_name=$(echo "$input" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('tool_name',''))" 2>/dev/null)

case "$tool_name" in
  Write)
    file_path=$(echo "$input" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('tool_input',{}).get('file_path',''))" 2>/dev/null)
    [[ -n "$file_path" ]] && mirror_one "$file_path"
    ;;
  Bash)
    # Sweep for Office/PDF files modified in the last 5 minutes under known project roots.
    [[ -d "$SCAN_ROOT" ]] || exit 0
    while IFS= read -r -d '' f; do
      mirror_one "$f"
    done < <(find "$SCAN_ROOT" -type f \( -iname "*.xlsx" -o -iname "*.docx" -o -iname "*.pptx" -o -iname "*.pdf" \) -mmin -5 -print0 2>/dev/null)
    ;;
esac

exit 0
