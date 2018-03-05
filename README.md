# X-Plane_SITL
This program is an open source program for control algorithms test of AutoPilot use by the commercial flight simulator software X-Plane.

このプログラムは商用飛行シミュレータソフトX-Planeを用いてオートパイロットの制御アルゴリズムをテストするためのオープンソースプログラムです。
X-Plane_SITLではPythonによって制御アルゴリズムを記述することができます。
X-Plane_SITLはUDP通信を用いてX-Planeとデータの送受信を行い、航空機を制御し、シミュレートされた航空機の状態を受け取ることができます。


## Quick Start
X-Plane_SITLで制御アルゴリズムのテストを行う前にX-Plane本体を以下の画像のように設定する必要があります。
### 1.setting of UDP
UDPポートの設定を行います。X-Plane/Settings/Net Connectionsを選択し、Dataタブを開いてください。　　
そこで、以下の画像の通りに設定します。
![net](https://user-images.githubusercontent.com/32607565/36968673-99d49780-20a6-11e8-943a-19196154769c.PNG)


### 2.Data output,input 
各種飛行データの入出力の設定を行います。X-Plane/Settings/Data Input&Outputを開き、以下の画像のように設定します。
![data](https://user-images.githubusercontent.com/32607565/36968671-98a258e8-20a6-11e8-9670-1ddb3223daa5.PNG)

3.settting to joystick
X-Plane_SITLではjoystickを用いた航空機の操作といくつかの機能を提供します。joystickからの信号はPygameを用いて読み込みます。
Pygameのインストールは以下のサイトか、もしくは''' pip install pygame'''でインストールしてください。
<http://gamepro.blog.jp/python/pygame/install>
pygameをインストール後は、まずは手持ちのjoystickのボタン・axisの値の割り振りを確認します。
以下のURLのプログラムを使用して割り振りを確認することを推奨します。　　
<http://d.hatena.ne.jp/kadotanimitsuru/20100321/joyprint>
割り振りを確認したのち、エレベーター・エルロン・ラダー・スロットルのjoystick入力の設定をします。
TF_Simulator.pyの85・86行目の'''j.get_axis()'''の（）の中を割り振りたいaxisの数字にすることで設定できます。
次に、X-Plane_SITLでは制御プログラムのON/OFF切り替えとプログラムの終了をボタンに割り当てることができます。
TF_Simulator.pyの92行目、94行目にそれぞれON/OFF切り替えとプログラムの終了を割り当てたいボタンの数字を指定することで設定することができます。

以上で各種設定は終了です。
X-Plane_SITLを実行するためには、TF_Simulator.pyを実行するだけです。

もし、独自の制御アルゴリズムをテストしたい場合はTransfer_function_plane.pyを書き換え、transfer_function関数の戻り値をroll,picht,yow,throttenの順でリストを返すことで制御アルゴリズムをテストすることができます。

## last
このプログラムは発展途上です。今後、このプログラムには以下のような機能が実装される予定です。
・制御コマンドや姿勢のリアルタイムグラフ表示機能
・舵面の作動遅れの表現
・強化学習デモ　etc...
乞うご期待です。

このプログラムがDrone開発&勉強の良い入門ツールになることを願って！

Thank you for reading.

## License
Copyright (c) 2018 Sato Keita
Released under the MIT license
<http://opensource.org/licenses/mit-license.php>
