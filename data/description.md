## Last Memorysについて
- Geek_Verseをメインとしたブロックチェーンゲームである。
- ゲームアプリにログインし、かつゲーム内で一定条件満たした場合のみ一日一回Geekトークンのエアドロップがもらえる(メソッドはxgeekToGeek)
- メソッドexportTokenによりゲーム内通貨をGeekに変換出来る。

## Geekトークンについての説明
- GeekトークンはERC20準拠である。
- GeekトークンはOASYS_Verseでmintされる。
- Geek_verseにあるGeekトークンはOASYS_Verseからbridgeされてきたもののみ。

## ウォレットについての説明
- Geek_Verseで一度でもexportToken,exportAdpメソッドにより転送先になった、またはxgeekToGeekメソッドにより送信元となったアドレスは、ゲームアプリと連携されたウォレット(ゲーム内ウォレット)である。
- トークンの流れについての説明により、取引所のGeekプールアドレス(0x1AB4973a48dc892Cd9971ECE8e01DcC7688f8F23,0x0D0707963952f2fBA59dD06f2b425ace40b492Fe)へ転送したアドレスは取引所への入金アドレスである。


## トークンの流れについての説明
- 取引所の入金アドレスに送金すると、その後時間をおいて各取引所のGeekプールアドレスへ自動的に転送される(bitget:0x1AB4973a48dc892Cd9971ECE8e01DcC7688f8F23,gate.io:0x0D0707963952f2fBA59dD06f2b425ace40b492Fe)

## address.jsonについて
- address.jsonはGeek_Verse, Oasys_Verse両方のアドレスで現在著者が把握している内容を書き記してある。
- アドレスはEOAでありGeek_Verse, Oasys_Verse共通である。

## method.jsonについて
- Geek_verse, Oasys_Verseのトランザクション履歴に使われているmethod一覧である。
- Geek_Verse, Oasys_Verseでわけて記載してある。
- どんなコントラクトのメソッドかは記載していない。
