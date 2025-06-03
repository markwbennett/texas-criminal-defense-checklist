#!./.venv/bin/python

import re
import os
from weasyprint import HTML, CSS
from bs4 import BeautifulSoup
import markdown
import uuid

def generate_anchor_id(text):
    """Generate a consistent anchor ID from text."""
    return re.sub(r'[^a-zA-Z0-9]+', '-', text.lower()).strip('-')

def process_markdown(md_file):
    """Convert markdown to HTML with anchors and internal links."""
    with open(md_file, 'r') as f:
        md_content = f.read()
    
    # Split content into pages based on \newpage
    pages = md_content.split('\\newpage')
    
    # Track all checklists for linking
    checklists = {}  # breadcrumb -> page_number
    current_page = 1
    
    processed_pages = []
    for page in pages:
        if not page.strip():
            continue
            
        # Parse the page
        soup = BeautifulSoup(markdown.markdown(page), 'html.parser')
        
        # Find the heading (breadcrumb)
        heading = soup.find('h1')
        if heading:
            breadcrumb = heading.text
            checklists[breadcrumb] = current_page
            
            # Generate anchor
            anchor_id = generate_anchor_id(breadcrumb)
            heading['id'] = anchor_id
        
        processed_pages.append(str(soup))
        current_page += 1
    
    # Second pass: add links to checklist items
    final_pages = []
    current_page = 1
    for page in processed_pages:
        soup = BeautifulSoup(page, 'html.parser')
        
        # Find all checklist items
        items = soup.find_all('li')
        for item in items:
            text = item.text.strip('[ ]').strip()
            # Look for potential child checklist
            for breadcrumb in checklists:
                if breadcrumb.endswith(text):
                    # Create link to that page
                    link = soup.new_tag('a')
                    link['href'] = f'#page{checklists[breadcrumb]}'
                    link.string = text
                    # Replace text with link
                    item.string = ''
                    item.append('[ ] ')
                    item.append(link)
        
        # Add page anchor
        page_div = soup.new_tag('div')
        page_div['id'] = f'page{current_page}'
        page_div['class'] = 'page'
        for tag in soup.contents:
            page_div.append(tag.extract())
        soup.append(page_div)
        
        final_pages.append(str(soup))
        current_page += 1
    
    # Combine pages with CSS for page breaks
    html_content = """
    <html>
    <head>
        <style>
            .page { page-break-after: always; }
            body { font-family: Arial, sans-serif; }
            h1 { color: #2c3e50; }
            li { margin: 8px 0; }
            a { color: #2980b9; text-decoration: none; }
            a:hover { text-decoration: underline; }
        </style>
    </head>
    <body>
    """ + "\n".join(final_pages) + "</body></html>"
    
    return html_content

def convert_to_pdf(md_file, pdf_file):
    """Convert markdown file to PDF."""
    html_content = process_markdown(md_file)
    
    # Create PDF
    HTML(string=html_content).write_pdf(
        pdf_file,
        stylesheets=[CSS(string='@page { size: letter; margin: 1in; }')]
    )

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python md_to_pdf.py input.md")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = os.path.splitext(input_file)[0] + ".pdf"
    convert_to_pdf(input_file, output_file) 