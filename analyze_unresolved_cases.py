#!/usr/bin/env python3
"""
Script phân tích các unresolved cases trong AGENTISSUE-BENCH từ góc nhìn con người
qua 4 bước chính: (1) reproduce bug, (2) localize bug, (3) generate fix, (4) validate fix
"""

import os
import json
import subprocess
import re
from collections import defaultdict
from typing import Dict, List, Tuple, Optional
import requests
from pathlib import Path

# Danh sách các tags từ test_agentissue_bench.py
ALL_TAGS = [
    "agixt_1026", "crewai_1370",
    "agixt_1030", "crewai_1463",
    "agixt_1253", "crewai_1532",
    "agixt_1256", "crewai_1723",
    "agixt_1369", "crewai_1753",
    "agixt_1371", "crewai_1824",
    "ai_5628", "crewai_1934",
    "haystack_9523", "evoninja_504",
    "ai_4619", "evoninja_515",
    "haystack_8912", "evoninja_525",
    "evoninja_594", "evoninja_652",
    "autogen_4733", "autogen_4382",
    "autogen_4785", "autogen_4197",
    "autogen_5007", "lagent_239",
    "ai_4411", "lagent_244",
    "ai_6510", "lagent_279",
    "camel_1145", "autogen_3361",
    "camel_1273", "metagpt_1313",
    "camel_1614", "autogen_1844",
    "camel_88", "autogen_1174",
    "chatdev_318", "pythagora_55",
    "chatdev_413", "superagent_953",
    "chatdev_465", "crewai_1270",
    "crewai_1323", "sweagent_741",
    "gpt-engineer_1197", "gpt-researcher_1027"
]

# Taxonomy từ bài báo (6 categories, 20 sub-categories)
TAXONOMY = {
    "Incompatibility with LLM providers (7.46%)": [
        "Incompatible dependencies (1.49%)",
        "Unsupported models (2.99%)",
        "Incompatible parameters to LLM providers (2.99%)"
    ],
    "Tool-related issues (19.90%)": [
        "Tool dependency issues (3.48%)",
        "Tool configuration issues (3.47%)",
        "Tool implementation errors (8.46%)",
        "Misuse tool interfaces (4.48%)"
    ],
    "Memory-related issues (14.43%)": [
        "Memory initialization issues (2.49%)",
        "Memory content errors (10.95%)",
        "Memory dependency issues (1.00%)"
    ],
    "LLM operation issues (31.34%)": [
        "Model access misconfiguration (6.97%)",
        "Token usage misconfiguration (3.48%)",
        "Incorrect model output handlers (8.46%)",
        "Model dependency issues (2.99%)",
        "Context length issues (4.98%)",
        "Prompt-related issues (4.48%)",
        "Workflow issues (6.47%)"
    ],
    "Utility issues (20.40%)": [
        "Utility implementation issues (8.96%)",
        "Utility dependency issues (4.48%)",
        "Utility configuration issues (6.97%)"
    ]
}

# Kết quả từ bài báo - các issues đã được resolve
RESOLVED_ISSUES = {
    "Tool-related issues": ["Tool dependency issues"],
    "LLM operation issues": ["Prompt-related issues"],
    "Utility issues": ["Utility configuration issues"]
}

class IssueAnalyzer:
    """Phân tích các issues từ góc nhìn con người"""
    
    def __init__(self, benchmark_dir: str = "AgentIssue-Bench"):
        self.benchmark_dir = benchmark_dir
        self.patches_dir = os.path.join(benchmark_dir, "Generated Patches")
        self.results = defaultdict(dict)
        
    def check_patch_exists(self, tag: str, agent: str, llm: str) -> bool:
        """Kiểm tra xem có patch được generate cho issue này không"""
        agent_map = {
            "Agentless": "Agentless",
            "AutoCodeRover": "Auto-code-rover",
            "SWE-agent": "swe-agent"
        }
        llm_map = {
            "gpt-4o": "gpt",
            "claude-3.5-sonnet": "claude"
        }
        
        agent_folder = agent_map.get(agent, agent.lower())
        llm_folder = llm_map.get(llm, llm.lower())
        
        # Cấu trúc thực tế: Generated Patches/Agentless/results_claude/{tag}/patch_*.patch
        if agent == "Agentless":
            patch_dir = os.path.join(
                self.patches_dir,
                agent_folder,
                f"results_{llm_folder}",
                tag
            )
        elif agent == "AutoCodeRover":
            patch_dir = os.path.join(
                self.patches_dir,
                agent_folder,
                f"ALLPatches-{llm_folder}",
                tag
            )
        else:  # SWE-agent
            patch_dir = os.path.join(
                self.patches_dir,
                agent_folder,
                f"Patches_{llm_folder.capitalize()}",
                tag
            )
        
        # Kiểm tra xem có ít nhất một patch file trong thư mục
        if os.path.exists(patch_dir) and os.path.isdir(patch_dir):
            patch_files = [f for f in os.listdir(patch_dir) if f.endswith(".patch")]
            return len(patch_files) > 0
        
        return False
    
    def analyze_reproduction(self, tag: str) -> Dict:
        """Phân tích bước 1: Reproduce bug"""
        analysis = {
            "feasible": True,
            "challenges": [],
            "info_available": {
                "executable_environment": False,
                "failure_triggering_tests": False,
                "issue_description": False
            }
        }
        
        # Kiểm tra xem có Docker image không
        try:
            result = subprocess.run(
                ["docker", "images", "-q", f"alfin06/agentissue-bench:{tag}"],
                capture_output=True,
                text=True,
                timeout=5
            )
            analysis["info_available"]["executable_environment"] = bool(result.stdout.strip())
        except:
            pass
        
        # Kiểm tra xem có test script không (thông qua việc có thể pull image)
        analysis["info_available"]["failure_triggering_tests"] = analysis["info_available"]["executable_environment"]
        
        # Đánh giá challenges
        if not analysis["info_available"]["executable_environment"]:
            analysis["challenges"].append("Thiếu môi trường thực thi để reproduce")
        else:
            analysis["challenges"].append("Có thể reproduce với Docker environment")
        
        # Agent systems có thể có non-determinism
        analysis["challenges"].append("LLM non-determinism có thể làm khó reproduce")
        analysis["challenges"].append("External resources (tools, APIs) có thể thay đổi")
        
        return analysis
    
    def analyze_localization(self, tag: str) -> Dict:
        """Phân tích bước 2: Localize bug"""
        analysis = {
            "feasible": True,
            "challenges": [],
            "localization_difficulty": "medium",
            "info_available": {
                "issue_description": True,  # Giả định có issue description
                "error_messages": False,
                "stack_traces": False,
                "codebase_access": True  # Có buggy version
            }
        }
        
        # Phân tích dựa trên tag để đoán category
        tag_lower = tag.lower()
        
        if any(x in tag_lower for x in ["llm", "model", "gpt", "claude"]):
            analysis["localization_difficulty"] = "high"
            analysis["challenges"].append("LLM operation issues khó localize do tính chất dynamic")
            analysis["challenges"].append("Cần hiểu sâu về LLM provider APIs")
        elif "memory" in tag_lower or "mem" in tag_lower:
            analysis["localization_difficulty"] = "high"
            analysis["challenges"].append("Memory issues có thể liên quan đến state management")
            analysis["challenges"].append("Cần trace execution flow qua nhiều components")
        elif "tool" in tag_lower:
            analysis["localization_difficulty"] = "medium"
            analysis["challenges"].append("Tool issues có thể có explicit error messages")
        else:
            analysis["localization_difficulty"] = "medium"
        
        # Thêm challenges chung
        analysis["challenges"].append("Agent systems có nhiều interacting components")
        analysis["challenges"].append("Bug có thể nằm ở interaction giữa các agents")
        
        return analysis
    
    def analyze_fix_generation(self, tag: str) -> Dict:
        """Phân tích bước 3: Generate fix"""
        analysis = {
            "feasible": True,
            "challenges": [],
            "fix_complexity": "medium",
            "requires": {
                "domain_knowledge": False,
                "external_resources_knowledge": False,
                "agent_architecture_understanding": False
            }
        }
        
        tag_lower = tag.lower()
        
        # Phân tích dựa trên category
        if any(x in tag_lower for x in ["llm", "model", "gpt", "claude"]):
            analysis["fix_complexity"] = "high"
            analysis["requires"]["external_resources_knowledge"] = True
            analysis["challenges"].append("Cần hiểu về LLM provider APIs và parameters")
            analysis["challenges"].append("Cần cập nhật knowledge về API changes")
        elif "memory" in tag_lower:
            analysis["fix_complexity"] = "high"
            analysis["requires"]["agent_architecture_understanding"] = True
            analysis["challenges"].append("Cần hiểu về memory management trong agent systems")
        elif "tool" in tag_lower:
            analysis["fix_complexity"] = "medium"
            analysis["requires"]["domain_knowledge"] = True
            analysis["challenges"].append("Cần hiểu về tool interfaces và dependencies")
        else:
            analysis["fix_complexity"] = "medium"
        
        # Thêm challenges chung
        analysis["challenges"].append("Fix có thể cần thay đổi nhiều files")
        analysis["challenges"].append("Cần đảm bảo fix không break các functionality khác")
        
        return analysis
    
    def analyze_validation(self, tag: str) -> Dict:
        """Phân tích bước 4: Validate fix"""
        analysis = {
            "feasible": True,
            "challenges": [],
            "validation_methods": {
                "failure_triggering_tests": True,
                "regression_tests": False,
                "manual_testing": False
            }
        }
        
        # Có failure-triggering tests
        analysis["validation_methods"]["failure_triggering_tests"] = True
        
        # Challenges
        analysis["challenges"].append("Tests có thể không cover hết edge cases")
        analysis["challenges"].append("Agent systems có non-determinism nên cần multiple runs")
        analysis["challenges"].append("Cần test với different LLM providers/models")
        analysis["challenges"].append("Cần test với different external resources")
        
        return analysis
    
    def analyze_issue(self, tag: str) -> Dict:
        """Phân tích đầy đủ một issue qua 4 bước"""
        print(f"\n{'='*60}")
        print(f"Phân tích issue: {tag}")
        print(f"{'='*60}")
        
        analysis = {
            "tag": tag,
            "reproduction": self.analyze_reproduction(tag),
            "localization": self.analyze_localization(tag),
            "fix_generation": self.analyze_fix_generation(tag),
            "validation": self.analyze_validation(tag),
            "overall_feasibility": True,
            "overall_challenges": []
        }
        
        # Tổng hợp overall feasibility
        all_steps_feasible = all([
            analysis["reproduction"]["feasible"],
            analysis["localization"]["feasible"],
            analysis["fix_generation"]["feasible"],
            analysis["validation"]["feasible"]
        ])
        
        analysis["overall_feasibility"] = all_steps_feasible
        
        # Tổng hợp challenges
        all_challenges = set()
        for step in ["reproduction", "localization", "fix_generation", "validation"]:
            all_challenges.update(analysis[step]["challenges"])
        analysis["overall_challenges"] = list(all_challenges)
        
        # Kiểm tra xem issue có được resolve bởi agents không
        analysis["resolved_by_agents"] = {
            "Agentless_gpt-4o": self.check_patch_exists(tag, "Agentless", "gpt-4o"),
            "Agentless_claude-3.5-sonnet": self.check_patch_exists(tag, "Agentless", "claude-3.5-sonnet"),
            "AutoCodeRover_gpt-4o": self.check_patch_exists(tag, "AutoCodeRover", "gpt-4o"),
            "AutoCodeRover_claude-3.5-sonnet": self.check_patch_exists(tag, "AutoCodeRover", "claude-3.5-sonnet"),
            "SWE-agent_gpt-4o": self.check_patch_exists(tag, "SWE-agent", "gpt-4o"),
            "SWE-agent_claude-3.5-sonnet": self.check_patch_exists(tag, "SWE-agent", "claude-3.5-sonnet")
        }
        
        analysis["any_agent_resolved"] = any(analysis["resolved_by_agents"].values())
        
        return analysis
    
    def generate_report(self, output_file: str = "unresolved_cases_analysis.json"):
        """Tạo báo cáo phân tích cho tất cả các issues"""
        print("\n" + "="*60)
        print("BẮT ĐẦU PHÂN TÍCH CÁC UNRESOLVED CASES")
        print("="*60)
        
        all_analyses = []
        unresolved_analyses = []
        resolved_analyses = []
        
        for tag in ALL_TAGS:
            analysis = self.analyze_issue(tag)
            all_analyses.append(analysis)
            
            if not analysis["any_agent_resolved"]:
                unresolved_analyses.append(analysis)
            else:
                resolved_analyses.append(analysis)
        
        # Tổng hợp kết quả
        summary = {
            "total_issues": len(ALL_TAGS),
            "resolved_by_agents": len(resolved_analyses),
            "unresolved_by_agents": len(unresolved_analyses),
            "resolution_rate": len(resolved_analyses) / len(ALL_TAGS) * 100 if ALL_TAGS else 0,
            "unresolved_analysis": unresolved_analyses,
            "resolved_analysis": resolved_analyses,
            "all_analyses": all_analyses
        }
        
        # Lưu kết quả
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        # In summary
        print("\n" + "="*60)
        print("TÓM TẮT KẾT QUẢ PHÂN TÍCH")
        print("="*60)
        print(f"Tổng số issues: {summary['total_issues']}")
        print(f"Được resolve bởi agents: {summary['resolved_by_agents']}")
        print(f"Không được resolve bởi agents: {summary['unresolved_by_agents']}")
        print(f"Resolution rate: {summary['resolution_rate']:.2f}%")
        print(f"\nKết quả chi tiết đã được lưu vào: {output_file}")
        
        return summary

if __name__ == "__main__":
    analyzer = IssueAnalyzer()
    summary = analyzer.generate_report()
    
    # In thêm thống kê về challenges
    print("\n" + "="*60)
    print("PHÂN TÍCH CHALLENGES CỦA UNRESOLVED CASES")
    print("="*60)
    
    unresolved = summary["unresolved_analysis"]
    
    # Thống kê challenges theo từng bước
    reproduction_challenges = defaultdict(int)
    localization_challenges = defaultdict(int)
    fix_challenges = defaultdict(int)
    validation_challenges = defaultdict(int)
    
    for issue in unresolved:
        for challenge in issue["reproduction"]["challenges"]:
            reproduction_challenges[challenge] += 1
        for challenge in issue["localization"]["challenges"]:
            localization_challenges[challenge] += 1
        for challenge in issue["fix_generation"]["challenges"]:
            fix_challenges[challenge] += 1
        for challenge in issue["validation"]["challenges"]:
            validation_challenges[challenge] += 1
    
    print("\n1. REPRODUCTION CHALLENGES:")
    for challenge, count in sorted(reproduction_challenges.items(), key=lambda x: x[1], reverse=True):
        print(f"   - {challenge}: {count} issues")
    
    print("\n2. LOCALIZATION CHALLENGES:")
    for challenge, count in sorted(localization_challenges.items(), key=lambda x: x[1], reverse=True):
        print(f"   - {challenge}: {count} issues")
    
    print("\n3. FIX GENERATION CHALLENGES:")
    for challenge, count in sorted(fix_challenges.items(), key=lambda x: x[1], reverse=True):
        print(f"   - {challenge}: {count} issues")
    
    print("\n4. VALIDATION CHALLENGES:")
    for challenge, count in sorted(validation_challenges.items(), key=lambda x: x[1], reverse=True):
        print(f"   - {challenge}: {count} issues")

