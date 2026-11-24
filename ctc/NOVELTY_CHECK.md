# 新穎性檢查：無訊號測試、κ–β 模型和過去守恆篩選

日期：2026-11-22，第三輪 2026-11-24（過去守恆篩選 vs. Hartle 1994，見文末），撰寫時使用 AI 輔助（Claude）。範圍有限：做了兩輪網路搜尋，讀到原文的有四篇（Bub–Stairs 全文；Araújo–Guérin–Baumeler 第 I–III 節；Allen 2014 大部分；Silva 等人 2017 全文）。其他判斷只根據摘要。沒有請專家確認，所以「沒找到」不等於「沒人做過」。

## 結論

| 本專案的結果 | 文獻裡有沒有 | 判斷 |
|---|---|---|
| P-CTC 讓 Alice 對共享糾纏的 Bob 超光速傳訊 | **有**。Bub & Stairs 2014 第 III 節明確主張用 P-CTC 可以超光速傳訊 | 不是新結果 |
| D-CTC 是否傳訊，取決於套用在約化態還是逐分支 | **有**。Bub & Stairs 2014 第 II 節：D-CTC 的結果取決於參考系，傳訊與否取決於狀態在哪個參考系中被視為糾纏；Cavalcanti–Menicucci–Pienaar 2012 的「製備問題」；Bennett 等人 2009 的「線性陷阱」 | 不是新結果 |
| P-CTC 不傳訊 ⇔ C†C ∝ 𝟙 | **實質上有**。Araújo–Guérin–Baumeler 2017 第 III 節：P-CTC 的映射是線性的，若且唯若後選擇機率對所有局部操作和輸入都是常數，而這正好就是 process matrix。C†C 這種寫法沒找到，但它只是單一參與者時的直接推論 | 新意很低 |
| 古典 κ–β 雙參數模型（P-CTC 和 D-CTC 是兩個角落） | 沒找到內插兩者的連續規則家族。**但最接近的前人工作是 Allen 2014：** 他明確把 T-CTC 寫成「P-CTC 加上一個普通量子通道」的加權混合（Eq. 33），並說轉移機率理論是一類理論、積分測度沒有唯一選擇。他只給了一個點，沒有連續家族，也沒有連到 D-CTC（第二輪，原文已讀，見下） | 可能是新的，但新意比原先估計的低；論文必須引用 Allen 2014 並說明差別 |
| 在 κ–β 家族裡，「重新加權」和「傳訊」是同一件事（命題 1） | 沒找到明確的陳述。精神上已隱含在 Baumeler–Wolf 的古典 process function 定義裡（要求對所有局部操作都有唯一、歸一化的自洽解，也就是不允許重新加權） | 新意低到中 |

**整體判斷：** 無訊號測試的核心結論，也就是「會重新加權就會傳訊、P-CTC 會傳訊、D-CTC 的傳訊取決於解讀」，都已經是文獻中的已知結果。本專案的版本是獨立重現。真正可能是新的，只有 κ–β 這個內插模型本身，以及在它上面畫出的傳訊圖。

## 對專案的意義

1. **好消息：** 程式獨立得到了跟 Bub–Stairs、Araújo 等人一致的結論，這是對程式正確性的外部支持。
2. **壞消息：** 「H2 跟無訊號條件互斥」大概不能當作研究筆記的主要貢獻，因為業界已經知道非線性的 P-CTC 會傳訊，也知道線性版本（process matrix）不會重新加權。
3. **Araújo 等人的結果讓 H2 的處境更清楚：** 不傳訊的 P-CTC 正好就是 process matrix。所以「保留自洽、放棄重新加權」的那條路，文獻裡已經有一個完整的框架，也就是階段 2 的 process matrix。H2 若要改寫，應該問的是：在 process matrix 框架裡，迴圈還能留下什麼可觀察的未來效應？

## 讀過的來源

- J. Bub, A. Stairs, "Quantum Interactions with Closed Timelike Curves and Superluminal Signaling", [arXiv:1309.4751](https://arxiv.org/abs/1309.4751)（全文）。他們的傳訊結論建立在自己提出的一致性條件上，Bennett 等人不同意。
- M. Araújo, P. A. Guérin, Ä. Baumeler, "Quantum computation with indefinite causal structures", Phys. Rev. A 96, 052315 (2017), [arXiv:1706.09854](https://arxiv.org/abs/1706.09854)（第 I–III 節原文；第 VI 節之後沒讀）。這篇的第 I–III 節沒有提到傳訊。
- E. Cavalcanti, N. Menicucci, J. Pienaar, "The preparation problem in nonlinear extensions of quantum theory", [arXiv:1206.2725](https://arxiv.org/abs/1206.2725)（只讀摘要）。
- J.-M. A. Allen, "Treating Time Travel Quantum Mechanically", Phys. Rev. A 90, 042107 (2014), [arXiv:1401.4933](https://arxiv.org/abs/1401.4933)（第二輪讀了到第 V 節的原文，只有最後約 19,000 字元沒讀）。
- R. Silva 等人, "Connecting processes with indefinite causal order and multi-time quantum states", New J. Phys. 19, 103022 (2017), [arXiv:1701.08638](https://arxiv.org/abs/1701.08638)（全文）。
- T. C. Ralph, "Problems with modelling closed timelike curves as post-selected teleportation", [arXiv:1107.4675](https://arxiv.org/abs/1107.4675)；S. Ghosh 等人, "Quantum Signaling to the Past Using P-CTCs", [arXiv:1708.03521](https://arxiv.org/abs/1708.03521)（只看搜尋摘要；這兩篇談的是傳訊到過去，不是類空傳訊）。
- Baumeler–Wolf 關於古典 process function 的系列論文，以及 [arXiv:2512.23599](https://arxiv.org/abs/2512.23599)（只看搜尋摘要）。

## 第二輪（同日）

**Allen 2014，第 IV C 節到第 V 節大部分原文已讀：**

- T-CTC 的定義（Eq. 24–26）：對迴圈的所有純態做 Haar 積分。閉式解（Eq. 33）是 P-CTC 項加上 d 倍的「完全隨機迴圈」通道。Allen 原話的意思是：T-CTC 是 P-CTC 和一個普通通道的加權混合，容易讓人以為它是「有雜訊的 P-CTC」。
- 轉移機率理論是「一類理論」，因為積分測度沒有唯一的自然選擇（§IV E.6）。
- 「加權 D-CTC」（§IV C）：在 D-CTC 有多個不動點時，給每個不動點一個權重。這是 D-CTC 內部的選擇規則，不是往 P-CTC 的內插。
- T-CTC 的傳訊：§IV E.5 說 T-CTC 的非線性讓「糾纏偵測器」成為可能，跟 D-CTC、P-CTC 一樣。
- 本專案已經把 T-CTC 實作成第四種規則，並重現了 Eq. 33、35、38、40，見 [T_CTC.md](T_CTC.md)。

**Silva 等人 2017（[arXiv:1701.08638](https://arxiv.org/abs/1701.08638)，全文已讀）：** process matrix 對應到一類「線性的」雙時間態，也就是對所有局部操作，歸一化條件都自動成立，不需要依賴測量的重新歸一化（Eq. 19、21、29）。這跟 Araújo 等人的線性條件是同一件事，但這篇完全沒有討論 CTC 或傳訊。

**內插規則家族的搜尋：** 用不同關鍵字做了幾輪搜尋，沒有找到內插 D-CTC 和 P-CTC 的連續規則家族。找到的都是單一模型、D-CTC 加上去相干（用來選出唯一不動點），或 P-CTC 的推廣。

**更新後的判斷：** κ–β 模型仍可能是新的，但 Allen 2014 已經走了「P-CTC 混合一個不篩選的通道」這一步，所以新意比原先估計的低。真正的差異在於：κ–β 是連續的雙參數家族、另一個角落是 D-CTC，而且有完整的傳訊圖。

## 第三輪（2026-11-24）：過去守恆篩選 vs. Hartle 1994

**來源：** J. B. Hartle, "Unitarity and causality in generalized quantum mechanics for nonchronal spacetimes", Phys. Rev. D 49, 6543 (1994), [arXiv:gr-qc/9309012](https://arxiv.org/abs/gr-qc/9309012)。**全文已讀**（arXiv v1 的 PDF 轉成文字，41 頁，第 I–VIII 節和附錄；公式符號在轉換時有部分毀損，下面的公式是對照上下文整理的）。

### Hartle 做了什麼

在有非時序區域 NC 的固定背景時空裡，用推廣量子力學（去相干泛函）處理穿過 NC 的非么正演化 X。核心公式是 Eq. (3.12)：

    D(β′, α′; β, α) = Tr(C_β′ X C_α′ ρ C_α† X† C_β†) / Tr(XρX†)

C_α 是 NC 之前的投影鏈，C_β 是 NC 之後的投影鏈。整個歷史用同一個常數 Tr(XρX†) 歸一化。

### 逐項比對

| 項目 | Hartle 1994 | 過去守恆篩選（PP） |
|---|---|---|
| NC 之後的狀態 | ρ̄ = XρX† / Tr(XρX†)（Eq. 6.7），就是 P-CTC 的公式（X 對應 C） | 每個世界 k 各自是 C\|k⟩/‖C\|k⟩‖ |
| NC 之前的機率 | p(α) = N·Tr(X C_α ρ C_α† X†)（Eq. 4.1），**會被未來的 NC 改變**。Hartle 稱之為 acausal，並說可以用實驗比較 (4.1) 和 (4.2) 來偵測未來的 NC | p(k) = ⟨k\|ρ\|k⟩，**不變** |
| 已記錄的初始狀態下的條件機率 | §V 的量測模型：初始選項 α 被儀器的持久紀錄去相干（Eq. 5.4）時，p(β\|α) = \|⟨β\|X\|α⟩\|² / Σ_β′ \|⟨β′\|X\|α⟩\|²（Eq. 5.6） | 完全相同（X 對應 C） |
| 已記錄的初始狀態下的聯合機率 | p(β, α) = N·\|⟨β\|X\|α⟩\|²·⟨α\|ρ\|α⟩（Eq. 5.5），所以 p(α) ∝ ⟨α\|ρ\|α⟩·‖X\|α⟩‖²，也就是 P-CTC 的重新加權 | p(α) = ⟨α\|ρ\|α⟩ |
| 世界沒有自洽歷史（X\|α⟩ = 0） | 沒有討論；(5.6) 是 0/0 | 退回 D-CTC |
| 有沒有「狀態」 | 明確說沒有：無法在類空面上定義 ρ_eff（第 IV 節） | 有：PP 是普通的量子通道 |
| 不能超光速傳訊 | 第 VII 節證明，但前提是兩個區域**初始不相關**，而且**共同的未來沒有 NC**（Eq. 7.6–7.7）。Hartle 也說，利用共同未來的 NC 產生的相關性「值得研究」 | 對任何共享態都成立（定理 0，固定記錄基底） |
| 有沒有提出「不重新加權過去」的版本 | **沒有**。重新加權被當成理論的特徵，不是要修掉的缺點 | 這就是 PP 的定義 |

### 結論

1. **PP 在每個世界之內的規則不是新的。** 它就是 Hartle 1994 Eq. (5.6)：初始狀態被持久紀錄去相干時的條件機率。這也等於 P-CTC 作用在確定輸入上（見 PERSPECTIVES.md 1.5）。
2. **PP 跟 Hartle 的差別只有一處，而且是刻意相反的選擇：** 已記錄的過去的機率。Hartle 的框架裡，過去的機率被 ‖X\|α⟩‖² 重新加權（他稱為 acausal）；PP 規定它們不變。用 Hartle 的話說，PP 就是「保留 Eq. (5.6) 的條件機率，但把聯合機率裡的世界權重換回 Eq. (4.2) 的因果版本」。
3. **在 Hartle 1994 裡找不到這個因果版本。** 但這只是一篇論文。引用 Hartle 1994 的後續工作還沒查，「已記錄的世界各自歸一化」這種結構在去相干歷史的文獻裡可能有人寫過。
4. **跟本專案無訊號結果的關係。** Hartle 的「不能傳訊」排除了初始糾纏的情況。NO_SIGNALLING.md 的 P-CTC 傳訊例子用的正是初始糾纏，所以兩者不矛盾：專案的結果落在 Hartle 明確排除、並說「值得研究」的那一塊。
5. **對記錄基底問題的啟發。** 在 Hartle 的框架裡，只有**去相干**的過去選項才能被指定機率，而且當 X 非么正時，哪些選項去相干本身也受未來的 NC 影響（Eq. 4.7）。他也指出，實際的去相干機制在時間上是局域的，大致不受未來 NC 影響。這給 PP 的記錄基底一個有文獻依據的候選定義：**記錄基底 = 被局域的環境機制去相干的那組過去選項**，跟 PERSPECTIVES.md 3.1「基底由交互作用決定，不依賴狀態」的建議一致。

**更新後的判斷：** PP 不能整體宣稱是新的規則。可能是新的部分縮小成一句話：在 Hartle 型的推廣量子力學裡，把已記錄的過去選項的機率固定為因果值，而只在每個記錄之內做 Hartle/P-CTC 的條件化；這樣得到的是一個不傳訊的量子通道，而且 H1′–H3′ 成立。研究筆記如果要用 PP，**必須引用 Hartle 1994 Eq. (5.5)–(5.6)，並把 PP 定位成 Hartle 框架的因果修改**，而不是一條全新的規則。

## 還沒查的

- 從 Lloyd 2011、Allen 2014、**Hartle 1994** 往後的完整引用追蹤（需要能看引用清單的資料庫，例如 INSPIRE 或 Semantic Scholar）。Hartle 1994 的後續工作是確認 PP 新穎性的下一步。
- 直接請熟悉 CTC 文獻的研究者確認。這是確認新穎性最可靠的方法。
