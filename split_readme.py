#!/usr/bin/env python3
"""
Split README.md into separate files by main sections
"""

def split_readme():
    with open('/home/user/ECC_Attacks/README.md', 'r', encoding='utf-8') as f:
        content = f.read()

    lines = content.split('\n')

    sections = []
    current_section = {'title': 'header', 'content': []}
    in_main_content = False

    for i, line in enumerate(lines):
        # Main section headers (single #)
        if line.startswith('# ') and not line.startswith('## '):
            if current_section['content']:
                sections.append(current_section)

            # Extract section title for filename
            title = line[2:].strip()
            # Clean title for filename
            filename = title.lower().replace(' ', '_').replace('-', '_')
            filename = ''.join(c for c in filename if c.isalnum() or c == '_')

            current_section = {
                'title': title,
                'filename': filename,
                'content': [line]
            }
            in_main_content = True
        else:
            current_section['content'].append(line)

    # Add the last section
    if current_section['content']:
        sections.append(current_section)

    # Write sections to files
    for idx, section in enumerate(sections):
        if section['title'] == 'header':
            filename = f'/home/user/ECC_Attacks/docs/00_header.md'
        else:
            filename = f'/home/user/ECC_Attacks/docs/{idx:02d}_{section["filename"]}.md'

        with open(filename, 'w', encoding='utf-8') as f:
            f.write('\n'.join(section['content']))

        print(f"Created: {filename}")
        print(f"  Title: {section['title']}")
        print(f"  Lines: {len(section['content'])}")
        print()

if __name__ == '__main__':
    split_readme()
