# AGENTISSUE-BENCH - Đánh Giá Patches

> **Đánh giá patches từ paper, không gen lại**  
> Sử dụng patches có sẵn trong `Generated Patches/`

---

## 📋 Tổng Quan

Repository này đánh giá patches đã được tạo sẵn từ paper, theo đúng quy trình trong GitHub:

1. ✅ Patches có sẵn trong `Generated Patches/` (685 patches)
2. ✅ Đã copy vào `Patches/` theo format đúng
3. ✅ Chạy `eval_patches.py` để đánh giá
4. ✅ Kết quả trong `patch_eval.log`

---

## 🚀 Cách Chạy

### Chạy Đánh Giá (Flexible - Không bắt buộc pull images)

```bash
cd /Users/tranvanhuy/Desktop/Research
python evaluate_patches.py
```

Script sẽ tự động:
- ✅ Dùng images đã có local
- ✅ Skip images không pull được (rate limit, ARM64)
- ✅ Chỉ evaluate với images có sẵn
- ✅ Không crash khi gặp lỗi

Hoặc chạy trực tiếp flexible script:

```bash
cd AgentIssue-Bench
python eval_patches_flexible.py
```

### Bước 3: Xem Kết Quả

```bash
cat AgentIssue-Bench/patch_eval.log
```

---

## 📊 Kết Quả

- **Patches đánh giá**: 961 patches (từ 685 patches gốc, có duplicates từ nhiều agents)
- **Tag directories**: 52 tags
- **Kết quả**: Xem trong `patch_eval.log`

---

## ⚠️ Lưu Ý

### Máy ARM64 (Mac M1/M2/M3)

Docker images chỉ hỗ trợ `linux/amd64`, không hỗ trợ ARM64.

**Khi chạy sẽ gặp lỗi:**
```
Error: no matching manifest for linux/arm64/v8
```

**Giải pháp:**
- Chạy trên máy Intel/AMD
- Hoặc dùng cloud VM (AWS/GCP/Azure)
- Hoặc dùng Docker với platform emulation (chậm)

---

## 📁 Cấu Trúc

```
Research/
├── evaluate_patches.py          # Script chạy đánh giá
├── benchmark_visualization.ipynb # Visualization
├── README.md                    # File này
│
└── AgentIssue-Bench/
    ├── Patches/                 # Patches để đánh giá (đã copy)
    ├── Generated Patches/       # Patches gốc từ paper
    ├── eval_patches.py         # Script đánh giá (từ GitHub)
    └── patch_eval.log          # Kết quả đánh giá
```

---

## 📖 Tài Liệu

- **GitHub**: https://github.com/alfin06/AgentIssue-Bench
- **Paper**: Xem file `paper_agentissue.pdf`
- **Hướng dẫn đánh giá**: Xem `AgentIssue-Bench/README.md`

---

## 🔑 API Keys

Cần set environment variables (cho Docker containers):

```bash
export OPENAI_API_KEY="sk-or-v1-..."
export OPENAI_API_BASE="https://openrouter.ai/api/v1"
```

---

**Lưu ý**: Script này chỉ đánh giá patches có sẵn, không gen patches mới.
# agent
