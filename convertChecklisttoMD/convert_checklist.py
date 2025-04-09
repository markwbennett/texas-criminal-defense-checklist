#!/usr/bin/env python3

import sys
import os
from collections import OrderedDict
from datetime import datetime

def count_indent(line):
    # Count leading spaces, tabs, or dashes
    indent = 0
    for char in line:
        if char in [' ', '\t', '-']:
            indent += 1
        else:
            break
    return indent

def get_path_hierarchy(lines, current_index):
    path = []
    current_indent = count_indent(lines[current_index])
    current_line = lines[current_index].strip().lstrip(' \t-')
    
    # Walk backwards to build the path
    i = current_index
    while i >= 0:
        line = lines[i].strip()
        if not line:
            i -= 1
            continue
            
        indent = count_indent(lines[i])
        if indent < current_indent:
            content = line.lstrip(' \t-').strip()
            path.insert(0, content)
            current_indent = indent
        i -= 1
    
    return ' | '.join(path) if path else path[0] if path else current_line

def get_filename(path):
    # Convert path to a valid filename
    return path.lower().replace(' | ', '_').replace(' ', '_') + '.md'

def get_tags(path):
    # Generate tags from path
    tags = []
    parts = path.split(' | ')
    for i, part in enumerate(parts):
        tag = part.lower().replace(' ', '_')
        tags.append(f"#{tag}")
        if i > 0:
            tags.append(f"#{parts[i-1].lower().replace(' ', '_')}")
    return ' '.join(tags)

def convert_to_markdown(input_file, output_file):
    with open(input_file, 'r') as f:
        lines = f.readlines()
    
    # Create output directory
    output_dir = os.path.splitext(input_file)[0]
    os.makedirs(output_dir, exist_ok=True)
    
    # Group items by their path
    checklists = OrderedDict()
    top_level_items = []
    
    for i, line in enumerate(lines):
        if not line.strip():
            continue
            
        content = line.lstrip(' \t-').strip()
        indent = count_indent(line)
        
        if indent == 0:
            top_level_items.append(content)
            continue
        
        path = get_path_hierarchy(lines, i)
        if path:  # Only add if we have a path
            if path not in checklists:
                checklists[path] = []
            checklists[path].append(content)
    
    # Generate main index file
    index_content = []
    index_content.append("---")
    index_content.append("title: Projects")
    index_content.append("created: " + datetime.now().strftime("%Y-%m-%d"))
    index_content.append("tags: #projects")
    index_content.append("---")
    index_content.append("")
    index_content.append("## Projects")
    for item in top_level_items:
        filename = get_filename(item)
        index_content.append(f"- [ ] [[{item}|{filename}]]")
    
    with open(output_file, 'w') as f:
        f.write('\n'.join(index_content))
    
    # Generate projects.md in output directory
    projects_file = os.path.join(output_dir, 'projects.md')
    with open(projects_file, 'w') as f:
        f.write('\n'.join(index_content))
    
    # Generate individual checklist files
    for path, items in checklists.items():
        content = []
        content.append("---")
        content.append(f"title: {path}")
        content.append("created: " + datetime.now().strftime("%Y-%m-%d"))
        content.append(f"tags: {get_tags(path)}")
        content.append("---")
        content.append("")
        content.append(f"## {path}")
        
        # Add link back to parent
        parent_path = ' | '.join(path.split(' | ')[:-1]) if ' | ' in path else 'Projects'
        parent_file = get_filename(parent_path)
        content.append(f"← [[{parent_path}|{parent_file}]]")
        content.append("")
        
        # Add items with links to their sub-checklists
        for item in items:
            sub_path = f"{path} | {item}"
            if sub_path in checklists:
                filename = get_filename(sub_path)
                content.append(f"- [ ] [[{item}|{filename}]]")
            else:
                content.append(f"- [ ] {item}")
        
        # Write to file
        filename = os.path.join(output_dir, get_filename(path))
        with open(filename, 'w') as f:
            f.write('\n'.join(content))

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python convert_checklist.py input.txt output.md")
        sys.exit(1)
    
    convert_to_markdown(sys.argv[1], sys.argv[2]) 