#!/usr/bin/env python3
"""
Split README.md into separate files by main sections (ignoring code blocks)
"""

def split_readme():
    with open('/home/user/ECC_Attacks/README.md', 'r', encoding='utf-8') as f:
        content = f.read()

    lines = content.split('\n')

    sections = []
    current_section = None
    in_code_block = False

    for i, line in enumerate(lines):
        # Track code blocks
        if line.strip().startswith('```'):
            in_code_block = not in_code_block

        # Main section headers (single #) - only if NOT in code block
        if line.startswith('# ') and not line.startswith('## ') and not in_code_block:
            # Save previous section
            if current_section is not None:
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
        else:
            if current_section is None:
                # Before first section (table of contents, etc.)
                if 'toc' not in locals():
                    toc = {'title': 'Table of Contents', 'filename': 'toc', 'content': [line]}
                else:
                    toc['content'].append(line)
            else:
                current_section['content'].append(line)

    # Add the last section
    if current_section:
        sections.append(current_section)

    # Add TOC as first section
    if 'toc' in locals():
        sections.insert(0, toc)

    # Clear docs directory first
    import os
    import shutil
    docs_dir = '/home/user/ECC_Attacks/docs'
    if os.path.exists(docs_dir):
        shutil.rmtree(docs_dir)
    os.makedirs(docs_dir)

    # Write sections to files
    for idx, section in enumerate(sections):
        filename = f'/home/user/ECC_Attacks/docs/{idx:02d}_{section["filename"]}.md'

        with open(filename, 'w', encoding='utf-8') as f:
            f.write('\n'.join(section['content']))

        print(f"Created: {filename}")
        print(f"  Title: {section['title']}")
        print(f"  Lines: {len(section['content'])}")
        print()

    print(f"\nTotal sections: {len(sections)}")

if __name__ == '__main__':
    split_readme()
