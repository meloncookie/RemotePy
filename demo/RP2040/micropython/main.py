from machine import Pin
from micropython import const
from gc import collect
import json
from UpyIrTx import UpyIrTx
from UpyIrRx import UpyIrRx

# RP2040 RX=Pin18, TX=Pin19
_GROVE_PIN = {'ATOM':  (32, 26),
              'CORE2': (33, 32),
              'BASIC': (22, 21),
              'GRAY':  (22, 21),
              'FIRE':  (22, 21),
              'GO':    (22, 21),
              'Stick': (33, 32),
              'Else':  (18, 19)}
_DEVICE = 'Else'
_TX_IDLE_LEVEL = const(0)
_TX_FREQ = const(38000)
_TX_DUTY = const(30)
_RX_IDLE_LEVEL = const(1)
_RX_SIZE = const(1023)

rx_pin = Pin(_GROVE_PIN[_DEVICE][0], Pin.IN)
rx = UpyIrRx(rx_pin, _RX_SIZE, _RX_IDLE_LEVEL)

tx_pin = Pin(_GROVE_PIN[_DEVICE][1], Pin.OUT)
tx = UpyIrTx(0, tx_pin, _TX_FREQ, _TX_DUTY, _TX_IDLE_LEVEL)

cmd = input()
while cmd != 'q':
    if len(cmd) > 0:
        if cmd[0] == 'r':
            # ex. cmd: 'r[3000, 200, 1023]
            try:
                _wait, _blank, _size = json.loads(cmd[1:])
                if rx.record(_wait, _blank, _size) == UpyIrRx.ERROR_NONE:
                    print(rx.get_calibrate_list())
                else:
                    print('[]')
            except:
                print('[]')
        elif cmd[0] == 'w':
            # ex. cmd: 'w[420, 1260, 420, ...]
            try:
                if tx.send(json.loads(cmd[1:])):
                    print('OK')
                else:
                    print('NG')
            except:
                print('NG')
        else:
            print('NG')
    del cmd
    collect()
    cmd = input()
