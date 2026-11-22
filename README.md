# Causal Loops Lab

**Exact toy models of information sent around a closed timelike curve (CTC), and what self-consistency would do to the future.**

[![tests](https://img.shields.io/badge/tests-93%20passing-2a78d6)](ctc/README.md)
[![IBM hardware](https://img.shields.io/badge/IBM%20hardware-21%2F21%20preregistered%20checks-2a78d6)](ctc/hardware/README.md)
[![python](https://img.shields.io/badge/python-3.11-2a78d6)](ctc/README.md)
[![code license](https://img.shields.io/badge/code-MIT-6b6a63)](LICENSE)
[![data license](https://img.shields.io/badge/docs%20%26%20data-CC%20BY%204.0-6b6a63)](LICENSES.md)
[![status](https://img.shields.io/badge/status-research%20prototype-6b6a63)](ROADMAP.md)
[![AI assisted](https://img.shields.io/badge/AI-assisted-6b6a63)](#honesty-statement)

[繁體中文說明](#繁體中文) · [Roadmap](ROADMAP.md) · [Hypotheses](HYPOTHESIS.md) · [Theorems](ctc/THEOREMS.md) · [Hardware runs](ctc/hardware/README.md) · [Code and results](ctc/README.md)

## The question

If a message could be sent back in time, and the universe only allowed self-consistent histories, would the grandfather paradox disappear? And would the loop then show up as *changed statistics in the future*?

This project turns that idea into three testable hypotheses and checks them against the two standard quantum models of time travel, Deutsch's **D-CTC** (1991) and Lloyd et al.'s postselected **P-CTC** (2011), plus Allen's transition-probability **T-CTC** (2014) and a classical two-parameter family that has D-CTC and P-CTC as corners.

| | Hypothesis | Plain words |
|---|---|---|
| H1 | Information sent to the past is always self-consistent | Paradoxical histories simply do not happen |
| H2 | The loop's observable effect appears in the future | Statistics after the loop differ from a world without it |
| H3 | Causality is global consistency | Without a loop, H1 reduces to ordinary cause-before-effect |

## Main findings so far

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="ctc/output/hardware_results_dark.png">
  <img alt="Predicted vs measured values on IBM quantum hardware for P-CTC and past-preserving selection" src="ctc/output/hardware_results.png">
</picture>

1. **H2 needs an extra assumption: the universe must prefer consistent branches.** With no consistency selection (β = 0), the world's probabilities never change, wherever the message comes from. ([details](ctc/BRANCHES.md))
2. **Reweighting the world is the same thing as faster-than-light signalling.** In every rule tested, whenever the loop reweights Alice's world, Alice can signal to a distant Bob who shares correlations with her. Only the non-reweighting rules are safe ([no-signalling map](ctc/output/signalling_map.png): zero only along s = 0). ([details](ctc/NO_SIGNALLING.md))
3. **Different selection rules give opposite answers.** Lloyd's gun never fires under P-CTC, but fires with probability sin²(θ/2) under D-CTC. ([details](ctc/LITERATURE_REPRODUCTION.md))
4. **In quantum mechanics "consistent" has two incompatible meanings.** Two logically consistent histories can cancel by interference, deleting a whole branch. ([details](ctc/QUANTUM_EFFECTS.md))
5. **An unconditional message looks exactly like an ordinary one.** From the receiver's side alone you cannot tell whether a message came from the future. ([details](ctc/README.md))
6. **A candidate fix for H2: past-preserving selection.** Recorded past facts keep their probabilities; consistency selection acts only inside each recorded past world. It is an ordinary quantum channel, so it can never signal. In a double-slit experiment with a time loop, its effect appears only in fringes sorted by an entangled idler, exactly like a delayed-choice quantum eraser. Letting decoherence fix the "record" basis makes the past continuously more fixed as the environment records it ([details](ctc/PAST_PRESERVING.md), [decoherence](ctc/DECOHERENCE.md)).
7. **Under past-preserving selection, all three hypotheses hold as theorems, in a modified form (H1′–H3′).** Every recorded world is self-consistent (a definite consistent history when one exists, Deutsch's mixed fixed point otherwise); the loop never changes recorded past probabilities, and inside each past world it conditions the future on consistency; when the loop does not act back, ordinary quantum mechanics is recovered exactly. The original H3 fails under P-CTC: a bit that merely controls the loop still has a branch deleted. Each theorem is checked on random circuits. ([theorems](ctc/THEOREMS.md))
8. **The predictions are measurable on real quantum hardware.** Postselected-teleportation circuits on IBM's `ibm_kingston` (figure above) reproduce every predicted effect: P-CTC changes the recorded past and a distant partner's statistics, past-preserving selection does not, inconsistent histories are suppressed to 3.5%, and the loop's effect in a delayed-choice eraser appears only in Bob-sorted fringes (visibility 0.870, shift 0.774 rad vs 0.785 predicted). Predictions and pass criteria were preregistered; 21 of 21 pass. Both rules are computed from the same shots, so this shows the predictions are measurable, not which rule nature uses. ([hardware runs](ctc/hardware/README.md))

**Novelty status.** An initial check found that findings 2–4 are already known in the literature (Bub & Stairs 2014; Araújo, Guérin & Baumeler 2017; Lloyd et al. 2011). The code reproduces them independently. The κ–β family interpolating D-CTC and P-CTC has no exact precedent found so far; the closest prior work is Allen's T-CTC (2014), a weighted mixture of P-CTC and an ordinary channel, reproduced [here](ctc/T_CTC.md). Novelty is unconfirmed. See [ctc/NOVELTY_CHECK.md](ctc/NOVELTY_CHECK.md).

![kappa-beta branch model](ctc/output/branches_map.png)

## Quick start

Requires Python 3.11+ and NumPy; figures need matplotlib.

```bash
python -B ctc/tests/test_models.py
python -B ctc/tests/test_literature.py
python -B ctc/tests/test_branches.py
python -B ctc/tests/test_quantum_effects.py
python -B ctc/tests/test_signalling.py
python -B ctc/tests/test_t_ctc.py
python -B ctc/tests/test_past_preserving.py
python -B ctc/tests/test_decoherence.py
python -B ctc/tests/test_theorems.py
python -B ctc/tests/test_hardware.py      # gate-level checks need qiskit, skipped without it
python -B ctc/run_signalling.py           # regenerates the no-signalling map
```

Every model is a small exact calculation (1–6 qubits); results are checked against closed-form formulas and against the published numbers in Lloyd et al. 2011 and Brun, Harrington & Wilde 2009.

The hardware experiments need `qiskit` (and `qiskit-ibm-runtime` plus your own IBM Quantum account for real devices):

```bash
python -B ctc/hardware/run_local.py       # ideal simulator, full analysis
python -B ctc/hardware/preregister.py     # fix predictions and criteria before a run
python -B ctc/hardware/run_ibm.py --dry-run
python -B ctc/hardware/plot_results.py    # regenerates the figure above
```

## Honesty statement

- This project does **not** claim that information can be sent to the past, and no simulation could show that: postselected simulations can always be explained in the normal time direction.
- The IBM hardware runs implement the loop rules by postselection. They show that each rule's predictions can be measured on a real device; they do not show that loops exist or which rule nature would use.
- It does not support any personal time-travel claim.
- Code and writing used AI assistance (Claude). There has been **no external peer review**. Corrections and expert feedback are very welcome: please open an issue.

## Contributing

Useful contributions right now:

- Pointers to prior work on rule families interpolating D-CTC and P-CTC (this decides whether the κ–β model is new).
- A quantum version of the κ–β model with a decoherence parameter.
- Reformulating H1–H3 in the process-matrix framework.

Open an issue or a pull request. If you use this work, GitHub's "Cite this repository" button gives the citation from [CITATION.cff](CITATION.cff).

## Earlier work in this repository

The repository started as an evidence package for two research proposals on a finite SYK information-transfer model and on uncertainty and cost checks for small quantum experiments. Those files are frozen and hash-checked:

- [Plan A evidence and reproduction](plan-a/README.md)
- [Plan B evidence and reproduction](plan-b/README.md)
- [Per-file provenance and transformations](PROVENANCE.json)
- [License scope and exclusions](LICENSES.md)
- [Recorded local checks](LOCAL_CHECKS.json)

All of those earlier results are simulations, planning arithmetic or synthetic tests; they involve no hardware execution (the IBM runs above belong to the CTC research, not to Plans A and B). The task is classical one-bit classification; no backward communication, physical wormhole, arbitrary-state teleportation or quantum advantage is established. The integrity check is `python -I -S -B VERIFY_PUBLIC.py`; it verifies hashes only. This README replaced the evidence-package README (subset v0.34, 14 October 2026) on 22 November 2026 and was updated with the theorems and hardware results on 23 November 2026; each time only its manifest hash was updated.

---

## 繁體中文

**用精確的玩具模型，研究「傳回過去的資訊」在自洽條件下會怎麼影響未來。**

### 問題

如果訊息能傳回過去，而宇宙只允許自洽的歷史，祖父悖論是不是就不會發生？迴圈的效應，會不會表現成「未來統計的改變」？

本專案把這個想法寫成三個可檢驗的假設（見上表與 [HYPOTHESIS.md](HYPOTHESIS.md)），並用兩種標準的量子時間旅行模型 D-CTC（Deutsch 1991）和 P-CTC（Lloyd 等人 2011），以及 Allen 2014 的 T-CTC 檢驗，另外建立了一個把 D-CTC 和 P-CTC 當作角落的古典雙參數模型（κ–β 模型）。

### 目前的發現

1. **H2 需要額外假設「宇宙偏好自洽的分支」。** 沒有自洽篩選（β = 0）時，世界本身的機率完全不變。
2. **重新加權世界，等於能超光速傳訊。** 在所有測過的規則裡，只要迴圈重新加權了 Alice 的世界，她就能對遠方共享相關性的 Bob 傳訊。只有不重新加權的規則是安全的。
3. **篩選規則不同，答案可以完全相反。**
4. **量子版本裡，「自洽」有兩種不相容的定義**：兩條各自邏輯自洽的歷史，可以因為干涉而互相抵消。
5. **無條件寄出的訊息，跟一般訊息完全一樣**：只看收件者這邊，分辨不出訊息是否來自未來。
6. **H2 的候選出路「過去守恆篩選」**：已記錄的過去機率不變，只在每個過去世界內做自洽篩選。它一定不能傳訊；在有時間迴圈的雙縫實驗裡，效應只出現在按閒置光子結果分組後的條紋裡，跟量子擦除同構。未解決：「已記錄」的基底由誰決定。
7. **在過去守恆篩選下，三個假設都能以修改後的形式（H1′–H3′）證明成定理。** 每個已記錄的世界都自洽（有自洽歷史時是確定的自洽歷史，沒有時是 Deutsch 混合不動點）；迴圈不改變已記錄的過去機率，只在每個過去世界之內，以自洽為條件改變未來；迴圈不回頭作用時，完全回到一般量子力學。原本的 H3 在 P-CTC 下不成立：只控制迴圈、不受迴圈影響的位元，分支仍會被刪掉。每條定理都用隨機電路驗證過。([定理](ctc/THEOREMS.md))
8. **這些預測在真實量子硬體上量得出來。** 在 IBM 的 `ibm_kingston` 上用後選擇 teleportation 電路（上圖），每個預測效應都量到了：P-CTC 改變已記錄的過去和遠方夥伴的統計，過去守恆不會；不自洽的歷史被壓到 3.5%；量子擦除裡迴圈的效應只出現在依 Bob 分組的條紋裡（清晰度 0.870，相位移 0.774 弧度，理論 0.785）。預測和判準事先登錄，21 項全部通過。三種規則來自同一批 shots，所以這說明預測量得出來，不說明自然界用哪一種規則。([硬體實驗](ctc/hardware/README.md))

**新穎性：** 初步檢查發現第 2–4 點文獻中已有（Bub & Stairs 2014、Araújo 等人 2017、Lloyd 等人 2011），本專案是獨立重現。κ–β 內插模型目前沒找到完全相同的前例；最接近的是 Allen 2014 的 T-CTC（P-CTC 和普通通道的加權混合），新穎性還沒有確認。

### 誠實聲明

本專案**不主張**資訊能傳回過去，也不支持任何個人的時間旅行說法。IBM 硬體實驗是用後選擇實作迴圈規則，只能說明各規則的預測量得出來，不能證明迴圈存在，也不能判斷自然界用哪一種規則。程式與文件使用 AI 輔助（Claude）撰寫，**沒有外部審查**。歡迎指正，請開 issue。

### 怎麼參與

最需要的是：D-CTC 和 P-CTC 之間內插規則家族的既有文獻、加上去相干參數的量子版 κ–β 模型，以及用 process matrix 框架重新表述 H1–H3。詳細計畫見 [ROADMAP.md](ROADMAP.md)。
