# frame을 위조해 차 문 열기 (Injection)

이 단계의 목표는 다음과 같습니다:
*  CAN frame에는 발신자 정보가 없어서, 버스에 닿으면 누구든 어떤 메시지든 보낼 수 있습니다.
*  이 차의 바디 컨트롤 모듈(BCM)은 아래 두 ID를 씁니다.

| ID | 방향 | layout |
| --- | --- | --- |
| `0x19A` | BCM 송신 | 바이트 0: `01` 잠김 / `00` 열림. 바이트 2-3: session counter(big-endian) |
| `0x19B` | BCM 수신 | 바이트 0: `02` 열기. 바이트 1: `FF` 전체 도어. 바이트 2-3: 현재 session counter |

*  session counter는 암호화 없이 그대로 broadcast되고, 30초마다 새 값으로 바뀝니다.
*  그 값을 읽어 `0x19B` frame을 위조해서 문을 열어야 합니다.

과제:
*  `0x19A`를 관찰해 현재 session counter를 읽으세요.

```
candump vcan0,19A:7FF
```

*  그 값으로 `0x19B` frame을 만들어 보내세요. `cansend`는 `candump`와 같은 표기를 씁니다.

```
cansend vcan0 19B#02FFABCD
```

*  바이트를 다음과 같이 채우세요.
   *  바이트 0은 `02`(열기), 바이트 1은 `FF`(전체 도어)입니다.
   *  바이트 2-3에는 방금 읽은 session counter를 넣으세요. 위 예시의 `ABCD` 자리입니다.
*  `0x19A`의 바이트 0이 `01`에서 `00`으로 바뀌는지 확인하세요.

힌트:
*  읽고 바로 보내세요. counter가 30초마다 바뀝니다.
*  다른 터미널에 `candump`를 띄워 두세요. counter와 결과를 동시에 볼 수 있습니다.
*  바이트 0이 계속 `01`이면 counter를 다시 읽어서 보내세요. 이미 지난 값입니다.

문이 열리면 플래그가 버스로 나옵니다. `candump -a vcan0`으로 확인하세요!
