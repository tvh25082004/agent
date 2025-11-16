#!/usr/bin/env python3
"""
Export real benchmark results to CSV format
"""

import json
import csv
import os
from pathlib import Path

# Load analyzed data
with open('real_benchmark_analysis.json', 'r') as f:
    data = json.load(f)

# All issues
ALL_ISSUES = [
    "agixt_1026", "crewai_1370", "agixt_1030", "crewai_1463",
    "agixt_1253", "crewai_1532", "agixt_1256", "crewai_1723",
    "agixt_1369", "crewai_1753", "agixt_1371", "crewai_1824",
    "ai_5628", "crewai_1934", "haystack_9523", "evoninja_504",
    "ai_4619", "evoninja_515", "haystack_8912", "evoninja_525",
    "evoninja_594", "evoninja_652", "autogen_4733", "autogen_4382",
    "autogen_4785", "autogen_4197", "autogen_5007", "lagent_239",
    "ai_4411", "lagent_244", "ai_6510", "lagent_279",
    "camel_1145", "autogen_3361", "camel_1273", "metagpt_1313",
    "camel_1614", "autogen_1844", "camel_88", "autogen_1174",
    "chatdev_318", "pythagora_55", "chatdev_413", "superagent_953",
    "chatdev_465", "crewai_1270", "crewai_1323", "sweagent_741",
    "gpt-engineer_1197", "gpt-researcher_1027"
]

# CSV 1: Overall Results Summary
csv1_file = "benchmark_results_summary.csv"
with open(csv1_file, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow([
        "Agent", "LLM", 
        "Coverage_Rate_%", "Issues_With_Patches", "Total_Issues",
        "Total_Patches_Generated", "Avg_Patches_Per_Issue",
        "Paper_Plausible_%", "Paper_Correct_%",
        "Paper_File_Localization_%", "Paper_Function_Localization_%"
    ])
    
    paper_results = {
        "Agentless": {
            "GPT-4o": {"plausible": 12.00, "correct": 3.33, "file": 27.82, "func": 12.99},
            "Claude-3.5-S": {"plausible": 12.00, "correct": 4.00, "file": 27.35, "func": 17.50}
        },
        "AutoCodeRover": {
            "GPT-4o": {"plausible": 7.33, "correct": 1.33, "file": 22.07, "func": 14.77},
            "Claude-3.5-S": {"plausible": 12.67, "correct": 4.67, "file": 25.81, "func": 19.18}
        },
        "SWE-agent": {
            "GPT-4o": {"plausible": 0.67, "correct": 0.67, "file": 11.67, "func": 4.22},
            "Claude-3.5-S": {"plausible": 2.00, "correct": 2.00, "file": 9.52, "func": 6.78}
        }
    }
    
    for agent in ["Agentless", "AutoCodeRover", "SWE-agent"]:
        for llm in ["GPT-4o", "Claude-3.5-S"]:
            result = data["analysis_results"][agent][llm]
            paper = paper_results[agent][llm]
            
            avg_patches = result["total_patches_generated"] / max(result["issues_with_patches"], 1)
            
            writer.writerow([
                agent, llm,
                f"{result['coverage_rate']:.2f}",
                result["issues_with_patches"],
                result["total_issues"],
                result["total_patches_generated"],
                f"{avg_patches:.2f}",
                f"{paper['plausible']:.2f}",
                f"{paper['correct']:.2f}",
                f"{paper['file']:.2f}",
                f"{paper['func']:.2f}"
            ])

print(f"✅ Created: {csv1_file}")

# CSV 2: Per-Issue Detailed Results
csv2_file = "benchmark_results_per_issue.csv"
with open(csv2_file, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    
    header = ["Issue_Tag", "Repository"]
    for agent in ["Agentless", "AutoCodeRover", "SWE-agent"]:
        for llm in ["GPT-4o", "Claude"]:
            header.append(f"{agent}_{llm}_Patches")
    header.extend(["Total_Patches", "Any_Agent_Attempted", "All_Agents_Failed"])
    
    writer.writerow(header)
    
    for issue in ALL_ISSUES:
        # Extract repository name from tag
        repo = issue.split('_')[0]
        
        row = [issue, repo]
        total = 0
        
        for agent in ["Agentless", "AutoCodeRover", "SWE-agent"]:
            for llm in ["GPT-4o", "Claude-3.5-S"]:
                patches = data["analysis_results"][agent][llm]["patches_per_issue"][issue]
                row.append(patches)
                total += patches
        
        row.append(total)
        row.append("Yes" if total > 0 else "No")
        row.append("Yes" if total == 0 else "No")
        
        writer.writerow(row)

print(f"✅ Created: {csv2_file}")

# CSV 3: Agent Comparison
csv3_file = "benchmark_agent_comparison.csv"
with open(csv3_file, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow([
        "Agent", 
        "Avg_Coverage_%", "Avg_Correct_%", 
        "Best_LLM", "Best_Correct_%",
        "Total_Patches_Generated",
        "Coverage_Rank", "Resolution_Rank"
    ])
    
    for agent in ["Agentless", "AutoCodeRover", "SWE-agent"]:
        gpt_coverage = data["analysis_results"][agent]["GPT-4o"]["coverage_rate"]
        claude_coverage = data["analysis_results"][agent]["Claude-3.5-S"]["coverage_rate"]
        avg_coverage = (gpt_coverage + claude_coverage) / 2
        
        gpt_correct = data["paper_comparison"][agent]["GPT-4o"]["paper_correct_rate"]
        claude_correct = data["paper_comparison"][agent]["Claude-3.5-S"]["paper_correct_rate"]
        avg_correct = (gpt_correct + claude_correct) / 2
        
        best_llm = "Claude" if claude_correct > gpt_correct else "GPT-4o"
        best_correct = max(gpt_correct, claude_correct)
        
        total_patches = (data["analysis_results"][agent]["GPT-4o"]["total_patches_generated"] +
                        data["analysis_results"][agent]["Claude-3.5-S"]["total_patches_generated"])
        
        writer.writerow([
            agent,
            f"{avg_coverage:.2f}",
            f"{avg_correct:.2f}",
            best_llm,
            f"{best_correct:.2f}",
            total_patches,
            "", ""  # Will fill ranks manually or in next step
        ])

print(f"✅ Created: {csv3_file}")

# CSV 4: Unresolved Issues Detail
csv4_file = "benchmark_unresolved_issues.csv"
with open(csv4_file, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow([
        "Issue_Tag", "Repository", 
        "Agentless_GPT", "Agentless_Claude",
        "ACR_GPT", "ACR_Claude",
        "SWE_GPT", "SWE_Claude",
        "Total_Attempts", "Status"
    ])
    
    for issue in ALL_ISSUES:
        repo = issue.split('_')[0]
        
        agentless_gpt = data["analysis_results"]["Agentless"]["GPT-4o"]["patches_per_issue"][issue]
        agentless_claude = data["analysis_results"]["Agentless"]["Claude-3.5-S"]["patches_per_issue"][issue]
        acr_gpt = data["analysis_results"]["AutoCodeRover"]["GPT-4o"]["patches_per_issue"][issue]
        acr_claude = data["analysis_results"]["AutoCodeRover"]["Claude-3.5-S"]["patches_per_issue"][issue]
        swe_gpt = data["analysis_results"]["SWE-agent"]["GPT-4o"]["patches_per_issue"][issue]
        swe_claude = data["analysis_results"]["SWE-agent"]["Claude-3.5-S"]["patches_per_issue"][issue]
        
        total = agentless_gpt + agentless_claude + acr_gpt + acr_claude + swe_gpt + swe_claude
        
        if total == 0:
            status = "Completely Unresolved"
        elif total < 3:
            status = "Mostly Unresolved"
        elif total < 10:
            status = "Partially Resolved"
        else:
            status = "Well Attempted"
        
        writer.writerow([
            issue, repo,
            agentless_gpt, agentless_claude,
            acr_gpt, acr_claude,
            swe_gpt, swe_claude,
            total, status
        ])

print(f"✅ Created: {csv4_file}")

print("\n" + "="*70)
print("ALL CSV FILES CREATED SUCCESSFULLY!")
print("="*70)
print(f"\n1. {csv1_file} - Overall summary with paper comparison")
print(f"2. {csv2_file} - Per-issue detailed breakdown")  
print(f"3. {csv3_file} - Agent comparison table")
print(f"4. {csv4_file} - Unresolved issues analysis")
print("\nAll files are in: /Users/tranvanhuy/Desktop/Research/")

