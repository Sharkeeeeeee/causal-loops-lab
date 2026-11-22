# 新穎性檢查：無訊號測試和 κ–β 模型

日期：2026-11-22，撰寫時使用 AI 輔助（Claude）。範圍有限：做了兩輪網路搜尋，讀到原文的有四篇（Bub–Stairs 全文；Araújo–Guérin–Baumeler 第 I–III 節；Allen 2014 大部分；Silva 等人 2017 全文）。其他判斷只根據摘要。沒有請專家確認，所以「沒找到」不等於「沒人做過」。

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

## 還沒查的

- 從 Lloyd 2011、Allen 2014 往後的完整引用追蹤（需要能看引用清單的資料庫，例如 INSPIRE 或 Semantic Scholar）。
- 直接請熟悉 CTC 文獻的研究者確認。這是確認新穎性最可靠的方法。
