#!/usr/bin/env python3
"""
Analyze REAL benchmark results from AGENTISSUE-BENCH
Compare with paper results to verify accuracy
"""

import os
import json
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Tuple

# Paper's reported results (from Table 2)
PAPER_RESULTS = {
    "Agentless": {
        "GPT-4o": {"plausible": 12.00, "correct": 3.33, "file_level": 27.82, "function_level": 12.99},
        "Claude-3.5-S": {"plausible": 12.00, "correct": 4.00, "file_level": 27.35, "function_level": 17.50}
    },
    "AutoCodeRover": {
        "GPT-4o": {"plausible": 7.33, "correct": 1.33, "file_level": 22.07, "function_level": 14.77},
        "Claude-3.5-S": {"plausible": 12.67, "correct": 4.67, "file_level": 25.81, "function_level": 19.18}
    },
    "SWE-agent": {
        "GPT-4o": {"plausible": 0.67, "correct": 0.67, "file_level": 11.67, "function_level": 4.22},
        "Claude-3.5-S": {"plausible": 2.00, "correct": 2.00, "file_level": 9.52, "function_level": 6.78}
    }
}

# All 50 issues from test_agentissue_bench.py
ALL_ISSUES = [
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

class BenchmarkAnalyzer:
    def __init__(self, benchmark_dir: str = "/Users/tranvanhuy/Desktop/Research/AgentIssue-Bench"):
        self.benchmark_dir = benchmark_dir
        self.patches_dir = os.path.join(benchmark_dir, "Generated Patches")
        
    def count_patches_per_issue(self, agent: str, llm: str) -> Dict[str, int]:
        """Count number of patches per issue for each agent+LLM combination"""
        agent_map = {
            "Agentless": "Agentless",
            "AutoCodeRover": "Auto-code-rover",
            "SWE-agent": "swe-agent"
        }
        llm_map = {
            "GPT-4o": "gpt",
            "Claude-3.5-S": "claude"
        }
        
        agent_folder = agent_map[agent]
        llm_folder = llm_map[llm]
        
        if agent == "Agentless":
            base_dir = os.path.join(self.patches_dir, agent_folder, f"results_{llm_folder}")
        elif agent == "AutoCodeRover":
            base_dir = os.path.join(self.patches_dir, agent_folder, f"ALLPatches-{llm_folder}")
        else:  # SWE-agent
            base_dir = os.path.join(self.patches_dir, agent_folder, f"Patches_{llm_folder.capitalize()}")
        
        patch_counts = {}
        for issue in ALL_ISSUES:
            issue_dir = os.path.join(base_dir, issue)
            if os.path.exists(issue_dir) and os.path.isdir(issue_dir):
                patches = [f for f in os.listdir(issue_dir) if f.endswith(".patch")]
                patch_counts[issue] = len(patches)
            else:
                patch_counts[issue] = 0
        
        return patch_counts
    
    def analyze_coverage(self, agent: str, llm: str) -> Dict:
        """Analyze which issues have patches (coverage)"""
        patch_counts = self.count_patches_per_issue(agent, llm)
        
        issues_with_patches = [issue for issue, count in patch_counts.items() if count > 0]
        issues_without_patches = [issue for issue, count in patch_counts.items() if count == 0]
        
        total_patches = sum(patch_counts.values())
        coverage_rate = len(issues_with_patches) / len(ALL_ISSUES) * 100
        
        return {
            "total_issues": len(ALL_ISSUES),
            "issues_with_patches": len(issues_with_patches),
            "issues_without_patches": len(issues_without_patches),
            "total_patches_generated": total_patches,
            "coverage_rate": coverage_rate,
            "issues_with_patches_list": issues_with_patches,
            "issues_without_patches_list": issues_without_patches,
            "patches_per_issue": patch_counts
        }
    
    def sample_patch_content(self, agent: str, llm: str, issue: str) -> str:
        """Sample một patch để xem nội dung"""
        agent_map = {
            "Agentless": "Agentless",
            "AutoCodeRover": "Auto-code-rover",
            "SWE-agent": "swe-agent"
        }
        llm_map = {
            "GPT-4o": "gpt",
            "Claude-3.5-S": "claude"
        }
        
        agent_folder = agent_map[agent]
        llm_folder = llm_map[llm]
        
        if agent == "Agentless":
            issue_dir = os.path.join(self.patches_dir, agent_folder, f"results_{llm_folder}", issue)
        elif agent == "AutoCodeRover":
            issue_dir = os.path.join(self.patches_dir, agent_folder, f"ALLPatches-{llm_folder}", issue)
        else:
            issue_dir = os.path.join(self.patches_dir, agent_folder, f"Patches_{llm_folder.capitalize()}", issue)
        
        if os.path.exists(issue_dir):
            patches = [f for f in os.listdir(issue_dir) if f.endswith(".patch")]
            if patches:
                patch_path = os.path.join(issue_dir, patches[0])
                with open(patch_path, 'r', encoding='utf-8') as f:
                    return f.read()
        return ""
    
    def generate_full_report(self) -> Dict:
        """Generate complete analysis report"""
        print("\n" + "="*70)
        print("ANALYZING REAL BENCHMARK DATA FROM AGENTISSUE-BENCH")
        print("="*70)
        
        all_results = {}
        
        for agent in ["Agentless", "AutoCodeRover", "SWE-agent"]:
            all_results[agent] = {}
            for llm in ["GPT-4o", "Claude-3.5-S"]:
                print(f"\nAnalyzing {agent} + {llm}...")
                coverage = self.analyze_coverage(agent, llm)
                all_results[agent][llm] = coverage
                
                print(f"  Coverage: {coverage['coverage_rate']:.2f}% ({coverage['issues_with_patches']}/{coverage['total_issues']})")
                print(f"  Total patches: {coverage['total_patches_generated']}")
        
        # Compare with paper results
        print("\n" + "="*70)
        print("COMPARISON WITH PAPER RESULTS")
        print("="*70)
        
        comparison = {}
        for agent in ["Agentless", "AutoCodeRover", "SWE-agent"]:
            comparison[agent] = {}
            for llm in ["GPT-4o", "Claude-3.5-S"]:
                paper_data = PAPER_RESULTS[agent][llm]
                our_data = all_results[agent][llm]
                
                # Paper reports plausible resolution rate (12%, 4%, etc.)
                # We can check coverage (how many issues have patches)
                comparison[agent][llm] = {
                    "paper_plausible_rate": paper_data["plausible"],
                    "paper_correct_rate": paper_data["correct"],
                    "our_coverage_rate": our_data["coverage_rate"],
                    "our_total_patches": our_data["total_patches_generated"],
                    "issues_attempted": our_data["issues_with_patches"],
                    "issues_not_attempted": our_data["issues_without_patches"]
                }
                
                print(f"\n{agent} + {llm}:")
                print(f"  Paper: {paper_data['plausible']:.2f}% plausible, {paper_data['correct']:.2f}% correct")
                print(f"  Our data: {our_data['coverage_rate']:.2f}% coverage ({our_data['issues_with_patches']}/50 issues)")
                print(f"  Total patches generated: {our_data['total_patches_generated']}")
        
        return {
            "analysis_results": all_results,
            "paper_comparison": comparison,
            "paper_reported_results": PAPER_RESULTS
        }

if __name__ == "__main__":
    analyzer = BenchmarkAnalyzer()
    results = analyzer.generate_full_report()
    
    # Save results
    output_file = "/Users/tranvanhuy/Desktop/Research/real_benchmark_analysis.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n{'='*70}")
    print(f"Full results saved to: {output_file}")
    print("="*70)
    
    # Show unresolved issues across all agents
    print("\n" + "="*70)
    print("UNRESOLVED ISSUES (No patches from any agent+LLM)")
    print("="*70)
    
    all_covered_issues = set()
    for agent in ["Agentless", "AutoCodeRover", "SWE-agent"]:
        for llm in ["GPT-4o", "Claude-3.5-S"]:
            covered = results["analysis_results"][agent][llm]["issues_with_patches_list"]
            all_covered_issues.update(covered)
    
    unresolved_issues = [issue for issue in ALL_ISSUES if issue not in all_covered_issues]
    
    print(f"\nTotal unresolved: {len(unresolved_issues)}/50")
    for issue in unresolved_issues:
        print(f"  - {issue}")
    
    print("\n" + "="*70)
    print("SAMPLE PATCH EXAMPLES")
    print("="*70)
    
    # Sample một vài patches
    sample_issues = ["crewai_1323", "autogen_4733", "agixt_1026"]
    for issue in sample_issues:
        print(f"\n### Issue: {issue}")
        for agent in ["Agentless"]:
            for llm in ["Claude-3.5-S"]:
                patch = analyzer.sample_patch_content(agent, llm, issue)
                if patch:
                    lines = patch.split('\n')
                    preview = '\n'.join(lines[:20])
                    print(f"\n{agent} + {llm} (first 20 lines):")
                    print(preview)
                    if len(lines) > 20:
                        print(f"... ({len(lines) - 20} more lines)")
                    break

