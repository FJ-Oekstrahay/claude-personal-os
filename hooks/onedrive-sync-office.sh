#!/bin/bash
# Copy Office/PDF files to OneDrive, mirroring the source directory structure.
# PostToolUse hook — runs after Write, never blocks, exits 0 always.
#
# Example: ~/foo/projects/financial/docs/reports/report.xlsx
#       -> OneDrive-Personal/foo/projects/financial/docs/reports/report-2026-06-29.xlsx

ONEDRIVE_ROOT=~/Library/CloudStorage/OneDrive-Personal
HOME_DIR=$(eval echo ~)

input=$(cat)
tool_name=$(echo "$input" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('tool_name',''))" 2>/dev/null)

if [[ "$tool_name" != "Write" ]]; then
  exit 0
fi

file_path=$(echo "$input" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('tool_input',{}).get('file_path',''))" 2>/dev/null)

if [[ -z "$file_path" ]]; then
  exit 0
fi

ext="${file_path##*.}"
ext_lower=$(echo "$ext" | tr '[:upper:]' '[:lower:]')

case "$ext_lower" in
  xlsx|docx|pptx|pdf) ;;
  *) exit 0 ;;
esac

if [[ ! -f "$file_path" ]]; then
  exit 0
fi

# Compute destination: mirror path relative to home dir
if [[ "$file_path" == "$HOME_DIR/"* ]]; then
  rel_path="${file_path#$HOME_DIR/}"
else
  # File outside home — put it under an _external/ prefix
  rel_path="_external${file_path}"
fi

dir_part="${rel_path%/*}"
basename="${file_path##*/}"
stem="${basename%.*}"
datestamp=$(date +%Y-%m-%d)

dest_dir="$ONEDRIVE_ROOT/$dir_part"
dest="$dest_dir/${stem}-${datestamp}.${ext_lower}"

mkdir -p "$dest_dir" 2>/dev/null
cp "$file_path" "$dest" 2>/dev/null

exit 0
