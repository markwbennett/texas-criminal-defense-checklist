#!/usr/bin/env python3

import sys
import os
from collections import OrderedDict
from datetime import datetime
import re
from weasyprint import HTML, CSS
from bs4 import BeautifulSoup
import markdown

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

def get_items_at_level(lines, start_index, target_indent, max_indent=None):
    """Get all items at a specific indent level until we hit an item with less/more indent."""
    items = []
    i = start_index
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
            continue
        
        indent = count_indent(line)
        content = line.lstrip(' \t-').strip()
        
        if indent < target_indent:
            break
        elif max_indent is not None and indent > max_indent:
            i += 1
            continue
        elif indent == target_indent:
            items.append((content, i))
        i += 1
    return items

def generate_anchor_id(text):
    """Generate a consistent anchor ID from text."""
    return re.sub(r'[^a-zA-Z0-9]+', '-', text.lower()).strip('-')

def process_level(lines, start_index, current_indent, hierarchy=None):
    """Process each level of the checklist."""
    if hierarchy is None:
        hierarchy = []
        
    content = []
    items = get_items_at_level(lines, start_index, current_indent)
    
    if not items:
        return content
    
    # Create checklist header
    if not hierarchy:
        content.append("# Main Checklist")
        content.append("<a id='level-1'></a>")
    else:
        # Create title for sub-pages
        current_id = generate_anchor_id('level-1-' + hierarchy[-1].lower().replace(' ', '-'))
        parent_item_id = generate_anchor_id('item-' + hierarchy[-1].lower().replace(' ', '-'))
        content.append(f"<a id='{current_id}'></a>")
        content.append(f"# [Main Checklist](#{parent_item_id}) | {hierarchy[-1]}")
    
    # Add items to the current checklist
    for item, _ in items:
        if not hierarchy:
            item_id = generate_anchor_id('item-' + item.lower().replace(' ', '-'))
            sub_list_id = generate_anchor_id(f"level-1-{item.lower().replace(' ', '-')}")
            content.append(f"<a id='{item_id}'></a>")
            content.append(f"☐ [{item}](#{sub_list_id})\n")
        else:
            content.append(f"☐ {item}\n")
    
    # Only add page break if there are items
    if items:
        content.append("\n\\newpage\n")
    
    # Process each item's children
    for item, idx in items:
        child_items = get_items_at_level(lines, idx + 1, current_indent + 1)
        if child_items:
            if not hierarchy:
                new_hierarchy = [item]
                new_id = generate_anchor_id(f"level-1-{item.lower().replace(' ', '-')}")
                item_id = generate_anchor_id('item-' + item.lower().replace(' ', '-'))
                content.append(f"<a id='{new_id}'></a>")
                content.append(f"# [Main Checklist](#{item_id}) | {item}")
                for child, _ in child_items:
                    content.append(f"☐ {child}\n")
                content.append("\n\\newpage\n")
                
                # Process Level 3 items
                for child, child_idx in child_items:
                    grandchild_items = get_items_at_level(lines, child_idx + 1, current_indent + 2)
                    if grandchild_items:
                        child_id = generate_anchor_id(f"level-1-{item.lower().replace(' ', '-')}-{child.lower().replace(' ', '-')}")
                        content.append(f"<a id='{child_id}'></a>")
                        content.append(f"# [Main Checklist](#{item_id}) | [{item}](#{new_id}) | {child}")
                        for grandchild, _ in grandchild_items:
                            content.append(f"☐ {grandchild}\n")
                        content.append("\n\\newpage\n")
    
    return content

def process_children(lines, start_index, indent_level, hierarchy):
    """Process children of a specific item."""
    content = []
    items = get_items_at_level(lines, start_index, indent_level, indent_level)
    
    if items:
        # Create title with links to parent items
        parts = []
        current_path = []
        for part in hierarchy[:-1]:  # All but the last part
            current_path.append(part)
            anchor = generate_anchor_id(' | '.join(current_path))
            parts.append(f"[{part}](#{anchor})")
        parts.append(hierarchy[-1])  # Last part without link
        title = " | ".join(parts)
        content.append(f"# {title}")
        
        for item, _ in items:
            content.append(f"- [ ] {item}")
        content.append("\n\\newpage\n")
    
    return content

def process_markdown_to_pdf(md_file):
    """Convert markdown to HTML with anchors and internal links."""
    with open(md_file, 'r') as f:
        md_content = f.read()
    
    # Split content into pages based on \newpage
    pages = md_content.split('\\newpage')
    
    # Track all checklists for linking
    checklists = {}  # breadcrumb -> (page_number, item_id)
    current_page = 1
    processed_pages = []
    
    for page in pages:
        if not page.strip():
            continue
            
        # Parse the page with markdown extensions
        html = markdown.markdown(page, extensions=['extra'])
        soup = BeautifulSoup(html, 'html.parser')
        
        # Add page anchor
        page_div = soup.new_tag('div')
        page_div['id'] = f'page{current_page}'
        page_div['class'] = 'page'
        for tag in soup.contents:
            page_div.append(tag.extract())
        soup.append(page_div)
        
        processed_pages.append(str(soup))
        current_page += 1
    
    # Combine pages with CSS for page breaks and link styling
    html_content = """
    <html>
    <head>
        <style>
            .page { page-break-after: always; }
            body { 
                font-family: Arial, sans-serif;
                font-size: 14pt;
            }
            h1 { 
                color: #2c3e50;
                font-weight: bold;
                font-size: 14pt;
            }
            h1 a { 
                color: #2c3e50; 
                text-decoration: underline;
                font-weight: bold;
            }
            a { 
                color: #2c3e50; 
                text-decoration: underline;
            }
            a:hover {
                text-decoration: underline;
            }
        </style>
    </head>
    <body>
    """ + "\n".join(processed_pages) + "</body></html>"
    
    return html_content

def convert_to_pdf(md_file):
    """Convert markdown file to PDF."""
    html_content = process_markdown_to_pdf(md_file)
    pdf_file = os.path.splitext(md_file)[0] + ".pdf"
    
    # Create PDF
    HTML(string=html_content).write_pdf(
        pdf_file,
        stylesheets=[CSS(string='@page { size: letter; margin: 1in; }')]
    )

def convert_to_markdown(input_file, output_file):
    with open(input_file, 'r') as f:
        lines = f.readlines()
    
    # Create output directory
    output_dir = os.path.splitext(input_file)[0]
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate content
    index_content = []
    index_content.append("---")
    index_content.append("title: Criminal Defense Checklist")
    index_content.append("created: " + datetime.now().strftime("%Y-%m-%d"))
    index_content.append("---")
    index_content.append("")
    
    # Process all levels
    content = process_level(lines, 0, 0)
    index_content.extend(content)
    
    # Write the output file
    with open(output_file, 'w') as f:
        f.write('\n'.join(index_content))
    
    # Convert to PDF
    convert_to_pdf(output_file)

if __name__ == "__main__":
    default_input = "CriminalDefenseChecklist.txt"
    
    if len(sys.argv) == 2:
        input_file = sys.argv[1]
        output_file = os.path.splitext(input_file)[0] + ".md"
    elif len(sys.argv) == 3:
        input_file = sys.argv[1]
        output_file = sys.argv[2]
    else:
        input_file = default_input
        output_file = os.path.splitext(default_input)[0] + ".md"
    
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' not found.")
        sys.exit(1)
    
    convert_to_markdown(input_file, output_file) 