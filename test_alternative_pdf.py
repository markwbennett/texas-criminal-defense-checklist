#!./.venv/bin/python

"""
Alternative PDF generation approach using direct HTML.
This script attempts to render a PDF with full-width underlines using a different approach.
"""

import os
import sys
import tempfile
from weasyprint import HTML, CSS

def create_test_pdf():
    # Create a simple HTML file with full-width underlines
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            @page {
                size: letter;
                margin: 1in;
            }
            body {
                font-family: Arial, sans-serif;
                font-size: 12pt;
                line-height: 1.5;
            }
            .field-container {
                display: flex;
                align-items: center;
                margin-bottom: 1em;
                width: 100%;
                position: relative;
                padding-top: 0.1em;
            }
            .field-label {
                margin-right: 0.5em;
            }
            .field-underline {
                flex-grow: 1;
                border-bottom: 1px solid black;
                min-width: 300px;
                height: 0;
                margin-bottom: 0.1em;
            }
            .checkbox {
                display: inline-block;
                width: 12pt;
                height: 12pt;
                border: 1px solid black;
                margin-right: 5px;
                vertical-align: middle;
            }
        </style>
    </head>
    <body>
        <h1>Test Form with Full-width Underlines</h1>
        
        <div class="field-container">
            <div class="checkbox">☐</div>
            <div class="field-label">Name:</div>
            <div class="field-underline"></div>
        </div>
        
        <div class="field-container">
            <div class="checkbox">☐</div>
            <div class="field-label">Address:</div>
            <div class="field-underline"></div>
        </div>
        
        <div class="field-container">
            <div class="checkbox">☐</div>
            <div class="field-label">Phone Number:</div>
            <div class="field-underline"></div>
        </div>
        
        <div class="field-container">
            <div class="checkbox">☐</div>
            <div class="field-label">Other cases in county?</div>
            <div class="field-underline"></div>
        </div>
        
        <div class="field-container">
            <div class="checkbox">☐</div>
            <div class="field-label">Other cases elsewhere?</div>
            <div class="field-underline"></div>
        </div>
        
        <div class="field-container">
            <div class="checkbox">☐</div>
            <div class="field-label">Other probation/parole/PPS matters?</div>
            <div class="field-underline"></div>
        </div>
    </body>
    </html>
    """
    
    # Save the HTML to a file for inspection
    html_inspection_file = 'alternative_underline_test.html'
    with open(html_inspection_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"Saved HTML for inspection: {html_inspection_file}")
    
    # Create a temporary HTML file
    with tempfile.NamedTemporaryFile(suffix='.html', delete=False) as f:
        f.write(html_content.encode('utf-8'))
        html_file = f.name
    
    try:
        # Generate PDF file
        pdf_file = 'alternative_underline_test.pdf'
        HTML(filename=html_file).write_pdf(pdf_file)
        print(f"Created PDF: {pdf_file}")
    finally:
        # Clean up the temporary HTML file
        os.unlink(html_file)

if __name__ == "__main__":
    create_test_pdf() 