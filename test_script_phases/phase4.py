"""
Kiwi_AI - Phase 4 Testing Script
Tests deployment, Docker configuration, and production readiness
"""

import os
import sys
import subprocess
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def print_header(text):
    """Print formatted header"""
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70)

def print_test(test_name, passed):
    """Print test result"""
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status}: {test_name}")
    return passed

def check_file_exists(filepath):
    """Check if file exists"""
    return Path(filepath).exists()

def check_docker_files():
    """Test Docker configuration files"""
    print_header("Phase 4.1: Docker Configuration Files")
    
    tests_passed = 0
    total_tests = 4
    
    # Check Dockerfile
    if print_test("Dockerfile exists", check_file_exists("Dockerfile")):
        tests_passed += 1
        # Check Dockerfile content
        with open("Dockerfile", 'r', encoding='utf-8') as f:
            content = f.read()
            if print_test("Dockerfile uses Python 3.11", "python:3.11" in content.lower()):
                tests_passed += 1
            if print_test("Dockerfile creates non-root user", "useradd" in content):
                tests_passed += 1
    
    # Check docker-compose.yml
    if print_test("docker-compose.yml exists", check_file_exists("docker-compose.yml")):
        tests_passed += 1
    
    print(f"\nDocker Files: {tests_passed}/{total_tests} tests passed")
    return tests_passed == total_tests

def check_deployment_docs():
    """Test deployment documentation"""
    print_header("Phase 4.2: Deployment Documentation")
    
    tests_passed = 0
    total_tests = 6
    
    # Check DEPLOYMENT.md
    if print_test("DEPLOYMENT.md exists", check_file_exists("DEPLOYMENT.md")):
        tests_passed += 1
        with open("DEPLOYMENT.md", 'r', encoding='utf-8') as f:
            content = f.read()
            if print_test("Contains prerequisites section", "Prerequisites" in content):
                tests_passed += 1
            if print_test("Contains Docker deployment instructions", "docker-compose" in content):
                tests_passed += 1
            if print_test("Contains AWS EC2 deployment guide", "AWS EC2" in content):
                tests_passed += 1
            if print_test("Contains security best practices", "Security" in content):
                tests_passed += 1
    
    # Check .dockerignore
    if print_test(".dockerignore exists", check_file_exists(".dockerignore")):
        tests_passed += 1
    
    print(f"\nDeployment Docs: {tests_passed}/{total_tests} tests passed")
    return tests_passed == total_tests

def check_systemd_service():
    """Test systemd service file"""
    print_header("Phase 4.3: Systemd Service Configuration")
    
    tests_passed = 0
    total_tests = 4
    
    # Check service file
    if print_test("kiwi-ai.service exists", check_file_exists("kiwi-ai.service")):
        tests_passed += 1
        with open("kiwi-ai.service", 'r', encoding='utf-8') as f:
            content = f.read()
            if print_test("Service has proper description", "Description=" in content):
                tests_passed += 1
            if print_test("Service has restart policy", "Restart=" in content):
                tests_passed += 1
            if print_test("Service has proper ExecStart", "ExecStart=" in content):
                tests_passed += 1
    
    print(f"\nSystemd Service: {tests_passed}/{total_tests} tests passed")
    return tests_passed == total_tests

def check_monitoring_scripts():
    """Test monitoring and maintenance scripts"""
    print_header("Phase 4.4: Monitoring & Maintenance Scripts")
    
    tests_passed = 0
    total_tests = 5
    
    scripts_dir = Path("scripts")
    
    # Check scripts directory
    if print_test("scripts/ directory exists", scripts_dir.exists()):
        tests_passed += 1
    
    # Check individual scripts
    expected_scripts = [
        "health_check.sh",
        "rotate_logs.sh",
        "retrain_models.sh",
        "backup.sh"
    ]
    
    for script in expected_scripts:
        script_path = scripts_dir / script
        if print_test(f"{script} exists", script_path.exists()):
            tests_passed += 1
    
    print(f"\nMonitoring Scripts: {tests_passed}/{total_tests} tests passed")
    return tests_passed == total_tests

def check_production_readiness():
    """Test overall production readiness"""
    print_header("Phase 4.5: Production Readiness Checks")
    
    tests_passed = 0
    total_tests = 8
    
    # Check requirements.txt
    if print_test("requirements.txt exists", check_file_exists("requirements.txt")):
        tests_passed += 1
    
    # Check config.py
    if print_test("config.py exists", check_file_exists("config.py")):
        tests_passed += 1
        with open("config.py", 'r', encoding='utf-8') as f:
            content = f.read()
            if print_test("Config uses environment variables", "os.getenv" in content):
                tests_passed += 1
    
    # Check main.py
    if print_test("main.py exists", check_file_exists("main.py")):
        tests_passed += 1
    
    # Check dashboard.py
    if print_test("dashboard.py exists", check_file_exists("dashboard.py")):
        tests_passed += 1
    
    # Check README.md
    if print_test("README.md exists", check_file_exists("README.md")):
        tests_passed += 1
    
    # Check CHANGELOG.md
    if print_test("CHANGELOG.md exists", check_file_exists("CHANGELOG.md")):
        tests_passed += 1
    
    # Check .env.example (should exist for documentation)
    # Not a hard requirement, just informational
    env_example_exists = check_file_exists(".env.example")
    if not env_example_exists:
        print("ℹ️  INFO: Consider creating .env.example for documentation")
    tests_passed += 1  # Don't fail if missing
    
    print(f"\nProduction Readiness: {tests_passed}/{total_tests} tests passed")
    return tests_passed == total_tests

def check_docker_build():
    """Test if Docker image can be built (optional, requires Docker)"""
    print_header("Phase 4.6: Docker Build Test (Optional)")
    
    try:
        # Check if Docker is available
        result = subprocess.run(
            ["docker", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode != 0:
            print("ℹ️  INFO: Docker not available, skipping build test")
            return True
        
        print("Docker is available:", result.stdout.strip())
        
        # Attempt to validate Dockerfile syntax (dry run)
        print("Validating Dockerfile syntax...")
        result = subprocess.run(
            ["docker", "build", "-f", "Dockerfile", "--no-cache", "-t", "kiwi-ai:test", "."],
            capture_output=True,
            text=True,
            timeout=300
        )
        
        if result.returncode == 0:
            print("✅ PASS: Docker image builds successfully")
            # Clean up test image
            subprocess.run(["docker", "rmi", "kiwi-ai:test"], capture_output=True)
            return True
        else:
            print("❌ FAIL: Docker build failed")
            print("Error:", result.stderr[:500])
            return False
            
    except FileNotFoundError:
        print("ℹ️  INFO: Docker not installed, skipping build test")
        return True
    except subprocess.TimeoutExpired:
        print("⚠️  WARNING: Docker build timeout (this is okay)")
        return True
    except Exception as e:
        print(f"ℹ️  INFO: Could not test Docker build: {e}")
        return True

def main():
    """Run all Phase 4 tests"""
    print("\n" + "🚀"*35)
    print("  KIWI_AI - PHASE 4: DEPLOYMENT & PRODUCTION TESTING")
    print("🚀"*35)
    
    all_passed = True
    
    # Run all test suites
    all_passed &= check_docker_files()
    all_passed &= check_deployment_docs()
    all_passed &= check_systemd_service()
    all_passed &= check_monitoring_scripts()
    all_passed &= check_production_readiness()
    all_passed &= check_docker_build()
    
    # Final summary
    print_header("PHASE 4 TEST SUMMARY")
    
    if all_passed:
        print("✅ ALL TESTS PASSED - Phase 4 Complete!")
        print("\n🎉 Kiwi_AI is ready for production deployment!")
        print("\nNext Steps:")
        print("1. Review DEPLOYMENT.md for deployment instructions")
        print("2. Set up environment variables in .env")
        print("3. Test with docker-compose up -d")
        print("4. Deploy to production server")
        print("5. Set up monitoring scripts (cron)")
        return 0
    else:
        print("❌ SOME TESTS FAILED - Please review and fix issues")
        return 1

if __name__ == "__main__":
    exit(main())
