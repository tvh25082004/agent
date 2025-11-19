#!/usr/bin/env python3
"""
Kiểm tra xem máy có đủ điều kiện chạy đầy đủ eval như GitHub không
"""

import subprocess
import sys
import platform

print("=" * 80)
print("KIỂM TRA ĐIỀU KIỆN HỆ THỐNG")
print("=" * 80)
print()

# 1. Check OS và Architecture
print("1. HỆ THỐNG:")
os_name = platform.system()
arch = platform.machine()
print(f"   OS: {os_name}")
print(f"   Architecture: {arch}")

if arch == "arm64":
    print("   ⚠️  ARM64 (Mac M1/M2/M3) - Docker images chỉ hỗ trợ amd64")
    arm64_issue = True
else:
    print("   ✓ Architecture phù hợp")
    arm64_issue = False

print()

# 2. Check Docker
print("2. DOCKER:")
try:
    result = subprocess.run(["docker", "--version"], capture_output=True, text=True)
    if result.returncode == 0:
        print(f"   ✓ Docker installed: {result.stdout.strip()}")
        
        # Check Docker running
        result = subprocess.run(["docker", "ps"], capture_output=True, text=True)
        if result.returncode == 0:
            print("   ✓ Docker daemon running")
        else:
            print("   ❌ Docker daemon not running")
            sys.exit(1)
    else:
        print("   ❌ Docker not installed")
        sys.exit(1)
except FileNotFoundError:
    print("   ❌ Docker not found")
    sys.exit(1)

# Check Docker images
result = subprocess.run(["docker", "images"], capture_output=True, text=True)
agentissue_images = [line for line in result.stdout.split('\n') if 'agentissue-bench' in line]
print(f"   Images có sẵn: {len(agentissue_images) - 1}")  # -1 vì có header

print()

# 3. Check Docker Hub rate limit
print("3. DOCKER HUB RATE LIMIT:")
print("   ⚠️  Đang kiểm tra rate limit...")
try:
    result = subprocess.run(
        ["docker", "pull", "hello-world"],
        capture_output=True,
        text=True,
        timeout=10
    )
    if "rate limit" in result.stderr.lower():
        print("   ❌ Đã vượt rate limit")
        rate_limit_issue = True
    else:
        print("   ✓ Chưa vượt rate limit")
        rate_limit_issue = False
except:
    print("   ⚠️  Không thể kiểm tra (có thể đã vượt limit)")
    rate_limit_issue = True

print()

# 4. Check network
print("4. NETWORK:")
try:
    result = subprocess.run(
        ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", "https://hub.docker.com"],
        timeout=5
    )
    if result.returncode == 0:
        print("   ✓ Có thể kết nối Docker Hub")
    else:
        print("   ⚠️  Không thể kết nối Docker Hub")
except:
    print("   ⚠️  Không thể kiểm tra network")

print()

# 5. Tổng kết
print("=" * 80)
print("KẾT LUẬN:")
print("=" * 80)

issues = []
if arm64_issue:
    issues.append("ARM64 không hỗ trợ Docker images (cần amd64)")

if rate_limit_issue:
    issues.append("Docker Hub rate limit")

if issues:
    print("\n❌ KHÔNG THỂ chạy đầy đủ trên máy này:")
    for issue in issues:
        print(f"   - {issue}")
    
    print("\n💡 GIẢI PHÁP:")
    print("   1. Dùng máy Intel/AMD (không phải Mac M1/M2/M3)")
    print("   2. Dùng cloud VM (AWS EC2, Google Cloud, Azure)")
    print("   3. Đăng nhập Docker Hub để tăng rate limit")
    print("   4. Đợi rate limit reset (sau vài giờ)")
    
    print("\n📊 HIỆN TẠI:")
    print("   - Script flexible sẽ skip các tags không có images")
    print("   - Chỉ evaluate được với images đã có")
    print("   - Không thể chạy đầy đủ như GitHub")
else:
    print("\n✅ Máy đủ điều kiện chạy đầy đủ!")
    print("   Có thể chạy: python evaluate_patches.py")

print("=" * 80)
