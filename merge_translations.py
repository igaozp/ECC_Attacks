#!/usr/bin/env python3
"""
Merge all translated files into README_zh.md
"""

def merge_translated_files():
    # List of translated files in order
    files = [
        '00_known_attacks_on_elliptic_curve_cryptography_zh.md',
        '01_introduction_zh.md',
        '02_introduction_to_elliptic_curves_zh.md',
        '03_elliptic_curves_in_the_context_of_cryptography_zh.md',
        '04_ecc_attacks_zh.md',
        '05_ecdh_attacks_zh.md',
        '06_ecdsa_attacks_zh.md',
        '07_conclusion_zh.md'
    ]

    output_content = []

    for filename in files:
        filepath = f'/home/user/ECC_Attacks/docs/{filename}'
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                # Remove leading/trailing whitespace but keep internal structure
                content = content.strip()
                output_content.append(content)
                print(f"Added: {filename}")
        except FileNotFoundError:
            print(f"Warning: File not found: {filename}")

    # Join all content with double newlines between sections
    final_content = '\n\n'.join(output_content)

    # Write to README_zh.md
    output_path = '/home/user/ECC_Attacks/README_zh.md'
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(final_content)

    print(f"\n✓ Successfully created {output_path}")
    print(f"Total size: {len(final_content)} characters")

if __name__ == '__main__':
    merge_translated_files()
