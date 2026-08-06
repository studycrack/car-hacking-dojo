# service에 흩어진 조각을 순서대로 맞추기 (Fragments)

이 단계의 목표는 다음과 같습니다:
*  타이어 공기압 gateway는 센서마다 service를 하나씩 둡니다. 네 바퀴와 스페어까지 다섯 개입니다.
*  그 다섯 service에 걸쳐 record 하나가 다섯 조각으로 나뉘어 있습니다.
*  센서마다 characteristic이 세 개씩 있습니다. RSSI, index, payload입니다.
*  payload가 조각이고, index가 그 조각의 순서를 알려 줍니다.
*  **handle 순서는 record 순서가 아닙니다.** index를 읽어서 맞춰야 합니다.

과제:
*  다섯 service를 열거하세요.

```
gatttool -b <주소> --primary
```

*  각 service 안의 characteristic을 확인하세요.

```
gatttool -b <주소> --characteristics
```

*  센서마다 index와 payload를 읽으세요.
*  index가 말하는 순서대로 payload를 이어 붙이세요.

힌트:
*  handle 순서대로 이어 붙이지 마세요. 뜻이 통하지 않습니다.
*  handle에 의미를 두지 마세요. 펌웨어가 attribute table을 만들 때 선언된 차례대로 붙는 번호일 뿐입니다.
*  index characteristic을 반드시 읽으세요. 조각이 어떻게 맞물리는지 알려 주는 것은 그것뿐입니다.
*  다섯 개를 다 읽었는지 세어 보세요. 하나를 빠뜨리면 중간이 비어 보입니다.

순서를 맞추면 플래그가 나옵니다!
