# BÁO CÁO PHÂN TÍCH UNRESOLVED CASES TRONG AGENTISSUE-BENCH

## Tổng quan

Bài báo "Can Agents Fix Agent Issues?" (OpenReview ID: N9HLe9iPhj) giới thiệu **AGENTISSUE-BENCH**, một benchmark gồm 50 agent issue resolution tasks được tạo từ 201 real-world GitHub issues. Kết quả cho thấy các SE agents hiện đại chỉ đạt **0.67% - 4.67% resolution rate**, rất thấp so với performance trên traditional software issues.

## Mục tiêu phân tích

Phân tích các unresolved cases từ góc nhìn con người qua 4 bước chính trong quá trình sửa lỗi:
1. **Reproduce bug**: Tái tạo lỗi
2. **Localize bug**: Định vị lỗi
3. **Generate fix**: Tạo bản sửa lỗi
4. **Validate fix**: Xác nhận bản sửa lỗi

Mục tiêu: Đánh giá xem các bugs có thể fix được với thông tin được cung cấp không, trước khi yêu cầu agents xử lý.

## Thông tin về AGENTISSUE-BENCH

### Cấu trúc benchmark

Mỗi issue resolution task trong AGENTISSUE-BENCH bao gồm:
- **Issue description**: Mô tả vấn đề từ người dùng
- **Buggy version**: Commit có bug của agent system
- **Developer-committed patch**: Code changes giữa buggy và fixed version (ground truth)
- **Failure-triggering tests**: Test scripts reproduce issue trên buggy version và pass trên patched version
- **Docker environment**: Container với tất cả dependencies và configurations cần thiết

### Taxonomy của Agent Issues

Bài báo phân loại 201 issues thành **6 categories** và **20 sub-categories**:

1. **Incompatibility with LLM providers (7.46%)**
   - Incompatible dependencies (1.49%)
   - Unsupported models (2.99%)
   - Incompatible parameters to LLM providers (2.99%)

2. **Tool-related issues (19.90%)**
   - Tool dependency issues (3.48%)
   - Tool configuration issues (3.47%)
   - Tool implementation errors (8.46%)
   - Misuse tool interfaces (4.48%)

3. **Memory-related issues (14.43%)**
   - Memory initialization issues (2.49%)
   - Memory content errors (10.95%)
   - Memory dependency issues (1.00%)

4. **LLM operation issues (31.34%)** - Category lớn nhất
   - Model access misconfiguration (6.97%)
   - Token usage misconfiguration (3.48%)
   - Incorrect model output handlers (8.46%)
   - Model dependency issues (2.99%)
   - Context length issues (4.98%)
   - Prompt-related issues (4.48%)
   - Workflow issues (6.47%)

5. **Utility issues (20.40%)**
   - Utility implementation issues (8.96%)
   - Utility dependency issues (4.48%)
   - Utility configuration issues (6.97%)

## Kết quả từ bài báo

### Overall Resolution Rate

| SE Agent | LLM | Plausibly Resolved % | Correctly Resolved % | Localization % (File-level) |
|----------|-----|---------------------|---------------------|----------------------------|
| Agentless | GPT-4o | 12.00 | 3.33 | 27.82 |
| Agentless | Claude-3.5-S | 12.00 | 4.00 | 27.35 |
| AutoCodeRover | GPT-4o | 7.33 | 1.33 | 22.07 |
| AutoCodeRover | Claude-3.5-S | 12.67 | **4.67** | 25.81 |
| SWE-agent | GPT-4o | 0.67 | 0.67 | 11.67 |
| SWE-agent | Claude-3.5-S | 2.00 | 2.00 | 9.52 |

**Key findings:**
- Resolution rates rất thấp (0.67% - 4.67%)
- Localization accuracy cũng thấp (< 28% file-level, < 20% function-level)
- Claude-3.5-Sonnet thường perform tốt hơn GPT-4o

### Resolved vs Unresolved Issues

**Resolved categories:**
- Tool-related issues: 2/12 (16.67%) - chủ yếu Tool dependency issues
- LLM operation issues: 1/11 (9.09%) - chủ yếu Prompt-related issues
- Utility issues: 2/12 (16.67%) - chủ yếu Utility configuration issues

**Unresolved categories:**
- **LLM provider incompatibility**: 0% resolved
- **Memory-related issues**: 0% resolved
- **Hầu hết LLM operation issues**: Không được resolve

## Phân tích từ góc nhìn con người

### 1. REPRODUCE BUG

**Thông tin có sẵn:**
- ✅ Executable Docker environment
- ✅ Failure-triggering tests
- ✅ Issue description từ người dùng

**Challenges:**
- **LLM non-determinism**: LLM outputs có thể khác nhau giữa các lần chạy, làm khó reproduce consistently
- **External resources volatility**: Tools và APIs mà agents tương tác có thể thay đổi (API endpoints, rate limits, etc.)
- **Complex interactions**: Agent systems có nhiều components tương tác, bug có thể chỉ manifest trong specific conditions

**Đánh giá:** 
- ✅ **Feasible**: Với Docker environment và failure-triggering tests, con người có thể reproduce bugs
- ⚠️ **Challenging**: Non-determinism và external dependencies có thể làm khó reproduce một cách consistent

### 2. LOCALIZE BUG

**Thông tin có sẵn:**
- ✅ Issue description
- ✅ Buggy codebase
- ⚠️ Error messages/stack traces (có thể có hoặc không)
- ⚠️ Execution logs (có thể có hoặc không)

**Challenges theo category:**

**LLM operation issues (31.34% - category lớn nhất):**
- **Difficulty: HIGH**
- LLM operations là dynamic và non-deterministic
- Cần hiểu sâu về LLM provider APIs và parameters
- Bug có thể nằm ở interaction giữa LLM calls và response handling
- Model output handlers có thể miss edge cases (empty responses, exceptions)

**Memory-related issues (14.43%):**
- **Difficulty: HIGH**
- Memory issues liên quan đến state management
- Cần trace execution flow qua nhiều components
- Memory content errors (10.95%) có thể do faulty storage logic
- Khó debug vì state có thể bị corrupt ở nhiều điểm

**Tool-related issues (19.90%):**
- **Difficulty: MEDIUM**
- Tool issues thường có explicit error messages
- Dependency issues có thể dễ identify hơn
- Tool configuration issues có thể có clear symptoms

**LLM provider incompatibility (7.46%):**
- **Difficulty: MEDIUM-HIGH**
- Cần knowledge về provider APIs
- Có thể có explicit error messages về incompatible parameters
- Nhưng cần cập nhật knowledge về API changes

**Đánh giá:**
- ✅ **Feasible**: Con người có thể localize với đủ thông tin
- ⚠️ **Very challenging** cho LLM và Memory issues do tính chất dynamic và complex interactions

### 3. GENERATE FIX

**Thông tin có sẵn:**
- ✅ Buggy codebase
- ✅ Developer-committed patch (ground truth) - nhưng agents không có access
- ✅ Issue description

**Challenges theo category:**

**LLM operation issues:**
- **Complexity: HIGH**
- Cần knowledge về LLM provider APIs và parameters
- Cần cập nhật knowledge về API changes (providers thường update APIs)
- Fix có thể cần thay đổi prompt handling, output parsing, error handling
- Cần hiểu về context length management, token usage

**Memory-related issues:**
- **Complexity: HIGH**
- Cần hiểu sâu về agent architecture và memory management
- Fix có thể cần thay đổi storage logic, initialization, state management
- Cần đảm bảo không break memory consistency

**Tool-related issues:**
- **Complexity: MEDIUM**
- Dependency issues: Thường straightforward (add missing dependencies)
- Configuration issues: Cần hiểu tool interfaces
- Implementation errors: Cần domain knowledge về tool

**LLM provider incompatibility:**
- **Complexity: MEDIUM-HIGH**
- Cần knowledge về provider APIs
- Có thể cần update dependencies, fix parameter usage
- Cần support cho new models

**Đánh giá:**
- ✅ **Feasible**: Con người có thể generate fixes với đủ domain knowledge
- ⚠️ **Very challenging** cho agent-specific issues (LLM, Memory) vì:
  - Cần knowledge về external resources (LLM providers, APIs)
  - Cần hiểu sâu về agent architecture
  - Knowledge base cần được cập nhật thường xuyên

### 4. VALIDATE FIX

**Thông tin có sẵn:**
- ✅ Failure-triggering tests
- ⚠️ Regression tests (có thể không đầy đủ)
- ⚠️ Manual testing (cần thực hiện)

**Challenges:**
- **Test coverage**: Tests có thể không cover hết edge cases
- **Non-determinism**: Agent systems có non-determinism nên cần multiple runs để validate
- **Different configurations**: Cần test với different LLM providers/models
- **External resources**: Cần test với different external resources (tools, APIs)
- **Overfitting to tests**: Plausible patches có thể pass tests nhưng không correct (bài báo đề cập đến vấn đề này)

**Đánh giá:**
- ✅ **Feasible**: Có failure-triggering tests để validate
- ⚠️ **Challenging**: Cần comprehensive testing để đảm bảo fix không break functionality khác và handle edge cases

## Tại sao agents không resolve được?

### 1. Thiếu knowledge về external resources
- LLM provider APIs thay đổi thường xuyên
- Agents không có evolving knowledge base về API documentation, release notes
- Cần knowledge về tool interfaces, dependencies

### 2. Thiếu understanding về agent architecture
- Agent systems có complex interactions giữa components
- Memory management, workflow orchestration là unique features
- Agents không được train specifically cho agent systems

### 3. Localization accuracy thấp
- File-level localization < 28%, function-level < 20%
- Gap lớn giữa issue description và root cause
- Cần dynamic analysis (execution trajectories, tool outputs) thay vì chỉ static analysis

### 4. Limited training data
- Agent systems là emerging paradigm
- Training data của LLMs ít cover agent-specific issues
- Cần fine-tuning với instances từ AGENTISSUE-BENCH

## Kết luận và Recommendations

### Kết luận

1. **Bugs có thể fix được với thông tin được cung cấp**: 
   - ✅ Reproduce: Feasible với Docker environment và tests
   - ✅ Localize: Feasible nhưng challenging cho LLM/Memory issues
   - ✅ Generate fix: Feasible nhưng cần domain knowledge
   - ✅ Validate: Feasible với tests

2. **Tại sao agents fail:**
   - Thiếu knowledge về external resources (LLM providers, APIs)
   - Thiếu understanding về agent architecture
   - Localization accuracy thấp
   - Limited training data cho agent-specific issues

3. **Unresolved cases khác với traditional bugs:**
   - Agent-specific features (LLM operations, memory, tools)
   - Non-determinism và external dependencies
   - Complex interactions giữa components
   - Cần evolving knowledge base

### Recommendations từ bài báo

1. **Adding knowledge base on agent-needed external resources**
   - Augment agents với evolving knowledge base từ API documentation, release notes, historical issues
   - Integrate knowledge để better reason về issues related to external resources

2. **Training SE agents with AGENTISSUE-BENCH instances**
   - Collect instances và trajectories từ benchmark
   - Fine-tune SE agents specifically cho agent issue resolution

3. **Adding dynamic analysis component**
   - Move beyond static analysis
   - Incorporate runtime information (execution trajectories, tool outputs)
   - Gather richer signals cho accurate bug localization và patch generation

## References

- Paper: "Can Agents Fix Agent Issues?" - OpenReview ID: N9HLe9iPhj
- Repository: https://github.com/alfin06/AgentIssue-Bench
- Leaderboard: https://alfin06.github.io/AgentIssue-Bench-Leaderboard/

