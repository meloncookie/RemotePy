# RemotePy

[ [English] ](https://github.com/meloncookie/RemotePy/blob/master/README.md) , 
[ [Japanese] ](https://github.com/meloncookie/RemotePy/blob/master/README_jp.md)

micropython 版の、赤外線リモコン送受信ライブラリです。

Arduino 版には、便利なライブラリ
[IRremote](https://github.com/Arduino-IRremote/Arduino-IRremote)
があります。しかし C/C++ 言語の壁に挫折されている方も多いでしょう。
より手軽な micropython で、必要最小限の機能を実現したライブラリです。

扇風機、テレビ、果てはデータ長の長いエアコンまで、メーカに依存せず、
安定して動作します。

マイコンは ESP32チップ と RP2040チップ(Raspberry Pi Pico)のみ対応しています。
本家 [micropython](https://micropython.org/) 上で動作します。
対応バージョンは v1.17以上です。

送信側の処理は、ボード固有の実験的 micropython API を使用しています。
将来仕様の変更に伴い、動作しなくなるリスクがあります。
(2022/5 現在 v1.18 までは動作確認しております。)

すぐに使えるように、サンプルプログラムも用意しています。PC側の
GUI アプリケーションソフトで、赤外線リモコンデータ収集/送信を、
試すことができます。

---

## 同梱ファイル

1. ESP32用の micropython ファームウェア
    - micropython v1.17以降
        + micropython/ESP32/FromV1_17/UpyIrRx.py
        + micropython/ESP32/FromV1_17/UpyIrTx.py

2. RP2040 (Raspberry Pi Pico) 用の micropython ファームウェア
    - micropython v1.17以降
        + micropython/RP2040/FromV1_17/UpyIrRx.py
        + micropython/RP2040/FromV1_17/UpyIrTx.py

3. デモ用の micropython メインファームウェア
    + demo/micropython/main.py

4. デモ用の PC 側 python アプリケーションソフト
    + demo/GUI/main.py

---

## マイコンボード側のプログラム手順

* 本家 [micropython](https://micropython.org/) から、
  マイコンボードに応じたファームウェアをダウンロードします。
* マイコンボードに micropython ファームウェアを書込みます。
* マイコンボードに応じた UpyIrRx.py / UpyIrTx.py を、
  マイコンボードに書込みます。
* これら2つのライブラリ UpyIrRx.py / UpyIrTx.py を使って、
  メインプログラムを記述します。赤外線送信は UpyIrTx.py を、
  赤外線受信は UpyIrRx.py を用います。
* マイコンボードとは別に、赤外線送受信する外付け基板を用意します。

---

## 外付け赤外線リモコン送受信回路

![TxRx](https://user-images.githubusercontent.com/70054769/170876136-5e2e392d-b7ca-4790-94bf-7cceee272171.jpg)

### *送信回路*

適切な波長(波長950nm前後) の赤外線LEDを、マイコンで
電流オンオフ制御します。下記の回路が、良く使われます。
TxPin をマイコンのピンに接続します。

信号のオン区間は 38kHz, Duty比 1/3 のPWM波が使われます。
信号のオフ区間は LED 消灯しています。よって、送信側には以下の3つの
パラメータがあります。これは、赤外線送信ライブラリ UpyIrTx.py の
コンストラクタ引数で明示します。(但し、RP2040 チップの場合は、
UpyIrTx.py を直接修正する必要があります。)

1. 信号変調周波数 (通常 38kHz)
2. 信号オン区間Duty比 (通常 30%)
3. 信号オフ区間の、マイコンGPIO出力レベル idle_level (上記回路では Low = 0)

![TX_Circuit](https://user-images.githubusercontent.com/70054769/170875035-52dca65b-af3c-4995-b8ad-72cde2b86a7e.png)

### *受信回路*

赤外線リモコン受光モジュールを使います。受光モジュールの出力 RxPin を
マイコンのピンに接続します。受光モジュールによっては、オープンコレクタ
出力の場合があり、その場合はプルアップ抵抗を取り付けます。

受信側には以下の1つのパラメータがあります。これは、赤外線送信ライブラリ
UpyIrRx.py のコンストラクタ引数で明示します。

*  受光無い場合の、赤外線リモコン受光モジュールの出力レベル idle_level
   (一般的なモジュールでは High = 1)

![RX_Circuit](https://user-images.githubusercontent.com/70054769/170875122-8a23d50c-663a-4415-909a-6cc82f63d144.png)

### *便利なモジュール*

個別部品で回路を組むのが大変な場合、出来合いのモジュールを購入すると
良いでしょう。Grove コネクタで接続できる
[IR REMOTE UNIT](https://docs.m5stack.com/en/unit/ir)
は、大変便利です。M5Stack と組み合わせて、数m の距離まで
赤外線信号が届きます。

![M5Stack](https://user-images.githubusercontent.com/70054769/170875733-371c58ea-0572-4239-bfab-3c58ea8ff3b9.jpg)

---

## 赤外線リモコン受信ライブラリ UpyIrRx.py (UpyIrRxクラス) の使い方

UpyIrRx クラスが、受信処理を司ります。赤外線リモコン受光モジュールの出力電圧は、以下の様に
デジタル信号です。このデジタル信号の時間長を、リスト形式で記録します。この記録データは
、下記赤外線リモコン送信ライブラリで使えます。

赤外線リモコン受光モジュールの出力レベルは、無受光時に High (=1) が一般的です(idle_levelと呼称)。
この出力が Low に切り替わった時点で、リモコン信号受信開始とします。

出力レベルが、一定時間以上(blank_time [msec]) 変化しなかったら、リモコン信号の終端と
みなして、受信データを確定します。

```
    __         ____       _________       ___________________ idle_level = 1 の場合の図
      |_______|    |_____|         |_____|
    start                                 <- blank time -> ここでリモコン信号終端と見なす
      <- t0 ->< t1 >< t2 ><-- t3 -->< t4 > ...   [usec]

    波形データリスト = [t0, t1, t2, t3, t4]  (単位は usec、要素数は奇数)
```

1. `__init__(pin, max_size=0, idle_level=1)`
    + パラメータ
        - pin

            受信信号の入力となるピンのピンオブジェクト (machine.Pin オブジェクト) です。           
            上記回路図の RxPin に接続されるマイコンピンに相当します。

        - max_size: int

            受信信号を保存出来る最大長 (デフォルト値 0 だと 1023データ長)

        - idle_level: int

            受光無い場合の、赤外線リモコン受光モジュールの出力レベル 0/1 (デフォルト1 で High)

2. `record(wait_ms=0, blank_ms=0, stop_size=0) -> int`

    wait_ms[msec] 時間だけブロッキングして、リモコン受信信号データを内部変数に記録します。
    本メソッドを呼び出すと、前の記録済データは破棄され、新しく記録されたデータで内部変数に
    上書きされます。正常に受信できなかった場合は、無効な記録データになります。
    正常に記録されたかどうかは、戻り値で判断します。

    + パラメータ
        - wait_ms: int

            リモコン受信信号を待ち受ける時間 [msec] です。この時間だけ、処理がブロッキングされます。
            デフォルト値 0 の場合、5000[msec] になります。

        - blank_ms: int

            リモコン受信信号の静止区間が本時間 [msec] を超えた時点で、リモコン信号終端とみなします。
            デフォルト値 0 の場合、200[msec] になります。

        - stop_size: int

            リモコン受信信号長の制約個数で、この信号長を超過した部分は、記録除外されます。
            デフォルト値 0 の場合、制約を加えません。但し、コンストラクタの max_size 長
            を超えた場合は、オーバーフローエラーになります。
    
    + 戻り値
        - UpyIrRx.ERROR_NONE (=0) : 正常に記録完了の場合
        - UpyIrRx.ERROR_NO_DATA (=1) : wait_sec [msec] 内に有意な信号無い場合
        - UpyIrRx.ERROR_OVERFLOW (=2) : コンストラクタで指定した、最大受信信号長を超過した場合
        - UpyIrRx.ERROR_START_POINT (=3) : record() メソッドを呼び出し時点で、出力レベルが idle_level で無い場合
        - UpyIrRx.ERROR_END_POINT (=3) : 信号終端時の、出力レベルが idle_level で無い場合
        - UpyIrRx.ERROR_TIMEOUT (=4) : wait_sec [msec] 内に、リモコン信号が終端条件を満たしていない場合

3. `get_mode() -> int`

    リモコン信号受信状態を取得します。

    + 戻り値
        - UpyIrRx.MODE_STAND_BY (=0) : 未だ record() 呼び出されていない状態
        - UpyIrRx.MODE_DONE_OK (=1) : 前回 record() 呼び出しで、有意な記録済データを保有している状態
        - UpyIrRx.MODE_DONE_NG (=2) : 前回 record() 呼び出しで、何らかの異常が発生し、記録済データ
        が無効な状態

4. `get_record_size() -> int`

    内部変数に記録されたリモコン受信信号の信号長を取得します。下記の get_calibrate_list() で取得される
    波形データの要素数に相当します。

    + 戻り値
        - 波形データリストの要素数。

5. `get_calibrate_list() -> list`

    前回の record() メソッドにより内部に記録されたリモコン受信信号データを、波形データリストとして
    取得します。このリストは、リモコン信号送信時に利用されます。正常な記録データが無い場合は、
    空リストが取得されます。

    + 戻り値
        - int型で、要素数が奇数の1次元リスト。 正常な記録データが無い場合は、空リスト。
          本メソッドを呼び出しても、内部の記録データは破棄されず、そのまま保持されます。
         
          赤外線リモコン受光モジュールの遅延特性の影響を、除外する校正
          処理を行った波形データが取得されます。

          姉妹版メソッドに、get_record_list() があります。こちらは、非校正の生データが
          取得されるため、推奨しません。校正されていないリモコン信号
          を元に、送信すると誤認識する場合が多々発生します。

---

## 赤外線リモコン送信ライブラリ UpyIrTx.py (UpyIrTxクラス)  の使い方

UpyIrTx クラスが、送信処理を司ります。上記 UpyIrRx オブジェクトで取得される、
リモコン受信信号データを元に、赤外線リモコン信号を送信します。


* idle_level = 0 の場合
```
    LED OFF区間   _______      _____           _____  LED OFF区間
    _____________|       |____|     |_________|     |_________
```
* idle_level = 1 の場合
```
    _____________         ____       _________       _________
                 |_______|    |_____|         |_____|

                 <- t0 ->< t1 >< t2 ><-- t3 -->< t4 > ...   [usec]
                  ON 区間      ON 区間         ON 区間

    signal_tuple = (t0, t1, t2, t3, t4)
```

ON 区間は、PWM波形です。PWM周波数と、Duty比を指定出来ます。

1. `__init__(ch, pin, freq=38000, duty=30, idle_level=0))`
    + パラメータ
        - ch: int

            0-7 のチャンネル番号です。
            ESP32 では、RMTペリフェラルのチャンネル番号です。
            RP2040 では、PIOペリフェラルのステートマシン番号です。
            未使用の番号を指定します。他に使っていなければ 0 で良いでしょう。

        - pin

            送信信号の出力となるピンのピンオブジェクト (machine.Pin オブジェクト) です。            
            上記回路図の TxPin に接続されるマイコンピンに相当します。

        - freq: int ※1

            ON区間のPWM周波数 [Hz]。デフォルト値は 38000 [Hz]。

        - duty: int ※1

            ON区間のPWM波形のDuty比 1-100 [%]。デフォルト値は 30 [%]

        - idle_level: int ※1

            赤外線LEDがOFFに相当する、論理レベル 0/1 (デフォルト0 で Low)。
            上記の一般的送信回路例では、Low になります。

    ※1: RP2040 チップの場合、本引数は無効となる。変更したい場合は、ソースコード UpyIrTx.py
    の以下の定数を変更します。

    ```python
    def pio_wave():
        T = const(26)      # Period: 1/38kHz*1M [us] (= OF_TIM + ON_TIM)
        OF_TIM = const(18) # Duty(30%) off time [us]
        OF_POR = const(0)  # Idle level
        ON_TIM = const(8)  # Duty(30%) on time [us]
        ON_POR = const(1)  # not Idle level
    ```

2. `send(signal_tuple: tuple) -> bool`

    引数の時間リストに従って、送信信号を出力します。送信完了までブロッキングされます。

    + パラメータ
        - signal_tuple: tuple or list

            時間情報のタプル又はリストを指定。上記 UpyIrRx オブジェクトで取得される
            リモコン受信信号データを利用します。要素数は奇数に限ります。

    + 戻り値
        - 送信の成否を bool型で返します。

---

## プログラム事例

ESP32 内蔵の [M5Stack ATOM](https://docs.m5stack.com/en/core/atom_matrix) と、
[IR REMOTE UNIT](https://docs.m5stack.com/en/unit/ir) を Grove コネクタで接続した
場合のプログラム事例です。
[M5Stack ATOM](https://docs.m5stack.com/en/core/atom_matrix)
本体には、赤外線送信回路が入っていますが、極短い距離しか飛ばないため
実用的ではありません。

```python
from machine import Pin
from UpyIrTx import UpyIrTx
from UpyIrRx import UpyIrRx

rx_pin = Pin(32, Pin.IN)   # Pin No.32
rx = UpyIrRx(rx_pin)

tx_pin = Pin(26, Pin.OUT)  # Pin No.26
tx = UpyIrTx(0, tx_pin)    # 0ch
...
# 3000msec 以内に、受信回路に向けてリモコン送信すると、リモコン信号取得される。
rx.record(3000)
if rx.get_mode() == UpyIrRx.MODE_DONE_OK:
    signal_list = rx.get_calibrate_list()
    # ex) [430, 1290, 430, 430, 430, 860, ...]
else:
    signal_list = []
...
# 送信回路から、リモコン信号を送信する。送信完了までブロッキング。
if signal_list:
    tx.send(signal_list)
...
```

---

## デモアプリケーション

付属のデモアプリケーションでは、PC側アプリケーションソフトと併せて、
簡単に赤外線リモコンの信号収集と、送信テストが出来ます。

* REPL環境と同じコマンド通信路を使用
* GUI画面で直感的な操作性
* 赤外線リモコン信号を記録し json ファイル化
* 新規または、既存 jsonファイルを呼び出して編集可能
* その場で記録信号を送信しテスト可能

### *マイコン側準備*

デモプログラムでは、[M5Stack ATOM](https://docs.m5stack.com/en/core/atom_matrix) と、
[IR REMOTE UNIT](https://docs.m5stack.com/en/unit/ir) を Grove コネクタで接続した
システムに準拠しています。マイコンに、"main.py", "UpyIrRx.py", "UpyIrTx.py" の
3つのファイルを書込みます。REPL環境下と同じく、PC側と M5Stack 間を、USBケーブルで
接続します。

他のシステムを利用する場合は、ソースコードの以下のピン配置を書き換えます。

**main.py の修正箇所**
```python
_GROVE_PIN = {'ATOM':  (32, 26),
              'CORE2': (33, 32),
              'BASIC': (22, 21),
              'GRAY':  (22, 21),
              'FIRE':  (22, 21),
              'GO':    (22, 21),
              'Stick': (33, 32),
              'Else':  (32, 12)}  # (RxPin番号, TxPin番号) に書換え
_DEVICE = 'ATOM'                  # 'Else' に書換え
_TX_IDLE_LEVEL = const(0)         # 送信側の idle_level(RP2040使用時は無効)
_TX_FREQ = const(38000)           # 送信側 ON区間の変調周波数(RP2040使用時は無効)
_TX_DUTY = const(30)              # 送信側 ON区間のDuty比(RP2040使用時は無効)
_RX_IDLE_LEVEL = const(1)         # 受信側の idle_level
```

### *PC側準備*

PC側のアプリケーションは python で書かれています。windows, Ubuntu, Raspbian OS で動作確認済です。
GUIフレームワーク Tkinter を用いています。

![gui](https://user-images.githubusercontent.com/70054769/172902379-3fce461f-63b1-4cf4-a9a1-cd01fe665a29.png)

1. python 3.8 以上をインストールします。

2. シリアル通信ライブラリ [pySerial](https://pythonhosted.org/pyserial/) をインストールします。

   `$ pip install pyserial`

3. pythonプログラムは6つのファイルから構成されています。そのうち communication.py の以下の箇所を
   、システムに応じて修正します。マイコン側 USBデバイスの、ベンダID(VID) とプロダクトID(PID) を
   指定します。サンプルプログラムは、M5Stack ATOM の事例です。これらの ID は PC から
   容易に調べることが出来ます。

   ```python
   class Communication():
        _DEFAULT_VID = 1027
        _DEFAULT_PID = 24577
    ```

    | Type | VID | PID |
    | :--- | ---: | ---: |
    | M5Stack ATOM | 1027 | 24577 |
    | M5Stack Core2 | 4292 | 60000 |
    | Raspberry Pi Pico | 11914 | 5 |
    | | | |

4. プログラムの起動は `$ python main.py` です。

### *PC側アプリケーションソフトの使い方*

1. 既存のセーブファイル名又は、新規セーブファイル名を **File** 欄に記入します。
    * **Select** ボタンから、ファイルエクスプローラ風に選択することも出来ます。
2. **Open** ボタンを押して編集を開始します。
    * この時点では **Save** ボタンは無効です。何らかの編集をしたら有効になります。
      セーブしてからファイルをクローズする場合に押します。
    * 一方 **Close** ボタンは常に有効です。セーブをせずにファイルをクローズする
      場合に押します。
3. **Key list** は、自分で命名したリモコン信号のキー名です。(例えば、テレビの音量大 = "vol_up")
    * 必ず `__sysytem__` キーが唯一存在しています。ファイルのコメント用に使うと良いでしょう。
    * 一つのキーは、リモコン信号と、コメントから構成されています。
4. **Key_list** に新しいリモコン信号のキー名を追加するには、**Edit key** 欄に記入してから、
   **Append** ボタンを押します。
5. **Key_list** のリモコン信号のキー名を削除するには、消したい **Key_list** を選択してから、
   **Delete** ボタンを押します。
6. **Key_list** のリモコン信号のキー名を変名するには、変名したい **Key_list** を選択して、
   **Edit key** 欄に記入して、**Rename** ボタンを押します。
7. **Key_list** にあるリモコン信号のキー名を選択して、**Record** ボタンを押すと、そのキー名のリモコン信号
   を記録します。ボタン押した後 Wait [sec] 以内に、赤外線リモコン受信モジュールに向けて、
   リモコン信号を送信します。
    * **Signal** 欄に波形データが表示されます。
    * **Comment** 欄に自由にコメントを記録できます。信号の意味(例えば、"volume up") を記述する
      と良いでしょう。
    * 変更された場合は背景が赤になります。
    * **Commit** ボタンを押して確定します。**Cancel** すると元に戻ります。
    * **Commit** ボタンを押さずに、**key_list** の別のキー名を選択すると **Cancel** とみなします。
    * このため、編集したら(= 背景が赤になる) すぐに **Commit** ボタンを押すと良いでしょう。**Commit** すると、
      編集箇所の背景は緑に戻ります。
8. **Send** ボタンを押すと、現在 **Signal** 欄のリモコン信号が送信されます。
9. 手順3-8の編集が全て終わったら、**Save** 又は **Close** ボタンでファイルをクローズします。
    * 編集内容をセーブして終了するには、**Save** ボタンです。
    * これまでの編集内容を全部破棄して終了するには、**Close** ボタンです。

### *生成される json ファイル*

json形式のテキストファイルです。辞書形式で、キーはリモコン信号のキー名です。バリューは
辞書形式です。
バリューの辞書形式は、"signal" と "comment" の2つキーから構成されています。
サンプルを下記に例示します。

```json
{"vol_up": {"signal": [430, 1290, 430, ...], "comment": "volume up"},
 "ch1":    {"signal": [430, 1290, 860, ...], "comment": "CH 1"},
 ...
}
```

---

## あとがき

処理速度の限界で、micropython を使ったリモコン信号送受信は、
意外と大変でした。特に、送信信号の生成は、sleep 処理を使った
波形生成では、ジッタが酷過ぎて実用に耐えません。

本ライブラリは、ESP32, RP2040 のチップ限定ですが、ボード固有
機能を使うことで克服しました。micropython の利便性を考えると、
ここまで苦労してでも、ライブラリ化した価値はあります。

WIFIと組み合わせて Home IoT にしても良いでしょう。タイマー処理
による、空調の自動化システムも実用的です。本ライブラリを活用して、
楽しい電子工作ライフを!
