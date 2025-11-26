#!/usr/bin/env python3
"""
Script đánh giá patches - Flexible version
- Skip images không pull được (rate limit, ARM64, etc.)
- Chỉ evaluate với images đã có hoặc pull được
- Không bắt buộc phải có tất cả images
"""

import os
import subprocess
import sys

PATCHES_ROOT = "Patches"
DOCKER_IMAGE_BASE = "alfin06/agentissue-bench"
LOG_FILE = "patch_eval.log"

global_success = 0
global_total = 0
grand_total_avg = 0
skipped_tags = []

def pull_image_safe(docker_image):
    """Pull image với error handling, return True nếu thành công"""
    try:
        result = subprocess.run(
            ["docker", "pull", docker_image],
            capture_output=True,
            text=True,
            timeout=60
        )
        if result.returncode == 0:
            return True
        else:
            # Check error type
            error_msg = result.stderr.lower()
            if "rate limit" in error_msg:
                print(f"⚠️  Rate limit - skipping {docker_image}")
            elif "arm64" in error_msg or "no matching manifest" in error_msg:
                print(f"⚠️  ARM64 not supported - skipping {docker_image}")
            else:
                print(f"⚠️  Pull failed - skipping {docker_image}: {result.stderr[:100]}")
            return False
    except subprocess.TimeoutExpired:
        print(f"⚠️  Timeout - skipping {docker_image}")
        return False
    except Exception as e:
        print(f"⚠️  Error - skipping {docker_image}: {e}")
        return False

def check_image_exists(docker_image):
    """Check xem image đã có local chưa"""
    try:
        # Check exact match
        result = subprocess.run(
            ["docker", "images", "--format", "{{.Repository}}:{{.Tag}}"],
            capture_output=True,
            text=True
        )
        existing_images = result.stdout.strip().split('\n')
        return docker_image in existing_images
    except:
        return False

with open(LOG_FILE, "w", encoding="utf-8") as log:
    print("=" * 80)
    print("FLEXIBLE PATCH EVALUATION")
    print("Sẽ skip images không pull được (rate limit, ARM64, etc.)")
    print("=" * 80)
    log.write("FLEXIBLE PATCH EVALUATION\n")
    log.write("=" * 80 + "\n")
    
    tags = sorted([d for d in os.listdir(PATCHES_ROOT) if os.path.isdir(os.path.join(PATCHES_ROOT, d))])
    total_tags = len(tags)
    
    print(f"\nTotal tags to evaluate: {total_tags}")
    print("=" * 80)
    
    for idx, tag in enumerate(tags, 1):
        patch_dir = os.path.join(PATCHES_ROOT, tag)
        if not os.path.isdir(patch_dir):
            continue

        patch_files = [f for f in os.listdir(patch_dir) if f.endswith(".patch")]
        if not patch_files:
            msg = f"Patch directory {patch_dir} has no .patch files, skipping."
            print(msg)
            log.write(msg + "\n")
            continue

        msg = f"\n[{idx}/{total_tags}] ===== Evaluating patches for tag: {tag} ====="
        print(msg)
        log.write(msg + "\n")
        docker_image = f"{DOCKER_IMAGE_BASE}:{tag}"

        # Check if image already exists
        if check_image_exists(docker_image):
            msg = f"✓ Docker image already exists: {docker_image}"
            print(msg)
            log.write(msg + "\n")
            image_available = True
        else:
            # Try to pull
            msg = f"Pulling docker image: {docker_image}"
            print(msg)
            log.write(msg + "\n")
            image_available = pull_image_safe(docker_image)
            
            if not image_available:
                skipped_tags.append(tag)
                msg = f"⚠️  Skipping tag {tag} (image not available)"
                print(msg)
                log.write(msg + "\n")
                continue

        success_count = 0
        total_count = len(patch_files)

        for patch_file in patch_files:
            patch_path = os.path.abspath(os.path.join(patch_dir, patch_file))
            msg = f"\n=== Testing patch: {patch_file} ==="
            print(msg)
            log.write(msg + "\n")
            docker_volumes = [
                "-v", f"{os.path.dirname(patch_path)}:/patches"
            ]
            if tag == "agixt_1369":
                # Special command for agixt_1369
                cmd = [
                    "docker", "run", "--rm",
                    "--network", "host",
                    "--entrypoint", "bash",
                    *docker_volumes,
                    "-e", "OPENAI_API_KEY=api-key",
                    "-e", "OPENAI_API_BASE=api-base-url",
                    docker_image,
                    "-c", f"/usr/local/bin/run_test_entrypoint.sh apply_patch /patches/{patch_file} && /usr/local/bin/run_test_entrypoint.sh test_patched"
                ]
                result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", timeout=300)
                output = result.stdout if result.stdout is not None else ""
                if "FAILED" in result.stdout or result.returncode != 0:
                    msg = f"❌ Patch {patch_file}: FAILED"
                    print(msg)
                    log.write(msg + "\n")
                    continue
                if ("PATCH SUCCEEDED" in result.stdout or 
                    "PATCH SUCCESSFULLY VERIFIED" in result.stdout or 
                    "FIX SUCCESSFULLY VERIFIED" in result.stdout or
                    "NO BUG" in result.stdout or
                    "FIX CONFIRMED" in result.stdout or
                    "PATCH VERIFIED" in result.stdout or
                    "patched succeeded" in result.stdout):
                    msg = f"✅ Patch {patch_file}: SUCCESS"
                    print(msg)
                    log.write(msg + "\n")
                    success_count += 1
                else:
                    msg = f"❌ Patch {patch_file}: FAILED"
                    print(msg)
                    log.write(msg + "\n")
            else:
                cmd = [
                    "docker", "run", "--rm",
                    "--entrypoint", "bash",
                    *docker_volumes,
                    "-e", "OPENAI_API_KEY=api-key",
                    "-e", "OPENAI_API_BASE=api-base-url",
                    docker_image,
                    "-c", f"/usr/local/bin/run_test_entrypoint.sh apply_patch /patches/{patch_file} && /usr/local/bin/run_test_entrypoint.sh test_patched"
                ]
                
                try:
                    result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", timeout=300)
                    output = result.stdout if result.stdout is not None else ""
                
                    if "FAILED" in result.stdout or result.returncode != 0:
                        msg = f"❌ Patch {patch_file}: FAILED"
                        print(msg)
                        log.write(msg + "\n")
                        continue
                    
                    if ("PATCH SUCCEEDED" in result.stdout or 
                        "PATCH SUCCESSFULLY VERIFIED" in result.stdout or 
                        "FIX SUCCESSFULLY VERIFIED" in result.stdout or
                        "NO BUG" in result.stdout or
                        "FIX CONFIRMED" in result.stdout or
                        "PATCH VERIFIED" in result.stdout):
                        msg = f"✅ Patch {patch_file}: SUCCESS"
                        print(msg)
                        log.write(msg + "\n")
                        success_count += 1
                    else:
                        msg = f"❌ Patch {patch_file}: FAILED"
                        print(msg)
                        log.write(msg + "\n")
                except subprocess.TimeoutExpired:
                    msg = f"❌ Patch {patch_file}: TIMEOUT"
                    print(msg)
                    log.write(msg + "\n")
                    container_ids = subprocess.check_output("docker ps -q", shell=True, text=True).splitlines()
                    for cid in container_ids:
                        if cid.strip():
                            subprocess.run(["docker", "rm", "-f", cid], check=False)
                    continue
                except Exception as e:
                    msg = f"❌ Patch {patch_file}: ERROR - {e}"
                    print(msg)
                    log.write(msg + "\n")
                    continue

        msg = f"\n=== Patch Testing Summary for {tag} ==="
        print(msg)
        log.write(msg + "\n")
        msg = f"Total patches tested: {total_count}"
        print(msg)
        log.write(msg + "\n")
        msg = f"Successful patches: {success_count}"
        print(msg)
        log.write(msg + "\n")
        msg = f"Failed patches: {total_count - success_count}"
        print(msg)
        log.write(msg + "\n")
        avg_score = success_count / total_count if total_count > 0 else 0
        msg = f"Plausible score: {avg_score:.2f}"
        print(msg)
        log.write(msg + "\n")
        grand_total_avg += avg_score
        msg = f"\n---------------------------------------------"
        print(msg)
        log.write(msg + "\n")

        global_success += success_count
        global_total += total_count

        # Optionally remove image after testing (comment out if want to keep)
        # subprocess.run(["docker", "rmi", "-f", docker_image], check=False)

    msg = "\n=== Global Patch Testing Summary ==="
    print(msg)
    log.write(msg + "\n")
    msg = f"Total patches tested: {global_total}"
    print(msg)
    log.write(msg + "\n")
    msg = f"Successful patches: {global_success}"
    print(msg)
    log.write(msg + "\n")
    msg = f"Failed patches: {global_total - global_success}"
    print(msg)
    log.write(msg + "\n")
    if global_total > 0:
        overall_score = global_success / global_total
        msg = f"Overall plausible score: {overall_score:.2f}"
    else:
        overall_score = 0
        msg = f"Overall plausible score: N/A (no patches tested)"
    print(msg)
    log.write(msg + "\n")
    
    if skipped_tags:
        msg = f"\n⚠️  Skipped tags ({len(skipped_tags)}): {', '.join(skipped_tags[:10])}"
        if len(skipped_tags) > 10:
            msg += f" ... and {len(skipped_tags) - 10} more"
        print(msg)
        log.write(msg + "\n")
        msg = f"Reason: Rate limit, ARM64 not supported, or pull failed"
        print(msg)
        log.write(msg + "\n")

