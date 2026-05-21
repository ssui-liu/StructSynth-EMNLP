# Level 6: Citations & References Audit Report

**Paper:** StructSynth (EMNLP submission)
**Date:** 2026-05-22

---

## Summary

| Category | Issues Found |
|---|---|
| 6.1 Citation format | 3 |
| 6.2 Citation placement | 1 |
| 6.3 Reference completeness | 8 |
| **Total** | **12** |

---

## 6.1 Citation Format

### 6.1.1 Bare `\cite{}` usage

**Finding:** Every single citation in the paper uses bare `\cite{}`. Zero `\citet` or `\citep` commands anywhere.

**Mitigating factor:** The ACL style file (`acl.sty`) contains `\renewcommand\cite{\citep}`, so bare `\cite{}` is automatically mapped to parenthetical `\citep`. All citations will compile correctly as "(Author, Year)".

No cases of incorrect textual-vs-parenthetical misuse were found. All citations either follow a method/system name (e.g., `GReaT~\cite{...}`) or are parenthetical at the end of a clause. The current usage is **acceptable** given the ACL style redefinition, but for best practice and portability, consider using explicit `\citet`/`\citep`.

### 6.1.2 Double parentheses

No double-parentheses issues found.

---

## 6.2 Citation Placement

### 6.2.1 Citations before periods

All citations are correctly placed before periods. No violations found.

### 6.2.2 Multiple citation ordering

**Issue I-1:** `appendix.tex:29` -- `\cite{naik2024applying, antonucci2023zero, arsenyan2024large}` is not in chronological order (2024, 2023, 2024). Should be `\cite{antonucci2023zero, naik2024applying, arsenyan2024large}`.

All other multi-key citations are in correct chronological order.

### 6.2.3 Citation-only sentences

No citation-only sentences found. All citations have accompanying context.

---

## 6.3 Reference Completeness

### 6.3.1 Every cited key exists in .bib

All 58 unique citation keys used in .tex files have corresponding entries in `references.bib`. **No missing bib entries.**

### 6.3.2 Orphan bib entries (MAJOR)

**Issue I-2:** The `references.bib` contains **211 entries** but only **58 are cited**, leaving **153 orphan entries** (73%). Notable orphans include quantum physics entries (einstein1905does, bohm1952suggested), ICA/disentanglement literature, sparse optimization papers, and unused software entries. The bib was clearly copied from another project. **Recommendation:** Strip to only cited entries.

### 6.3.3 Bib entry completeness

**Issue I-3:** `kiciman2023causal` -- TMLR journal article missing volume/pages fields.

**Issue I-4:** `manning2024automated` -- `@techreport` (NBER). Check if formally published.

**Issue I-5 (info):** Dataset entries (`kaggleSocialAnxiety`, `kaggleGlobalMarket`, `propublicaMachineBias`, `adult_2`) correctly use `@misc` with `howpublished` fields.

### 6.3.4 Venue name consistency

**Issue I-6:** Inconsistent venue formatting:
- NeurIPS: `xu2019modeling` uses lowercase "Advances in neural information processing systems" while `van2021decaf` uses title case "Advances in Neural Information Processing Systems"
- ICLR: `liu2023goggle` uses "Eleventh" (capitalized) while `tabsyn` uses "twelfth" (lowercase)

### 6.3.5 ArXiv preprints that may have published versions

**Issue I-7:** Four cited arXiv preprints to check:

1. **`qian2023synthcity`** (arXiv:2301.07573) -- Published at **NeurIPS 2023**. Entry is still `@misc`. **Update required.**
2. **`ban2023causal`** (arXiv:2311.11689, Nov 2023) -- Over 2 years old. Check for published version.
3. **`antonucci2023zero`** (arXiv:2312.14670, Dec 2023) -- Over 2 years old. Check for published version.
4. **`jiralerspong2024efficient`** (arXiv:2402.01207, Feb 2024) -- Over 1 year old. Check for published version.
5. **`zanna2025fairness`** (arXiv:2503.17569, Mar 2025) -- Very recent, acceptable as arXiv.

### 6.3.6 Author name consistency

**Issue I-8:** "van der Schaar" capitalization varies: lowercase "van" in `van2023membership` and `cllm2024`, but uppercase "Van" in `van2021decaf`.

### 6.3.7 Duplicate bib entries

**Issue I-9 (info):** `scutari2010learning` (cited) and `bnlearn` (orphan) are duplicate entries for the same Scutari 2010 paper.

### 6.3.8 FCI citation

**Issue I-10:** In `appendix.tex:481`, FCI is cited as `\cite{spirtes2000causation}` (the Spirtes et al. book). However, earlier in `appendix.tex:26`, FCI is correctly cited with its original paper `spirtes1995causal`. For consistency when distinguishing PC from FCI, line 481 should use `spirtes1995causal` for FCI.

---

## Detailed Issue Table

| # | Severity | Location | Description |
|---|---|---|---|
| I-1 | Low | appendix.tex:29 | Multi-citation not in chronological order |
| I-2 | **Medium** | references.bib | 153 orphan bib entries (only 58 of 211 cited) |
| I-3 | Low | references.bib | kiciman2023causal missing volume/pages for TMLR |
| I-4 | Low | references.bib | manning2024automated is @techreport -- check for formal pub |
| I-5 | Info | references.bib | Dataset @misc entries are fine |
| I-6 | Low | references.bib | Inconsistent venue capitalization (NeurIPS, ICLR) |
| I-7 | **Medium** | references.bib | 4 arXiv preprints may have published versions (esp. qian2023synthcity = NeurIPS 2023) |
| I-8 | Low | references.bib | "van der Schaar" vs "Van der Schaar" |
| I-9 | Info | references.bib | Duplicate bnlearn entry (one orphan) |
| I-10 | Low | appendix.tex:481 | FCI should cite spirtes1995causal not spirtes2000causation |

## Priority Recommendations

1. **Clean references.bib** -- Remove 153 orphan entries
2. **Update qian2023synthcity** to NeurIPS 2023 publication; check other arXiv preprints
3. **Standardize venue names** (NeurIPS capitalization, ICLR ordinal capitalization)
4. **Fix citation ordering** in appendix.tex:29
5. **Fix FCI citation** in appendix.tex:481
6. **Fix author name consistency** for "van der Schaar"
7. **(Optional)** Use explicit `\citet`/`\citep` instead of bare `\cite`
