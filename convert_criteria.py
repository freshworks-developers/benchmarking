#!/usr/bin/env python3
"""
Convert plain text criteria to JSON format
Helps users who want to paste requirements as plain text instead of JSON

Usage:
    python3 convert_criteria.py
    (paste your plain text requirements)
    (type 'END' when done)
"""

import json
import sys

def parse_plain_text_criteria():
    """Parse plain text criteria into structured JSON"""
    print("\n" + "="*80)
    print("📝 PASTE YOUR REQUIREMENTS (Plain Text)")
    print("="*80)
    print("\nPaste your requirements below. Type 'END' on a new line when done.")
    print("\nExample format:")
    print("""
App Type: Frontend
Product: freshdesk

Requirements:
- OAuth 2.0
- Webhooks
- Platform 3.0
- Crayons UI

Features:
- Request templates
- Data methods
- Custom iParams

Expected Files:
- manifest.json
- server/server.js
- config/oauth_config.json

Description:
Ticket automation app with external API integration
""")
    print("\nYour requirements:")
    print("-" * 80)
    
    lines = []
    try:
        while True:
            line = input()
            if line.strip().upper() == 'END':
                break
            lines.append(line)
    except EOFError:
        pass
    
    return lines

def convert_to_json(lines):
    """Convert plain text lines to JSON criteria"""
    criteria = {
        "requirements": [],
        "expected_files": [],
        "description": ""
    }
    
    current_section = None
    description_lines = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Detect sections
        line_lower = line.lower()
        if line_lower.startswith('requirements:') or line_lower.startswith('requirement:'):
            current_section = 'requirements'
            continue
        elif line_lower.startswith('features:') or line_lower.startswith('feature:'):
            current_section = 'requirements'
            continue
        elif line_lower.startswith('expected files:') or line_lower.startswith('files:'):
            current_section = 'files'
            continue
        elif line_lower.startswith('description:'):
            current_section = 'description'
            continue
        elif line_lower.startswith('app type:') or line_lower.startswith('product:'):
            # Skip metadata lines
            continue
        
        # Process based on current section
        if current_section == 'requirements':
            # Remove leading dash/bullet if present
            item = line.lstrip('•-*').strip()
            if item and item not in criteria['requirements']:
                criteria['requirements'].append(item)
        elif current_section == 'files':
            item = line.lstrip('•-*').strip()
            if item and item not in criteria['expected_files']:
                criteria['expected_files'].append(item)
        elif current_section == 'description':
            description_lines.append(line)
        else:
            # If no section detected, treat as requirement
            item = line.lstrip('•-*').strip()
            if item and item not in criteria['requirements']:
                criteria['requirements'].append(item)
    
    # Join description lines
    if description_lines:
        criteria['description'] = ' '.join(description_lines)
    
    # Auto-detect expected files if not provided
    if not criteria['expected_files']:
        criteria['expected_files'] = [
            "manifest.json",
            "app/index.html",
            "app/scripts/app.js",
            "server/server.js",
            "config/iparams.json"
        ]
    
    return criteria

def main():
    print("\n🔄 Plain Text to JSON Converter")
    print("Convert your plain text requirements to JSON format for setup_test.py\n")
    
    lines = parse_plain_text_criteria()
    
    if not lines:
        print("\n❌ No input provided")
        return
    
    criteria = convert_to_json(lines)
    
    print("\n" + "="*80)
    print("✅ CONVERTED TO JSON")
    print("="*80)
    print("\nGenerated JSON:")
    print("-" * 80)
    json_output = json.dumps(criteria, indent=2)
    print(json_output)
    print("-" * 80)
    
    # Save to file
    output_file = "converted-criteria.json"
    with open(output_file, 'w') as f:
        f.write(json_output)
    
    print(f"\n✅ Saved to: {output_file}")
    print("\n" + "="*80)
    print("📋 NEXT STEPS")
    print("="*80)
    print("\n1. Review the JSON above")
    print("2. Edit converted-criteria.json if needed")
    print("3. Use with setup_test.py:")
    print(f"\n   python3 setup_test.py APP001 --criteria-file {output_file}")
    print("\n" + "="*80)

if __name__ == '__main__':
    main()
