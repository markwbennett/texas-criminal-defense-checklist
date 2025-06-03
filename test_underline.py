#!./.venv/bin/python

"""
Test script for the underscore functionality in the checklist converter.
This script creates a simple checklist with underscore fields to test the fill_line_with_underscores function.
"""

import os
import sys
import tempfile

# Add the parent directory to the path so we can import from convertChecklisttoPDF
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from convertChecklisttoPDF.convert_checklist import convert_to_markdown

def main():
    # Create a temporary directory
    with tempfile.TemporaryDirectory() as tempdir:
        # Create a test file
        test_file = os.path.join(tempdir, "test_underscores.txt")
        with open(test_file, "w") as f:
            f.write("# Test Checklist\n\n")
            f.write("Name_\n")
            f.write("Address_\n")
            f.write("Phone Number_\n")
            f.write("Other cases in county?_\n")
            f.write("Other cases elsewhere?_\n")
            f.write("Other probation/parole/PPS matters?_\n")
        
        # Create the output file
        output_file = os.path.join(tempdir, "test_underscores.md")
        
        # Convert to markdown and PDF
        convert_to_markdown(test_file, output_file)
        
        # Copy the output to the current directory
        import shutil
        current_dir = os.getcwd()
        md_output = os.path.join(current_dir, "test_underline_output.md")
        pdf_output = os.path.join(current_dir, "test_underline_output.pdf")
        html_output = os.path.join(current_dir, "test_underline_output.html")
        
        shutil.copy(output_file, md_output)
        pdf_file = os.path.splitext(output_file)[0] + ".pdf"
        if os.path.exists(pdf_file):
            shutil.copy(pdf_file, pdf_output)
            print(f"Created PDF: {pdf_output}")
        else:
            print("PDF was not created successfully.")
        
        # Copy HTML inspection file if it exists
        html_inspection_file = os.path.splitext(output_file)[0] + "_inspection.html"
        if os.path.exists(html_inspection_file):
            shutil.copy(html_inspection_file, html_output)
            print(f"Created HTML inspection file: {html_output}")
        else:
            print("HTML inspection file was not found.")
        
        print(f"Created markdown: {md_output}")

if __name__ == "__main__":
    main() 