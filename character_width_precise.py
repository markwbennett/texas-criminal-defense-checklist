#!./.venv/bin/python

from PIL import ImageFont, ImageDraw, Image
import os
import json
import platform
import string
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

def measure_multi_character_widths(font_path, font_sizes=None, repetitions=21):
    """Measure character widths by creating strings of repeated characters."""
    if font_sizes is None:
        font_sizes = [12]
    
    # Characters to measure
    chars_to_measure = list(string.ascii_lowercase + string.ascii_uppercase + 
                           string.digits + string.punctuation + ' ')
    
    # Add checkbox character
    chars_to_measure.append('☐')
    
    results = {}
    
    try:
        for size in font_sizes:
            font = ImageFont.truetype(font_path, size)
            
            # Dictionary to store results for this font size
            size_results = {}
            
            # Measure single characters first as baseline
            single_widths = {}
            for char in chars_to_measure:
                width = font.getlength(char)
                single_widths[char] = width
            
            # Measure multi-character strings
            multi_widths = {}
            for char in chars_to_measure:
                # Create a string with repetitions of the character
                char_string = char * repetitions
                
                # Measure the total width
                total_width = font.getlength(char_string)
                
                # Calculate the width per character
                width_per_char = total_width / repetitions
                
                # Store the result
                multi_widths[char] = width_per_char
            
            # Compare single vs multi-character measurements
            comparison = {}
            for char in chars_to_measure:
                single_width = single_widths[char]
                multi_width = multi_widths[char]
                diff = abs(single_width - multi_width)
                diff_percent = (diff / single_width) * 100 if single_width > 0 else 0
                
                comparison[char] = {
                    'single_width': single_width,
                    'multi_width': multi_width,
                    'difference': diff,
                    'difference_percent': diff_percent
                }
            
            # Store all results for this font size
            size_results = {
                'single_widths': single_widths,
                'multi_widths': multi_widths,
                'comparison': comparison
            }
            
            results[size] = size_results
            
        return results
    except Exception as e:
        print(f"Error: {e}")
        return None

def format_width_comparison_table(width_data, font_size):
    """Format width comparison data as a table."""
    output = []
    
    output.append(f"Arial Character Width Comparison - {font_size}pt")
    output.append("=" * 80)
    output.append(f"{'Char':^6} | {'Single Width':^12} | {'Multi Width':^12} | {'Diff':^8} | {'Diff %':^8} | {'ASCII':^6}")
    output.append("-" * 80)
    
    # Get data for this font size
    size_data = width_data[font_size]
    
    # Sort characters alphabetically, but with special handling for space and non-printable chars
    chars = sorted(size_data['comparison'].keys(), 
                  key=lambda x: (x == ' ', not x.isprintable(), x.lower(), x.isupper()))
    
    for char in chars:
        data = size_data['comparison'][char]
        # Display char safely (for space and special chars)
        display_char = repr(char)[1:-1] if char == ' ' or not char.isprintable() else char
        
        # Get ASCII code
        ascii_code = ord(char) if len(char) == 1 else 'N/A'
        
        output.append(f"{display_char:^6} | {data['single_width']:^12.4f} | {data['multi_width']:^12.4f} | "
                     f"{data['difference']:^8.4f} | {data['difference_percent']:^8.2f}% | {ascii_code:^6}")
    
    return "\n".join(output)

def create_test_image(font_path, font_size=12, repetitions=21):
    """Create a test image showing the measurement method."""
    font = ImageFont.truetype(font_path, font_size)
    
    # Select a subset of characters to visualize
    test_chars = ['a', 'i', 'm', 'W', '1', '.', ' ', '☐']
    
    # Calculate the width and height of the image
    line_height = font_size * 2
    max_width = 0
    for char in test_chars:
        char_string = char * repetitions
        width = font.getlength(char_string)
        max_width = max(max_width, width)
    
    # Add some padding
    padding = 50
    img_width = int(max_width) + padding * 2
    img_height = len(test_chars) * line_height + padding * 2
    
    # Create image with white background
    img = Image.new('RGB', (img_width, img_height), color='white')
    draw = ImageDraw.Draw(img)
    
    # Draw the measurement lines and text
    y_position = padding
    for char in test_chars:
        char_string = char * repetitions
        
        # Draw the character string
        draw.text((padding, y_position), char_string, font=font, fill='black')
        
        # Draw vertical lines at the first and last character
        first_char_width = font.getlength(char)
        full_string_width = font.getlength(char_string)
        
        draw.line([(padding, y_position - 5), (padding, y_position + font_size)], fill='red', width=1)
        draw.line([(padding + full_string_width, y_position - 5), 
                  (padding + full_string_width, y_position + font_size)], fill='blue', width=1)
        
        # Draw a text label for the measurement
        measurement_text = f"Width: {full_string_width:.2f}px, Per char: {full_string_width/repetitions:.4f}px"
        draw.text((padding, y_position + font_size), measurement_text, font=font, fill='green')
        
        y_position += line_height
    
    # Save the image
    img.save('character_width_method.png')
    print("Created visual example of measurement method in 'character_width_method.png'")

def main():
    # Get the font path
    font_path = get_font_path()
    if not font_path or not os.path.exists(font_path):
        print(f"Arial font not found at {font_path}")
        return
    
    # Font sizes to analyze
    font_sizes = [12, 16]
    repetitions = 21  # Use 21 repetitions for measurement
    
    print(f"Measuring Arial character widths at {font_sizes}pt with {repetitions} repetitions...")
    width_data = measure_multi_character_widths(font_path, font_sizes, repetitions)
    
    if not width_data:
        print("Failed to measure character widths.")
        return
    
    # Create visualizations
    create_test_image(font_path, 12, repetitions)
    
    # Format and display results
    print("\n" + "=" * 80)
    print("MEASUREMENT RESULTS")
    print("=" * 80)
    
    for size in font_sizes:
        table = format_width_comparison_table(width_data, size)
        print("\n" + table + "\n")
    
    # Save data to JSON
    results_data = {
        "font": "Arial",
        "repetitions": repetitions,
        "sizes": {}
    }
    
    for size in font_sizes:
        size_data = width_data[size]
        results_data["sizes"][size] = {
            "single_widths": {char: float(width) for char, width in size_data["single_widths"].items()},
            "multi_widths": {char: float(width) for char, width in size_data["multi_widths"].items()}
        }
    
    with open("arial_precise_widths.json", "w") as f:
        json.dump(results_data, f, indent=2)
    
    print(f"Precise width measurements saved to arial_precise_widths.json")

if __name__ == "__main__":
    main() 