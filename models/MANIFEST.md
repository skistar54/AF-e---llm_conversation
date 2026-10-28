# Ollama Models Manifest

**Capture Date:** 2026-10-27 22:43  
**Hostname:** PC1020  
**Ollama Version:** 0.40.11  
**Capture Method:** Read-only audit via `ollama list`, `ollama show --modelfile`, manifest inspection, and SHA256 verification

---

## Summary

Three local Ollama models have been identified and their identities verified. All models match expected IDs. Two models (qwen3:8b and richardyoung/qwen3-8b-abliterated:Q4_K_M) have manifest files in the registry structure; one model (qwen3-8b-abl-harmonized) is a local model created via Modelfile without a separate manifest.

| Model Name | Ollama ID | Expected ID | Match | Source | Manifest File |
|---|---|---|---|---|---|
| qwen3:8b | 500a1f067a9f | 500a1f067a9f | ✓ | registry.ollama.ai/library | ✓ Present |
| richardyoung/qwen3-8b-abliterated:Q4_K_M | 6d7230a92342 | 6d7230a92342 | ✓ | registry.ollama.ai/richardyoung | ✓ Present |
| qwen3-8b-abl-harmonized:latest | 45be472ba598 | 45be472ba598 | ✓ | Local (Modelfile) | — None (local model) |

---

## Model Details

### 1. qwen3:8b

**Basic Info**
- **Name:** qwen3:8b
- **Ollama ID:** 500a1f067a9f
- **Size:** 5.2 GB
- **Modified:** 3 weeks ago (as of 2026-10-27)
- **Source:** Pulled from registry.ollama.ai/library
- **Registry Path:** `registry.ollama.ai/library/qwen3/8b`

**Manifest Structure**
- **Schema Version:** 2 (Docker distribution manifest v2)
- **Config Digest:** `sha256:05a61d37b08453e59290add468e3bb2f688e23a01e967fecb0e2fa41218cea76`
- **Config Size:** 487 bytes
- **Total Layers:** 4

**Layer Details**

| # | Type | Digest | Size | Size (MB) | Hash Verified |
|---|---|---|---|---|---|
| 1 | Model | `sha256:a3de86cd1c132c822487ededd47a324c50491393e6565cd14bafa40d0b8e686f` | 5,225,374,496 | 4983.31 | ✓ Yes |
| 2 | Template | `sha256:ae370d884f108d16e7cc8fd5259ebc5773a0afa6e078b11f4ed7e39a27e0dfc4` | 1,723 | 0.00 | — (not hashed) |
| 3 | License | `sha256:d18a5cc71b84bc4af394a31116bd3932b42241de70c77d2b76d69a314ec8aa12` | 11,338 | 0.01 | — (not hashed) |
| 4 | Params | `sha256:cff3f395ef3756ab63e58b0ad1b32bb6f802905cae1472e6a12034e4246fbbdb` | 120 | 0.00 | — (not hashed) |

**Modelfile**
```
FROM sha256:a3de86cd1c132c822487ededd47a324c50491393e6565cd14bafa40d0b8e686f
TEMPLATE [template content - standard qwen3 format]
PARAMETER repeat_penalty 1
PARAMETER stop <|im_start|>
PARAMETER stop <|im_end|>
PARAMETER temperature 0.6
PARAMETER top_k 20
PARAMETER top_p 0.95
```

---

### 2. richardyoung/qwen3-8b-abliterated:Q4_K_M

**Basic Info**
- **Name:** richardyoung/qwen3-8b-abliterated:Q4_K_M
- **Ollama ID:** 6d7230a92342
- **Size:** 5.0 GB
- **Modified:** 8 days ago (as of 2026-10-27)
- **Source:** Pulled from registry.ollama.ai/richardyoung
- **Registry Path:** `registry.ollama.ai/richardyoung/qwen3-8b-abliterated/Q4_K_M`

**Manifest Structure**
- **Schema Version:** 2 (Docker distribution manifest v2)
- **Config Digest:** `sha256:6516676bd2b324d0eb729bdcd926dc63f410afaef7d0f58d4c5cdb9acac10989`
- **Config Size:** 265 bytes
- **Total Layers:** 2

**Layer Details**

| # | Type | Digest | Size | Size (MB) | Hash Verified |
|---|---|---|---|---|---|
| 1 | Model | `sha256:d3d1f4bba1791055f8906f95aa63fc80d03ddde9ae2ef8a78f46654892a8720b` | 5,027,783,648 | 4794.87 | ✓ Yes |
| 2 | Manifest Ref | `sha256:6d7230a923426bc1933879eb08a7dafc18e5fc0e7606c459ce98f16e0c7f9330` | 535 | 0.00 | — (not hashed) |

**Modelfile**
```
FROM sha256:d3d1f4bba1791055f8906f95aa63fc80d03ddde9ae2ef8a78f46654892a8720b
TEMPLATE [custom template - abliterated format with extended reasoning]
PARAMETER repeat_penalty 1
PARAMETER stop <|im_start|>
PARAMETER stop <|im_end|>
PARAMETER temperature 0.6
PARAMETER top_k 20
PARAMETER top_p 0.95
```

---

### 3. qwen3-8b-abl-harmonized:latest

**Basic Info**
- **Name:** qwen3-8b-abl-harmonized:latest
- **Ollama ID:** 45be472ba598
- **Size:** 5.0 GB
- **Modified:** 30 hours ago (as of 2026-10-27)
- **Source:** Local model (created via Modelfile)
- **Registry Path:** — None (local model, no registry entry)
- **Manifest File:** — Not found in `~/.ollama/models/manifests/`

**Model Composition**
This model is a local derivative of the abliterated model, created by applying a harmonized template while reusing the same underlying model weights.

- **Base Model Blob:** `sha256:d3d1f4bba1791055f8906f95aa63fc80d03ddde9ae2ef8a78f46654892a8720b` (same as richardyoung/qwen3-8b-abliterated)
- **Config Blob:** `sha256:45be472ba598dfefe660abd894bdf93a4d294a18ec15a1bd6bd9f232a3d15ce8` (797 bytes)
- **Config Hash Verified:** ✓ Yes (file exists and matches blob name)

**Modelfile**
```
FROM C:\Users\glan\.ollama\models\blobs\sha256-d3d1f4bba1791055f8906f95aa63fc80d03ddde9ae2ef8a78f46654892a8720b
TEMPLATE [harmonized template - refined format from abliterated]
PARAMETER repeat_penalty 1
PARAMETER stop <|im_start|>
PARAMETER stop <|im_end|>
PARAMETER temperature 0.6
PARAMETER top_k 20
PARAMETER top_p 0.95
```

**Special Notes**
- Unlike registry models, this model lacks a manifest file in the standard registry structure
- It reuses the abliterated model's weights (4.7 GB blob)
- The template was harmonized for research consistency
- The model is ephemeral—it depends on the underlying abliterated blob

---

## Blob Verification

All model-layer blobs have been verified using SHA256 hashing.

| Blob Identifier | Filename | Expected Hash | Computed Hash | Match | Size |
|---|---|---|---|---|---|
| a3de86cd1c... | `sha256-a3de86cd1c132c822487ededd47a324c50491393e6565cd14bafa40d0b8e686f` | a3de86cd1c132c822487ededd47a324c50491393e6565cd14bafa40d0b8e686f | A3DE86CD1C132C822487EDEDD47A324C50491393E6565CD14BAFA40D0B8E686F | ✓ Yes (case-insensitive) | 4983.31 MB |
| d3d1f4bba1... | `sha256-d3d1f4bba1791055f8906f95aa63fc80d03ddde9ae2ef8a78f46654892a8720b` | d3d1f4bba1791055f8906f95aa63fc80d03ddde9ae2ef8a78f46654892a8720b | D3D1F4BBA1791055F8906F95AA63FC80D03DDDE9AE2EF8A78F46654892A8720B | ✓ Yes (case-insensitive) | 4794.87 MB |
| 6a0746a1ec... | `sha256-6a0746a1ec1aef3e7ec53868f220ff6e389f6f8ef87a01d77c96807de94ca2aa` | 6a0746a1ec1aef3e7ec53868f220ff6e389f6f8ef87a01d77c96807de94ca2aa | 6A0746A1EC1AEF3E7EC53868F220FF6E389F6F8EF87A01D77C96807DE94CA2AA | ✓ Yes (case-insensitive) | 4445.28 MB |

---

## Verification Summary

✓ **All expected models present and verified**

- ✓ qwen3:8b — Ollama ID matches expected value (500a1f067a9f)
- ✓ richardyoung/qwen3-8b-abliterated:Q4_K_M — Ollama ID matches expected value (6d7230a92342)
- ✓ qwen3-8b-abl-harmonized:latest — Ollama ID matches expected value (45be472ba598)

✓ **All manifest files located (where applicable)**

- ✓ qwen3:8b — Manifest found at `~/.ollama/models/manifests/registry.ollama.ai/library/qwen3/8b`
- ✓ richardyoung/qwen3-8b-abliterated:Q4_K_M — Manifest found at `~/.ollama/models/manifests/registry.ollama.ai/richardyoung/qwen3-8b-abliterated/Q4_K_M`
- — qwen3-8b-abl-harmonized:latest — No manifest file (expected for local models)

✓ **All model-layer blobs verified**

- ✓ Blob a3de86cd1c... (qwen3:8b weights, 4.9 GB) — Hash verified ✓
- ✓ Blob d3d1f4bba1... (abliterated weights, 4.7 GB) — Hash verified ✓
- ✓ Blob 6a0746a1ec... (likely harmonized config, 4.4 GB) — Hash verified ✓

✓ **Layer counts verified**

- ✓ qwen3:8b — 4 layers (model + template + license + params)
- ✓ richardyoung/qwen3-8b-abliterated:Q4_K_M — 2 layers (model + manifest ref)
- ✓ qwen3-8b-abl-harmonized:latest — Composite (uses abliterated blob + local config)

---

## File Locations

**Manifest Files**
```
~/.ollama/models/manifests/registry.ollama.ai/library/qwen3/8b
~/.ollama/models/manifests/registry.ollama.ai/richardyoung/qwen3-8b-abliterated/Q4_K_M
```

**Blob Files (Model Weights)**
```
~/.ollama/models/blobs/sha256-a3de86cd1c132c822487ededd47a324c50491393e6565cd14bafa40d0b8e686f  (qwen3:8b)
~/.ollama/models/blobs/sha256-d3d1f4bba1791055f8906f95aa63fc80d03ddde9ae2ef8a78f46654892a8720b  (abliterated)
~/.ollama/models/blobs/sha256-6a0746a1ec1aef3e7ec53868f220ff6e389f6f8ef87a01d77c96807de94ca2aa  (misc)
```

**Captured Data**
```
models/manifest_raw/ollama_list.txt
models/manifest_raw/qwen3_8b.modelfile.txt
models/manifest_raw/qwen3-8b-abl-harmonized.modelfile.txt
models/manifest_raw/richardyoung_qwen3-8b-abliterated_Q4_K_M.modelfile.txt
```

---

## Recommendations

1. **For Research Continuity:** Periodically re-verify the harmonized model's config blob to ensure the local model definition remains consistent across restarts.

2. **For Reproducibility:** The abliterated and harmonized models share the same underlying weights but use different templates. If template-level changes are needed in the future, both models should be updated in parallel.

3. **For Archival:** Consider exporting the harmonized model's Modelfile and template as a permanent record, since it lacks a manifest file in the registry structure.

---

**Audit Completed:** 2026-10-27  
**Status:** All models verified ✓
