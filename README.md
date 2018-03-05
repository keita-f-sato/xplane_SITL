# X-Plane_SITL
This program is an open source program for control algorithms test of AutoPilot use by the commercial flight simulator software X-Plane.

このプログラムは商用飛行シミュレータソフトX-Planeを用いてオートパイロットの制御アルゴリズムをテストするためのオープンソースプログラムです。
X-Plane_SITLではPythonによって制御アルゴリズムを記述することができます。Pythonは
X-Plane_SITLはUDP通信を用いてX-Planeとデータの送受信を行い、航空機を制御し、シミュレートされた航空機から状態情報を受け取ることができます。


##Quick Start
X-Plane_SITLで制御アルゴリズムのテストを行う前にX-Plane本体を以下の画像のように設定する必要があります。

X-plane_SITLの使用を開始するためには、以下の項目をソースコードを自分の環境に合わせて書き換えてください。

1.setting of UDP
X-Plane side

X-Plane_SITL side
'''Python:TF_Simulator.py
    self.host = '127.0.0.1'
    self.port = 49007
    self.sedport = 49000
'''

2.Data output,input 
![data](https://user-images.githubusercontent.com/32607565/36968671-98a258e8-20a6-11e8-9670-1ddb3223daa5.PNG)

3.settting to joystick


##License
Copyright (c) 2018 Sato Keita
Released under the MIT license
<http://opensource.org/licenses/mit-license.php>
