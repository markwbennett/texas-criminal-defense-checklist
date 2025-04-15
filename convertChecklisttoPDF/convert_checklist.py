#!/usr/bin/env python3

"""
Texas Criminal Defense Checklist Converter

This script converts a hierarchical text-based checklist into a structured markdown document
and then generates a PDF with proper formatting, navigation, and page breaks.

The script processes a text file containing a hierarchical checklist with indentation-based
structure and converts it into a well-formatted PDF document with:
- Proper hierarchical navigation
- Internal links between sections
- Page breaks between major sections
- Consistent styling and formatting

The input file should be a text file with indentation-based hierarchy (using spaces, tabs, or dashes).
The script will generate both a markdown file and a PDF file with the same base name.

Usage:
    python convert_checklist.py [input_file] [output_file]
    
    If no arguments are provided, it defaults to:
    - Input: CriminalDefenseChecklist.txt
    - Output: CriminalDefenseChecklist.md (and .pdf)
"""

import sys
import os
from collections import OrderedDict
from datetime import datetime
import re
from weasyprint import HTML, CSS
from bs4 import BeautifulSoup
import markdown

def count_indent(line):
    """
    Count the indentation level of a line by counting leading spaces, tabs, or dashes.
    
    This function is used to determine the hierarchy level of items in the checklist.
    It counts consecutive spaces, tabs, or dashes at the beginning of a line.
    
    Args:
        line (str): The line to count indentation for
        
    Returns:
        int: The number of indentation characters at the start of the line
    """
    # Count leading spaces, tabs, or dashes
    indent = 0
    for char in line:
        if char in [' ', '\t', '-']:
            indent += 1
        else:
            break
    return indent

def is_comment_or_command(line):
    """
    Check if a line is a comment or command (starts with #).
    
    Args:
        line (str): The line to check
        
    Returns:
        bool: True if the line is a comment or command, False otherwise
    """
    stripped = line.strip()
    return stripped.startswith('#')

def is_end_command(line):
    """
    Check if a line is the #end command.
    
    Args:
        line (str): The line to check
        
    Returns:
        bool: True if the line is the #end command, False otherwise
    """
    stripped = line.strip().lower()
    return stripped == '#end'

def get_path_hierarchy(lines, current_index):
    """
    Build the full path hierarchy for a given line by walking backwards through the file.
    
    This function determines the complete path to an item by looking at all parent items
    based on indentation levels. It's used to create breadcrumb navigation and section titles.
    
    Args:
        lines (list): All lines from the input file
        current_index (int): Index of the current line to build path for
        
    Returns:
        str: The full path hierarchy joined by ' | ' or just the current line if no parents
    """
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
    """
    Convert a path hierarchy into a valid filename.
    
    This function takes a path hierarchy (with ' | ' separators) and converts it to a
    valid filename by replacing spaces and separators with underscores and converting to lowercase.
    
    Args:
        path (str): The path hierarchy to convert
        
    Returns:
        str: A valid filename with .md extension
    """
    # Convert path to a valid filename
    return path.lower().replace(' | ', '_').replace(' ', '_') + '.md'

def get_tags(path):
    """
    Generate hashtag tags from a path hierarchy.
    
    This function creates hashtag tags for each level in the path hierarchy,
    including parent-child relationships for better organization and searching.
    
    Args:
        path (str): The path hierarchy to generate tags from
        
    Returns:
        str: Space-separated hashtag tags
    """
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
    """
    Get all items at a specific indent level until we hit an item with less/more indent.
    
    This function extracts all items at a specific indentation level, which is used
    to process the checklist hierarchy level by level.
    
    Args:
        lines (list): All lines from the input file
        start_index (int): Index to start searching from
        target_indent (int): The indentation level to find items for
        max_indent (int, optional): Maximum indentation level to consider
        
    Returns:
        list: List of tuples containing (content, index) for each item at the target level
    """
    items = []
    i = start_index
    while i < len(lines):
        line = lines[i]
        if not line.strip() or is_comment_or_command(line):
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
    """
    Generate a consistent anchor ID from text.
    
    This function creates valid HTML anchor IDs from text by replacing non-alphanumeric
    characters with hyphens and converting to lowercase.
    
    Args:
        text (str): The text to convert to an anchor ID
        
    Returns:
        str: A valid HTML anchor ID
    """
    return re.sub(r'[^a-zA-Z0-9]+', '-', text.lower()).strip('-')

def process_level(lines, start_index, current_indent, hierarchy=None):
    """
    Process each level of the checklist.
    
    This is the core function that recursively processes the checklist hierarchy.
    It generates markdown content with proper headings, checkboxes, and navigation links
    for each level of the checklist.
    
    Args:
        lines (list): All lines from the input file
        start_index (int): Index to start processing from
        current_indent (int): Current indentation level being processed
        hierarchy (list, optional): List of parent items in the hierarchy
        
    Returns:
        list: Lines of markdown content for this level
    """
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
        # Add anchor for current level before the heading
        current_id = generate_anchor_id('level-1-' + '-'.join([h.lower().replace(' ', '-') for h in hierarchy]))
        content.append(f"<a id='{current_id}'></a>")
        
        # Build breadcrumb navigation
        breadcrumb = []
        current_path = []
        
        # Add "Main Checklist" as first item
        main_id = generate_anchor_id('level-1')
        breadcrumb.append(f"[Main Checklist](#{main_id})")
        
        # Add intermediate levels
        for i, part in enumerate(hierarchy[:-1]):
            current_path.append(part)
            # Link to the level heading instead of the item
            level_id = generate_anchor_id('level-1-' + '-'.join([h.lower().replace(' ', '-') for h in current_path]))
            breadcrumb.append(f"[{part}](#{level_id})")
        
        # Add current level (without link)
        breadcrumb.append(hierarchy[-1])
        
        # Create title with breadcrumb navigation
        content.append(f"# {' | '.join(breadcrumb)}")
    
    # Add items to the current checklist
    for item, idx in items:
        if is_comment_or_command(item):
            continue
            
        # Check if this item has children
        has_children = False
        if idx + 1 < len(lines):
            next_line = lines[idx + 1]
            next_indent = count_indent(next_line)
            if next_indent > current_indent:
                has_children = True
        
        # Generate item ID and add anchor
        item_id = generate_anchor_id('item-' + item.lower().replace(' ', '-'))
        content.append(f"<a id='{item_id}'></a>")
        
        # Add item with link if it has children
        if has_children:
            new_hierarchy = hierarchy + [item]
            # Link to the level heading instead of the item
            sub_list_id = generate_anchor_id('level-1-' + '-'.join([h.lower().replace(' ', '-') for h in new_hierarchy]))
            content.append(f"☐ [{item}](#{sub_list_id})\n")
        else:
            content.append(f"☐ {item}\n")
    
    # Add page break if there are items
    if items:
        content.append("\n\\newpage\n")
    
    # Process each item's children recursively
    for item, idx in items:
        if is_comment_or_command(item):
            continue
            
        # Check if this item has children
        has_children = False
        if idx + 1 < len(lines):
            next_line = lines[idx + 1]
            next_indent = count_indent(next_line)
            if next_indent > current_indent:
                has_children = True
        
        if has_children:
            # Create a new hierarchy with the current item
            new_hierarchy = hierarchy + [item]
            
            # Process children recursively
            child_content = process_level(lines, idx + 1, current_indent + 1, new_hierarchy)
            content.extend(child_content)
    
    return content

def process_children(lines, start_index, indent_level, hierarchy):
    """
    Process children of a specific item.
    
    This function processes the children of a specific item in the hierarchy,
    creating a section with proper navigation links to parent items.
    
    Args:
        lines (list): All lines from the input file
        start_index (int): Index to start processing from
        indent_level (int): Indentation level of the children
        hierarchy (list): List of parent items in the hierarchy
        
    Returns:
        list: Lines of markdown content for the children
    """
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
    """
    Convert markdown to HTML with anchors and internal links.
    
    This function takes a markdown file and converts it to HTML with proper
    page breaks, styling, and internal navigation links.
    
    Args:
        md_file (str): Path to the markdown file
        
    Returns:
        str: HTML content with styling and page breaks
    """
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
        <meta charset="UTF-8">
        <style>
            .page { page-break-after: always; }
            body { 
                font-family: Arial, sans-serif;
                font-size: 14pt;
                line-height: 1.5;
            }
            h1 { 
                color: #2c3e50;
                font-weight: bold;
                font-size: 14pt;
                margin-top: 1em;
                margin-bottom: 0.5em;
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
            @page { 
                size: letter; 
                margin: 1in;
            }
        </style>
    </head>
    <body>
    """ + "\n".join(processed_pages) + "</body></html>"
    
    return html_content

def convert_to_pdf(md_file):
    """
    Convert markdown file to PDF.
    
    This function takes a markdown file and converts it to a PDF using WeasyPrint,
    applying proper page sizing and margins.
    
    Args:
        md_file (str): Path to the markdown file
    """
    import time
    import signal
    
    html_content = process_markdown_to_pdf(md_file)
    pdf_file = os.path.splitext(md_file)[0] + ".pdf"
    
    # Define a timeout handler
    def timeout_handler(signum, frame):
        raise TimeoutError("PDF generation timed out after 60 seconds")
    
    # Set a timeout of 60 seconds
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(60)
    
    try:
        # Create PDF with optimized settings
        HTML(string=html_content).write_pdf(
            pdf_file,
            optimize_size=('fonts', 'images'),
            presentational_hints=True
        )
    except TimeoutError:
        print("PDF generation timed out. The document may be too large or complex.")
        print("Try breaking it into smaller sections or simplifying the content.")
    except Exception as e:
        print(f"Error generating PDF: {e}")
    finally:
        # Disable the alarm
        signal.alarm(0)
    
    # Check if PDF was created
    if os.path.exists(pdf_file):
        print(f"PDF created successfully: {pdf_file}")
    else:
        print("Failed to create PDF. Check the error messages above.")

def convert_to_markdown(input_file, output_file):
    """
    Convert a text-based checklist to markdown and then to PDF.
    
    This is the main function that orchestrates the conversion process:
    1. Reads the input text file
    2. Processes the hierarchy to create markdown content
    3. Writes the markdown file
    4. Converts the markdown to PDF
    
    Args:
        input_file (str): Path to the input text file
        output_file (str): Path to write the markdown file
    """
    with open(input_file, 'r') as f:
        lines = f.readlines()
    
    # Check for #end command and truncate lines if found
    for i, line in enumerate(lines):
        if is_end_command(line):
            lines = lines[:i]
            break
    
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
    
    # If input_file is not an absolute path, look in the script's directory
    if not os.path.isabs(input_file) and not os.path.exists(input_file):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        potential_path = os.path.join(script_dir, input_file)
        if os.path.exists(potential_path):
            input_file = potential_path
            if len(sys.argv) <= 2:  # If output file wasn't explicitly specified
                output_file = os.path.join(script_dir, output_file)
    
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' not found.")
        print(f"Current working directory: {os.getcwd()}")
        print(f"Script directory: {os.path.dirname(os.path.abspath(__file__))}")
        sys.exit(1)
    
    print(f"Processing {input_file} to {output_file}")
    convert_to_markdown(input_file, output_file) 