#!./.venv/bin/python

import os
import sys
import random
import string
import statistics
import math
from weasyprint import HTML, CSS
from bs4 import BeautifulSoup
import markdown

def generate_random_text(length):
    """Generate random text of specified length with realistic word distribution."""
    if length < 2:
        return "A"
    
    # Create a mix of short, medium and long words for realistic text
    words = [
        "a", "an", "the", "of", "to", "in", "is", "and", "for", "on", "at", "by", # short
        "with", "from", "this", "that", "have", "will", "case", "court", "legal", # medium
        "document", "attorney", "evidence", "criminal", "defendant", "procedure"  # long
    ]
    
    result = ""
    while len(result) < length:
        word = random.choice(words)
        # Add space if not first word
        if result and len(result) + len(word) + 1 <= length:
            result += " " + word
        # Add word without space if first word or space won't fit
        elif len(result) + len(word) <= length:
            result += word
        # If adding any word would exceed length, pad with characters
        else:
            remaining = length - len(result)
            if remaining > 0:
                if result:
                    result += " " + "A" * (remaining - 1)
                else:
                    result += "A" * remaining
            break
    
    # Ensure exact length
    if len(result) < length:
        result += "A" * (length - len(result))
    elif len(result) > length:
        result = result[:length]
    
    return result

def generate_half_text_half_underscores(total_length):
    """Generate a line with first half as random text and second half as underscores."""
    # Checkbox and spaces are INCLUDED in the total character count
    # This is the full line length, no deductions
    
    # Define the fixed characters that will be in every line
    checkbox = "☐"
    space_after_checkbox = " "
    separator_space = " "
    
    # Calculate remaining length for content (text + underscores)
    fixed_chars_length = len(checkbox) + len(space_after_checkbox) + len(separator_space)
    content_length = total_length - fixed_chars_length
    
    # Split the content length approximately in half
    text_length = math.ceil(content_length / 2)
    underscore_length = content_length - text_length
    
    # Generate the random text part
    random_text = generate_random_text(text_length)
    
    # Create underscores using regular underscores instead of dashes
    underscores = "_" * underscore_length
    
    # Combine into the full line with a space between text and underscores
    full_text = f"{checkbox}{space_after_checkbox}{random_text}{separator_space}{underscores}"
    
    # Calculate final character counts
    checkbox_count = 1  # Always 1 checkbox
    spaces_count = 2    # Space after checkbox + separator space
    text_chars = len(random_text)
    underscore_count = underscore_length
    
    return full_text, checkbox_count, spaces_count, text_chars, underscore_count

def generate_focused_test_lines(min_chars=70, max_chars=82, samples_per_length=10):
    """Generate multiple test lines for each length in the specified range."""
    lines = []
    for length in range(min_chars, max_chars + 1):
        for sample in range(samples_per_length):
            full_text, checkbox_count, spaces_count, text_chars, underscore_count = generate_half_text_half_underscores(length)
            
            # Store detailed character count breakdown
            char_counts = {
                'total': length,
                'checkbox': checkbox_count,
                'spaces': spaces_count,
                'text': text_chars,
                'underscores': underscore_count
            }
            
            lines.append((length, full_text, sample + 1, char_counts))
    return lines

def create_focused_test_pdf(output_file, min_chars=70, max_chars=82, samples_per_length=10):
    """Create a PDF focused on a specific character length range with multiple samples."""
    # Generate test lines in the focused range
    test_lines = generate_focused_test_lines(min_chars, max_chars, samples_per_length)
    
    # Create HTML content directly for better control over rendering
    html_content = f"""
    <html>
    <head>
        <style>
            @page {{ size: letter; margin: 1in; }}
            .page {{ page-break-after: always; }}
            body {{ font-family: Arial, sans-serif; line-height: 1.5; padding: 0; margin: 0; }}
            h1, h2 {{ color: #2c3e50; margin-top: 20px; }}
            p {{ margin: 8px 0; }}
            .line-container {{ margin-bottom: 12px; }}
            .line {{ 
                font-family: Arial, sans-serif; 
                font-size: 1em;
                white-space: pre-wrap;
                margin: 5px 0;
            }}
            .details {{
                font-size: 0.9em;
                color: #555;
                margin: 3px 0 12px 0;
            }}
            .underscore {{
                text-decoration: underline;
                display: inline-block;
                width: 0.5em;
            }}
        </style>
    </head>
    <body>
        <h1>Character Count Test: {min_chars}-{max_chars} Range</h1>
        <p>This document shows {samples_per_length} samples for each line length from {min_chars} to {max_chars} characters.</p>
        <p>Each line has approximately half random text, a space, and then half underscores.</p>
        <p><strong>IMPORTANT: The total character count INCLUDES the checkbox and all spaces.</strong></p>
    """
    
    # Group by character length
    current_length = None
    for length, text, sample_num, char_counts in test_lines:
        if current_length != length:
            if current_length is not None:
                html_content += "</div>"
            html_content += f"""
            <h2>{length} Total Characters</h2>
            <div class="length-section">
            """
            current_length = length
        
        # Replace underscores with properly rendered HTML
        parts = text.split()
        last_part = parts[-1]
        if "_" in last_part:
            parts[-1] = '<span style="text-decoration: underline;">' + "&nbsp;" * len(last_part) + '</span>'
        processed_text = " ".join(parts)
        
        html_content += f"""
        <div class="line-container">
            <div class="line">{processed_text}</div>
            <div class="details">(Char counts: {char_counts['total']} total | 
               {char_counts['checkbox']} checkbox | 
               {char_counts['spaces']} spaces | 
               {char_counts['text']} text | 
               {char_counts['underscores']} underscores) [Sample {sample_num}]</div>
        </div>
        """
    
    # Close the last section
    if current_length is not None:
        html_content += "</div>"
    
    html_content += """
    </body>
    </html>
    """
    
    # Create PDF with the same page size and margins as the checklist
    HTML(string=html_content).write_pdf(output_file)
    
    print(f"Generated focused test PDF at {output_file}")
    print(f"This PDF contains {samples_per_length} samples for each line length from {min_chars} to {max_chars} characters")
    print(f"Each line has approximately half random text, a space, and then half underscores")
    print(f"The total character count INCLUDES the checkbox and all spaces")

def generate_test_lines(min_chars=10, max_chars=120, increment=5):
    """Generate test lines of varying lengths using checklist format."""
    lines = []
    for length in range(min_chars, max_chars + 1, increment):
        full_text, checkbox_count, spaces_count, text_chars, underscore_count = generate_half_text_half_underscores(length)
        lines.append((length, full_text))
    return lines

def create_test_pdf(output_file):
    """Create a PDF with test lines using the checklist formatting."""
    # Generate test lines of various lengths
    test_lines = generate_test_lines()
    
    # Create HTML content directly for better control over rendering
    html_content = f"""
    <html>
    <head>
        <style>
            @page {{ size: letter; margin: 1in; }}
            .page {{ page-break-after: always; }}
            body {{ font-family: Arial, sans-serif; line-height: 1.5; padding: 0; margin: 0; }}
            h1, h2 {{ color: #2c3e50; margin-top: 20px; }}
            .line-container {{ margin-bottom: 15px; }}
            .line {{ 
                font-family: Arial, sans-serif; 
                font-size: 1em;
                white-space: pre-wrap;
                margin: 5px 0;
            }}
            .details {{
                font-size: 0.9em;
                color: #555;
                margin: 3px 0 12px 0;
            }}
        </style>
    </head>
    <body>
        <h1>Character Count Test Document</h1>
        <p>This document shows lines of different lengths using realistic text with proper proportional spacing.</p>
        <p>Each line has approximately half random text, a space, and then half underscores.</p>
        <p><strong>IMPORTANT: The total character count INCLUDES the checkbox and all spaces.</strong></p>
    """
    
    for length, text in test_lines:
        html_content += f"""
        <div class="line-container">
            <div class="line">{text}</div>
            <div class="details">[{length} total chars]</div>
        </div>
        """
    
    html_content += """
    </body>
    </html>
    """
    
    # Create PDF with the same page size and margins as the checklist
    HTML(string=html_content).write_pdf(output_file)
    
    print(f"Generated test PDF at {output_file}")
    print(f"This PDF contains test lines with realistic text from 10 to 120 characters in 5-character increments")
    print(f"Use this to determine how many characters fit on a line with checklist formatting")
    print(f"The total character count INCLUDES the checkbox and all spaces")

def analyze_existing_file(input_file, output_file):
    """Analyze an existing file and create a PDF report with checklist formatting."""
    line_lengths = []
    lines_with_counts = []
    
    with open(input_file, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f, 1):
            line = line.rstrip('\n')
            # Skip lines that are just HTML/markdown formatting
            if line.strip() and not line.strip().startswith('<') and not line.strip().startswith('\\'):
                length = len(line)
                line_lengths.append(length)
                # Truncate long lines for display
                display_line = line if len(line) <= 80 else line[:77] + '...'
                lines_with_counts.append((i, display_line, length))
    
    # Calculate statistics
    stats = {
        'count': len(line_lengths),
        'min': min(line_lengths) if line_lengths else 0,
        'max': max(line_lengths) if line_lengths else 0,
        'mean': statistics.mean(line_lengths) if line_lengths else 0,
        'median': statistics.median(line_lengths) if line_lengths else 0,
        'stdev': statistics.stdev(line_lengths) if len(line_lengths) > 1 else 0,
    }
    
    # Create histogram data for line lengths
    histogram = {}
    for length in line_lengths:
        bucket = (length // 10) * 10
        histogram[bucket] = histogram.get(bucket, 0) + 1
    
    # Create HTML content directly for better control over rendering
    html_content = f"""
    <html>
    <head>
        <style>
            @page {{ size: letter; margin: 1in; }}
            .page {{ page-break-after: always; }}
            body {{ font-family: Arial, sans-serif; line-height: 1.5; padding: 0; margin: 0; }}
            h1, h2 {{ color: #2c3e50; margin-top: 20px; }}
            ul {{ margin-top: 10px; padding-left: 20px; }}
            li {{ margin: 8px 0; }}
        </style>
    </head>
    <body>
        <h1>Line Length Analysis: {os.path.basename(input_file)}</h1>
        
        <h2>Statistics</h2>
        <ul>
            <li>Total non-empty lines: {stats['count']}</li>
            <li>Average characters per line: {stats['mean']:.2f}</li>
            <li>Median characters per line: {stats['median']:.2f}</li>
            <li>Minimum line length: {stats['min']}</li>
            <li>Maximum line length: {stats['max']}</li>
            <li>Standard deviation: {stats['stdev']:.2f}</li>
        </ul>
        
        <h2>Line Length Distribution</h2>
        <ul>
    """
    
    for bucket, count in sorted(histogram.items()):
        bar = "#" * (count // 5 + 1)  # Scale the bar
        html_content += f"<li>{bucket}-{bucket+9} chars: {count} lines {bar}</li>\n"
    
    html_content += """
        </ul>
        
        <h2>Sample Lines</h2>
        <ul>
    """
    
    for line_num, content, length in lines_with_counts[:15]:
        html_content += f"<li>Line {line_num}: ({length} chars) {content}</li>\n"
    
    html_content += """
        </ul>
    </body>
    </html>
    """
    
    # Create PDF with the same page size and margins as the checklist
    HTML(string=html_content).write_pdf(output_file)
    
    print(f"Analysis complete.")
    print(f"Average characters per line: {stats['mean']:.2f}")
    print(f"Generated PDF report at {output_file}")

if __name__ == "__main__":
    if len(sys.argv) == 1:
        # No arguments, create test document
        output_file = "checklist_format_test.pdf"
        create_test_pdf(output_file)
    elif len(sys.argv) >= 2:
        if sys.argv[1] == "--test":
            # Create test document with specified name
            output_file = "checklist_format_test.pdf"
            if len(sys.argv) >= 3:
                output_file = sys.argv[2]
            create_test_pdf(output_file)
        elif sys.argv[1] == "--focused":
            # Create focused test with more samples in the specified character range
            output_file = "checklist_70_82_test.pdf"
            if len(sys.argv) >= 3:
                output_file = sys.argv[2]
            create_focused_test_pdf(output_file, min_chars=70, max_chars=82)
        else:
            # Analyze existing file
            input_file = sys.argv[1]
            if len(sys.argv) >= 3:
                output_file = sys.argv[2]
            else:
                output_file = os.path.splitext(input_file)[0] + "_checklist_analysis.pdf"
            analyze_existing_file(input_file, output_file) 