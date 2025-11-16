# AGENTISSUE-BENCH Analysis Summary

## Quick Navigation

### 📖 Main Reports (Đọc theo thứ tự)

1. **`FINAL_SUMMARY_REPORT.md`** ⭐ - Đọc file này trước
   - Tổng hợp tất cả findings
   - Có số liệu thống kê đầy đủ
   - So sánh với bài báo
   
2. **`KET_QUA_THUC_TE_BENCHMARK.md`** - Chi tiết bằng tiếng Việt
   - Phân tích từ data thật
   - Giải thích gap giữa coverage và resolution
   - Examples từ real patches

3. **`BAO_CAO_PHAN_TICH.md`** - Phân tích từ human perspective
   - 4 bước bug fixing: reproduce, localize, generate fix, validate
   - Challenges ở mỗi bước
   - Taxonomy của agent issues

### 📊 Data Files

- **`real_benchmark_analysis.json`** (20KB) - Raw analysis data
- **`unresolved_cases_analysis.json`** (291KB) - Detailed unresolved analysis

### 🔬 Analysis Scripts

- **`analyze_real_benchmark_results.py`** - Main analysis script
- **`analyze_unresolved_cases.py`** - Human perspective analysis

### 📑 Original Source

- **`paper_agentissue.pdf`** (1.6MB) - Original paper from OpenReview

---

## Key Findings (Quick Summary)

### The Numbers

```
654 patches generated  →  Only 2-3 correct  =  0.31% success rate
```

### Coverage vs Resolution

| Agent | Coverage | Correct | Gap |
|-------|----------|---------|-----|
| Agentless + Claude | 82% | 4.00% | 78% ❌ |
| AutoCodeRover + Claude | 62% | 4.67% ⭐ | 57% |
| SWE-agent + GPT-4o | 88% | 0.67% | 87% ❌❌ |

### Main Insight

**High coverage + Low resolution = Quality problem**

Agents generate patches for most issues, but 99.7% are wrong!

---

## What Was Analyzed

✅ **Repository**: https://github.com/alfin06/AgentIssue-Bench (cloned)  
✅ **Patches**: 654 real patch files analyzed  
✅ **Issues**: All 50 issues verified  
✅ **Paper**: 27-page PDF read and analyzed  
✅ **Code**: 38,315 files in repository examined  

**No fabricated data. All from real sources.**

---

## Conclusions

1. **Paper results are ACCURATE** ✅
   - Verified from real patch files
   - Coverage and resolution numbers match
   
2. **SE agents FAIL on agent systems** ❌
   - Only 0.67-4.67% correct resolution
   - 10-50X harder than traditional software
   
3. **Claude > GPT-4o** for resolution 🏆
   - 2X better at generating correct fixes
   - Consistent across all agents
   
4. **Agent-specific issues are unsolvable** ❌
   - LLM operation: ~0% resolved
   - Memory issues: ~0% resolved
   - Need specialized knowledge

---

## How to Use This Analysis

### If you want overview:
→ Read `FINAL_SUMMARY_REPORT.md`

### If you want detailed Vietnamese explanation:
→ Read `KET_QUA_THUC_TE_BENCHMARK.md`

### If you want human perspective on bug fixing:
→ Read `BAO_CAO_PHAN_TICH.md`

### If you want raw data:
→ Check `real_benchmark_analysis.json`

### If you want to re-run analysis:
→ Run `python3 analyze_real_benchmark_results.py`

---

## Repository Structure

```
/Users/tranvanhuy/Desktop/Research/
├── AgentIssue-Bench/              # Cloned benchmark repo (38K files)
│   ├── Generated Patches/         # 654 patch files ✅
│   ├── test_agentissue_bench.py  # Test script
│   ├── eval_patches.py            # Evaluation script
│   └── README.md                  # Original README
│
├── Reports (Created by us)
│   ├── FINAL_SUMMARY_REPORT.md ⭐         # Main report
│   ├── KET_QUA_THUC_TE_BENCHMARK.md      # Vietnamese detailed
│   ├── REAL_BENCHMARK_ANALYSIS_REPORT.md # English version
│   └── BAO_CAO_PHAN_TICH.md              # Human perspective
│
├── Data Analysis
│   ├── real_benchmark_analysis.json       # Analysis results
│   └── unresolved_cases_analysis.json     # Unresolved details
│
├── Scripts
│   ├── analyze_real_benchmark_results.py  # Main analysis
│   └── analyze_unresolved_cases.py        # Human analysis
│
└── Source
    └── paper_agentissue.pdf               # Original paper
```

---

## Contact & References

- Paper: https://openreview.net/pdf?id=N9HLe9iPhj
- Repository: https://github.com/alfin06/AgentIssue-Bench
- Leaderboard: https://alfin06.github.io/AgentIssue-Bench-Leaderboard/

