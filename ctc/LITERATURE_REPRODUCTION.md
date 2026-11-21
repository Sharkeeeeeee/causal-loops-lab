# 文獻數值重現：Lloyd 等人 2011、Brun–Harrington–Wilde 2009

建立日期：2026-11-22，撰寫時使用 AI 輔助（Claude）。沒有外部審查。

```text
python -B ctc/tests/test_literature.py   # 11 項測試
python -B ctc/reproduce_literature.py    # 產生 output/literature.json 和 output/lloyd_fig4_theory.png
```

電路接線是從兩篇論文 arXiv PDF 的圖讀出來的，程式在 [literature.py](literature.py)。標示「本專案推導」的項目不是論文的內容。

## 來源

- **[L11]** S. Lloyd, L. Maccone, R. Garcia-Patron, V. Giovannetti, Y. Shikano, S. Pirandola, L. A. Rozema, A. Darabi, Y. Soudagar, L. K. Shalm, A. M. Steinberg, "Closed timelike curves via post-selection: theory and experimental demonstration", [arXiv:1005.2219v1](https://arxiv.org/abs/1005.2219)；Phys. Rev. Lett. 106, 040403 (2011)。
- **[L11-PRD]** S. Lloyd 等人, "The quantum mechanics of time travel through post-selected teleportation", [arXiv:1007.2615v2](https://arxiv.org/abs/1007.2615)；Phys. Rev. D 84, 025007 (2011)。引用其中的 Eq. (8)–(9)。
- **[BHW]** T. A. Brun, J. Harrington, M. M. Wilde, "Localized closed timelike curves can perfectly distinguish quantum states", [arXiv:0811.1209v2](https://arxiv.org/abs/0811.1209)；Phys. Rev. Lett. 102, 210402 (2009)。

## 重現結果

| 論文中的說法 | 位置 | 本專案結果 |
|---|---|---|
| 兩態電路能完全分辨 \|0⟩ 和 \|−⟩，迴圈的自洽解唯一，分別是 \|0⟩⟨0\| 和 \|1⟩⟨1\| | [BHW] Fig. 1 | ✅ 測量結果分別是 0 和 1，不動點唯一 |
| BB84 四個態完全分辨：\|00⟩→\|00⟩、\|+0⟩→\|10⟩、\|10⟩→\|01⟩、\|−0⟩→\|11⟩ | [BHW] Fig. 2、Eq. (3) | ✅ 四個輸入都以機率 1 得到宣稱的結果 |
| BB84 的自洽解唯一，而且是計算基底態 | [BHW] 正文 | ✅ 不動點空間維度是 1，不動點就是 \|ab⟩⟨ab\| |
| 祖父悖論在完美的槍（σx）下，P-CTC 的投影振幅永遠是零 | [L11] 第 3 頁 | ✅ C = Tr_CTC U 作用後得到 0，後選擇成功率是 0 |
| D-CTC 唯一的不動點是 (\|0⟩⟨0\| + \|1⟩⟨1\|)/2，而且「用 Deutsch 的 CTC 她總是成功」 | [L11] 第 2 頁、Fig. 2 說明 | ✅ 不動點唯一，兩個探針結果相反的機率是 1 |
| 不完美的槍下，探針從來不會出現 01 或 10 | [L11] 第 3 頁、Fig. 4 | ✅ 在 P-CTC 下，所有 θ < π 的情況都是 0 |
| Fig. 4 的理論曲線：θ = 0 時是 0.5，θ = 180° 時降到 0 | [L11] Fig. 4 | ✅ 後選擇成功率是 cos²(θ/2)/2，θ = 90° 時是 0.25。閉式公式是本專案推導的，論文只畫了曲線 |
| 後選擇 teleportation 等於 CρC† / Tr，其中 C = Tr_CTC U | [L11-PRD] Eq. (8)–(9) | ✅ 直接模擬 teleportation 電路，跟 C 公式的結果一致，成功率也一致，是 Tr[CρC†]/d² |
| 未證明定理悖論：證明位元的值完全隨機，因為它和從 CTC 出來的位元最大糾纏 | [L11] Fig. 2b 說明 | ✅ 輸出是 (\|00⟩ + \|11⟩)/√2，證明位元的約化態是 I/2 |

![Lloyd Fig. 4 theory](output/lloyd_fig4_theory.png)

## 本專案推導的額外結果

| 結果 | 意義 |
|---|---|
| D-CTC 下，Lloyd 的槍讓兩個探針結果相反（「殺死」）的機率是 sin²(θ/2) | 跟 P-CTC 完全相反：P-CTC 下永遠「沒殺成」，D-CTC 下槍越準越容易「殺成」 |
| 未證明定理電路在 D-CTC 下，得到的是古典相關的混合態 (\|00⟩⟨00\| + \|11⟩⟨11\|)/2 | 兩種規則的統計一樣，但 P-CTC 給出糾纏，D-CTC 只給出古典相關。這跟 ctc/README.md 中自舉悖論的結果一致 |
| BB84 電路吃一個混合輸入（\|0⟩ 和 \|+⟩ 各一半），輸出不等於兩個輸出的平均 | D-CTC 是非線性的。這正是 Bennett、Leung、Smith、Smolin（PRL 103, 170502, 2009；[L11] 參考文獻 [19]）質疑的「線性陷阱」問題，本專案只是示範，沒有評斷爭論的結論 |

## 慣例與需要說明的地方

1. **槍的寫法：** [L11] 寫成 U(θ) = e^{−iθσx}，展開卻寫 cos(θ/2)𝟙 − i sin(θ/2)σx，又說 θ = π 時會翻轉位元。三者要一致，必須是 **e^{−iθσx/2}**，這裡採用這個寫法。如果照字面用 e^{−iθσx}，θ = π 時是 −𝟙，槍根本不會擊發。
2. **Lloyd 的實驗電路：** Fig. 3a 中，探針都接在「向前」的偏振位元上，這個位元在 P-CTC 的描述裡就是穿越時間的位元。這裡直接用 Fig. 2a 的抽象電路，不模擬光學元件。
3. **BB84 的接線：** 正文只說「兩個 SWAP，接著四個受控么正」。Fig. 2 顯示：ψ 跟第一個 CTC 位元交換，輔助位元跟第二個 CTC 位元交換，每個 U_ab 作用在兩個 CTC 位元上，由 CR 位元的值 ab 控制。U_00 和 U_11 裡的 SWAP 是兩個 CTC 位元之間的交換，張量積的第一個因子作用在第一個 CTC 位元上。
4. **成功機率的歸一化：** Tr[CρC†]/d² 是用最大糾纏態 Σ\|ii⟩/√d 做 teleportation 時的成功機率。`ctc/output/toy_results.csv` 裡的 `p_ctc_weight` 欄位是沒有除以 d² 的 Tr[CρC†]。

## 限制

- 只重現理論預測，沒有重現 [L11] 的實驗數據點。Fig. 4 的數據點來自實際量測，論文說同態曲線和理論的差異來自 1.1 ± 0.1° 的偏振片偏差，異態機率量到 0.01 ± 0.04。
- [BHW] 的一般 N 態構造（Gram–Schmidt 建出 U_k）還沒有實作，只做了 N = 2 和 N = 4 的例子。
- 論文是用 arXiv 版本核對的，沒有核對期刊版本。
