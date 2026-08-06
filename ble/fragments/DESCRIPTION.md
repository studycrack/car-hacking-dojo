# service에 흩어진 조각을 순서대로 맞추기

이 단계의 목표는 다음과 같습니다:
*  타이어 공기압 gateway는 센서마다 service를 하나씩 둡니다.
*  네 바퀴와 스페어까지 다섯 개입니다.
*  그 다섯 service에 걸쳐 record 하나가 다섯 조각으로 나뉘어 있습니다.
*  센서마다 characteristic이 세 개씩 있습니다. RSSI, index, payload입니다.
*  payload가 조각입니다. index가 그 조각의 순서를 알려 줍니다.

과제:
*  다섯 service를 열거해 각 센서의 index와 payload를 읽으세요.
*  index가 말하는 순서대로 조각을 이어 붙이세요.

힌트:
*  handle 순서대로 읽으면 뜻이 통하지 않습니다.
*  **handle 순서는 record 순서가 아닙니다.**
*  handle은 펌웨어가 attribute table을 만들 때 선언된 차례대로 붙는 번호입니다.
*  표에서의 위치 말고는 아무 의미도 없습니다.
*  조각이 어떻게 맞물리는지 알려 주는 것은 index characteristic뿐입니다.

순서를 맞추면 플래그가 나옵니다!
