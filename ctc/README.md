# 階段 1：CTC 玩具模型

建立日期：2026-11-22，撰寫時使用 AI 輔助（Claude）。全部都是小型精確數值計算，沒有硬體執行，也沒有外部審查。這些模型描述的是「如果存在時間迴圈，世界會怎麼運作」，**不是資訊能回到過去的證據**。這些檔案不在 `PUBLIC_MANIFEST.json` 裡。

```text
python -B ctc/tests/test_models.py      # 10 項測試，對照手算的解析結果
python -B ctc/tests/test_literature.py  # 11 項測試，重現 Lloyd 2011 和 Brun–Harrington–Wilde 2009
python -B ctc/run_toy.py                # 產生 output/ 底下的 CSV、JSON 和圖
python -B ctc/reproduce_literature.py   # 產生文獻重現的 JSON 和圖
python -B ctc/tests/test_branches.py    # 8 項測試，κ–β 分支模型
python -B ctc/run_branches.py           # 產生 κ–β 平面的 CSV 和圖
python -B ctc/tests/test_quantum_effects.py  # 7 項測試，自洽歷史之間的量子干涉
python -B ctc/tests/test_signalling.py  # 11 項測試，無訊號條件
python -B ctc/run_signalling.py         # 產生無訊號測試的 JSON 和圖
```

只有量子版本才有的效應見 [QUANTUM_EFFECTS.md](QUANTUM_EFFECTS.md)。無訊號測試的結果見 [NO_SIGNALLING.md](NO_SIGNALLING.md)。

文獻重現的結果見 [LITERATURE_REPRODUCTION.md](LITERATURE_REPRODUCTION.md)。把 P-CTC 和 D-CTC 放進同一個雙參數模型的結果見 [BRANCHES.md](BRANCHES.md)。

需要 NumPy，畫圖需要 matplotlib。這裡用 Python 3.11.0、NumPy 2.3.2、matplotlib 3.10.0 執行過。

## 檔案

| 檔案 | 內容 |
|---|---|
| `models.py` | 三種規則：無迴圈、P-CTC（Lloyd 等人 2011）、D-CTC（Deutsch 1991）；另外有直接模擬後選擇 teleportation 的檢查 |
| `circuits.py` | 三個情境：祖父悖論、KFK 型提醒、自舉悖論；另外有兩個只有量子版本才有效應的電路：受控相位干涉、只帶相位的迴圈 |
| `literature.py` | 從論文圖中讀出的電路：Lloyd 2011 Fig. 2、Brun–Harrington–Wilde 2009 Fig. 1–2 |
| `branches.py` | 古典的「有權重分支」模型：κ（訊息從哪裡來）和 β（自洽篩選強度），P-CTC 和 D-CTC 是其中兩個角落 |
| `tests/test_branches.py` | 角落等於量子 P-CTC 和 D-CTC、β = 0 時不重新加權、閉式解 |
| `tests/test_quantum_effects.py` | 自洽歷史互相干涉時 P-CTC 會刪掉分支；古典模型拒絕帶相位的電路 |
| `signalling.py` | 加上遠方的 Bob，檢查 Alice ↔ Bob 兩個方向能不能傳訊 |
| `tests/test_signalling.py` | 各規則的傳訊量、P-CTC 的 C†C 判準、D-CTC 兩種套用方式 |
| `run_signalling.py` | 傳訊量總表與 κ–β 平面上的傳訊圖 |
| `run_branches.py` | κ–β 平面的掃描與畫圖 |
| `tests/test_models.py` | 么正性、不動點、與解析公式的比對 |
| `tests/test_literature.py` | 逐條重現論文中的說法 |
| `run_toy.py` | 參數掃描與畫圖 |
| `reproduce_literature.py` | 文獻重現的數值與圖 |
| `output/toy_results.csv` | 圖中所有數值，可以當表格查看 |
| `output/bootstrap.json` | 自舉悖論的結果 |

D-CTC 的不動點如果不只一個，這裡選「從最大混合態出發的 Cesàro 極限」。在這些情境中，它就是熵最大的不動點，但不保證一般情況都是如此。

## 結果

![toy figure](output/toy_figure.png)

### (a) 祖父悖論
收到一個位元，打算送回它的相反值，但這個動作有 ε 的機率失敗。

| 規則 | P(動作失敗) | 自洽是怎麼達成的 |
|---|---|---|
| 無迴圈 | ε | 不需要自洽 |
| P-CTC | **1**，不管 ε 多小 | 只有「動作失敗」的歷史是自洽的。ε = 0 時沒有任何自洽歷史，規則沒有定義 |
| D-CTC | ε | 迴圈中的訊息變成 50/50 的混合態，未來的統計沒有改變 |

**對假設的意義：** H2「效應出現在未來」在 P-CTC 下成立，而且效應很強；在 D-CTC 下，這個情境完全不成立。所以兩種時間觀的差別不只是哲學問題，它們會給出不同的預測。

### (b) KFK 型提醒
有一個人，沒有提醒時會以 q = 0.3 的機率做出壞選擇。提醒有 r 的機率生效。

| 寄件者 | 規則 | P(壞結果) |
|---|---|---|
| 沒有訊息（基準） | — | q |
| 無條件寄出（一定會提醒） | P-CTC 和 D-CTC 相同 | q(1 − r) |
| 有動機才寄（壞結果發生了才寄） | P-CTC | q(1 − r) / (1 − qr) |
| 有動機才寄 | D-CTC | q / (1 + qr) |

觀察：

1. **無條件寄出**，也就是 KFK 自稱的「我來只是為了提醒」：兩種規則一致，沒有悖論，也沒有重新加權。從收到訊息的人的角度看，這跟一則普通的訊息完全一樣，所以**只看收件者這邊，無法分辨訊息是不是來自未來**。
2. **有動機才寄**，屬於祖父悖論的一種：提醒成功就沒有理由寄出提醒。
   - 在 P-CTC 下，r = 1 時壞結果的機率變成 0。但原因不是提醒成功了：剩下的唯一自洽歷史，是「沒有收到提醒，而這個人剛好自己選對了」。未來確實改變了，但改變它的是自洽篩選，不是訊息本身。
   - 在 D-CTC 下，效應溫和得多：r = 1 時是 0.3 / 1.3 ≈ 0.23。
3. 在 P-CTC 下，q = 1、r = 1 時沒有任何自洽歷史，是真正的悖論。

### (c) 自舉悖論
一則沒有來源的訊息：它被記錄下來，再原封不動地送回去。

| 規則 | P(記錄 = 1) | 記錄的 ⟨X⟩ |
|---|---|---|
| 無迴圈（外部輸入未知的位元） | 0.5 | 0 |
| P-CTC | 0.5 | **1**（相干的疊加態） |
| D-CTC | 0.5 | 0（混合態） |

在一般的測量基底下，三種規則的統計一樣。但量 X 基底時，P-CTC 和 D-CTC 會給出不同的結果。這是一個可以區分兩種規則的觀測量。不過結果也取決於基準怎麼選：如果外部輸入是 |+⟩，無迴圈的情況也會得到 ⟨X⟩ = 1。

## 限制

- 所有情境都是一到五個位元的玩具電路，而且大多是古典可逆電路配上古典輸入。
- P-CTC 和 D-CTC 是文獻中已知的模型，結果 (a) 在概念上和 Lloyd 等人 2011 的討論一致。Lloyd 2011 和 Brun–Harrington–Wilde 2009 的具體說法已經逐條重現，見 [LITERATURE_REPRODUCTION.md](LITERATURE_REPRODUCTION.md)。
- 在一般的量子電腦上用後選擇模擬 P-CTC，會得到同樣的數字，但那只是模擬，不是證據。
- `p_ctc_weight` 欄位是未歸一化的 Tr[CρC†]。除以 d²（迴圈維度的平方）就是用 teleportation 實作時的後選擇成功機率，可以用 `models.p_ctc_success_probability` 計算。
