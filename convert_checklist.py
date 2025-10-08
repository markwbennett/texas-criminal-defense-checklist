#!./.venv/bin/python

"""
Texas Criminal-Defense Checklist Converter

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
import csv

# Font constants
FONT_FAMILY = "Arial"
FONT_SIZE = 12

# Character width data from CSV file
def load_character_widths(csv_file):
    """
    Load character width data from CSV file.
    
    Args:
        csv_file (str): Path to the CSV file with character width data
        
    Returns:
        dict: Dictionary mapping characters to their widths
    """
    char_widths = {}
    
    try:
        with open(csv_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                char = row.get('Character', '')
                if not char:
                    continue
                    
                try:
                    width_str = row.get('Px/Pt Ratio', '')
                    if width_str:
                        width = float(width_str)
                        char_widths[char] = width
                except (ValueError, TypeError):
                    # Skip invalid values
                    continue
    except Exception as e:
        print(f"Warning: Could not load character width data: {e}")
        return {}
    
    return char_widths

def calculate_line_width(text, char_widths):
    """
    Calculate the width of a line of text using character width data.
    
    Args:
        text (str): The text to calculate width for
        char_widths (dict): Dictionary mapping characters to their widths
        
    Returns:
        float: The calculated width of the text
    """
    width = 0
    for char in text:
        if char in char_widths:
            width += char_widths[char] * FONT_SIZE
        else:
            # Use average character width if character not in data
            width += 0.5 * FONT_SIZE
    return width

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

def is_form_start(line):
    """
    Check if a line starts a FORM section.

    Args:
        line (str): The line to check

    Returns:
        bool: True if the line is #FORM, False otherwise
    """
    return line.strip().upper() == '#FORM'

def is_form_end(line):
    """
    Check if a line ends a FORM section.

    Args:
        line (str): The line to check

    Returns:
        bool: True if the line is #FORMEND, False otherwise
    """
    return line.strip().upper() == '#FORMEND'

def process_form_section(lines, start_index):
    """
    Process a form section between #FORM and #FORMEND markers.

    Forms are kept together on one page and rendered as plain text without checkboxes.

    Args:
        lines (list): All lines from the input file
        start_index (int): Index of the #FORM line

    Returns:
        tuple: (list of markdown content lines, index after #FORMEND)
    """
    content = []
    content.append('<div class="form-section">')

    i = start_index + 1
    while i < len(lines):
        line = lines[i]

        if is_form_end(line):
            content.append('</div>\n')
            return (content, i + 1)

        # Skip comment lines within the form
        if is_comment_or_command(line):
            i += 1
            continue

        # Preserve the line but strip leading tabs/spaces for form content
        stripped = line.lstrip('\t ')
        if stripped:
            content.append(stripped.rstrip() + '  ')  # Two spaces for line break in markdown
        else:
            content.append('')  # Preserve blank lines

        i += 1

    # If we get here, #FORMEND was not found
    content.append('</div>\n')
    return (content, i)

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
    # Find the path to the CSV file
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_file = os.path.join(script_dir, "arial_px_pt_ratios.csv")
    
    # Load character width data
    char_widths = load_character_widths(csv_file)
    
    # Maximum width in pixels (letter size with 1-inch margins)
    page_width_inches = 8.5 - 2  # Letter width minus 1-inch margins
    max_width = page_width_inches * 72  # Convert to points (72 points per inch)
    
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
    
    # Track items that have FORM sections (so we don't recursively process their children)
    items_with_forms = set()

    # Add items to the current checklist
    for item, idx in items:
        if is_comment_or_command(item):
            continue

        # Check if the next line is a FORM section
        if idx + 1 < len(lines) and is_form_start(lines[idx + 1]):
            # Generate item ID and add anchor
            item_id = generate_anchor_id('item-' + item.lower().replace(' ', '-'))
            content.append(f"<a id='{item_id}'></a>")
            content.append(f"☐ **{item}**\n")

            # Process the form section
            form_content, next_idx = process_form_section(lines, idx + 1)
            content.extend(form_content)
            content.append('')  # Add blank line after form

            # Mark this item as having a form so we don't process its children recursively
            items_with_forms.add(idx)
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
        
        # Check if the item needs underscores
        if item.endswith('_'):
            # Handle items with underscores using a flex container
            base_item = item[:-1].strip()  # Remove trailing underscore and extra spaces
            
            # Create HTML markup for a flex container to handle the underline
            if has_children:
                new_hierarchy = hierarchy + [item]
                sub_list_id = generate_anchor_id('level-1-' + '-'.join([h.lower().replace(' ', '-') for h in new_hierarchy]))
                content.append(f'<div class="field-container"><span class="checkbox">☐</span> <span class="field-label">[{base_item}](#{sub_list_id})</span><span class="field-underline"></span></div>\n')
            else:
                content.append(f'<div class="field-container"><span class="checkbox">☐</span> <span class="field-label">{base_item}</span><span class="field-underline"></span></div>\n')
        else:
            # Add item with link if it has children (standard behavior without underscores)
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

        # Skip recursive processing for items with FORM sections (already processed above)
        if idx in items_with_forms:
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
    # Find the path to the CSV file
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_file = os.path.join(script_dir, "arial_px_pt_ratios.csv")
    
    # Load character width data
    char_widths = load_character_widths(csv_file)
    
    # Maximum width in pixels (letter size with 1-inch margins)
    page_width_inches = 8.5 - 2  # Letter width minus 1-inch margins
    max_width = page_width_inches * 72  # Convert to points (72 points per inch)
    
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
            # Check if the item needs underscores
            if item.endswith('_'):
                # Handle items with underscores using a flex container
                base_item = item[:-1].strip()  # Remove trailing underscore and extra spaces
                content.append(f'<div class="field-container"><span class="checkbox">☐</span> <span class="field-label">{base_item}</span><span class="field-underline"></span></div>')
            else:
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
        
        # Fix issue with paragraph tags wrapping field containers
        # Markdown parser often wraps divs in <p> tags, which can break the layout
        html = html.replace('<p><div class="field-container">', '<div class="field-container">')
        html = html.replace('</div></p>', '</div>')
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # Clean up any remaining nested paragraphs inside field containers
        for field_container in soup.select('.field-container'):
            for p in field_container.select('p'):
                p.unwrap()  # Remove the paragraph tag but keep its contents
        
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
                font-family: """ + FONT_FAMILY + """, sans-serif;
                font-size: """ + str(FONT_SIZE) + """pt;
                line-height: 1.5;
            }
            h1 { 
                color: #2c3e50;
                font-weight: bold;
                font-size: """ + str(FONT_SIZE) + """pt;
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
            /* Field container styles for flex-based layout */
            .field-container {
                display: flex;
                align-items: center; /* Change from baseline to center for better vertical alignment */
                width: 100%;
                margin-bottom: 0.5em;
                position: relative; /* Add relative positioning */
                padding-top: 0.1em; /* Add small padding to adjust vertical position */
            }
            .field-label {
                margin-right: 0.5em;
            }
            .checkbox {
                margin-right: 0.5em;
            }
            .field-underline {
                flex-grow: 1;
                border-bottom: 1px solid black;
                min-width: 300px;
                height: 0; /* Change from 1px to 0 to improve alignment */
                margin-bottom: 0.1em; /* Add a small bottom margin for vertical position */
            }
            /* Fix paragraph margins within flex containers */
            .field-container p {
                margin: 0;
                padding: 0;
            }
            /* Form section styles */
            .form-section {
                border: 1px solid #ccc;
                padding: 1em;
                margin: 1em 0;
                background-color: #f9f9f9;
                page-break-inside: avoid; /* Keep form sections together on one page */
            }
            .form-section p {
                margin: 0.25em 0;
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
    
    # Save the HTML content for inspection
    html_inspection_file = os.path.splitext(md_file)[0] + "_inspection.html"
    with open(html_inspection_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"Saved HTML for inspection: {html_inspection_file}")
    
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
    index_content.append("title: Criminal-Defense Checklist")
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