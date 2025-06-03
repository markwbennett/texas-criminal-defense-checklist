#!./.venv/bin/python

import os
import random
import string
from weasyprint import HTML, CSS
from bs4 import BeautifulSoup

def generate_random_text(min_length, max_length):
    """Generate random text of varying lengths."""
    length = random.randint(min_length, max_length)
    chars = string.ascii_letters + string.digits + ' ' * 10  # Add extra spaces to make it more realistic
    return ''.join(random.choice(chars) for _ in range(length))

def generate_line_stats_pdf(output_file, line_count=50, min_length=30, max_length=120):
    """Generate a PDF with varying line lengths to calculate average characters per line."""
    
    # Generate HTML content with various line lengths
    lines = []
    total_chars = 0
    
    # Create lines with character counts
    for i in range(1, line_count + 1):
        text = generate_random_text(min_length, max_length)
        char_count = len(text)
        total_chars += char_count
        lines.append(f"<p><span class='line-number'>{i}:</span> <span class='text'>{text}</span> <span class='char-count'>[{char_count} chars]</span></p>")
    
    # Calculate average
    average_chars = total_chars / line_count
    
    # Create HTML document
    html_content = f"""
    <html>
    <head>
        <style>
            body {{ font-family: monospace; font-size: 12px; line-height: 1.5; }}
            .line-number {{ font-weight: bold; color: #2980b9; }}
            .char-count {{ color: #c0392b; }}
            .text {{ background-color: #f8f9fa; padding: 2px 4px; }}
            .stats {{ margin-top: 20px; font-weight: bold; }}
        </style>
    </head>
    <body>
        <h1>Line Character Count Analysis</h1>
        <p>This document contains {line_count} lines of text with varying character counts.</p>
        <p>Use this to measure average character counts in your specific font and page settings.</p>
        <hr>
        
        <div class="lines">
            {"".join(lines)}
        </div>
        
        <div class="stats">
            <p>Total characters: {total_chars}</p>
            <p>Average characters per line: {average_chars:.2f}</p>
            <p>Lines measured: {line_count}</p>
        </div>
    </body>
    </html>
    """
    
    # Create PDF
    HTML(string=html_content).write_pdf(
        output_file,
        stylesheets=[CSS(string='@page { size: letter; margin: 1in; }')]
    )
    
    print(f"Generated PDF at {output_file}")
    print(f"Average characters per line: {average_chars:.2f}")

if __name__ == "__main__":
    output_file = "line_stats.pdf"
    generate_line_stats_pdf(output_file) 