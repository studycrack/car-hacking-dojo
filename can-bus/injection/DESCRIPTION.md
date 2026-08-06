# frame을 위조해 문 열기

이 단계의 목표는 다음과 같습니다:
*  CAN frame에는 발신자 정보가 없습니다.
*  버스에 닿으면 누구든 어떤 메시지든 보낼 수 있습니다.
*  이 차의 바디 컨트롤 모듈(BCM)은 아래 두 ID를 씁니다.

| ID | 방향 | layout |
| --- | --- | --- |
| `0x19A` | BCM 송신 | 바이트 0: `01` 잠김 / `00` 열림. 바이트 2-3: session counter(big-endian) |
| `0x19B` | BCM 수신 | 바이트 0: `02` 열기. 바이트 1: `FF` 전체 도어. 바이트 2-3: 현재 session counter |

*  session counter는 평문으로 broadcast됩니다. 30초마다 바뀝니다.

과제:
*  BCM이 알리는 session counter를 읽으세요.
*  그 값으로 `0x19B` frame을 만들어 문을 여세요.

힌트:
*  `cansend`는 `candump`와 같은 표기를 씁니다.

        cansend vcan0 19B#0200ABCD

*  위 예시는 `0x19B`에 `02 00 AB CD`를 실어 보냅니다.
*  counter가 30초마다 바뀝니다. 읽고 바로 보내세요.
*  다른 터미널에 `candump`를 띄워 두세요.

문이 열리면 플래그가 버스로 나옵니다!
