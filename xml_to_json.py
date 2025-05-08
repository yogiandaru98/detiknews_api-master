import os
import re
import json
import xml.etree.ElementTree as ET
from pathlib import Path

def fix_xml_content(xml_content):
    """Perbaiki karakter ilegal dan entitas yang tidak valid di XML."""

    # Hapus karakter tidak valid (karakter kontrol selain tab, newline, carriage return)
    xml_content = re.sub(r'[^\x09\x0A\x0D\x20-\uD7FF\uE000-\uFFFD]', '', xml_content)

    # Escape tanda & yang tidak diikuti oleh entitas valid
    xml_content = re.sub(r'&(?!amp;|lt;|gt;|quot;|apos;)', '&amp;', xml_content)

    return xml_content

def xml_to_dict(element):
    """Konversi elemen XML ke dictionary."""
    result = {}
    for child in element:
        if len(child) > 0:
            result[child.tag] = xml_to_dict(child)
        else:
            result[child.tag] = child.text.strip() if child.text else ""
    return result

def convert_xml_to_json(xml_path, json_path):
    """Konversi file XML menjadi JSON setelah diperbaiki kontennya."""
    try:
        with open(xml_path, 'r', encoding='utf-8-sig') as f:
            xml_content = f.read().strip().lstrip('\ufeff')

        fixed_xml = fix_xml_content(xml_content)
        root = ET.fromstring(fixed_xml)
        data_dict = {root.tag: xml_to_dict(root)}

        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data_dict, f, indent=4, ensure_ascii=False)

        return True
    except ET.ParseError as e:
        print(f"❌ ERROR parsing {xml_path.name}: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ ERROR converting {xml_path.name}: {str(e)}")
        return False

def main():
    current_dir = Path(__file__).parent
    xml_input_dir = current_dir / "split_data"
    json_output_dir = current_dir / "json_output"
    json_output_dir.mkdir(exist_ok=True)

    if not xml_input_dir.exists():
        print(f"❌ Folder tidak ditemukan: {xml_input_dir}")
        return

    xml_files = list(xml_input_dir.glob("*.xml"))
    if not xml_files:
        print("❌ Tidak ada file XML ditemukan.")
        return

    print(f"🔄 Memulai konversi {len(xml_files)} file XML ke JSON...")

    success_count = 0
    for xml_file in xml_files:
        json_file = json_output_dir / f"{xml_file.stem}.json"
        if convert_xml_to_json(xml_file, json_file):
            success_count += 1

    print("\n📊 Hasil konversi:")
    print(f"✅ Berhasil: {success_count}")
    print(f"❌ Gagal: {len(xml_files) - success_count}")
    print(f"📁 Output JSON tersimpan di: {json_output_dir}")

if __name__ == "__main__":
    main()
