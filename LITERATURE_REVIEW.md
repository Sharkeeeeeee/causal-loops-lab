# 文獻盤點：H1、H2、H3 與 ctc/ 玩具結果在 P-CTC / D-CTC 文獻中的位置

建立日期：2026-11-22。撰寫時使用 AI 輔助（Claude），沒有外部審查。這是 ROADMAP 階段 0「文獻盤點」的成果，不是已發表的綜述。

**閱讀程度的分級**（每一條主張都應該能對回這裡）：

- **[全文]**：我把 PDF 轉成文字後讀了相關段落（不是逐字通讀全文）。Lloyd 等人 PRL（1005.2219）與 PRD（1007.2615）、Ralph 的評論（1107.4675）、Allen（1401.4933）、Bennett–Leung–Smith–Smolin（0908.3023）屬於這一級。其中 PRD、Allen、BLSS 是用關鍵字定位後讀相關段落。
- **[HTML/摘要+]**：讀了 arXiv HTML 版的前段，其餘是模型摘要（可能有誤，引用前須對照原文）。Baumeler 等人 2019（1703.00779）、Tobar–Costa（2001.02511）屬於這一級。
- **[摘要]**：只讀了 arXiv 摘要頁或搜尋結果摘要。其餘論文都是這一級。
- **[未驗證]**：沒有看到任何一手來源，只是記憶或二手說法。這類內容會明確標記，且不給 arXiv 編號。

專案自己的結論（P-CTC 與 D-CTC 的數字）來自 `ctc/README.md`，本文沒有重跑 `ctc/` 的程式。

---

## 1. 對照表

| 項目 | 狀態 | 對應文獻與說明 |
|---|---|---|
| **H1** 傳回過去的資訊必定自洽（無祖父悖論） | **已知** | 古典：Novikov 自洽原則、Echeverria–Klinkhammer–Thorne 1991 的 billiard ball 分析（只看到摘要層級的二手說明，且發現的是自洽解**不唯一**，[摘要]）。量子：Deutsch 1991 用密度矩陣不動點保證自洽，Lloyd 等人 2011 用後選擇「機率振幅為零的事件不發生」直接實作 Novikov 原則 [全文]。注意兩者的「自洽」強度不同：Deutsch 只要求迴圈系統自己的密度矩陣自洽，**不保留**它與 CR 變數的關聯；P-CTC 要求連同關聯一起自洽（Lloyd 等人 PRD §I [全文]）。H1 在專案裡要指定「哪一種自洽」才有確定的內容。 |
| **H2(1)** 迴圈的效應可觀察，且出現在未來統計 | **部分已知，且有爭議** | P-CTC 下，Lloyd 等人 PRL 明確說明矛盾事件的機率為零、其餘重新歸一化（非線性）[全文]。但 Ralph 2011（1107.4675）[全文] 主張 P-CTC 在有糾纏時允許「訊號傳到 CTC 建立之前」，Lloyd 等人的回覆（1108.0153）[摘要+ar5iv 摘要層級] 與 Bub–Stairs（1309.4751）[摘要] 都認為 Ralph 的構造不完整或有缺陷。所以「效應只出現在未來」這句話在 P-CTC 下是有爭議的，不是已定論。D-CTC 下，效應在 CR 系統上表現為非線性的不動點通道，不是單純重新加權。 |
| **H2(2)** 差異完全由「排除不自洽歷史並重新加權」決定 | **P-CTC 下已知（形式上），一般陳述未見** | P-CTC 規則本身就是「投影後歸一化」，對古典可逆電路等於對自洽歷史條件化（Lloyd 等人 [全文]；Svetlichny 的「機率性模擬」[摘要]）。我**沒有**找到把它寫成 `P_loop ∝ P_0 × [自洽]`、並與 D-CTC 逐項對比的一般性陳述，但這個否定結論只基於我搜到的範圍。 |
| **H3** 沒有迴圈影響時退化成一般因果 QM | **已知但平凡，有一個角落案例** | 這是兩種規則的形式直接推得的：若 U = V ⊗ W（迴圈與 CR 不耦合），則 C = V·Tr[W]，P-CTC 輸出為 VρV†，D-CTC 也一樣。**本檔自己推導、未在文獻中核對**。角落案例：若 Tr[W] = 0（例如迴圈系統單獨做 Z），P-CTC 規則沒有定義，所以 H3 在 P-CTC 下需要附加「迴圈本身自洽」的條件。process matrix 框架中的對應是「因果可分」或古典極限回到因果順序（Oreshkov–Costa–Brukner 摘要稱 classical limit 下因果順序總會出現 [摘要]）。 |
| **(a)** 祖父悖論，失敗機率 ε：P-CTC 讓失敗變成確定，D-CTC 保持 ε | **已知** | Lloyd 等人 PRL 的 Fig. 2a 和正文就是這個電路：理想 NOT 時 P-CTC 的矛盾事件機率為零；不完美的 NOT（旋轉角偏離 π）時，非線性後選擇把偏差放大，只剩「槍失效」的自洽歷史；D-CTC 下她「總是成功」，迴圈位元變成完全混合。光子實驗（量子點單光子）檢驗了 P-CTC 的預測 [全文]。`ctc/` 的 (a) 在定性上重現了這個結果；**定量數值尚未對照該文的圖表**（ROADMAP 階段 1 的待辦）。 |
| **(b)** KFK 型提醒：無條件寄出 = 一般訊息 | **已知（隱含）** | 無條件寄出時 U 對迴圈位元只是複製，P-CTC 與 D-CTC 一致，是一般通道。H3 的特例，沒有找到專門論述。 |
| **(b)** KFK 型提醒：有動機才寄，P-CTC 給 q(1−r)/(1−qr)，D-CTC 給 q/(1+qr) | **明顯未見（apparently open）** | 這是祖父悖論的「帶機率動機」版本，結構與 (a) 相同，因此**定性**上已知（P-CTC 排除矛盾歷史、D-CTC 混合）。但我沒有在檢索到的文獻中找到這個「單一接收者＋動機寄件者＋兩種規則的閉式比較」。這是「沒找到」，不是「確定沒人做過」。 |
| **(c)** 自舉悖論：Z 統計相同，P-CTC 相干（⟨X⟩=1），D-CTC 混合（⟨X⟩=0） | **部分已知，且需要對照一個敘述差異** | Lloyd 等人 PRL：P-CTC 把純態送到純態、不產生熵；D-CTC 需要另外加「最大熵」假設來解決 unproved-theorem 悖論 [全文]。這與 (c) 的方向一致。**但**同一篇 PRL 又說該電路「自動指派完全混合值」（Fig. 2b 說明文字），這是指 proof 位元與迴圈中另一個位元最大糾纏、其約化態是混合的；與 `ctc/` 把記錄寫成相干疊加並不矛盾，但需要弄清楚「被測的是哪個系統」。另外，Ralph 2011 以 unproved-theorem 為由反對 P-CTC，Lloyd 等人回覆說他漏了一步（Bob 讀書）[摘要層級]。見缺口 3。 |

---

## 2. 重點論文：它們建立了什麼

以下每段都標了閱讀程度。

**Deutsch 1991，Quantum mechanics near closed timelike lines，Phys. Rev. D 44, 3197（DOI 10.1103/PhysRevD.44.3197）[摘要/二手]。** 提出 D-CTC：迴圈系統的狀態 ρ_CTC = Tr_CR[U(ρ_CR⊗ρ_CTC)U†] 必有至少一個不動點；若不唯一，Deutsch 另外假設取最大熵者（這是 Lloyd 等人 PRD 對 Deutsch 規則的描述，[全文]）。他的規則使迴圈出口的狀態與 CR 變數不相關，所以記憶「已不再有效」。我沒有讀 Deutsch 原文，所有關於它的敘述都經由 Lloyd 等人和其他論文轉述。

**Bennett & Schumacher 2005 talk、Svetlichny，Time travel: Deutsch vs. teleportation，Int. J. Theor. Phys. 50, 3903（2011；DOI 10.1007/s10773-011-0973-x；arXiv 版 0902.4898，標題 Effective Quantum Time Travel）[摘要]。** 用 teleportation 加後選擇機率性地模擬帶有「往回連線」的量子電路，摘要稱機率性質「解決任何悖論」。Bennett–Schumacher 是未發表的演講（透過 Svetlichny 的引用得知，我沒有讀到演講內容，[未驗證內容]）。這是專案 P-CTC 規則的源頭。

**Lloyd 等人 2011 PRL，Closed timelike curves via postselection: theory and experimental test of consistency（arXiv 1005.2219，PRL 106, 040403）[全文]。** 定義 P-CTC，與 Deutsch 物理上不等價；祖父悖論電路、不完美「槍」的非線性放大、光子實驗；P-CTC 純態進純態；unproved theorem 悖論被「無偏見電路得到所有證明的無偏混合」解決；P-CTC 的計算能力在 PP 中。對本專案：結果 (a)、(c) 的概念原型，H2 在 P-CTC 下的最直接來源。

**Lloyd 等人 2011 PRD，The quantum mechanics of time travel through post-selected teleportation（arXiv 1007.2615，PRD 84, 025007）[全文，關鍵字定位]。** PRL 的完整版：Hilbert 空間公式、與路徑積分一致、Deutsch 規則的比較。文中明說「目前無法決定 P-CTC 與 D-CTC 孰對孰錯，也許要等到量子重力理論」；並稱 P-CTC 「更少病態」（不需要最大熵規則、計算能力較弱）。非線性「重新歸一化機率」就是計算能力與放大的來源。這也是本專案「選擇規則尚未決定」立場的文獻依據。

**Brun, Harrington, Wilde 2009，Localized closed timelike curves can perfectly distinguish quantum states（arXiv 0811.1209，PRL 102, 210402）[摘要]。** 在 D-CTC 模型下，局域 CTC 可以完全區分非正交態，使 BB84 等 QKD 可被破解，並違反 Holevo 界。

**Bennett, Leung, Smith, Smolin 2009，Can closed timelike curves or nonlinear quantum mechanics improve quantum state discrimination or help solve hard problems?（arXiv 0908.3023，PRL 103, 170502）[全文，關鍵字定位]。** 提出 linearity trap：非線性映射作用在混合態上，不等於它對各純態成分作用結果的混合，因此對「未知混合態」的辨別、以及對「標記混合」的計算要小心定義。他們建議把計算定義為對「帶標記的正交輸入混合」正確求值；在這個定義下，不清楚 CTC 是否有幫助，而且 CTC 的辨別優勢可以用直接解不動點方程來重現。與 Brun–Harrington–Wilde 構成辯論。對本專案：D-CTC 的結果取決於「輸入是未知混合」還是「標記混合」，我們的 `ctc/` 一律是前者的簡單版本，這個區別要在報告中明說。

**Aaronson & Watrous 2009，Closed timelike curves make quantum and classical computing equivalent（arXiv 0808.2669，Proc. R. Soc. A 465, 631）[摘要，加上 PDF 的章節目錄]。** 在 Deutsch 模型下，古典與量子電腦配 CTC 都等於 PSPACE。至於不動點不唯一時它如何處理（是否用最大熵），我**沒有讀到內文**，標為未驗證。

**Brun & Wilde 2012，Perfect state distinguishability and computational speedups with postselected closed timelike curves（arXiv 1008.0433，Found. Phys. 42, 341，DOI 10.1007/s10701-011-9601-0）[摘要，加上章節標題]。** 在 P-CTC 下，單一位元通過 CTC 就能以機率 1 做任何後選擇量測（摘要層級），並展示 P-CTC 可用來解難題。P-CTC 計算力為 PP 這一點，我在 Lloyd 等人 PRL 與 Araújo–Guérin–Baumeler（1706.09854）的摘要中看到，在 Brun–Wilde 內文中沒有親自確認。

**Ralph & Myers 2010，Information flow of quantum states interacting with closed timelike curves（arXiv 1003.1987，PRA 82, 062330）[摘要]。** 追蹤資訊流，導出「等價電路」並得到唯一解，用來客觀比較不同 CTC 模型，並稱 CTC 若存在會是強大的量子資訊資源。Ralph 在評論中稱 Deutsch 的最大熵猜想「已被獨立導出」並引用此文（[全文] 1107.4675 的最後一段），但這篇的推導內容我沒有讀。Allen 2014 的摘要稱這種「等價電路模型」含有錯誤 [摘要]；Brun–Wilde 也提到它的歧義（二手）。**Ralph & Myers / Ralph 等人 event-CTC 的細節我沒有核實**：我原本想核對的「event-CTC」說法沒有在搜尋中找到明確論文，沒有證實存在，故不列入結論。

**Pienaar, Ralph, Myers 2013，Open timelike curves violate Heisenberg's uncertainty principle（arXiv 1206.5485，PRL 110, 060501）[摘要]、Ringbauer 等人 2014，Experimental simulation of closed timelike curves（Nat. Commun. 5, 4145；arXiv 1501.05014）[摘要]。** 前者對沒有迴圈內交互作用的「open timelike curve」做模型；後者用光子模擬 D-CTC 的單位元電路（觀察到非正交態的完全辨別）。這兩篇是 D-CTC 側的實驗與延伸，我沒有讀全文。

**Ralph 2011，Problems with modelling closed timelike curves as post-selected teleportation（arXiv 1107.4675）[全文] 與 Lloyd 等人的回覆（arXiv 1108.0153）[摘要+ar5iv 摘要層級]。** Ralph 用「一臂糾纏態送過蟲洞，Bob 用相位翻轉送訊」的構造，主張 P-CTC 允許訊號傳到 CTC 建立之前，並重現 unproved-theorem 悖論。回覆說 Ralph 漏掉了 Bob「讀書」這一步（相位翻轉必須由 Alice 的書控制），補上後整個過程的振幅為零，或只剩平凡不動點。Bub–Stairs 2014（1309.4751）[摘要] 也說 Ralph 的做法有缺陷（理由是糾纏依賴參考系）。**這場爭論直接牽涉到 H2「只影響未來」是否成立**，也沒有看到定論。

**Allen 2014，Treating time travel quantum mechanically（arXiv 1401.4933，PRA 90, 042107）[全文，T-CTC 部分]。** 回顧 D-CTC 與 P-CTC 的優缺點，提出「transition probability」CTC（T-CTC）：對所有純態 |ψ⟩，以 p(ψ) = |⟨ψ|U|i⟩|² 的權重做混合，並以部分投影求 CR 輸出，公式約為 ρ_f = Z⁻¹ ∫dψ (…)；化簡後是「P-CTC 運動方程與一個普通量子通道的加權混合」（Eq. 33）。摘要宣稱 T-CTC 沒有悖論、不能完美辨別非正交態、不能複製或刪除任意純態；內文指出它的計算力不超過 PP，並說它不能做任意後選擇量測。我沒有讀它對祖父悖論的具體數值。這是專案「選擇規則 X」最現成的第三個候選。

**Brun 等人與 Dunlap（多世界解讀）。** Dunlap 2015（arXiv 1510.02742）[摘要] 主張 D-CTC 需要比 Everett 更強的形上學補充（多個相同的世界副本），所以它不是「純量子」的悖論解。這與 HYPOTHESIS.md 把 D-CTC 對應 B「分支時間線」有關；我沒有找到對 P-CTC 的多世界讀法的專門論述（搜尋範圍有限）。

**Novikov / Echeverria–Klinkhammer–Thorne 1991。** 我只有 OSTI 紀錄（https://www.osti.gov/biblio/5219973）確認論文存在與標題；卷頁數**未驗證**，Novikov 原始論文**未找到一手來源**，不給編號。二手說明稱 Echeverria–Klinkhammer 發現了不只一個自洽解 [摘要層級]。對本專案：古典層次的「自洽不保證唯一」是 H1 在古典下要面對的事實，這也是 D-CTC 的不動點非唯一問題的古典前身。

**Politzer（hep-th/9207076）、Hartle（gr-qc/9309012）[摘要]。** 路徑積分／推廣量子力學對非時序時空的處理：Hartle 的框架在非么正下仍保持機率規則；Lloyd 等人聲稱 P-CTC 與這些路徑積分作法一致 [全文]。

**Oreshkov–Costa–Brukner 2012，Quantum correlations with no causal order（arXiv 1105.4464，Nat. Commun. 3, 1092）[摘要]。** 只假設局部量子力學成立，建立沒有預設因果順序的 process matrix 框架，找到違反因果不等式的相關性。**Araújo–Feix–Navascués–Brukner 2017，A purification postulate for quantum mechanics with indefinite causal order（arXiv 1611.08535，Quantum 1, 10）[摘要]：** 只有可純化的 process 才算物理，並說有些已知 process 不滿足；摘要沒有說原始 OCB process 是否在內，也沒有談後選擇。

**Baumeler & Wolf 2014/2016。** Perfect signaling among three parties violating predefined causal order（arXiv 1312.5916）[摘要]；The space of logically consistent classical processes without causal order（我只在 ar5iv 結果中看到 1507.01714 這個編號，**未經證實**，請自行核對）；Baumeler & Wolf，Computational tameness of classical non-causal models（arXiv 1611.05641，Proc. R. Soc. A 474, 20170698）[摘要]：邏輯自洽的古典非因果電路模型精確對應 UP ∩ coUP，比其他 CTC 模型弱。

**Baumeler–Costa–Ralph–Wolf–Zych 2019，Reversible time travel with freedom of choice（arXiv 1703.00779，CQG 36, 224002）[HTML/摘要+]。** 注意作者名單：Baumeler、Costa、Ralph、Wolf、Zych（不是 Woods，任務簡述有誤）。結果：在與任意局部操作相容的古典確定性動力學下，所有這類動力學可以用可逆交互作用實現；三方可以彼此互在對方的過去與未來，同時各自仍有自由局部選擇。**全篇是確定性的，沒有機率性的「重新加權未來」。** 關於量子延伸，它說量子化是否可行仍不清楚，並對 D-CTC / P-CTC 的比較留待後續論文（這是模型摘要層級的說法，需要對原文核實）。

**Tobar & Costa 2020，Reversible dynamics with closed time-like curves and freedom of choice（arXiv 2001.02511，CQG 37, 205011）[HTML/摘要+]。** 把確定性 CTC process 的刻畫推廣到任意 N 個區域，找到無法化約為三方的四方 process。同樣是古典、確定性，沒有機率重新加權。**注意：** arXiv 頁面的備註說 2512.23599（Dourdent 等人，2025 年 12 月）的反例影響 1703.00779 的刻畫定理（可能有勘誤）；我沒有讀該反例，也不知道影響範圍，所以 ROADMAP 階段 2「重現 Baumeler–Wolf 古典非因果例子」若要依賴刻畫定理，必須先查證。

**Araújo–Guérin–Baumeler 2017，Quantum computation with indefinite causal structures（arXiv 1706.09854，PRA 96, 052315）[摘要]。** 摘要稱 process matrix 對應 P-CTC 的一個線性特例，因此計算力以 PP 為上界。這是 process matrix 與 P-CTC 最直接的連結，也是專案階段 2 的第一手參考。

**Jean–Silva–Vilasini 2025，An equivalence between time-symmetry and cyclic causality in quantum theory（arXiv 2508.02463）[摘要]。** 證明「多時間態」（前後選擇）形式與 P-CTC 在操作上等價。這支持「P-CTC 可以當作後選擇的一種重述」，也暗示 P-CTC 是否為「真的迴圈」是詮釋問題。

**Arvidsson-Shukur 等人 2023，Nonclassical advantage in metrology established via quantum simulations of hypothetical closed timelike curves（arXiv 2207.07666，PRL 131, 150202）[摘要]。** 把 P-CTC 當作可用 teleportation 後選擇模擬的資源，展示計量學優勢。與 ROADMAP「不主張資訊回到過去」的立場一致：它只做模擬，不做時間旅行宣稱。

**其他。** Aaronson–Bavarian–Gueltrini，Computability theory of closed timelike curves（arXiv 1609.05507）[摘要層級，只在搜尋結果中提到] 指出 2008 年的工作限定多項式大小，結果是 PSPACE。

---

## 3. 可能的缺口（依優先順序）

排序標準：對專案現有程式的利用程度、能否在 1–2 個月內得到可檢驗的結果、以及「apparently open」的把握程度。**所有「沒找到」都只代表我在這次檢索範圍內沒找到**。

### 缺口 1：「動機寄件者」家族的閉式比較，以及一般定理 (b′)

- **為何可能空白**：(a) 已知；(b) 的「有動機才寄」是 (a) 加上機率與一個接收者，我沒有找到以此為主題的論文。文獻裡的 P-CTC/D-CTC 比較大多針對計算力、狀態辨別，而不是「概率情境下未來統計差多少」。
- **第一個結果會是什麼樣子**：一個命題：對古典可逆電路加古典隨機輸入，P-CTC 輸出分布等於把 P_0 對「存在不動點歷史」條件化（H2(2) 的精確版本）；D-CTC 輸出分布等於不動點通道。然後給出 (b) 的 q、r 全參數相圖，標出兩種規則差異最大的區域（含 P-CTC 無定義的邊界 qr=1）。附帶：與 Lloyd 的 ε 槍例子重現的數值對照（補完 ROADMAP 階段 1 的待辦）。
- **如何使用 `ctc/`**：直接用 `circuits.py` 的 KFK 與祖父悖論電路，擴成二參數掃描，在 `tests/` 加入對閉式的核對；新增一個「對 P_0 條件化」的獨立古典計算，與 `models.py` 的 P-CTC 實作互相檢查。

### 缺口 2：「自由選擇」作為 H2 的判準，連接 process matrix

- **為何可能空白**：process matrix 與 Baumeler 等人的確定性框架要求「對任意局部操作都自洽」，所以不需要重新歸一化，也就**沒有 H2 那種重新加權**；而 P-CTC 的重新加權正是代價：自洽事件的條件化會改變 CR 輸入本身的分布。Araújo 等人說 process matrix 是 P-CTC 的線性特例（摘要層級）。我沒有找到把「P_loop 是否改變 CR 輸入分布」當作區分「自由選擇保存」與「後選擇」的判準的論述。
- **第一個結果**：定義 freedom-of-choice 指標 Δ = 對 CR 輸入邊際分布的改變量（P_loop 對 P_0）。證明或數值顯示：Δ = 0 等價於 process 在所有輸入下自洽（無需歸一化）；Δ > 0 就是 P-CTC 的重新加權。在 (a)(b) 中算出 Δ，說明 H2 的效應其實**包含** CR 內部「選擇」被改寫，這與 KFK 場景中「剩下的唯一歷史是那人剛好選對」一致。
- **如何使用 `ctc/`**：在 `models.py` 的 P-CTC 輸出之外多回報「輸入邊際」；`circuits.py` 現有三個情境直接可算。階段 2 的 process matrix 重述會用到 `cvxpy`，這需要新增依賴。

### 缺口 3：區分 P-CTC 與 D-CTC 的可觀測量，並與 Lloyd/Ralph 的爭論對齊

- **為何可能空白**：(c) 與 Lloyd 的敘述方向一致，但 PRL 說 proof 位元「完全混合」，`ctc/` 說記錄相干，需要統一「測的是哪個系統、基準是什麼」；Ralph 與 Lloyd 的爭論（signalling to the past、unproved theorem）停在互相回覆，我沒找到後續的決定性分析。
- **第一個結果**：一張表：在 (c) 以及 Ralph 的糾纏構造中，對 {Z, X, 與參考系統的關聯} 這些觀測量，P-CTC、D-CTC、（缺口 5 的）T-CTC 各給什麼值；並明確指出哪些是「規則差異」、哪些是「基準選擇造成的」。`ctc/README` 已經提醒了後者。
- **如何使用 `ctc/`**：在 `circuits.py` 加入帶參考量子位元的 (c) 與 Ralph 構造（Lloyd 回覆說需補上 Bob 讀書的受控操作），用現有 P-CTC / D-CTC 求解器算出。

### 缺口 4：D-CTC 不動點選擇的敏感度

- **為何可能空白**：Deutsch 的最大熵規則是附加假設（Lloyd 等人 PRD [全文]）；Ralph 稱已被獨立導出（引文 [全文]，推導未讀）；專案用「Cesàro 平均從最大混合態出發」，不保證等於最大熵。我沒有找到系統比較各種選擇規則在非唯一不動點電路上的差異。
- **第一個結果**：找一個會讓「Cesàro 極限」與「最大熵不動點」不同的小電路（若存在），或證明在某類電路（如古典可逆）上兩者一致。這直接約束 `ctc/README` 那句「不保證一般情況都是如此」。
- **如何使用 `ctc/`**：在 `models.py` 加入顯式的不動點集合枚舉（解 `L[τ]=τ` 的零空間）與熵最大化，與現有 Cesàro 結果比對；`tests/` 已有不動點檢查可擴充。

### 缺口 5：把 T-CTC 加成第三個規則並重跑 (a)(b)(c)

- **為何可能空白**：Allen 的摘要稱 T-CTC 沒有悖論（無確定的矛盾）、不能完美辨別非正交態，Eq. (33) 顯示它是 P-CTC 與普通通道的混合。但我**沒有讀到** T-CTC 對祖父悖論或 KFK 型情境的數值，也沒找到後續工作使用它。ROADMAP 階段 1 的決策點明說可以「提出新的選擇規則」，T-CTC 是現成選項，專案可以檢驗它是否在 (b) 給出介於兩者之間的值。
- **第一個結果**：T-CTC 在 (a)(b)(c) 的數字（預期：(a) 的失敗機率介於 ε 與 1 之間，未驗證），並對 Allen 的計算做獨立檢查。
- **如何使用 `ctc/`**：在 `models.py` 加一個 `t_ctc` 函式（對迴圈純態積分或用 Eq. 33 的閉式）；其他程式不動。注意：Allen 的積分需要小心歸一化，`tests/` 用 Eq. 33 做解析比對。

### 缺口 6（風險較高、時間較長）：機率版的「自由選擇＋自洽」

- **為何可能空白**：Baumeler 等人與 Tobar–Costa 都是確定性的；Baumeler 等人自己寫量子化是否可行仍不清楚（[HTML/摘要+]）。機率性、非確定性的 process 與 P-CTC 的重新加權的關係，在我讀到的文獻裡沒有出現。
- **第一個結果**：一個小例子，顯示對古典機率 process，條件化到自洽集合後，是否仍能保持自由選擇；或給出反例。
- **注意**：2512.23599 對刻畫定理的反例可能影響起點，須先讀。

---

## 4. 參考文獻

只列出我實際看到編號或 DOI 的條目。「層級」見檔首。

| 條目 | 連結 | 層級 |
|---|---|---|
| Deutsch 1991, Phys. Rev. D 44, 3197 | https://doi.org/10.1103/PhysRevD.44.3197 | 只有書目資訊 |
| Lloyd et al. 2011, PRL 106, 040403 (arXiv:1005.2219) | https://arxiv.org/abs/1005.2219 ; https://doi.org/10.1103/PhysRevLett.106.040403 | 全文 |
| Lloyd et al. 2011, PRD 84, 025007 (arXiv:1007.2615) | https://arxiv.org/abs/1007.2615 ; https://doi.org/10.1103/PhysRevD.84.025007 | 全文（部分） |
| Lloyd et al. reply (arXiv:1108.0153) | https://arxiv.org/abs/1108.0153 | 摘要＋ar5iv 轉述 |
| Ralph comment (arXiv:1107.4675) | https://arxiv.org/abs/1107.4675 | 全文 |
| Svetlichny, Int. J. Theor. Phys. 50, 3903 (arXiv:0902.4898) | https://doi.org/10.1007/s10773-011-0973-x ; https://arxiv.org/abs/0902.4898 | 摘要 |
| Bennett & Schumacher 2005 talk | 無（透過 Svetlichny 的引用得知，未讀） | 未驗證內容 |
| Brun, Harrington, Wilde 2009 (arXiv:0811.1209) | https://arxiv.org/abs/0811.1209 | 摘要 |
| Bennett, Leung, Smith, Smolin 2009 (arXiv:0908.3023) | https://arxiv.org/abs/0908.3023 | 全文（部分） |
| Aaronson & Watrous 2009 (arXiv:0808.2669) | https://arxiv.org/abs/0808.2669 | 摘要＋目錄 |
| Brun & Wilde 2012 (arXiv:1008.0433) | https://arxiv.org/abs/1008.0433 ; https://doi.org/10.1007/s10701-011-9601-0 | 摘要＋標題 |
| Ralph & Myers 2010 (arXiv:1003.1987) | https://arxiv.org/abs/1003.1987 | 摘要 |
| Pienaar, Ralph, Myers 2013 (arXiv:1206.5485) | https://arxiv.org/abs/1206.5485 | 摘要 |
| Ringbauer et al. 2014 (arXiv:1501.05014) | https://arxiv.org/abs/1501.05014 ; https://doi.org/10.1038/ncomms5145 | 摘要 |
| Allen 2014 (arXiv:1401.4933) | https://arxiv.org/abs/1401.4933 | 全文（部分） |
| Bub & Stairs 2014 (arXiv:1309.4751) | https://arxiv.org/abs/1309.4751 | 摘要 |
| Dunlap 2015 (arXiv:1510.02742) | https://arxiv.org/abs/1510.02742 | 摘要 |
| Echeverria, Klinkhammer, Thorne 1991 | https://www.osti.gov/biblio/5219973 | 只有書目紀錄 |
| Politzer (hep-th/9207076); Hartle (gr-qc/9309012) | https://arxiv.org/abs/hep-th/9207076 ; https://arxiv.org/abs/gr-qc/9309012 | 摘要 |
| Oreshkov, Costa, Brukner 2012 (arXiv:1105.4464) | https://arxiv.org/abs/1105.4464 ; https://doi.org/10.1038/ncomms2076 | 摘要 |
| Araújo, Feix, Navascués, Brukner 2017 (arXiv:1611.08535) | https://arxiv.org/abs/1611.08535 ; https://doi.org/10.22331/q-2017-04-26-10 | 摘要 |
| Baumeler & Wolf 2014 (arXiv:1312.5916) | https://arxiv.org/abs/1312.5916 | 摘要 |
| Baumeler & Wolf, Computational tameness (arXiv:1611.05641) | https://arxiv.org/abs/1611.05641 | 摘要 |
| Baumeler, Feix, Wolf (arXiv:1403.7333) | https://arxiv.org/abs/1403.7333 | 只見於搜尋結果 |
| Baumeler et al. 2019 (arXiv:1703.00779) | https://arxiv.org/abs/1703.00779 | HTML/摘要+ |
| Tobar & Costa 2020 (arXiv:2001.02511) | https://arxiv.org/abs/2001.02511 ; https://doi.org/10.1088/1361-6382/aba4bc | HTML/摘要+ |
| Araújo, Guérin, Baumeler 2017 (arXiv:1706.09854) | https://arxiv.org/abs/1706.09854 | 摘要 |
| Dourdent et al. 2025 (arXiv:2512.23599) | https://arxiv.org/abs/2512.23599 | 摘要 |
| Jean, Silva, Vilasini 2025 (arXiv:2508.02463) | https://arxiv.org/abs/2508.02463 | 摘要 |
| Arvidsson-Shukur et al. 2023 (arXiv:2207.07666) | https://arxiv.org/abs/2207.07666 | 摘要 |
| Aaronson, Bavarian, Gueltrini (arXiv:1609.05507) | https://arxiv.org/abs/1609.05507 | 只見於搜尋結果 |

---

## 5. 限制

- **沒有讀全文的論文占多數**。只有 5 篇做了 PDF 文字抽取並讀相關段落，其中只有 Lloyd 等人 PRL 讀得比較完整；多數條目只讀了摘要或搜尋結果摘要。凡是表中「[摘要]」標記的內容，只能代表摘要所說，不能代表論文實際證明了什麼。
- **PDF 抓取失敗後的補救**：網頁抓取工具對 PDF 回傳壓縮串流，我改用本地 `pdftotext` 抽取。抽出的文字經過版面轉換，公式符號（如 ψ、ρ、†）有毀損，所以公式只能靠上下文，不應直接抄用。
- **沒有讀到或沒有核實的內容**：Deutsch 1991 原文、Novikov 原始論文、Bennett–Schumacher 演講、Aaronson–Watrous 對多不動點的處理、Ralph–Myers 的最大熵推導、Brun–Harrington–Wilde 全文、Brun–Wilde 的 PP 結論本身、Ralph 與 Lloyd 回覆之外的後續討論、Oreshkov–Costa–Brukner 與 Araújo 等人的內文（包括原始 process 是否可純化）、1403.7333 與 1507.01714 的具體內容。Hawking 的 chronology protection 與 Deutsch–Lockwood 的科普文，我沒有找到一手來源，不予引用。
- **「apparently open」不等於「沒人做過」**。判斷基於這次的有限搜尋（約 20 次搜尋、約 10 篇 PDF 的文字抽取），沒有掃過引用這些論文的所有後續工作，也沒有查會議論文與博士論文。在缺口 1–6 開工前，應該先對各缺口做一次針對性的引用追蹤。
- **兩處自己的推導未經核對**：H3 的 Tr[W]=0 角落案例，以及缺口 2 的 Δ 指標。兩者都只是由 HYPOTHESIS.md 的公式直接推出的想法，不是文獻結果。
- **沒有重跑 `ctc/`**，也沒有核對 `ctc/README` 的數字；表中 (a)(b)(c) 的數字都引自該 README。
- **工作方式**：本次檢索使用網路搜尋與網頁抓取，並用了子代理協助抓取頁面；子代理的報告我只當作資料看待，其中的內容在寫入前已與我自己讀到的 PDF 文字交叉核對（Lloyd、Ralph、Allen、BLSS）；其餘（如 2508.02463、2512.23599、1108.0153 的細節）僅憑子代理轉述的摘要，未獨立核對。
- **AI 輔助揭露**：本檔由 Claude（Sonnet 5.5）撰寫，沒有外部審查。未經人工核對原文之前，請不要把表中任何一格當成已驗證的文獻事實。
- 本檔不主張資訊能傳回過去；所有討論都是關於數學模型的行為。
