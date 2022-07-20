# RemotePy

[ [English] ](https://github.com/meloncookie/RemotePy/blob/master/README.md) , 
[ [Japanese] ](https://github.com/meloncookie/RemotePy/blob/master/README_jp.md)

This is an infrared remote control send / receive library by micropython.

Fans, TVs, and even air conditioners with long data lengths operate stably
regardless of the manufacturer.

The microcomputer supports only the ESP32 chip and the RP2040 chip (Raspberry Pi Pico).
It works on the original [micropython](https://micropython.org/).
The supported version is v1.17 or higher.

The send process uses a board-specific experimental micropython API.
There is a risk that it will not work due to changes in specifications in the future.
I have confirmed the operation up to v1.19.(2022/07)

A sample program is also available for immediate use.
You can try infrared remote control data acquisition /
transmission with GUI application software for PC.

---

## Bundled files

1. Micropython firmware for ESP32
    - After micropython v1.17
        + micropython/ESP32/FromV1_17/UpyIrRx.py
        + micropython/ESP32/FromV1_17/UpyIrTx.py

2. Micropython firmware for RP2040 (Raspberry Pi Pico)
    - After micropython v1.17
        + micropython/RP2040/FromV1_17/UpyIrRx.py
        + micropython/RP2040/FromV1_17/UpyIrTx.py

3. Demo micropython main firmware
    + For M5Stack ATOM(Lite & MATRIX) : demo/M5StackATOM/micropython/main.py
    + For RP2040 (Raspberry Pi Pico) : demo/RP2040/micropython/main.py

4. Demonstration PC side python application software
    + For M5Stack ATOM(Lite & MATRIX) : demo/M5StackATOM/GUI
    + For RP2040 (Raspberry Pi Pico) : demo/RP2040/GUI
---

## Program procedure on the microcomputer board side
* Download the firmware corresponding to the microcomputer board
  from the orginal [micropython](https://micropython.org/).
* Write the micropython firmware to the microcontroller board.
* Write UpyIrRx.py / UpyIrTx.py according to the microcomputer board.
* Use these two libraries UpyIrRx.py / UpyIrTx.py to write your main program.
  Use UpyIrTx.py for infrared transmission and UpyIrRx.py for infrared reception.
* Separately from the microcomputer board, prepare an external board
  for transmitting and receiving infrared remote control.

---

## External infrared remote control transmission / reception circuit

![TxRx](https://user-images.githubusercontent.com/70054769/170876136-5e2e392d-b7ca-4790-94bf-7cceee272171.jpg)

### *Transmission circuit*

Infrared LEDs with an appropriate wavelength (wavelength around 950 nm)
are controlled on and off with a microcomputer.
The following circuits are ofte
Connect the TxPin to the pins of the microcomputer.


For the on section of the signal, a PWM wave with 38kHz and a duty ratio of 1/3 is used.
The LED is off during the signal off section.
Therefore, the sender has the following three parameters.
This is specified in the constructor argument of the infrared transmission library UpyIrTx.py.
(However, in the case of the RP2040 chip, You need to modify UpyIrTx.py directly.)

1. Signal modulation frequency (usually 38kHz)
2. Signal-on section duty ratio (usually 30%)
3. Microcomputer GPIO output level in signal off section "idle_level".
   (Low = 0 in the above circuit)

![TX_Circuit](https://user-images.githubusercontent.com/70054769/170875035-52dca65b-af3c-4995-b8ad-72cde2b86a7e.png)

### *Receive circuit*

Use the infrared remote control light receiving module.
Connect the output RxPin of the light receiving module to the pin of the microcomputer.
Depending on the light receiving module, it may have an open collector output,
in which case a pull-up resistor is installed.

The receiver has the following one parameter.
This is specified in the constructor argument of the infrared transmission library UpyIrRx.py.

* Output level of infrared remote control light receiving module
  when there is no light receiving  "idle_level".
  (High = 1 for general modules)

![RX_Circuit](https://user-images.githubusercontent.com/70054769/170875122-8a23d50c-663a-4415-909a-6cc82f63d144.png)

### *Convenient commercial module*

If it is difficult to build a circuit with individual parts,
it is a good idea to purchase a ready-made module.
The [IR REMOTE UNIT](https://docs.m5stack.com/en/unit/ir),
which can be connected with the Grove connector, is very convenient.
In combination with M5Stack, infrared signals can reach distances of several meters.

![M5Stack](https://user-images.githubusercontent.com/70054769/170875733-371c58ea-0572-4239-bfab-3c58ea8ff3b9.jpg)

---

## How to use the infrared remote control reception library UpyIrRx.py (UpyIrRx class)

The UpyIrRx class controls the reception process.
The output voltage of the infrared remote control light receiving module
is a digital signal as shown below.
Record the time length of this digital signal in list format.
This recorded data can be used in the infrared remote control transmission library below.


The output level of the infrared remote control light receiving module is
generally High (= 1) when no light is received (called idle_level).
When this output switches to Low, remote control signal reception starts.
If the output level does not change for a certain period of time
(blank_time [msec]), it is regarded as the end of the remote control signal
and the received data is confirmed.

```
    __         ____       _________       ___________________ If idle_level = 1
      |_______|    |_____|         |_____|
    start                                 <- blank time -> End of signal
      <- t0 ->< t1 >< t2 ><-- t3 -->< t4 > ...   [usec]

    Waveform data list = [t0, t1, t2, t3, t4] 
    ( The unit is usec, and the number of elements is odd. )
```

1. `__init__(pin, max_size=0, idle_level=1)`
    + Parameters
        - pin

           It is a pin object (machine.Pin object) of the pin that is the input of
           the received signal.           
           It is a microcomputer pin connected to RxPin in the above circuit.

        - max_size: int

            Maximum length that can store the received signal
            (If the default value is 0, the data length is 1023.)

        - idle_level: int

            Output level of infrared remote control light receiving module
            when there is no light receiving 0/1 (High = 1 by default)

2. `record(wait_ms=0, blank_ms=0, stop_size=0) -> int`

    After waiting for wait_ms[msec], the remote control reception signal data is
    recorded in the internal variable.
    When this method is called, the previously recorded data will be discarded.
    The newly recorded data will be overwritten with internal variables.
    If it cannot be received normally, the recorded data will be invalid.
    Whether or not it was recorded normally is judged by the return value.

    + Parameters
        - wait_ms: int

            It is time [msec] to wait for the remote control reception signal.
            During this time, processing will be blocked.
            If the default value is 0, it will be 5000 [msec].

        - blank_ms: int

            When the stationary section of the remote control received signal exceeds
            this time [msec], it is considered to be the end of the remote control signal.
            If the default value is 0, it will be 200 [msec].

        - stop_size: int

            The part that exceeds this signal length is excluded from recording.
            If the default value is 0, no constraint is applied.
            However, if the max_size length of the constructor is exceeded,
            an overflow error will occur.
    
    + Return
        - UpyIrRx.ERROR_NONE (=0) : When recording is completed normally
        - UpyIrRx.ERROR_NO_DATA (=1) : If there is no significant signal in wait_ms time
        - UpyIrRx.ERROR_OVERFLOW (=2) : When the maximum received signal length specified
          in the constructor is exceeded
        - UpyIrRx.ERROR_START_POINT (=3) : If the output level is not idle_level at the
          time of calling the record () method
        - UpyIrRx.ERROR_END_POINT (=3) : When the output level is not idle_level
          at the end of the signal
        - UpyIrRx.ERROR_TIMEOUT (=4) : If the remote control signal does not meet the
          termination condition in wait_ms time

3. `get_mode() -> int`

    Acquires the remote control signal reception status.

    + Return
        - UpyIrRx.MODE_STAND_BY (=0) : record() has not been called yet
        - UpyIrRx.MODE_DONE_OK (=1) : A state in which normal recorded data is 
          retained in the previous call to record().
        - UpyIrRx.MODE_DONE_NG (=2) : The last call to record() caused some error
          and the recorded data is invalid.

4. `get_record_size() -> int`

    Acquires the signal length of the remote control reception signal recorded
    in the internal variable.
    It corresponds to the number of elements of the waveform data acquired by
    get_calibrate_list() below.

    + Return
        - The number of elements in the waveform data list.

5. `get_calibrate_list() -> list`

    Acquires the remote control received signal data recorded internally by
    the previous record() method.
    This list is used when sending remote control signals.
    If there is no normal recorded data, an empty list will be acquired.

    + Return
        - A one-dimensional list of int type with an odd number of elements.
          Empty list if there is no normal recorded data.
          Even if this method is called, the internal recorded data is not
          destroyed and is retained.
         
          Waveform data that has been calibrated to exclude the influence of the delay
          characteristics of the infrared remote control light receiving module is acquired.

          A sister version of the method is get_record_list().
          This is not recommended as it will capture uncalibrated raw data.
          Sending uncalibrated remote control signals is often misidentified.

---

## How to use the infrared remote control transmission library UpyIrTx.py (UpyIrTx class)

The UpyIrTx class is responsible for the send process.
The infrared remote control signal is transmitted based on the remote control
reception signal data acquired by the above UpyIrRx object.

* If idle_level = 0
```
    LED OFF time  _______      _____           _____  LED OFF time
    _____________|       |____|     |_________|     |_________
```
* If idle_level = 1
```
    _____________         ____       _________       _________
                 |_______|    |_____|         |_____|

                 <- t0 ->< t1 >< t2 ><-- t3 -->< t4 > ...   [usec]
                  ON time      ON time         ON time

    signal_tuple = (t0, t1, t2, t3, t4)
```

The ON section is the PWM waveform. You can specify the PWM frequency and duty ratio.

1. `__init__(ch, pin, freq=38000, duty=30, idle_level=0))`
    + Parameters
        - ch: int

            The channel number is 0-7.
            On the ESP32, this is the RMT peripheral channel number.
            On the RP2040, this is the state machine number of the PIO peripheral.
            Specify an unused number. If you haven't used it elsewhere, 0 is fine.

        - pin

            A pin object (machine.Pin object) for the pin that outputs the transmitted signal.
            It is a microcomputer pin connected to TxPin in the above circuit.

        - freq: int *1

            PWM frequency [Hz] in the ON section.
            The default value is 38000 [Hz].

        - duty: int *1

            Duty ratio of PWM waveform in ON section 1-100 [%].
            The default value is 30 [%].

        - idle_level: int *1

            Logic level corresponding to infrared LED OFF 0/1 (Low with default 0)。
            In the general transmission circuit example above, it will be Low (=0).

    *1: In the case of RP2040 chip, this argument is invalid.
    If you want to change it, change the following constants in the source code UpyIrTx.py.

    ```python
    def pio_wave():
        T = const(26)      # Period: 1/38kHz*1M [us] (= OF_TIM + ON_TIM)
        OF_TIM = const(18) # Duty(30%) off time [us]
        OF_POR = const(0)  # Idle level
        ON_TIM = const(8)  # Duty(30%) on time [us]
        ON_POR = const(1)  # not Idle level
    ```

2. `send(signal_tuple: tuple) -> bool`

    The transmission signal is output according to the time list of the argument.
    It will be blocked until the transmission is completed.

    + Parameters
        - signal_tuple: tuple or list

            Specify a tuple or list of time information.
            Use the remote control received signal data acquired by the above UpyIrRx object.
            The number of elements is limited to odd numbers.

    + Return
        - Returns the success or failure of the transmission as a bool type.

---

## Program example

This is a program example when [M5Stack ATOM](https://docs.m5stack.com/en/core/atom_matrix)
and [IR REMOTE UNIT](https://docs.m5stack.com/en/unit/ir) are connected
with a Grove connector.
Although the [M5Stack ATOM](https://docs.m5stack.com/en/core/atom_matrix)
main unit contains an infrared transmission circuit,
it is not practical because it can fly only a very short distance.

```python
from machine import Pin
from UpyIrTx import UpyIrTx
from UpyIrRx import UpyIrRx

rx_pin = Pin(32, Pin.IN)   # Pin No.32
rx = UpyIrRx(rx_pin)

tx_pin = Pin(26, Pin.OUT)  # Pin No.26
tx = UpyIrTx(0, tx_pin)    # 0ch
...
# If the remote control is transmitted to the receiving circuit
# within 3000 msec, the remote control signal is acquired.
rx.record(3000)
if rx.get_mode() == UpyIrRx.MODE_DONE_OK:
    signal_list = rx.get_calibrate_list()
    # ex) [430, 1290, 430, 430, 430, 860, ...]
else:
    signal_list = []
...
if signal_list:
    tx.send(signal_list)
...
```

---

## Demo application


In the attached demo application, along with the application software on the PC side,
You can easily collect signals from the infrared remote controller and test the transmission.

* Uses the same command channel as the REPL environment
* Intuitive operability on the GUI screen
* Record infrared remote control signal and create json file
* Can be edited by calling a new or existing json file
* Can be tested by sending a recording signal

> --- caution ---
> 
> The main.py written to the microcomputer is automatically executed after the power is turned on.
> Inside main.py, the keystroke input () is in an infinite loop.
> In this state, writing the program to the microcomputer will be blocked.
> If you want to return to the REPL environment,
> use the terminal software for serial communication and enter a line feed after the q key.
> (Or Ctrl+c)

### *Microcomputer side preparation For M5Stack ATOM(Lite & Matrix)*

The demo program runs on a system with
[M5Stack ATOM](https://docs.m5stack.com/en/core/atom_matrix)
and [IR REMOTE UNIT](https://docs.m5stack.com/en/unit/ir) connected via a Grove connector.
Write the three files "main.py", "UpyIrRx.py", and "UpyIrTx.py" to the microcomputer.
As in the REPL environment, connect the PC side and M5Stack with a USB cable.

If you want to use another ESP32 module, modify the source code as shown in main.py below.

### *Microcomputer side preparation For RP2040(Raspberry Pi Pico)*

Write the three files "main.py", "UpyIrRx.py", and "UpyIrTx.py" to the microcomputer.
An external infrared transmitter / receiver circuit can be connected to any GPIO pin.
In this example,
Connect the output of the infrared remote control light receiving module to GPIO Pin.18,
The infrared remote control transmission signal is connected to GPIO Pin.19.

If you want to use other pins, rewrite the following pin layout in the source code.

**Modifications of main.py**
```python
_GROVE_PIN = {'ATOM':  (32, 26),
              'CORE2': (33, 32),
              'BASIC': (22, 21),
              'GRAY':  (22, 21),
              'FIRE':  (22, 21),
              'GO':    (22, 21),
              'Stick': (33, 32),
              'Else':  (18, 19)}  # Rewrite (RxPin Number, TxPin Number)
_DEVICE = 'Else'                  # Rewrite 'Else'
_TX_IDLE_LEVEL = const(0)         # Sender idle_level(Invalid when using RP2040)
_TX_FREQ = const(38000)           # Sender modulation frequency(Invalid when using RP2040)
_TX_DUTY = const(30)              # Sender duty ratio(Invalid when using RP2040)
_RX_IDLE_LEVEL = const(1)         # Receiver idle_level
```

### *PC side preparation*

The application on the PC side is written in python.
It has been confirmed to work on windows, Ubuntu, and Raspbian OS.
It uses the GUI framework Tkinter.

![gui](https://user-images.githubusercontent.com/70054769/172902379-3fce461f-63b1-4cf4-a9a1-cd01fe665a29.png)

1. Install python 3.8 or above.

2. Install serial communication library [pySerial](https://pythonhosted.org/pyserial/).

   `$ pip install pyserial`

3. The python program consists of 6 files.
   
4. If you want to use a microcomputer board other than the sample example, modify the following part of communication.py.
   Specify the vendor ID (VID) and product ID (PID) of the USB device.
   These IDs can be easily found from your PC.

   ```python
   class Communication():
        _DEFAULT_VID = 1027   # A unique USB VID is assigned to each microcomputer board.
        _DEFAULT_PID = 24577  # Also USB PID
    ```

    | Type | VID | PID |
    | :--- | ---: | ---: |
    | M5Stack ATOM | 1027 | 24577 |
    | M5Stack Core2 | 4292 | 60000 |
    | Raspberry Pi Pico | 11914 | 5 |
    | | | |

4. Start the program `$ python main.py`

### *How to use application software on the PC side*

1. Enter the name of the existing save file or the new save file in the **file** field.
    * You can also select it like a file explorer from the **Select** button.
2. Press the **Open** button to start editing.
    * The **Save** button is disabled at this point. It will be effective after some editing.
      Press to save and then close the file.
    * On the other hand, the **Close** button is always valid.
      Press to close the file without saving.
3. **Key list** is the key name of the remote control signal you named.
    * There is always only one `__sysytem__` key. Use it to comment on files.
    * One key consists of a remote control signal and a comment.
4. To add a new remote control signal key name to **Key_list**, fill in the **Edit key** field, then
   Press the **Append** button.
5. To delete the key name of the remote control signal of **Key_list**,
   select the **Key_list** you want to delete, and then press the **Delete** button.
6. To rename the key name of the remote control signal of **Key_list**,
   select the **Key_list** you want to rename, fill in the **Edit key** field,
   and press the **Rename** button. 
7. Select the key name of the remote control signal in **Key_list** and press the **Record** button
   to record the remote control signal of that key name.
   Within Wait [sec] after pressing the button, let's send the remote control signal
   to the infrared remote control receiver module.
    * The waveform data is displayed in the **Signal** field.
    * You can freely record your comments in the **Comment** field.
      It is a good idea to describe the meaning of the signal (for example, "volume up").
    * If the field is changed, the background will be red.
    * Press the **Commit** button to confirm. Press the **Cancel** button to return to the original data.
    * If you select another key name for **Key_list** without pressing the **Commit** button,
      it will be considered as **Cancel**.
    * For this reason, it's a good idea to press **Commit** button as soon as you edit (= the background turns red). 
      If you press the **Commit** button, the background of the edited part will return to green.
8. Pressing the **Send** button will now send the remote control signal in the **Signal** column.
9. When you have finished editing steps 3-8, click the **Save** or **Close** button to close the file.
    * Press the **Save** button to save and exit your edits.
    * Click the **Close** button to discard all previous edits and exit.

### *Generated json file*

This is a json format text file.
In dictionary format, the key is the key name of the remote control signal.
Value is in dictionary format.

The value dictionary format consists of two keys, "signal" and "comment".
A sample is illustrated below.

```json
{"vol_up": {"signal": [430, 1290, 430, ...], "comment": "volume up"},
 "ch1":    {"signal": [430, 1290, 860, ...], "comment": "CH 1"},
 ...
}
```

---

## Afterword

Due to the limit of processing speed,
sending and receiving remote control signals using micropython was difficult.

Especially for the generation of the transmission signal,
the jitter is too severe for the waveform generation using the sleep process, and it is not practical.
This library is limited to ESP32 and RP2040 chips, but is board-specific.
I overcame it by using the function.
Considering the convenience of micropython, even if you have such a hard time,
it is worth making it into a library.

You can also use Home IoT in combination with WIFI.
An automated system for air conditioning by timer processing is also practical.
Make use of this library and have a fun electronic work life!
