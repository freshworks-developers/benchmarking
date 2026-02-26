#!/usr/bin/env python3
"""
Automated Benchmarking Test Script
Automates setup, validation, and scoring of generated Freshworks apps

INCLUDES: Automatic skill learning from FDK validation failures
"""

import os
import sys
import json
import subprocess
import time
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

# Import error learner for automatic skill updates
try:
    from error_learner import ErrorLearner
    ERROR_LEARNING_ENABLED = True
except ImportError:
    ERROR_LEARNING_ENABLED = False
    print("⚠️  Error learning disabled (error_learner.py not found)")

class BenchmarkAutomation:
    def __init__(self, benchmark_dir='/Users/dchatterjee/benchmark-test'):
        self.benchmark_dir = Path(benchmark_dir)
        self.use_cases_file = Path(__file__).parent / 'use-cases' / 'use_cases.json'
        self.results_dir = Path(__file__).parent / 'results'
        self.results_dir.mkdir(exist_ok=True)
        
        # Initialize error learner for automatic skill updates
        if ERROR_LEARNING_ENABLED:
            skill_root = Path(__file__).parent.parent.parent
            self.error_learner = ErrorLearner(skill_root)
            print("✅ Error learning enabled - Will track validation failures")
        else:
            self.error_learner = None
        
    def load_use_cases(self):
        """Load use cases from JSON"""
        with open(self.use_cases_file, 'r') as f:
            data = json.load(f)
        return data['use_cases']
    
    def setup_app_folder(self, app_id):
        """Create app folder for testing"""
        app_path = self.benchmark_dir / app_id
        app_path.mkdir(parents=True, exist_ok=True)
        print(f"✅ Created folder: {app_path}")
        return app_path
    
    def get_prompt(self, use_case):
        """Get the prompt for a use case"""
        return use_case['prompt']
    
    def save_prompt_file(self, app_path, use_case):
        """Save prompt to file for manual execution"""
        prompt_file = app_path / 'PROMPT.txt'
        with open(prompt_file, 'w') as f:
            f.write(f"App ID: {use_case['id']}\n")
            f.write(f"Name: {use_case['name']}\n")
            f.write(f"Type: {use_case['app_type']}\n")
            f.write(f"Product: {use_case['product']}\n")
            f.write(f"\nPROMPT:\n")
            f.write("=" * 80 + "\n")
            f.write(use_case['prompt'])
            f.write("\n" + "=" * 80 + "\n")
        print(f"✅ Saved prompt to: {prompt_file}")
        return prompt_file
    
    def validate_app(self, app_path, product='freshdesk'):
        """Run fdk validate on generated app"""
        print(f"\n🔍 Validating app at {app_path}...")
        
        try:
            # Run fdk validate (product context inferred from manifest)
            result = subprocess.run(
                ['fdk', 'validate'],
                cwd=app_path,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # Parse validation output for detailed errors
            output = result.stdout + result.stderr
            
            # Extract error categories
            platform_errors = []
            lint_errors = []
            warnings = []
            
            # Parse the output for specific error types
            lines = output.split('\n')
            current_section = None
            
            for line in lines:
                if 'Platform errors:' in line:
                    current_section = 'platform'
                elif 'Lint errors:' in line:
                    current_section = 'lint'
                elif 'Please ensure that the following are addressed' in line:
                    current_section = 'warnings'
                elif line.strip().startswith('✖'):
                    error_msg = line.strip()
                    if current_section == 'platform':
                        platform_errors.append(error_msg)
                    elif current_section == 'lint':
                        lint_errors.append(error_msg)
                elif line.strip().startswith('⚠'):
                    warnings.append(line.strip())
            
            validation_result = {
                'success': result.returncode == 0,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'return_code': result.returncode,
                'platform_errors': platform_errors,
                'lint_errors': lint_errors,
                'warnings': warnings,
                'product': product
            }
            
            if validation_result['success']:
                print("✅ FDK validation passed!")
                # Show validation output for transparency
                if result.stdout:
                    print(f"Output:\n{result.stdout}")
            else:
                print("❌ FDK validation failed!")
                if platform_errors:
                    print(f"\n🚫 Platform Errors ({len(platform_errors)}):")
                    for err in platform_errors:
                        print(f"  {err}")
                if lint_errors:
                    print(f"\n🔍 Lint Errors ({len(lint_errors)}):")
                    for err in lint_errors:
                        print(f"  {err}")
                if warnings:
                    print(f"\n⚠️  Warnings ({len(warnings)}):")
                    for warn in warnings[:5]:  # Show first 5 warnings
                        print(f"  {warn}")
                    if len(warnings) > 5:
                        print(f"  ... and {len(warnings) - 5} more warnings")
                if result.stderr:
                    print(f"\nRaw Errors:\n{result.stderr}")
                if result.stdout:
                    print(f"\nRaw Output:\n{result.stdout}")
            
            # Record errors for automatic skill learning
            if self.error_learner and (platform_errors or lint_errors):
                try:
                    app_id = app_path.name
                    error_data = self.error_learner.parse_fdk_output(output)
                    self.error_learner.record_error(app_id, error_data)
                    print(f"\n📝 Recorded {len(platform_errors) + len(lint_errors)} errors for skill learning")
                except Exception as e:
                    print(f"⚠️  Failed to record errors: {e}")
            
            return validation_result
            
        except subprocess.TimeoutExpired:
            print("⚠️  Validation timeout")
            return {'success': False, 'error': 'Timeout', 'product': product}
        except FileNotFoundError:
            print("⚠️  FDK not found. Install with: npm install -g @freshworks/fdk")
            return {'success': False, 'error': 'FDK not installed', 'product': product}
    
    def check_file_structure(self, app_path, expected_files):
        """Check if expected files exist"""
        print(f"\n📁 Checking file structure...")
        
        results = {}
        for file_path in expected_files:
            full_path = app_path / file_path
            exists = full_path.exists()
            results[file_path] = exists
            
            status = "✅" if exists else "❌"
            print(f"{status} {file_path}")
        
        return results
    
    def check_platform3_compliance(self, app_path):
        """Check Platform 3.0 compliance"""
        print(f"\n🔍 Checking Platform 3.0 compliance...")
        
        manifest_path = app_path / 'manifest.json'
        compliance = {
            'platform_version_3_0': False,
            'modules_structure': False,
            'no_whitelisted_domains': False,
            'engines_present': False,
            'correct_location_placement': False
        }
        
        if not manifest_path.exists():
            print("❌ manifest.json not found")
            return compliance
        
        try:
            with open(manifest_path, 'r') as f:
                manifest = json.load(f)
            
            # Check platform version
            if manifest.get('platform-version') == '3.0':
                compliance['platform_version_3_0'] = True
                print("✅ Platform version 3.0")
            else:
                print(f"❌ Platform version: {manifest.get('platform-version')}")
            
            # Check modules structure
            if 'modules' in manifest:
                compliance['modules_structure'] = True
                print("✅ Uses 'modules' structure")
            else:
                print("❌ Missing 'modules' structure")
            
            # Check no whitelisted-domains
            if 'whitelisted-domains' not in manifest and 'whitelisted_domains' not in manifest:
                compliance['no_whitelisted_domains'] = True
                print("✅ No whitelisted-domains")
            else:
                print("❌ Uses whitelisted-domains (deprecated)")
            
            # Check engines
            if 'engines' in manifest:
                compliance['engines_present'] = True
                print("✅ Engines block present")
            else:
                print("❌ Missing engines block")
            
            # Check location placement
            modules = manifest.get('modules', {})
            common = modules.get('common', {})
            common_locations = common.get('location', {})
            
            # Check if product-specific locations are NOT in common
            invalid_locations = ['ticket_sidebar', 'asset_sidebar', 'deal_entity_menu']
            has_invalid = any(loc in common_locations for loc in invalid_locations)
            
            if not has_invalid and modules:
                compliance['correct_location_placement'] = True
                print("✅ Correct location placement")
            else:
                print("❌ Invalid location placement")
        
        except json.JSONDecodeError:
            print("❌ Invalid JSON in manifest.json")
        except Exception as e:
            print(f"❌ Error checking compliance: {e}")
        
        return compliance
    
    def check_crayons_usage(self, app_path):
        """Check if Crayons components are used"""
        print(f"\n🎨 Checking Crayons usage...")
        
        html_files = list(app_path.glob('app/**/*.html'))
        
        crayons_usage = {
            'cdn_included': False,
            'fw_button_used': False,
            'fw_input_used': False,
            'plain_html_found': False
        }
        
        for html_file in html_files:
            try:
                content = html_file.read_text()
                
                # Check for Crayons CDN
                if 'crayons' in content.lower() and 'cdn.jsdelivr.net' in content:
                    crayons_usage['cdn_included'] = True
                
                # Check for Crayons components
                if '<fw-button' in content:
                    crayons_usage['fw_button_used'] = True
                
                if '<fw-input' in content:
                    crayons_usage['fw_input_used'] = True
                
                # Check for plain HTML (bad)
                if '<button' in content and '<fw-button' not in content:
                    crayons_usage['plain_html_found'] = True
                
            except Exception as e:
                print(f"⚠️  Error reading {html_file}: {e}")
        
        if crayons_usage['cdn_included']:
            print("✅ Crayons CDN included")
        else:
            print("❌ Crayons CDN not found")
        
        if crayons_usage['fw_button_used']:
            print("✅ fw-button used")
        
        if crayons_usage['plain_html_found']:
            print("❌ Plain HTML elements found (should use Crayons)")
        
        return crayons_usage
    
    def calculate_score(self, validation, file_structure, compliance, crayons):
        """Calculate overall quality score"""
        score = 0
        max_score = 0
        
        # Validation (20 points)
        max_score += 20
        if validation.get('success'):
            score += 20
        
        # File structure (20 points)
        if file_structure:
            total_files = len(file_structure)
            present_files = sum(1 for exists in file_structure.values() if exists)
            score += (present_files / total_files) * 20
            max_score += 20
        
        # Platform 3.0 compliance (40 points - 8 per item)
        max_score += 40
        compliance_score = sum(8 for v in compliance.values() if v)
        score += compliance_score
        
        # Crayons usage (20 points)
        max_score += 20
        crayons_score = 0
        if crayons.get('cdn_included'):
            crayons_score += 10
        if crayons.get('fw_button_used'):
            crayons_score += 5
        if not crayons.get('plain_html_found'):
            crayons_score += 5
        score += crayons_score
        
        percentage = (score / max_score) * 100 if max_score > 0 else 0
        
        return {
            'total_score': score,
            'max_score': max_score,
            'percentage': round(percentage, 2),
            'grade': self._get_grade(percentage)
        }
    
    def _get_grade(self, percentage):
        """Convert percentage to grade"""
        if percentage >= 90:
            return 'A'
        elif percentage >= 80:
            return 'B'
        elif percentage >= 70:
            return 'C'
        elif percentage >= 60:
            return 'D'
        else:
            return 'F'
    
    def save_results(self, app_id, results):
        """Save test results to JSON"""
        timestamp = datetime.now().isoformat()
        results['timestamp'] = timestamp
        results['app_id'] = app_id
        
        result_file = self.results_dir / f'{app_id}_result.json'
        with open(result_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n💾 Results saved to: {result_file}")
    
    def run_test(self, app_id):
        """Run complete test for one app"""
        print(f"\n{'='*80}")
        print(f"🚀 Starting test for {app_id}")
        print(f"{'='*80}\n")
        
        # Load use case
        use_cases = self.load_use_cases()
        use_case = next((uc for uc in use_cases if uc['id'] == app_id), None)
        
        if not use_case:
            print(f"❌ Use case {app_id} not found")
            return
        
        # Setup
        app_path = self.setup_app_folder(app_id)
        prompt_file = self.save_prompt_file(app_path, use_case)
        
        print(f"\n{'='*80}")
        print(f"⏸️  MANUAL STEP - OPEN IN SEPARATE CURSOR INSTANCE")
        print(f"{'='*80}")
        print(f"\n🚨 IMPORTANT: Open in a SEPARATE Cursor window (NOT this workspace!)")
        print(f"\nOption 1: Open via command")
        print(f"  cursor {app_path}")
        print(f"\nOption 2: Open via Cursor File menu")
        print(f"  File → Open Folder → {app_path}")
        print(f"\nOption 3: Open via terminal")
        print(f"  cd {app_path} && cursor .")
        print(f"\nThen:")
        print(f"  1. Copy prompt from: {prompt_file.name}")
        print(f"  2. Send to Cursor AI")
        print(f"  3. Wait for generation to complete")
        print(f"  4. Return here and press ENTER to validate...")
        print(f"\n{'='*80}")
        
        input()
        
        # Validate with product context
        validation = self.validate_app(app_path, product=use_case.get('product', 'freshdesk'))
        file_structure = self.check_file_structure(app_path, use_case['expected_files'])
        compliance = self.check_platform3_compliance(app_path)
        crayons = self.check_crayons_usage(app_path)
        
        # Calculate score
        score = self.calculate_score(validation, file_structure, compliance, crayons)
        
        # Compile results
        results = {
            'app_id': app_id,
            'name': use_case['name'],
            'validation': validation,
            'file_structure': file_structure,
            'platform3_compliance': compliance,
            'crayons_usage': crayons,
            'score': score
        }
        
        # Save results
        self.save_results(app_id, results)
        
        # Print summary
        print(f"\n{'='*80}")
        print(f"📊 TEST SUMMARY - {app_id}")
        print(f"{'='*80}")
        print(f"Score: {score['total_score']}/{score['max_score']} ({score['percentage']}%)")
        print(f"Grade: {score['grade']}")
        print(f"{'='*80}\n")
        
        return results

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Automated Freshworks App Benchmarking')
    parser.add_argument('app_id', nargs='?', default='APP001', help='App ID to test (e.g., APP001)')
    parser.add_argument('--benchmark-dir', default='/Users/dchatterjee/benchmark-test', 
                       help='Benchmark directory path')
    parser.add_argument('--generate-skill-updates', action='store_true',
                       help='Generate skill update suggestions from recorded errors')
    parser.add_argument('--show-stats', action='store_true',
                       help='Show error learning statistics')
    
    args = parser.parse_args()
    
    automation = BenchmarkAutomation(benchmark_dir=args.benchmark_dir)
    
    # Run test
    if not args.generate_skill_updates and not args.show_stats:
        automation.run_test(args.app_id)
    
    # Generate skill updates if requested or after test if errors found
    if ERROR_LEARNING_ENABLED and automation.error_learner:
        if args.generate_skill_updates:
            print("\n" + "="*80)
            print("🔍 Analyzing error patterns and generating skill updates...")
            print("="*80 + "\n")
            
            new_patterns = automation.error_learner.identify_new_patterns()
            automation.error_learner.create_skill_update_document(new_patterns)
            
            if new_patterns:
                print(f"\n✅ Generated skill updates for {len(new_patterns)} error patterns")
                print(f"📄 See: .dev/planning/AUTO_SKILL_UPDATES.md")
            else:
                print("\n✅ No new error patterns detected - skill is up to date!")
        
        elif args.show_stats:
            stats = automation.error_learner.get_statistics()
            
            print("\n" + "="*80)
            print("📊 ERROR LEARNING STATISTICS")
            print("="*80 + "\n")
            print(f"Total errors recorded: {stats['total_errors_recorded']}")
            print(f"Unique patterns: {stats['unique_patterns']}")
            print(f"Fixed patterns: {stats['fixed_patterns']}")
            print(f"Unfixed patterns: {stats['unfixed_patterns']}")
            print("\n📈 Most common patterns:")
            for pattern, count in stats['most_common_patterns']:
                status = "✅" if automation.error_learner.error_db['patterns'][pattern].get('fixed') else "❌"
                print(f"  {status} {pattern}: {count} occurrences")
            
            if stats['unfixed_patterns'] > 0:
                print(f"\n💡 Run with --generate-skill-updates to create suggestions for fixing these patterns")

if __name__ == '__main__':
    main()
