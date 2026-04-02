#!/usr/bin/env python3
"""
Automated Benchmarking Test Script
Automates setup, validation, and scoring of generated Freshworks apps

INCLUDES: Automatic skill learning from FDK validation failures
"""
from __future__ import annotations

import os
import re
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
    def __init__(self, benchmark_dir=None):
        repo_root = Path(__file__).parent
        self.benchmark_dir = Path(benchmark_dir) if benchmark_dir else repo_root / 'test-apps'
        self.use_cases_file = repo_root / 'use-cases' / 'use_cases.json'
        self.results_dir = repo_root / 'results'
        self.results_dir.mkdir(exist_ok=True)
        
        # Initialize error learner for automatic skill updates (skill_root = repo root)
        if ERROR_LEARNING_ENABLED:
            skill_root = repo_root
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
                elif line.strip().startswith('✖') or line.strip().startswith('⨯'):
                    error_msg = line.strip()
                    if current_section == 'platform':
                        platform_errors.append(error_msg)
                    elif current_section == 'lint':
                        lint_errors.append(error_msg)
                    elif current_section is None:
                        # Errors before any section header are platform errors
                        platform_errors.append(error_msg)
                elif line.strip().startswith('⚠'):
                    warnings.append(line.strip())
            
            # Check if validation actually failed (has errors, not just warnings)
            has_errors = platform_errors or lint_errors
            validation_result = {
                'success': result.returncode == 0 and not has_errors,
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
            
            # Record errors for automatic skill learning (only if there are actual errors)
            if self.error_learner and has_errors:
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
            print(
                "⚠️  FDK not found. Install with: "
                "npm install https://cdn.freshdev.io/fdk/latest-v24.tgz -g"
            )
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
            
            # Detect app type
            has_ui_location = False
            has_background_location = False
            is_pure_serverless = True
            
            # Background placeholders that are valid
            background_placeholders = [
                'ticket_background', 'contact_background', 'contact_list_background',
                'asset_background', 'company_background', 'deal_background'
            ]
            
            # Check all modules for locations
            for module_name, module_config in modules.items():
                if 'location' in module_config:
                    locations = module_config.get('location', {})
                    for loc_name in locations.keys():
                        if loc_name in background_placeholders:
                            has_background_location = True
                        else:
                            has_ui_location = True
                            is_pure_serverless = False
            
            # Check common locations
            if common_locations:
                for loc_name in common_locations.keys():
                    if loc_name in background_placeholders:
                        has_background_location = True
                    else:
                        has_ui_location = True
                        is_pure_serverless = False
            
            # If no locations at all, it's pure serverless (events/functions only)
            if not has_ui_location and not has_background_location:
                is_pure_serverless = True
            
            # Validate location placement
            if is_pure_serverless:
                # Pure serverless app - no location validation needed
                compliance['correct_location_placement'] = True
                print("✅ Serverless app (no UI location required)")
            elif has_background_location and not has_ui_location:
                # Background placeholder app - location validation passes
                compliance['correct_location_placement'] = True
                print("✅ Background placeholder app (valid location)")
            else:
                # UI app - check if product-specific locations are NOT in common
                invalid_locations = ['ticket_sidebar', 'asset_sidebar', 'deal_entity_menu', 
                                   'contact_sidebar', 'company_sidebar', 'deal_sidebar']
                has_invalid = any(loc in common_locations for loc in invalid_locations)
                
                if not has_invalid and modules:
                    compliance['correct_location_placement'] = True
                    print("✅ Correct location placement")
                else:
                    print("❌ Invalid location placement (product-specific locations in common)")
        
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

    @staticmethod
    def infer_expected_platform_features_from_criteria(criteria: dict) -> list[str]:
        """Return expected_platform_features lines, or legacy expected_features slugs if epf omitted."""
        epf = criteria.get("expected_platform_features")
        if isinstance(epf, list) and epf:
            return [str(x).strip() for x in epf if str(x).strip()]
        ef = criteria.get("expected_features")
        if isinstance(ef, list) and ef:
            return [str(x).strip() for x in ef if str(x).strip()]
        return []

    _PLATFORM_FEATURE_SLUG_ALIASES: dict[str, str] = {
        "oauth_config": "oauth",
        "custom_iparam": "iparams",
        "crayons": "crayons_ui",
        "ms_graph": "microsoft_graph",
        "smi_functions": "functions",
        "app_locations": "locations",
    }

    @classmethod
    def _normalize_platform_feature_slug(cls, raw: str) -> str | None:
        s = raw.strip().lower().replace("-", "_")
        s = re.sub(r"\s+", "_", s)
        s = re.sub(r"_+", "_", s).strip("_")
        if not s:
            return None
        if re.fullmatch(r"[a-z0-9_]+", s):
            return cls._PLATFORM_FEATURE_SLUG_ALIASES.get(s, s)
        return None

    def _slug_matches_platform_feature(
        self,
        slug: str,
        hay: str,
        signals: dict,
        has_oauth_file: bool,
        has_req_file: bool,
        has_ip: bool,
        has_smi: bool,
    ) -> bool:
        if slug == "request_templates":
            return has_req_file or signals["has_requests"]
        if slug == "iparams":
            return has_ip
        if slug == "scheduled_events":
            return signals["has_scheduled"]
        if slug == "serverless_events":
            return signals["has_events"] or signals["has_scheduled"]
        if slug == "oauth":
            return has_oauth_file or "oauth" in hay
        if slug == "data_methods":
            return "client.data" in hay or "client.interface" in hay
        if slug == "crayons_ui":
            return "crayons" in hay or "fw-button" in hay or "fw-" in hay
        if slug == "smi":
            return has_smi
        if slug == "functions":
            return signals["has_functions"]
        if slug == "locations":
            return signals["has_locations"]
        if slug == "webhooks":
            return "webhook" in hay
        if slug == "whitelisted_domains":
            return signals["has_whitelisted"]
        if slug == "hybrid_app":
            return "hybrid" in hay
        if slug in ("microsoft_graph", "graph_api"):
            return "graph" in hay or "microsoft" in hay or "teams" in hay
        if slug == "jira":
            return "jira" in hay
        if slug == "zendesk":
            return "zendesk" in hay
        if slug == "ticket_sidebar":
            return "ticket_sidebar" in hay
        if slug == "full_page_app":
            return "full_page" in hay or "full page" in hay
        if slug == "placeholder":
            return "placeholder" in hay
        if slug == "on_app_install" or slug == "app_install":
            return "onappinstall" in hay or "on_app_install" in hay
        return False

    def _platform_signals_from_manifest(self, manifest: dict) -> dict:
        out = {
            "has_events": False,
            "has_scheduled": False,
            "has_requests": False,
            "has_functions": False,
            "has_locations": False,
            "has_whitelisted": bool(
                manifest.get("whitelisted-domains") or manifest.get("whitelisted_domains")
            ),
        }

        def scan_block(block: dict) -> None:
            if not isinstance(block, dict):
                return
            ev = block.get("events") or {}
            if isinstance(ev, dict):
                for k in ev:
                    if k == "onScheduledEvent":
                        out["has_scheduled"] = True
                    else:
                        out["has_events"] = True
            req = block.get("requests")
            if isinstance(req, dict) and req:
                out["has_requests"] = True
            fn = block.get("functions")
            if isinstance(fn, dict) and fn:
                out["has_functions"] = True
            loc = block.get("location")
            if isinstance(loc, dict) and loc:
                out["has_locations"] = True

        for key in ("modules", "product"):
            container = manifest.get(key)
            if isinstance(container, dict):
                for _name, block in container.items():
                    scan_block(block if isinstance(block, dict) else {})
        return out

    def _line_matches_platform_feature(
        self,
        raw: str,
        hay: str,
        signals: dict,
        has_oauth_file: bool,
        has_req_file: bool,
        has_ip: bool,
        has_smi: bool,
    ) -> bool:
        slug = self._normalize_platform_feature_slug(raw)
        if slug:
            return self._slug_matches_platform_feature(
                slug, hay, signals, has_oauth_file, has_req_file, has_ip, has_smi
            )
        # Legacy human-readable lines (e.g. prose from CSV or old criteria)
        s = raw.strip().lower()
        if len(s) >= 3 and s in hay:
            return True
        tokens = [t for t in re.findall(r"[a-z0-9._]+", s) if len(t) >= 3]
        if len(tokens) >= 2 and all(t in hay for t in tokens):
            return True
        if "oauth" in s and (has_oauth_file or "oauth" in hay):
            return True
        if "iparam" in s and has_ip:
            return True
        if ("request" in s and "template" in s) or "requests.json" in s:
            if has_req_file or signals["has_requests"]:
                return True
        if "scheduled" in s and signals["has_scheduled"]:
            return True
        if "serverless" in s and (signals["has_events"] or signals["has_scheduled"]):
            return True
        if "smi" in s and has_smi:
            return True
        if "function" in s and signals["has_functions"]:
            return True
        if any(
            k in s
            for k in ("location", "sidebar", "full_page", "full page", "placeholder")
        ):
            if signals["has_locations"]:
                return True
        if "data method" in s or "client.data" in s:
            if "client.data" in hay or "client.interface" in hay:
                return True
        if "crayon" in s:
            if "crayons" in hay or "fw-button" in hay or "fw-" in hay:
                return True
        if "webhook" in s and "webhook" in hay:
            return True
        if ("graph" in s or "microsoft" in s or "teams" in s) and (
            "graph" in hay or "microsoft" in hay or "teams" in hay
        ):
            return True
        if "jira" in s and "jira" in hay:
            return True
        if "zendesk" in s and "zendesk" in hay:
            return True
        return False

    def check_expected_platform_features(
        self, app_path, expected_lines: list[str] | str | None
    ):
        """
        Score against criteria.expected_platform_features (20 pt bucket).
        Prefer snake_case slugs (request_templates, oauth, …); prose lines still match via heuristics.
        Proportional: matched_lines / total_lines * 20. Empty criteria => full 20 (no rubric).
        """
        app_path = Path(app_path)
        raw = expected_lines
        if isinstance(raw, str):
            raw = [ln.strip() for ln in raw.splitlines() if ln.strip()]
        elif raw is None:
            raw = []
        lines = [str(x).strip() for x in raw if str(x).strip()]
        print(f"\n📋 Checking Expected Platform Features ({len(lines)} criteria lines)...")
        if not lines:
            print("   (none in criteria — full credit for this bucket)")
            return {
                "criteria_lines": [],
                "matched": [],
                "unmatched": [],
                "score": 20.0,
                "max_score": 20.0,
                "full_credit_no_criteria": True,
            }

        manifest: dict = {}
        mp = app_path / "manifest.json"
        if mp.exists():
            try:
                manifest = json.loads(mp.read_text(encoding="utf-8", errors="replace"))
            except (json.JSONDecodeError, OSError):
                manifest = {}

        hay_parts = [json.dumps(manifest, default=str).lower()]
        srv = app_path / "server" / "server.js"
        if srv.exists():
            try:
                hay_parts.append(srv.read_text(encoding="utf-8", errors="replace").lower()[:80000])
            except OSError:
                pass
        for p in list(app_path.glob("app/**/*.html"))[:15] + list(app_path.glob("app/**/*.js"))[:15]:
            try:
                hay_parts.append(p.read_text(encoding="utf-8", errors="replace").lower()[:20000])
            except OSError:
                pass
        hay = "\n".join(hay_parts)

        cfg_oauth = app_path / "config" / "oauth_config.json"
        cfg_req = app_path / "config" / "requests.json"
        cfg_ip_j = app_path / "config" / "iparams.json"
        cfg_ip_h = app_path / "config" / "iparams.html"
        has_oauth_file = cfg_oauth.exists()
        has_req_file = cfg_req.exists()
        has_ip = cfg_ip_j.exists() or cfg_ip_h.exists()
        has_smi = (app_path / "smi.json").exists()
        signals = self._platform_signals_from_manifest(manifest)

        matched = []
        unmatched = []
        for raw in lines:
            ok = self._line_matches_platform_feature(
                raw, hay, signals, has_oauth_file, has_req_file, has_ip, has_smi
            )
            if ok:
                matched.append(raw)
                disp = raw[:77] + "…" if len(raw) > 80 else raw
                print(f"   ✅ {disp}")
            else:
                unmatched.append(raw)
                disp = raw[:77] + "…" if len(raw) > 80 else raw
                print(f"   ❌ {disp}")

        per = 20.0 * len(matched) / len(lines) if lines else 20.0
        return {
            "criteria_lines": lines,
            "matched": matched,
            "unmatched": unmatched,
            "score": round(per, 2),
            "max_score": 20.0,
            "full_credit_no_criteria": False,
        }

    def calculate_score(self, validation, file_structure, compliance, crayons, epf_check):
        """Calculate overall quality score (100-point scale when all buckets apply)."""
        score = 0.0
        max_score = 0.0
        components: dict[str, float] = {}

        # FDK validation (20 points)
        max_score += 20
        v_pts = 20 if validation.get("success") else 0
        score += v_pts
        components["fdk_validation"] = float(v_pts)

        # File structure (15 points; was 20 — 5 moved to Expected Platform Features bucket)
        if file_structure:
            total_files = len(file_structure)
            present_files = sum(1 for exists in file_structure.values() if exists)
            fs_pts = (present_files / total_files) * 15
            max_score += 15
            score += fs_pts
            components["file_structure"] = round(fs_pts, 2)

        # Platform 3.0 compliance (40 points - 8 per item)
        max_score += 40
        compliance_score = sum(8 for v in compliance.values() if v)
        score += compliance_score
        components["platform3_compliance"] = float(compliance_score)

        # Crayons usage (5 points; was 20 — 15 moved to Expected Platform Features rubric)
        max_score += 5
        cray_raw = 0
        if crayons.get("cdn_included"):
            cray_raw += 10
        if crayons.get("fw_button_used"):
            cray_raw += 5
        if not crayons.get("plain_html_found"):
            cray_raw += 5
        cray_pts = (cray_raw / 20.0) * 5.0
        score += cray_pts
        components["crayons_usage"] = round(cray_pts, 2)

        # Expected platform features from criteria (20 points)
        max_score += 20
        epf_pts = float(epf_check.get("score", 20))
        score += epf_pts
        components["expected_platform_features"] = round(epf_pts, 2)

        percentage = (score / max_score) * 100 if max_score > 0 else 0

        return {
            "total_score": round(score, 2),
            "max_score": max_score,
            "percentage": round(percentage, 2),
            "grade": self._get_grade(percentage),
            "components": components,
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
        epf_lines = use_case.get("expected_platform_features") or []
        epf_check = self.check_expected_platform_features(app_path, epf_lines)

        # Calculate score
        score = self.calculate_score(validation, file_structure, compliance, crayons, epf_check)

        # Compile results
        results = {
            'app_id': app_id,
            'name': use_case['name'],
            'validation': validation,
            'file_structure': file_structure,
            'platform3_compliance': compliance,
            'crayons_usage': crayons,
            'expected_platform_features_check': epf_check,
            'score': score,
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
    
    def evaluate_existing_app(self, app_path, app_id=None, requirements=None):
        """Evaluate an already-generated app without regeneration"""
        app_path = Path(app_path)
        
        if not app_path.exists():
            print(f"❌ App path not found: {app_path}")
            return
        
        # Generate app_id if not provided
        if not app_id:
            app_id = f"EVAL_{app_path.name.upper()}"
        
        print(f"\n{'='*80}")
        print(f"🔍 Evaluating existing app: {app_path.name}")
        print(f"{'='*80}\n")
        
        # Try to load use case if app_id matches
        use_case = None
        if app_id.startswith('APP'):
            use_cases = self.load_use_cases()
            use_case = next((uc for uc in use_cases if uc['id'] == app_id), None)
        
        # Determine product from manifest or use case
        product = 'freshdesk'  # default
        manifest_path = app_path / 'manifest.json'
        if manifest_path.exists():
            try:
                with open(manifest_path, 'r') as f:
                    manifest = json.load(f)
                    product = manifest.get('product', {}).get('freshdesk', 'freshdesk')
                    # Extract first product if multiple
                    if isinstance(product, dict):
                        product = list(product.keys())[0] if product else 'freshdesk'
            except:
                pass
        
        if use_case:
            product = use_case.get('product', product)
        
        # Parse requirements if provided
        requirements_list = []
        expected_files_from_criteria = []
        expected_platform_lines: list[str] = []

        if requirements:
            # Check if requirements is a file path
            requirements_path = Path(requirements)
            if requirements_path.exists() and requirements_path.suffix == '.json':
                # Load from criteria file
                print(f"📄 Loading requirements from: {requirements_path}\n")
                try:
                    with open(requirements_path, 'r') as f:
                        criteria = json.load(f)
                        requirements_list = criteria.get('requirements', [])
                        expected_files_from_criteria = criteria.get('expected_files', [])
                        expected_platform_lines = (
                            criteria.get("expected_platform_features") or []
                        )
                        if not expected_platform_lines:
                            expected_platform_lines = (
                                self.infer_expected_platform_features_from_criteria(
                                    criteria
                                )
                            )
                        # Infer minimal expected_files from expected_instances and/or platform slugs
                        if not expected_files_from_criteria:
                            inst = criteria.get("expected_instances") or {}
                            slugs: list[str] = []
                            for x in criteria.get("expected_platform_features") or []:
                                n = self._normalize_platform_feature_slug(str(x))
                                if n:
                                    slugs.append(n)
                            for x in criteria.get("expected_features") or []:
                                n = self._normalize_platform_feature_slug(str(x))
                                if n:
                                    slugs.append(n)
                            if inst or slugs:
                                expected_files_from_criteria = ["manifest.json"]
                                if inst.get("request_templates") or "request_templates" in slugs:
                                    expected_files_from_criteria.append("config/requests.json")
                                if (
                                    inst.get("iparams")
                                    or inst.get("custom_iparam")
                                    or "iparams" in slugs
                                ):
                                    expected_files_from_criteria.append("config/iparams.json")
                                if inst.get("scheduled_events") or "scheduled_events" in slugs:
                                    expected_files_from_criteria.append("server/server.js")
                        if not requirements_list:
                            if criteria.get("expected_platform_features"):
                                requirements_list = [
                                    str(x) for x in criteria["expected_platform_features"]
                                ]
                            elif criteria.get("expected_features"):
                                requirements_list = list(criteria["expected_features"])
                        if requirements_list:
                            print(f"📋 Requirements ({len(requirements_list)}):")
                            for req in requirements_list:
                                print(f"   • {req}")
                            print()
                except Exception as e:
                    print(f"⚠️  Could not load criteria file: {e}")
                    print("Treating as comma-separated requirements instead.\n")
                    requirements_list = [r.strip() for r in requirements.split(',')]
            else:
                # Parse as comma-separated string
                requirements_list = [r.strip() for r in requirements.split(',')]
                print(f"📋 Requirements: {', '.join(requirements_list)}\n")
        
        # Run validation checks
        validation = self.validate_app(app_path, product=product)
        
        # Determine expected files
        expected_files = []
        if expected_files_from_criteria:
            # Use expected files from criteria file
            expected_files = expected_files_from_criteria
        elif use_case:
            expected_files = use_case['expected_files']
        else:
            # Auto-detect expected files based on app type
            expected_files = ['manifest.json']
            if (app_path / 'app').exists():
                expected_files.extend(['app/index.html', 'app/scripts/app.js'])
            if (app_path / 'server').exists():
                expected_files.append('server/server.js')
            if (app_path / 'config').exists():
                if (app_path / 'config/iparams.json').exists():
                    expected_files.append('config/iparams.json')
                if (app_path / 'config/requests.json').exists():
                    expected_files.append('config/requests.json')
        
        file_structure = self.check_file_structure(app_path, expected_files)
        compliance = self.check_platform3_compliance(app_path)
        crayons = self.check_crayons_usage(app_path)
        epf_check = self.check_expected_platform_features(
            app_path, expected_platform_lines
        )

        # Calculate score
        score = self.calculate_score(
            validation, file_structure, compliance, crayons, epf_check
        )

        # Compile results
        results = {
            'app_id': app_id,
            'name': use_case['name'] if use_case else app_path.name,
            'app_path': str(app_path),
            'requirements': requirements_list,
            'validation': validation,
            'file_structure': file_structure,
            'platform3_compliance': compliance,
            'crayons_usage': crayons,
            'expected_platform_features_check': epf_check,
            'score': score,
            'evaluation_mode': True,
        }
        
        # Save results
        self.save_results(app_id, results)
        
        # Print summary
        print(f"\n{'='*80}")
        print(f"📊 EVALUATION SUMMARY - {app_id}")
        print(f"{'='*80}")
        print(f"App: {app_path.name}")
        if requirements_list:
            print(f"Requirements: {', '.join(requirements_list)}")
        print(f"Score: {score['total_score']}/{score['max_score']} ({score['percentage']}%)")
        print(f"Grade: {score['grade']}")
        print(f"{'='*80}\n")
        
        return results

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Automated Freshworks App Benchmarking')
    parser.add_argument('app_id', nargs='?', help='App ID to test (e.g., APP001)')
    parser.add_argument('--benchmark-dir', default=None,
                       help='Benchmark directory path (default: repo test-apps/)')
    parser.add_argument('--evaluate', type=str, metavar='PATH',
                       help='Evaluate an existing app at the given path (relative or absolute)')
    parser.add_argument('--app-id', type=str,
                       help='App ID to use for evaluation (optional, auto-generated if not provided)')
    parser.add_argument('--requirements', type=str,
                       help='Comma-separated requirements OR path to criteria JSON file (e.g., test-criteria/APP001-criteria.json)')
    parser.add_argument('--generate-skill-updates', action='store_true',
                       help='Generate skill update suggestions from recorded errors')
    parser.add_argument('--show-stats', action='store_true',
                       help='Show error learning statistics')
    
    args = parser.parse_args()
    
    automation = BenchmarkAutomation(benchmark_dir=args.benchmark_dir)
    
    # Evaluate existing app mode
    if args.evaluate:
        # Convert relative path to absolute if needed
        eval_path = Path(args.evaluate)
        if not eval_path.is_absolute():
            eval_path = Path(__file__).parent / eval_path
        
        results = automation.evaluate_existing_app(
            app_path=eval_path,
            app_id=args.app_id,
            requirements=args.requirements
        )
        if results is None:
            sys.exit(1)
        # Exit 1 if validation failed
        if not results.get('validation', {}).get('success', True):
            sys.exit(1)
        sys.exit(0)
    # Generate skill updates
    elif args.generate_skill_updates:
        if ERROR_LEARNING_ENABLED and automation.error_learner:
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
    # Show statistics
    elif args.show_stats:
        if ERROR_LEARNING_ENABLED and automation.error_learner:
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
    # Run normal test
    elif args.app_id:
        results = automation.run_test(args.app_id)
        if results is None:
            sys.exit(1)
        sys.exit(0)
    else:
        parser.print_help()
        print("\n❌ Error: Please provide either --app APP_ID, --evaluate PATH, --show-stats, or --generate-skill-updates")
        sys.exit(2)

if __name__ == '__main__':
    main()
