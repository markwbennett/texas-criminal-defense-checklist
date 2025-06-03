#!./.venv/bin/python

from PIL import ImageFont, ImageDraw, Image
import os
import json
import platform
from collections import defaultdict

def get_font_path():
    """Get the path to Arial font based on the operating system."""
    system = platform.system()
    if system == "Darwin":  # macOS
        arial_paths = [
            "/Library/Fonts/Arial Unicode.ttf",
            "/Library/Fonts/Arial.ttf"
        ]
        for path in arial_paths:
            if os.path.exists(path):
                return path
    elif system == "Windows":
        return "C:\\Windows\\Fonts\\arial.ttf"
    else:  # Linux and others
        # Common locations on Linux
        paths = [
            "/usr/share/fonts/truetype/msttcorefonts/Arial.ttf",
            "/usr/share/fonts/TTF/arial.ttf"
        ]
        for path in paths:
            if os.path.exists(path):
                return path
    return None

def calculate_char_widths(font_path, font_sizes=None):
    """Calculate the width of each character in the given font sizes."""
    if font_sizes is None:
        font_sizes = [12, 14, 16]
    
    try:
        result = {}
        for size in font_sizes:
            font = ImageFont.truetype(font_path, size)
            
            # Calculate width for ASCII characters (32-126) plus common symbols
            chars = [chr(i) for i in range(32, 127)]
            
            # Create a dictionary of character widths
            widths = {}
            for char in chars:
                width = font.getlength(char)
                widths[char] = width
            
            # Store in result dictionary
            result[size] = widths
            
        return result
    except Exception as e:
        print(f"Error: {e}")
        return None

def calculate_relative_widths(widths_dict):
    """Calculate relative widths using the width of 'x' as a baseline."""
    result = {}
    
    for size, char_widths in widths_dict.items():
        baseline = char_widths.get('x', 1)  # Use 'x' as the baseline
        relative = {char: width/baseline for char, width in char_widths.items()}
        result[size] = relative
    
    return result

def find_common_character_groups(relative_widths):
    """Group characters by similar relative widths."""
    # Use the first font size for grouping
    first_size = list(relative_widths.keys())[0]
    width_map = relative_widths[first_size]
    
    # Group by width (rounded to 1 decimal place for clustering)
    groups = defaultdict(list)
    for char, width in width_map.items():
        rounded_width = round(width, 1)
        groups[rounded_width].append(char)
    
    # Sort groups by width
    sorted_groups = sorted(groups.items())
    return sorted_groups

def format_text_table(font_sizes, char_widths, relative_widths):
    """Format the character width data as a text table."""
    output = []
    
    # Header
    output.append("Arial Character Width Table")
    output.append("=" * 70)
    
    # Size info
    for size in font_sizes:
        output.append(f"Font Size: {size}pt")
        output.append("-" * 70)
        output.append(f"{'Char':^6} | {'ASCII':^6} | {'Width (px)':^10} | {'Relative to x':^15}")
        output.append("-" * 70)
        
        # Get widths for this size
        widths = char_widths[size]
        rel_widths = relative_widths[size]
        
        # Sort by ASCII code
        for i in range(32, 127):
            char = chr(i)
            if char in widths:
                # Special formatting for space and control characters
                display_char = repr(char)[1:-1] if i < 33 or i == 127 else char
                output.append(f"{display_char:^6} | {i:^6} | {widths[char]:^10.2f} | {rel_widths[char]:^15.2f}")
        
        output.append("\n")
    
    return "\n".join(output)

def format_width_groups(groups):
    """Format the character groups by width."""
    output = []
    
    output.append("Character Groups by Relative Width")
    output.append("=" * 70)
    
    for width, chars in groups:
        char_display = " ".join(chars)
        output.append(f"Width {width:.1f}x: {char_display}")
    
    return "\n".join(output)

def calculate_sample_text_widths(sample_texts, font_sizes, font_path):
    """Calculate total width for sample text strings."""
    output = []
    
    output.append("\nSample Text Width Calculations")
    output.append("=" * 70)
    
    for size in font_sizes:
        font = ImageFont.truetype(font_path, size)
        output.append(f"Font Size: {size}pt")
        output.append("-" * 70)
        
        for text in sample_texts:
            width = font.getlength(text)
            output.append(f"'{text}': {width:.2f}px")
        
        output.append("\n")
    
    return "\n".join(output)

def calculate_checklist_examples(font_path):
    """Calculate widths for checklist examples of different lengths."""
    output = []
    size = 12  # Standard font size for checklist
    font = ImageFont.truetype(font_path, size)
    
    output.append("\nChecklist Item Width Analysis")
    output.append("=" * 70)
    output.append(f"Font Size: {size}pt (standard for checklist)")
    output.append("-" * 70)
    
    # Create sample checklist items of varying lengths
    checkbox = "☐ "
    
    # Range of character lengths to test
    lengths = list(range(70, 83))
    
    output.append("Character Count | Total Width | Fits on Line?")
    output.append("-" * 70)
    
    # Get page width (assuming letter size with 1 inch margins)
    page_width_inches = 8.5 - 2  # Letter width minus 1-inch margins on each side
    page_width_px = page_width_inches * 72  # Convert to points (72 points per inch)
    
    for length in lengths:
        # Generate text of appropriate length after checkbox
        text_length = length - len(checkbox)
        half_text_length = text_length // 2
        text_part = "a" * half_text_length
        underscore_part = "_" * (text_length - half_text_length)
        
        # Full line with checkbox, text, and underscores
        full_line = f"{checkbox}{text_part} {underscore_part}"
        
        # Calculate width
        width = font.getlength(full_line)
        
        # Check if it fits on the page
        fits = "YES" if width <= page_width_px else "NO"
        
        output.append(f"{length} chars | {width:.2f}px | {fits}")
    
    return "\n".join(output)

def main():
    # Get the font path based on OS
    font_path = get_font_path()
    if not font_path or not os.path.exists(font_path):
        print(f"Arial font not found at {font_path}")
        print("Trying to use default font...")
        try:
            # Try to use a default font
            font_path = ImageFont.truetype("arial").path
        except Exception:
            print("Could not find Arial font. Please specify the path manually in the script.")
            return
    
    # Font sizes to analyze
    font_sizes = [12, 14, 16]
    
    # Calculate character widths
    print(f"Calculating character widths for Arial font at sizes: {font_sizes}")
    char_widths = calculate_char_widths(font_path, font_sizes)
    
    if not char_widths:
        print("Failed to calculate character widths.")
        return
    
    # Calculate relative widths
    relative_widths = calculate_relative_widths(char_widths)
    
    # Find groups of similar-width characters
    width_groups = find_common_character_groups(relative_widths)
    
    # Sample text for width calculation
    sample_texts = [
        "Hello World",
        "This is a test of the emergency broadcast system",
        "☐ This is a checkbox item"
    ]
    
    # Format as text tables
    table_output = format_text_table(font_sizes, char_widths, relative_widths)
    group_output = format_width_groups(width_groups)
    sample_output = calculate_sample_text_widths(sample_texts, font_sizes, font_path)
    checklist_output = calculate_checklist_examples(font_path)
    
    # Print to console
    print(table_output)
    print(group_output)
    print(sample_output)
    print(checklist_output)
    
    # Save to file
    with open("arial_metrics.txt", "w") as f:
        f.write(table_output)
        f.write("\n\n")
        f.write(group_output)
        f.write("\n\n")
        f.write(sample_output)
        f.write("\n\n")
        f.write(checklist_output)
    
    # Save the actual metrics as JSON for programmatic use
    metrics_data = {
        "absolute": {str(size): {char: float(width) for char, width in widths.items()} 
                    for size, widths in char_widths.items()},
        "relative": {str(size): {char: float(rel) for char, rel in rels.items()} 
                     for size, rels in relative_widths.items()},
        "checklist_examples": {}
    }
    
    # Add checklist examples to JSON
    size = 12
    font = ImageFont.truetype(font_path, size)
    checkbox = "☐ "
    
    metrics_data["checklist_examples"] = {
        "page_width_px": (8.5 - 2) * 72,
        "samples": {}
    }
    
    for length in range(70, 83):
        text_length = length - len(checkbox)
        half_text_length = text_length // 2
        text_part = "a" * half_text_length
        underscore_part = "_" * (text_length - half_text_length)
        full_line = f"{checkbox}{text_part} {underscore_part}"
        width = font.getlength(full_line)
        
        metrics_data["checklist_examples"]["samples"][length] = {
            "width_px": float(width),
            "fits_on_page": width <= (8.5 - 2) * 72
        }
    
    with open("arial_metrics.json", "w") as f:
        json.dump(metrics_data, f, indent=2)
    
    print(f"\nMetrics saved to arial_metrics.txt and arial_metrics.json")

if __name__ == "__main__":
    main() 