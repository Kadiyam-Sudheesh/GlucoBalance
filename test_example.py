"""
Test script for GlucoBalance - writes output to file to avoid console encoding issues.
"""
import sys
import io

# Set UTF-8 encoding for stdout
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from glucobalance import GlucoBalance, create_example_context

# Create example context
context = create_example_context()

# Generate analysis
assistant = GlucoBalance()
report = assistant.generate_comprehensive_analysis(context)

# Write to file
with open('sample_output.txt', 'w', encoding='utf-8') as f:
    f.write(report)

print("Analysis generated successfully!")
print("Output written to 'sample_output.txt'")
print(f"Report length: {len(report)} characters")
