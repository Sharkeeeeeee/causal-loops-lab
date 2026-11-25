# An invitation to anyone who can send information into the past

**DRAFT, not published.** Protocol `cll-future-reply-v1`. Rules and checker: [README.md](README.md), [reply.py](reply.py).

---

## English

If you can send information to an earlier time, please send us the hash of any Bitcoin block **before that block is mined**.

Nobody can know a block hash in advance. A message that is anchored in the Bitcoin blockchain at least 6 blocks before the block whose hash it contains could only have come from the future. One such message is enough.

**How to reply (either way works):**

1. **A Bitcoin transaction** with an OP_RETURN output whose data is the 37 bytes
   `434c4c4601` followed by the 32-byte block hash, as it is usually displayed.
   Anyone can find it in the blockchain, at any later time.
2. **A text file**, stamped with OpenTimestamps (https://opentimestamps.org), containing the line
   `CLL-FUTURE-REPLY-v1 hash=<64 hex digits of the block hash>`
   and made public together with its `.ots` proof (for example as an issue on github.com/Sharkeeeeeee/causal-loops-lab).

**When:** if you can choose, please anchor your reply within about one day of this invitation: in one of the blocks P, P + 1, …, P + 144, naming a block no later than P + 150, where P is the block in which this invitation is first timestamped (its OpenTimestamps proof shows P). The block you name must still be at least 6 blocks after your reply's block. A reply at any other time, earlier or later, counts just as much.

You may add any text you like. We ask for nothing else: no predictions, no warnings, nothing that could harm anyone. The block hash alone proves the message came from the future.

We know that a time machine may not be able to reach times before it was built. That is one possible reason why no reply may arrive; others are that no such machine is ever built, or that nobody chooses to reply. Whatever happens, we will record it as it is.

---

## 中文

如果你能把資訊送回過去，請把**任何一個比特幣區塊的雜湊值**，在那個區塊被挖出來**之前**送給我們。

沒有人能事先知道區塊的雜湊值。一則訊息只要被記錄在比特幣區塊鏈上，而且比它所寫的那個區塊早至少 6 個區塊，就只可能來自未來。只要一則就夠了。

**回覆方式（任選一種）：**

1. **一筆比特幣交易**，其中一個 OP_RETURN 輸出的資料是 37 個位元組：
   `434c4c4601`，後面接 32 位元組的區塊雜湊值（一般顯示的順序）。
   任何人在任何時候都能在區塊鏈上找到它。
2. **一個文字檔**，用 OpenTimestamps（https://opentimestamps.org）蓋上時間戳，內容包含這一行：
   `CLL-FUTURE-REPLY-v1 hash=<區塊雜湊值的 64 個十六進位數字>`
   並連同它的 `.ots` 證明檔一起公開出來（例如在 github.com/Sharkeeeeeee/causal-loops-lab 開一個 issue）。

**時間：** 如果你可以選，請讓回覆錨定在這份邀請發布後大約一天內，也就是第 P、P + 1、…、P + 144 個區塊之中，而且你寫的區塊不要晚於第 P + 150 個。P 是這份邀請第一次被蓋上時間戳的區塊，它的 OpenTimestamps 證明裡寫著 P。你寫的那個區塊，仍然要比你的回覆所在的區塊晚至少 6 個區塊。在其他時間送達的回覆，不論更早或更晚，一樣算數。

你可以附上任何文字。我們不要求其他東西：不要預言、不要警告、不要任何可能傷害別人的內容。光是區塊雜湊值，就足以證明訊息來自未來。

我們知道，時光機可能無法把訊息送回它建造之前的時間。如果一直沒有回覆，這是可能的原因之一；也可能是這種機器從來沒有被造出來，或是沒有人選擇回覆。不論結果如何，我們都會照實記錄。
