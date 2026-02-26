#!/usr/bin/env python3
"""
Setup Test Script
Quickly set up test criteria and prepare apps for evaluation

Usage:
    python3 setup_test.py APP001
    python3 setup_test.py APP001 --criteria-file criteria.json
    python3 setup_test.py APP001 --app-path /path/to/app
"""

import os
import sys
import json
import shutil
from pathlib import Path
from datetime import datetime

class TestSetup:
    def __init__(self):
        self.script_dir = Path(__file__).parent
        self.test_apps_dir = self.script_dir / 'test-apps'
        self.test_criteria_dir = self.script_dir / 'test-criteria'
        self.use_cases_file = self.script_dir / 'use-cases' / 'use_cases.json'
        
        # Create directories if they don't exist
        self.test_apps_dir.mkdir(exist_ok=True)
        self.test_criteria_dir.mkdir(exist_ok=True)
    
    def fix_common_typos(self, text):
        """Fix common typos in requirements"""
        typo_map = {
            'erverless': 'Serverless',
            'serverles': 'Serverless',
            'frontent': 'Frontend',
            'frontned': 'Frontend',
            'iparam': 'iParam',
            'iparms': 'iParams',
            'oAuth': 'OAuth',
            'oauth': 'OAuth',
            'wehbook': 'Webhook',
            'webhok': 'Webhook',
            'crayons': 'Crayons',
            'crayon': 'Crayons'
        }
        
        for typo, correct in typo_map.items():
            if typo.lower() in text.lower():
                # Case-insensitive replacement
                import re
                text = re.sub(re.escape(typo), correct, text, flags=re.IGNORECASE)
        
        return text
    
    def parse_plain_text_to_criteria(self, lines):
        """Convert plain text lines to criteria JSON"""
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
            if any(keyword in line_lower for keyword in ['requirements:', 'requirement:', 'features:', 'feature:']):
                current_section = 'requirements'
                continue
            elif any(keyword in line_lower for keyword in ['expected files:', 'files:']):
                current_section = 'files'
                continue
            elif 'description:' in line_lower:
                current_section = 'description'
                continue
            elif any(keyword in line_lower for keyword in ['app type:', 'product:', 'type:']):
                # Skip metadata lines
                continue
            
            # Process based on current section
            if current_section == 'requirements':
                item = line.lstrip('•-*').strip()
                # Fix common typos
                item = self.fix_common_typos(item)
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
                # Fix common typos
                item = self.fix_common_typos(item)
                if item and item not in criteria['requirements']:
                    criteria['requirements'].append(item)
        
        # Join description lines
        if description_lines:
            criteria['description'] = ' '.join(description_lines)
        
        # Auto-detect expected files if not provided
        if not criteria['expected_files']:
            # Detect app type from requirements
            all_requirements_text = ' '.join(criteria['requirements']).lower()
            
            is_frontend = any(keyword in all_requirements_text for keyword in ['frontend', 'front-end', 'ui', 'sidebar', 'full_page'])
            is_serverless = any(keyword in all_requirements_text for keyword in ['serverless', 'server-less', 'backend', 'webhook', 'scheduled event', 'event'])
            
            # Base files
            criteria['expected_files'] = ["manifest.json"]
            
            # Frontend files
            if is_frontend or not is_serverless:
                criteria['expected_files'].extend([
                    "app/index.html",
                    "app/scripts/app.js"
                ])
            
            # Serverless files
            if is_serverless:
                criteria['expected_files'].append("server/server.js")
            
            # Common config files
            if any(keyword in all_requirements_text for keyword in ['iparam', 'config', 'setting']):
                criteria['expected_files'].append("config/iparams.json")
            
            if any(keyword in all_requirements_text for keyword in ['request', 'api', 'http']):
                criteria['expected_files'].append("config/requests.json")
            
            if any(keyword in all_requirements_text for keyword in ['oauth', 'authentication']):
                criteria['expected_files'].append("config/oauth_config.json")
        
        return criteria
    
    def get_criteria_from_user(self):
        """Get criteria from user input (accepts both JSON and plain text)"""
        print("\n" + "="*80)
        print("📋 PASTE YOUR CRITERIA (JSON or Plain Text)")
        print("="*80)
        print("\nPaste your criteria below. Type 'END' on a new line when done.")
        print("\nAccepts JSON format:")
        print('''{
  "requirements": ["OAuth 2.0", "Webhooks"],
  "expected_files": ["manifest.json", "server/server.js"],
  "description": "Your app description"
}''')
        print("\nOR Plain text format:")
        print('''Requirements:
- OAuth 2.0
- Webhooks
- Platform 3.0

Features:
- Request templates
- Data methods

Description:
Your app description''')
        print("\nYour input:")
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
        
        if not lines:
            return None
        
        text = '\n'.join(lines)
        
        # Try to parse as JSON first
        try:
            criteria = json.loads(text)
            print("\n✅ Parsed as JSON")
            return criteria
        except json.JSONDecodeError:
            # Not JSON, try plain text
            print("\n📝 Detected plain text format, converting to JSON...")
            criteria = self.parse_plain_text_to_criteria(lines)
            
            if criteria['requirements'] or criteria['expected_files'] or criteria['description']:
                print("✅ Converted to JSON successfully!")
                return criteria
            else:
                print("❌ Could not parse input. Please provide requirements or files.")
                return None
    
    def save_criteria(self, app_id, criteria):
        """Save criteria to JSON file"""
        criteria_file = self.test_criteria_dir / f'{app_id}-criteria.json'
        
        # Add metadata
        full_criteria = {
            "app_id": app_id,
            "created_at": datetime.now().isoformat(),
            **criteria
        }
        
        with open(criteria_file, 'w') as f:
            json.dump(full_criteria, f, indent=2)
        
        print(f"\n✅ Criteria saved to: {criteria_file}")
        return criteria_file
    
    def setup_app_directory(self, app_id, source_path=None):
        """Set up app directory in test-apps"""
        app_dir = self.test_apps_dir / app_id
        
        if app_dir.exists():
            print(f"\n⚠️  Directory already exists: {app_dir}")
            response = input("Overwrite? (y/n): ").lower()
            if response != 'y':
                print("❌ Cancelled")
                return None
            shutil.rmtree(app_dir)
        
        app_dir.mkdir(parents=True)
        print(f"\n✅ Created directory: {app_dir}")
        
        if source_path:
            source = Path(source_path)
            if not source.exists():
                print(f"❌ Source path not found: {source_path}")
                return None
            
            print(f"\n📦 Copying app from: {source_path}")
            if source.is_dir():
                shutil.copytree(source, app_dir, dirs_exist_ok=True)
            else:
                print("❌ Source must be a directory")
                return None
            print("✅ App copied successfully!")
        else:
            print(f"\n📁 Empty directory created. Copy your app to: {app_dir}")
        
        return app_dir
    
    def get_use_case_info(self, app_id):
        """Get use case info if it exists"""
        if not self.use_cases_file.exists():
            return None
        
        try:
            with open(self.use_cases_file, 'r') as f:
                data = json.load(f)
            
            use_cases = data.get('use_cases', [])
            for uc in use_cases:
                if uc['id'] == app_id:
                    return uc
        except:
            pass
        
        return None
    
    def generate_evaluation_command(self, app_id, criteria):
        """Generate the evaluation command"""
        app_dir = self.test_apps_dir / app_id
        
        # Build command
        cmd_parts = ['python3', 'automate_test.py', '--evaluate', f'test-apps/{app_id}']
        
        # Add app-id
        cmd_parts.extend(['--app-id', app_id])
        
        # Add requirements if present
        if 'requirements' in criteria:
            reqs = ','.join(criteria['requirements'])
            cmd_parts.extend(['--requirements', f'"{reqs}"'])
        
        return ' '.join(cmd_parts)
    
    def print_summary(self, app_id, criteria_file, app_dir, eval_command):
        """Print setup summary"""
        print("\n" + "="*80)
        print("✅ SETUP COMPLETE")
        print("="*80)
        print(f"\nApp ID: {app_id}")
        print(f"Criteria: {criteria_file}")
        print(f"App Directory: {app_dir}")
        
        print("\n" + "="*80)
        print("📋 NEXT STEPS")
        print("="*80)
        
        if not app_dir or not list(Path(app_dir).glob('*')):
            print("\n1. Copy your app to the directory:")
            print(f"   cp -r /path/to/your/app/* {app_dir}/")
            print("\n2. Run evaluation:")
        else:
            print("\n1. Run evaluation:")
        
        print(f"   {eval_command}")
        
        print("\n" + "="*80)
    
    def run(self, app_id, criteria_file=None, app_path=None):
        """Main setup flow"""
        print("\n" + "="*80)
        print(f"🚀 SETTING UP TEST FOR {app_id}")
        print("="*80)
        
        # Check if use case exists
        use_case = self.get_use_case_info(app_id)
        if use_case:
            print(f"\n📌 Found existing use case: {use_case['name']}")
            print(f"   Type: {use_case['app_type']}")
            print(f"   Product: {use_case['product']}")
        
        # Get or load criteria
        if criteria_file:
            print(f"\n📄 Loading criteria from: {criteria_file}")
            try:
                with open(criteria_file, 'r') as f:
                    criteria = json.load(f)
            except Exception as e:
                print(f"❌ Error loading criteria: {e}")
                return
        else:
            criteria = self.get_criteria_from_user()
            if not criteria:
                print("\n❌ Setup cancelled - invalid criteria")
                return
        
        # Display criteria
        print("\n" + "="*80)
        print("📋 CRITERIA SUMMARY")
        print("="*80)
        print(json.dumps(criteria, indent=2))
        
        # Confirm (skip if criteria file was provided)
        if not criteria_file:
            response = input("\n✅ Save this criteria? (y/n): ").lower()
            if response != 'y':
                print("❌ Cancelled")
                return
        else:
            print("\n✅ Using criteria from file")
        
        # Save criteria
        criteria_file = self.save_criteria(app_id, criteria)
        
        # Setup app directory
        app_dir = self.setup_app_directory(app_id, app_path)
        
        # Generate evaluation command
        eval_command = self.generate_evaluation_command(app_id, criteria)
        
        # Print summary
        self.print_summary(app_id, criteria_file, app_dir, eval_command)

def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Setup test criteria and app directory for evaluation',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Interactive mode - paste criteria JSON (type 'END' when done)
  python3 setup_test.py APP001
  
  # Load criteria from file (recommended)
  python3 setup_test.py APP001 --criteria-file my-criteria.json
  
  # Copy app from existing location
  python3 setup_test.py APP001 --app-path /path/to/my/app
  
  # Both criteria file and app path
  python3 setup_test.py APP001 --criteria-file criteria.json --app-path /path/to/app

Criteria JSON format:
  {
    "requirements": ["OAuth 2.0", "Webhooks", "Platform 3.0"],
    "expected_files": ["manifest.json", "server/server.js"],
    "description": "What this app should do"
  }

Interactive mode tip:
  After pasting JSON, type 'END' on a new line and press Enter.
  Or use Ctrl+D (Mac/Linux) or Ctrl+Z+Enter (Windows).
        '''
    )
    
    parser.add_argument('app_id', help='App ID (e.g., APP001, CUSTOM_APP)')
    parser.add_argument('--criteria-file', help='Path to criteria JSON file')
    parser.add_argument('--app-path', help='Path to existing app to copy')
    
    args = parser.parse_args()
    
    setup = TestSetup()
    setup.run(args.app_id, args.criteria_file, args.app_path)

if __name__ == '__main__':
    main()
