# Bluetooth 동글을 bridge 삼아 다른 버스에 닿기

이 단계의 목표는 다음과 같습니다:
*  목표인 이모빌라이저는 파워트레인 버스에 있습니다. 여러분은 그 버스에 있지 않습니다.
*  이번에는 악용할 gateway routing table도 없습니다.
*  `candump vcan0`을 해 보면 커널이 권한을 거절합니다.
*  대신 OBD-II 포트에 Bluetooth 동글이 꽂혀 있습니다.
*  이 동글은 버스에 붙어 있습니다. 그게 존재 이유입니다.
*  동시에 전파에도 있습니다. 그래야 앱과 대화합니다.
*  즉 bridge입니다. 그리고 bridge는 양쪽으로 건널 수 있습니다.

과제:
*  동글을 열거해 버스가 어떤 characteristic으로 노출되는지 확인하세요.
*  frame을 쓰는 characteristic 하나와, 들은 frame을 notification으로 보내 주는 characteristic 하나가 있습니다.
*  notification에 먼저 subscribe한 뒤 frame을 보내세요.
*  건너간 frame으로 이모빌라이저에 UDS request를 보내 routine `0xC001`을 실행하세요.

힌트:
*  frame은 지금까지 계속 읽어 온 표기 그대로 건너갑니다.

```
6F2#0322F19000000000
```

*  건너간 다음은 앞의 두 모듈 그대로입니다.
*  ISO-TP가 여전히 분할하고, UDS가 여전히 알맞은 session을 요구합니다.
*  이모빌라이저는 자기에게 닿은 상대라면 `0xC001`을 실행해 줍니다.
*  프로토콜은 자기 아래가 전선에서 무선으로 바뀐 줄 모르고, 알 필요도 없습니다.
*  **보내기 전에 subscribe하세요.** 이유는 이제 아실 겁니다.

routine response가 notification으로 돌아오고, 그 안에 플래그가 있습니다!
