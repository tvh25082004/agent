#!/usr/bin/env python3
"""
Script đánh giá patches từ paper (theo hướng dẫn GitHub)
Sử dụng patches có sẵn trong Generated Patches, không gen lại
"""

import os
import sys
import subprocess
from pathlib import Path

# Paths
BENCHMARK_DIR = Path("/Users/tranvanhuy/Desktop/Research/AgentIssue-Bench")
PATCHES_DIR = BENCHMARK_DIR / "Patches"
EVAL_SCRIPT = BENCHMARK_DIR / "eval_patches.py"

def check_setup():
    """Kiểm tra setup trước khi chạy"""
    print("=" * 80)
    print("KIỂM TRA SETUP")
    print("=" * 80)
    
    # Check Patches directory
    if not PATCHES_DIR.exists():
        print(f"❌ Patches directory không tồn tại: {PATCHES_DIR}")
        print("   Chạy: python AgentIssue-Bench/prepare_patches_for_eval.py")
        return False
    print(f"✓ Patches directory: {PATCHES_DIR}")
    
    # Count patches
    patch_count = sum(1 for _ in PATCHES_DIR.rglob("*.patch"))
    tag_count = len([d for d in PATCHES_DIR.iterdir() if d.is_dir()])
    print(f"✓ Total patches: {patch_count}")
    print(f"✓ Tag directories: {tag_count}")
    
    # Check eval script
    if not EVAL_SCRIPT.exists():
        print(f"❌ Eval script không tồn tại: {EVAL_SCRIPT}")
        return False
    print(f"✓ Eval script: {EVAL_SCRIPT}")
    
    # Check API keys
    api_key = os.getenv("OPENAI_API_KEY")
    api_base = os.getenv("OPENAI_API_BASE")
    if not api_key:
        print("⚠️  OPENAI_API_KEY chưa set (có thể cần cho Docker containers)")
    else:
        print(f"✓ OPENAI_API_KEY: {api_key[:20]}...")
    if api_base:
        print(f"✓ OPENAI_API_BASE: {api_base}")
    
    print("=" * 80)
    return True

def run_evaluation():
    """Chạy đánh giá patches"""
    print("\n" + "=" * 80)
    print("BẮT ĐẦU ĐÁNH GIÁ PATCHES")
    print("=" * 80)
    print(f"Patches directory: {PATCHES_DIR}")
    print(f"Eval script: {EVAL_SCRIPT}")
    print(f"Kết quả sẽ lưu: {BENCHMARK_DIR / 'patch_eval.log'}")
    print("\n⏱️  Estimated time: 1-2 giờ (tùy số patches và Docker images)")
    print("⚠️  Lưu ý: Máy ARM64 có thể gặp lỗi khi pull Docker images")
    print("=" * 80)
    print()
    
    # Change to benchmark directory
    os.chdir(BENCHMARK_DIR)
    
    # Use flexible version if available, otherwise use original
    flexible_script = BENCHMARK_DIR / "eval_patches_flexible.py"
    script_to_run = flexible_script if flexible_script.exists() else EVAL_SCRIPT
    
    print(f"Using script: {script_to_run.name}")
    
    # Run eval script
    try:
        result = subprocess.run(
            [sys.executable, str(script_to_run)],
            check=False,
            cwd=str(BENCHMARK_DIR)
        )
        
        if result.returncode == 0:
            print("\n" + "=" * 80)
            print("✅ ĐÁNH GIÁ HOÀN TẤT!")
            print("=" * 80)
            print(f"📝 Xem kết quả: cat {BENCHMARK_DIR / 'patch_eval.log'}")
        else:
            print("\n" + "=" * 80)
            print("⚠️  ĐÁNH GIÁ CÓ LỖI")
            print("=" * 80)
            print(f"📝 Xem log: cat {BENCHMARK_DIR / 'patch_eval.log'}")
            print("⚠️  Có thể do Docker images không hỗ trợ ARM64")
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"\n❌ Lỗi khi chạy evaluation: {e}")
        return False

def main():
    """Main function"""
    print("\n" + "=" * 80)
    print("AGENTISSUE-BENCH - EVALUATE PATCHES")
    print("Đánh giá patches từ paper (không gen lại)")
    print("=" * 80)
    print()
    
    # Check setup
    if not check_setup():
        print("\n❌ Setup không đầy đủ. Vui lòng kiểm tra lại.")
        sys.exit(1)
    
    # Confirm
    print("\nBắt đầu đánh giá? (y/n) [y]: ", end="")
    response = input().strip().lower()
    if response and response != 'y':
        print("Đã hủy.")
        sys.exit(0)
    
    # Run evaluation
    success = run_evaluation()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()

