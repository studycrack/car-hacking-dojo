# Bluetooth 동글을 bridge 삼아 다른 버스에 닿기 (Pivot)

이 단계의 목표는 다음과 같습니다:
*  목표인 이모빌라이저는 파워트레인 버스에 있고, 여러분은 그 버스에 있지 않습니다.
*  이번에는 악용할 gateway routing table도 없습니다. `candump vcan0`을 해 보면 커널이 권한을 거절합니다.
*  대신 OBD-II 포트에 Bluetooth 동글이 꽂혀 있습니다. 이 동글은 버스에 붙어 있고(그게 존재 이유입니다), 동시에 전파에도 있습니다(그래야 앱과 대화합니다).
*  즉 bridge이고, bridge는 양쪽으로 건널 수 있습니다.
*  동글을 통해 frame을 버스로 내보내, 이모빌라이저의 routine `0xC001`을 실행해야 합니다.

과제:
*  동글을 열거해 버스가 어떤 characteristic으로 노출되는지 확인하세요.
   *  frame을 **쓰는** characteristic 하나
   *  들은 frame을 notification으로 **보내 주는** characteristic 하나
*  **notification에 먼저 subscribe**하세요. 앞의 `trigger` 문제와 같은 이유입니다.
*  같은 연결에서 frame을 써서 버스로 내보내세요. 지금까지 계속 읽어 온 표기 그대로입니다.

```
6F2#0322F19000000000
```

*  건너간 뒤는 앞의 두 모듈 그대로입니다. ISO-TP로 분할하고, 알맞은 session에 들어가세요.
*  routine을 실행하세요.

```
31 01 C0 01
```

힌트:
*  ISO-TP와 UDS를 그대로 얹으세요. 프로토콜은 자기 아래가 전선에서 무선으로 바뀐 줄 모릅니다.
*  보내기 전에 subscribe하세요. 응답도 같은 경로로 돌아옵니다.
*  인증을 찾지 마세요. 이모빌라이저는 닿기만 하면 `0xC001`을 실행해 줍니다.
*  `/challenge/ble.py`의 클라이언트를 쓰세요. 한 연결 안에서 subscribe와 쓰기를 모두 할 수 있습니다.

routine 응답이 notification으로 돌아오고, 그 안에 플래그가 있습니다!
