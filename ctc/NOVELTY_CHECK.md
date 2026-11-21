# 新穎性檢查：無訊號測試和 κ–β 模型

日期：2026-11-22，撰寫時使用 AI 輔助（Claude）。範圍有限：做了幾輪網路搜尋，只有兩篇論文讀到原文段落（Bub–Stairs 全文；Araújo–Guérin–Baumeler 第 I–III 節）。其他判斷只根據摘要。沒有請專家確認，所以「沒找到」不等於「沒人做過」。

## 結論

| 本專案的結果 | 文獻裡有沒有 | 判斷 |
|---|---|---|
| P-CTC 讓 Alice 對共享糾纏的 Bob 超光速傳訊 | **有**。Bub & Stairs 2014 第 III 節明確主張用 P-CTC 可以超光速傳訊 | 不是新結果 |
| D-CTC 是否傳訊，取決於套用在約化態還是逐分支 | **有**。Bub & Stairs 2014 第 II 節：D-CTC 的結果取決於參考系，傳訊與否取決於狀態在哪個參考系中被視為糾纏；Cavalcanti–Menicucci–Pienaar 2012 的「製備問題」；Bennett 等人 2009 的「線性陷阱」 | 不是新結果 |
| P-CTC 不傳訊 ⇔ C†C ∝ 𝟙 | **實質上有**。Araújo–Guérin–Baumeler 2017 第 III 節：P-CTC 的映射是線性的，若且唯若後選擇機率對所有局部操作和輸入都是常數，而這正好就是 process matrix。C†C 這種寫法沒找到，但它只是單一參與者時的直接推論 | 新意很低 |
| 古典 κ–β 雙參數模型（P-CTC 和 D-CTC 是兩個角落） | 沒找到內插兩者的連續規則家族。Allen 2014 的 T-CTC 是第三種規則，不是內插 | 可能是新的，但價值中等，需要專家確認 |
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
- J.-M. A. Allen, "Treating Time Travel Quantum Mechanically", Phys. Rev. A 90, 042107 (2014), [arXiv:1401.4933](https://arxiv.org/abs/1401.4933)（只讀摘要）。
- T. C. Ralph, "Problems with modelling closed timelike curves as post-selected teleportation", [arXiv:1107.4675](https://arxiv.org/abs/1107.4675)；S. Ghosh 等人, "Quantum Signaling to the Past Using P-CTCs", [arXiv:1708.03521](https://arxiv.org/abs/1708.03521)（只看搜尋摘要；這兩篇談的是傳訊到過去，不是類空傳訊）。
- Baumeler–Wolf 關於古典 process function 的系列論文，以及 [arXiv:2512.23599](https://arxiv.org/abs/2512.23599)（只看搜尋摘要）。

## 還沒查的

- Silva、Guryanova、Short、Skrzypczyk、Brunner、Popescu 2017 關於 process matrix 和多時間態的論文（可能也有「後選擇機率與局部操作無關」的條件）。
- T-CTC 是否傳訊。
- 從 Lloyd 2011、Allen 2014 往後的完整引用追蹤，特別是有沒有人做過內插 D-CTC 和 P-CTC 的規則家族。
