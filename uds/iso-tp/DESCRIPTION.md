# ISO-TP로 8바이트보다 긴 진단 요청 주고받기 (ISO-TP)

이 단계의 목표는 다음과 같습니다:
*  VIN 17자는 CAN frame 8바이트에 들어가지 않습니다. 그래서 진단 통신은 **ISO-TP**(ISO 15765-2)라는 전송 계층 위에서 돌아갑니다.
*  ISO-TP는 payload의 첫 바이트를 제어 필드로 씁니다.

| 첫 니블 | 종류 | 형식 |
| --- | --- | --- |
| `0` | Single Frame | `0L` 다음에 `L`바이트 |
| `1` | First Frame | `1LLL`, 12비트 전체 길이 + 첫 6바이트 |
| `2` | Consecutive Frame | `2N`, 순번 `1,2,…,F,0,…` + 최대 7바이트 |
| `3` | Flow Control | `30 BS ST`, 계속 · block size · 최소 간격 |

*  전송을 이끄는 쪽은 **수신자**입니다. First Frame을 받은 송신자는 멈춰서 Flow Control이 올 때까지 기다립니다.
*  그 위에 **UDS**(ISO 14229)가 올라갑니다. request는 service 바이트와 인자이고, positive response는 service 바이트에 `0x40`을 더한 값입니다.
*  엔진 컨트롤러는 `0x7E0`으로 받고 `0x7E8`으로 답합니다.
*  Flow Control을 직접 보내 VIN을 받아내고, 이어서 DID `0xF1AB`를 읽어야 합니다.

과제:
*  응답을 볼 수 있도록 캡처를 먼저 걸어 두세요.

```
candump vcan0,7E8:7FF &
```

*  VIN을 요청하세요. `22 F1 90` 세 바이트를 Single Frame(`03` 헤더)으로 감싼 것입니다.

```
cansend vcan0 7E0#0322F19000000000
```

*  First Frame이 온 뒤 전송이 멈춥니다. Flow Control을 직접 보내 나머지를 받아내세요.
   *  `30`은 계속 보내라는 뜻입니다.
   *  뒤의 두 바이트는 block size와 최소 간격입니다.
*  같은 컨트롤러에서 DID `0xF1AB`를 읽으세요. 부트로더 unlock token입니다.

힌트:
*  조각을 이어 붙여서 읽으세요. VIN 응답은 `62 F1 90` 뒤에 17바이트가 이어집니다.
*  전송이 멈추면 Flow Control을 보내세요. ECU는 30초 동안 기다립니다.
*  ECU가 조용하면 잠시 뒤 다시 요청하세요. 기다리는 동안에는 다른 request에 답하지 않습니다.
*  직접 처리하기 번거로우면 `isotpreq`를 쓰세요. 분할과 Flow Control을 대신 해 줍니다.

```
isotpreq vcan0 7E0 7E8 22F190
```

`0xF1AB` 응답 안에 플래그가 들어 있습니다!
