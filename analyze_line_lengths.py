#!./.venv/bin/python

import os
import sys
import statistics
from weasyprint import HTML, CSS

def analyze_file(input_file):
    """Analyze a text file and return line length statistics."""
    line_lengths = []
    lines_with_counts = []
    
    with open(input_file, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f, 1):
            line = line.rstrip('\n')
            length = len(line)
            if length > 0:  # Skip empty lines
                line_lengths.append(length)
                # Truncate long lines for display
                display_line = line if len(line) <= 80 else line[:77] + '...'
                lines_with_counts.append((i, display_line, length))
    
    stats = {
        'count': len(line_lengths),
        'min': min(line_lengths) if line_lengths else 0,
        'max': max(line_lengths) if line_lengths else 0,
        'mean': statistics.mean(line_lengths) if line_lengths else 0,
        'median': statistics.median(line_lengths) if line_lengths else 0,
        'stdev': statistics.stdev(line_lengths) if len(line_lengths) > 1 else 0,
    }
    
    # Create histogram data
    histogram = {}
    for length in line_lengths:
        # Group into buckets of 10
        bucket = (length // 10) * 10
        histogram[bucket] = histogram.get(bucket, 0) + 1
    
    histogram_sorted = sorted(histogram.items())
    
    return stats, lines_with_counts, histogram_sorted

def generate_pdf(input_file, output_file):
    """Generate a PDF report of line length statistics."""
    stats, lines_with_counts, histogram = analyze_file(input_file)
    
    # Create histogram HTML
    max_count = max(histogram, key=lambda x: x[1])[1] if histogram else 0
    histogram_html = ""
    for bucket, count in histogram:
        percentage = (count / max_count) * 100 if max_count > 0 else 0
        histogram_html += f"""
        <div class="histogram-row">
            <span class="bucket">{bucket}-{bucket+9}</span>
            <div class="bar-container">
                <div class="bar" style="width: {percentage}%"></div>
                <span class="count">{count}</span>
            </div>
        </div>
        """
    
    # Create sample lines HTML
    sample_lines_html = ""
    # Show first 10 non-empty lines
    for line_num, line, length in lines_with_counts[:10]:
        sample_lines_html += f"""
        <tr>
            <td class="line-number">{line_num}</td>
            <td class="text">{line}</td>
            <td class="char-count">{length}</td>
        </tr>
        """
    
    html_content = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.5; padding: 20px; }}
            h1, h2 {{ color: #2c3e50; }}
            .stats {{ margin: 20px 0; }}
            .stats-table {{ border-collapse: collapse; width: 100%; }}
            .stats-table th, .stats-table td {{ padding: 8px; text-align: left; border-bottom: 1px solid #ddd; }}
            .stats-table th {{ background-color: #f2f2f2; }}
            
            .histogram {{ margin: 30px 0; }}
            .histogram-row {{ display: flex; margin-bottom: 5px; }}
            .bucket {{ width: 80px; text-align: right; padding-right: 10px; }}
            .bar-container {{ flex-grow: 1; display: flex; align-items: center; }}
            .bar {{ background-color: #3498db; height: 20px; }}
            .count {{ margin-left: 10px; }}
            
            .line-samples {{ width: 100%; border-collapse: collapse; }}
            .line-samples th, .line-samples td {{ padding: 8px; text-align: left; border-bottom: 1px solid #ddd; }}
            .line-samples th {{ background-color: #f2f2f2; }}
            .line-number {{ width: 50px; color: #7f8c8d; }}
            .text {{ font-family: monospace; }}
            .char-count {{ width: 80px; text-align: right; color: #e74c3c; }}
        </style>
    </head>
    <body>
        <h1>Line Length Analysis</h1>
        <p>File analyzed: {os.path.basename(input_file)}</p>
        
        <div class="stats">
            <h2>Statistics</h2>
            <table class="stats-table">
                <tr>
                    <th>Metric</th>
                    <th>Value</th>
                </tr>
                <tr>
                    <td>Total non-empty lines</td>
                    <td>{stats['count']}</td>
                </tr>
                <tr>
                    <td>Average characters per line</td>
                    <td>{stats['mean']:.2f}</td>
                </tr>
                <tr>
                    <td>Median characters per line</td>
                    <td>{stats['median']:.2f}</td>
                </tr>
                <tr>
                    <td>Minimum line length</td>
                    <td>{stats['min']}</td>
                </tr>
                <tr>
                    <td>Maximum line length</td>
                    <td>{stats['max']}</td>
                </tr>
                <tr>
                    <td>Standard deviation</td>
                    <td>{stats['stdev']:.2f}</td>
                </tr>
            </table>
        </div>
        
        <div class="histogram">
            <h2>Line Length Distribution</h2>
            {histogram_html}
        </div>
        
        <div class="samples">
            <h2>Sample Lines</h2>
            <table class="line-samples">
                <tr>
                    <th>Line #</th>
                    <th>Content</th>
                    <th>Length</th>
                </tr>
                {sample_lines_html}
            </table>
        </div>
    </body>
    </html>
    """
    
    # Create PDF
    HTML(string=html_content).write_pdf(
        output_file,
        stylesheets=[CSS(string='@page { size: letter; margin: 0.75in; }')]
    )
    
    print(f"Analysis complete.")
    print(f"Average characters per line: {stats['mean']:.2f}")
    print(f"Generated PDF report at {output_file}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python analyze_line_lengths.py <input_file> [output_file]")
        sys.exit(1)
    
    input_file = sys.argv[1]
    
    if len(sys.argv) >= 3:
        output_file = sys.argv[2]
    else:
        # Default output name based on input file
        output_file = os.path.splitext(input_file)[0] + "_line_analysis.pdf"
    
    generate_pdf(input_file, output_file) 