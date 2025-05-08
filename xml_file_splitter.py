import os
import xml.etree.ElementTree as ET
from xml.sax.saxutils import escape

def split_xml_by_data(input_file, output_dir):
    """Split XML file by <data> elements into separate files using a more robust approach."""
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Read the entire file content
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract XML declaration and root opening tag
    xml_declaration = content.split('\n')[0].strip()
    root_opening_tag = content.split('\n')[1].strip()
    root_tag = root_opening_tag[1:].split(' ')[0].split('>')[0]
    
    # Find all <data>...</data> sections
    data_sections = []
    start_tag = '<data>'
    end_tag = '</data>'
    start = 0
    
    while True:
        start_idx = content.find(start_tag, start)
        if start_idx == -1:
            break
        end_idx = content.find(end_tag, start_idx) + len(end_tag)
        data_sections.append(content[start_idx:end_idx])
        start = end_idx
    
    # Process each data section
    for i, data_section in enumerate(data_sections, start=1):
        # Create output filename
        output_file = os.path.join(output_dir, f"data_{i}.xml")
        
        # Write the complete XML structure
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"{xml_declaration}\n")
            f.write(f"{root_opening_tag}\n")
            f.write(f"{data_section}\n")
            f.write(f"</{root_tag}>")
        
        print(f"Created: {output_file}")

if __name__ == "__main__":
    # Configuration
    input_file = 'berita.xml'  # Input XML file in project root
    output_dir = 'split_data'  # Output directory in project root
    
    # Run the splitting process
    print(f"Splitting {input_file} by <data> elements...")
    try:
        split_xml_by_data(input_file, output_dir)
        print(f"\nProcess completed. Files saved to: {os.path.abspath(output_dir)}")
    except Exception as e:
        print(f"\nError occurred: {str(e)}")
        print("Please check if your XML file is well-formed and try again.")