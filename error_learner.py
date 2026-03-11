#!/usr/bin/env python3
"""
Error Learning System - Automatically update skill from FDK validation failures

This script:
1. Tracks all FDK validation errors
2. Identifies new error patterns
3. Suggests skill updates
4. Applies updates to prevent future occurrences
"""

import json
import re
from pathlib import Path
from datetime import datetime
from collections import defaultdict, Counter

class ErrorLearner:
    """Learn from FDK validation failures and update skill"""
    
    def __init__(self, skill_root):
        self.skill_root = Path(skill_root)
        self.error_db_path = self.skill_root / '.dev' / 'comparison' / 'error_database.json'
        self.skill_updates_path = self.skill_root / '.dev' / 'planning' / 'AUTO_SKILL_UPDATES.md'
        
        # Initialize error database
        self.error_db = self.load_error_database()
        
        # Error patterns to track
        self.error_patterns = {
            'platform_errors': [],
            'lint_errors': [],
            'warnings': [],
            'first_seen': {},
            'occurrence_count': defaultdict(int),
            'fixed_errors': []
        }
    
    def load_error_database(self):
        """Load existing error database or create new one"""
        if self.error_db_path.exists():
            with open(self.error_db_path, 'r') as f:
                return json.load(f)
        else:
            return {
                'errors': [],
                'patterns': {},
                'skill_updates': [],
                'last_updated': None
            }
    
    def save_error_database(self):
        """Save error database to file"""
        self.error_db_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.error_db_path, 'w') as f:
            json.dump(self.error_db, f, indent=2)
        
        print(f"✅ Error database saved to {self.error_db_path}")
    
    def parse_fdk_output(self, validation_output):
        """Parse FDK validation output to extract errors"""
        errors = {
            'platform_errors': [],
            'lint_errors': [],
            'warnings': [],
            'summary': {}
        }
        
        lines = validation_output.split('\n')
        current_section = None
        
        for line in lines:
            # Detect section
            if 'Platform errors:' in line:
                current_section = 'platform'
            elif 'Lint errors:' in line:
                current_section = 'lint'
            elif 'Please ensure that the following are addressed' in line:
                current_section = 'warnings'
            
            # Extract errors
            if line.strip().startswith('✖'):
                error_msg = line.strip().replace('✖ ', '')
                
                # Parse error details
                error_detail = self.parse_error_detail(error_msg)
                
                if current_section == 'platform':
                    errors['platform_errors'].append(error_detail)
                elif current_section == 'lint':
                    errors['lint_errors'].append(error_detail)
            
            elif line.strip().startswith('⚠'):
                warning_msg = line.strip().replace('⚠ ', '')
                warning_detail = self.parse_error_detail(warning_msg)
                errors['warnings'].append(warning_detail)
            
            # Extract summary
            elif 'Total Platform Errors:' in line:
                match = re.search(r'Total Platform Errors:\s*(\d+)', line)
                if match:
                    errors['summary']['platform_errors'] = int(match.group(1))
            elif 'Total Lint Errors:' in line:
                match = re.search(r'Total Lint Errors:\s*(\d+)', line)
                if match:
                    errors['summary']['lint_errors'] = int(match.group(1))
            elif 'Total Warnings:' in line:
                match = re.search(r'Total Warnings:\s*(\d+)', line)
                if match:
                    errors['summary']['warnings'] = int(match.group(1))
        
        return errors
    
    def parse_error_detail(self, error_msg):
        """Parse error message to extract details"""
        detail = {
            'raw_message': error_msg,
            'file': None,
            'line': None,
            'error_type': None,
            'message': error_msg,
            'pattern': None
        }
        
        # Extract file and line number (e.g., "server/server.js::42:")
        file_match = re.match(r'([^:]+)::(\d+):\s*(.+)', error_msg)
        if file_match:
            detail['file'] = file_match.group(1)
            detail['line'] = int(file_match.group(2))
            detail['message'] = file_match.group(3)
        
        # Identify error patterns
        detail['pattern'] = self.identify_error_pattern(detail['message'])
        detail['error_type'] = self.categorize_error(detail['message'])
        
        return detail
    
    def identify_error_pattern(self, message):
        """Identify the error pattern for categorization using comprehensive patterns"""
        # Try to use comprehensive patterns first
        try:
            from error_patterns_comprehensive import get_pattern_for_error
            pattern_name, pattern_data = get_pattern_for_error(message)
            return pattern_name
        except ImportError:
            # Fallback to basic patterns if comprehensive module not available
            patterns = {
                'deprecated_request_api': r'(post|get|put|delete) is no longer supported in Request API',
                'async_no_await': r'Async function .* has no .await. expression',
                'unused_parameter': r"'.*' is (defined but never used|assigned a value but never used)",
                'function_complexity': r'has a complexity of (\d+)\. Maximum allowed is',
                'variable_scoping': r"'.*' (declared|assigned) (in different scopes|a value but never used)",
                'whitelisted_domains': r'"whitelisted-domains" has been deprecated',
                'invalid_location': r'Invalid location\(s\) mentioned in modules',
                'oauth_integrations': r'OAuth config must have required property .integrations.',
                'oauth_additional_props': r'OAuth config must NOT have additional properties',
                'missing_icon': r'Icon .* is not found',
                'missing_file': r'Template file .* is not found',
                'missing_module': r'Missing locations for module',
                'request_schema_error': r'Request template .* schema',
                'product_field_deprecated': r'(Platform version >= 3\.0 does not support "product"|"product".*deprecated|must use "modules")',
            }
            
            for pattern_name, regex in patterns.items():
                if re.search(regex, message, re.IGNORECASE):
                    return pattern_name
            
            return 'unknown'
    
    def categorize_error(self, message):
        """Categorize error into broad types"""
        if any(keyword in message.lower() for keyword in ['deprecated', 'no longer supported']):
            return 'deprecated_api'
        elif any(keyword in message.lower() for keyword in ['async', 'await']):
            return 'async_pattern'
        elif any(keyword in message.lower() for keyword in ['unused', 'never used']):
            return 'unused_code'
        elif any(keyword in message.lower() for keyword in ['complexity']):
            return 'code_complexity'
        elif any(keyword in message.lower() for keyword in ['oauth']):
            return 'oauth_config'
        elif any(keyword in message.lower() for keyword in ['location', 'module']):
            return 'manifest_structure'
        elif any(keyword in message.lower() for keyword in ['not found', 'missing']):
            return 'missing_file'
        elif any(keyword in message.lower() for keyword in ['schema', 'request template']):
            return 'request_config'
        else:
            return 'other'
    
    def record_error(self, app_id, error_data):
        """Record error in database"""
        error_record = {
            'app_id': app_id,
            'timestamp': datetime.now().isoformat(),
            'platform_errors': error_data['platform_errors'],
            'lint_errors': error_data['lint_errors'],
            'warnings': error_data['warnings'],
            'summary': error_data['summary']
        }
        
        self.error_db['errors'].append(error_record)
        
        # Update patterns
        for error_type in ['platform_errors', 'lint_errors', 'warnings']:
            for error in error_data[error_type]:
                pattern = error['pattern']
                if pattern not in self.error_db['patterns']:
                    self.error_db['patterns'][pattern] = {
                        'count': 0,
                        'first_seen': datetime.now().isoformat(),
                        'examples': [],
                        'fixed': False
                    }
                
                self.error_db['patterns'][pattern]['count'] += 1
                
                # Store first 3 examples
                if len(self.error_db['patterns'][pattern]['examples']) < 3:
                    self.error_db['patterns'][pattern]['examples'].append({
                        'app_id': app_id,
                        'message': error['raw_message']
                    })
        
        self.error_db['last_updated'] = datetime.now().isoformat()
        self.save_error_database()
    
    def identify_new_patterns(self):
        """Identify new error patterns that need skill updates"""
        new_patterns = []
        
        for pattern, data in self.error_db['patterns'].items():
            # Consider patterns with 2+ occurrences that aren't fixed yet
            if data['count'] >= 2 and not data.get('fixed', False):
                new_patterns.append({
                    'pattern': pattern,
                    'count': data['count'],
                    'first_seen': data['first_seen'],
                    'examples': data['examples']
                })
        
        return sorted(new_patterns, key=lambda x: x['count'], reverse=True)
    
    def generate_skill_update(self, pattern_data):
        """Generate skill update suggestion for a pattern"""
        pattern = pattern_data['pattern']
        examples = pattern_data['examples']
        
        updates = {
            'deprecated_request_api': {
                'title': 'NEVER Use Deprecated Request API Methods',
                'section': 'Code Quality Requirements',
                'wrong': '$request.post(), $request.get(), $request.put(), $request.delete()',
                'correct': '$request.invokeTemplate()',
                'explanation': 'Platform 3.0 requires using request templates defined in config/requests.json'
            },
            'async_no_await': {
                'title': 'Only Use async When You Actually await',
                'section': 'Code Quality Requirements',
                'wrong': 'async function without await inside',
                'correct': 'Remove async keyword if no await',
                'explanation': 'Unnecessary async keywords cause lint errors'
            },
            'unused_parameter': {
                'title': 'No Unused Parameters',
                'section': 'Code Quality Requirements',
                'wrong': 'function handler(args) { // args never used }',
                'correct': 'function handler() { // no unused params }',
                'explanation': 'FDK linter flags unused parameters as errors'
            },
            'function_complexity': {
                'title': 'Function Complexity Max 7',
                'section': 'Code Quality Requirements',
                'wrong': 'Complex nested functions with high cyclomatic complexity',
                'correct': 'Break into smaller helper functions',
                'explanation': 'FDK enforces maximum complexity of 7'
            },
            'whitelisted_domains': {
                'title': 'NEVER Use whitelisted-domains',
                'section': 'Manifest Structure',
                'wrong': '"whitelisted-domains": ["https://..."]',
                'correct': 'Use request templates in config/requests.json',
                'explanation': 'whitelisted-domains is deprecated in Platform 3.0'
            },
            'invalid_location': {
                'title': 'Correct Location Placement',
                'section': 'Manifest Structure',
                'wrong': 'ticket_sidebar in common module',
                'correct': 'ticket_sidebar in support_ticket/service_ticket module',
                'explanation': 'Product-specific locations must be in product modules'
            },
            'oauth_integrations': {
                'title': 'OAuth Config Requires integrations Wrapper',
                'section': 'OAuth Configuration',
                'wrong': '{ "client_id": "...", "client_secret": "..." }',
                'correct': '{ "integrations": { "oauth_name": { ... } } }',
                'explanation': 'Platform 3.0 requires integrations wrapper in oauth_config.json'
            },
            'missing_icon': {
                'title': 'ALWAYS Generate icon.svg',
                'section': 'File Structure',
                'wrong': 'Skipping icon.svg file generation',
                'correct': 'Always create app/styles/images/icon.svg',
                'explanation': 'Icon file must exist even if manifest references it'
            },
        }
        
        return updates.get(pattern, {
            'title': f'Fix {pattern}',
            'section': 'General',
            'wrong': 'Pattern that causes error',
            'correct': 'Correct pattern',
            'explanation': f'Based on {pattern_data["count"]} occurrences'
        })
    
    def create_skill_update_document(self, new_patterns):
        """Create markdown document with skill update suggestions"""
        if not new_patterns:
            print("✅ No new error patterns detected!")
            return
        
        content = [
            "# Automatic Skill Updates from FDK Validation Failures",
            "",
            f"**Generated:** {datetime.now().strftime('%B %d, %Y at %H:%M')}",
            f"**New Patterns Detected:** {len(new_patterns)}",
            "",
            "---",
            "",
            "## 📊 Error Patterns Requiring Skill Updates",
            ""
        ]
        
        for i, pattern_data in enumerate(new_patterns, 1):
            update = self.generate_skill_update(pattern_data)
            
            content.extend([
                f"## {i}. {update['title']}",
                "",
                f"**Pattern:** `{pattern_data['pattern']}`",
                f"**Occurrences:** {pattern_data['count']}",
                f"**First Seen:** {pattern_data['first_seen']}",
                f"**Target Section:** {update['section']}",
                "",
                "### Examples from Apps",
                ""
            ])
            
            for ex in pattern_data['examples']:
                content.extend([
                    f"**{ex['app_id']}:**",
                    f"```",
                    f"{ex['message']}",
                    f"```",
                    ""
                ])
            
            content.extend([
                "### Suggested Skill Update",
                "",
                f"**Add to:** `.cursor/rules/freshworks-platform3.mdc` - {update['section']}",
                "",
                "```markdown",
                f"### Rule: {update['title']}",
                "",
                f"❌ WRONG: {update['wrong']}",
                "",
                f"✅ CORRECT: {update['correct']}",
                "",
                f"**Explanation:** {update['explanation']}",
                "```",
                "",
                "### Validation Checklist Addition",
                "",
                "```markdown",
                f"- [ ] **{update['title']}** ✅",
                f"  - Explanation: {update['explanation']}",
                "```",
                "",
                "---",
                ""
            ])
        
        # Save to file
        self.skill_updates_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.skill_updates_path, 'w') as f:
            f.write('\n'.join(content))
        
        print(f"✅ Skill update suggestions saved to {self.skill_updates_path}")
        print(f"📊 {len(new_patterns)} new patterns require attention")
    
    def mark_pattern_as_fixed(self, pattern):
        """Mark a pattern as fixed in the skill"""
        if pattern in self.error_db['patterns']:
            self.error_db['patterns'][pattern]['fixed'] = True
            self.error_db['patterns'][pattern]['fixed_date'] = datetime.now().isoformat()
            self.save_error_database()
            print(f"✅ Marked pattern '{pattern}' as fixed")
    
    def get_statistics(self):
        """Get error statistics"""
        stats = {
            'total_errors_recorded': len(self.error_db['errors']),
            'unique_patterns': len(self.error_db['patterns']),
            'fixed_patterns': sum(1 for p in self.error_db['patterns'].values() if p.get('fixed', False)),
            'unfixed_patterns': sum(1 for p in self.error_db['patterns'].values() if not p.get('fixed', False)),
            'most_common_patterns': []
        }
        
        # Get top 10 most common patterns
        pattern_counts = [(p, data['count']) for p, data in self.error_db['patterns'].items()]
        pattern_counts.sort(key=lambda x: x[1], reverse=True)
        stats['most_common_patterns'] = pattern_counts[:10]
        
        return stats


def main():
    """Main function for testing"""
    import sys
    
    skill_root = Path(__file__).parent
    learner = ErrorLearner(skill_root)
    
    # Example: Record an error
    if len(sys.argv) > 1 and sys.argv[1] == 'record':
        app_id = sys.argv[2] if len(sys.argv) > 2 else 'TEST_APP'
        
        # Example validation output
        example_output = """
Platform errors:
✖ server/server.js::42: post is no longer supported in Request API

Lint errors:
✖ app/scripts/app.js::14: Async function 'onAppActivated' has no 'await' expression

Total Platform Errors: 1
Total Lint Errors: 1
"""
        
        errors = learner.parse_fdk_output(example_output)
        learner.record_error(app_id, errors)
        print(f"✅ Recorded errors for {app_id}")
    
    # Generate skill updates
    elif len(sys.argv) > 1 and sys.argv[1] == 'suggest':
        new_patterns = learner.identify_new_patterns()
        learner.create_skill_update_document(new_patterns)
    
    # Show statistics
    elif len(sys.argv) > 1 and sys.argv[1] == 'stats':
        stats = learner.get_statistics()
        
        print("\n📊 Error Learning Statistics")
        print("=" * 80)
        print(f"Total errors recorded: {stats['total_errors_recorded']}")
        print(f"Unique patterns: {stats['unique_patterns']}")
        print(f"Fixed patterns: {stats['fixed_patterns']}")
        print(f"Unfixed patterns: {stats['unfixed_patterns']}")
        print("\nMost common patterns:")
        for pattern, count in stats['most_common_patterns']:
            status = "✅" if learner.error_db['patterns'][pattern].get('fixed') else "❌"
            print(f"  {status} {pattern}: {count} occurrences")
    
    else:
        print("Usage:")
        print("  python error_learner.py record [app_id]  - Record errors from validation")
        print("  python error_learner.py suggest           - Generate skill update suggestions")
        print("  python error_learner.py stats             - Show error statistics")


if __name__ == '__main__':
    main()
