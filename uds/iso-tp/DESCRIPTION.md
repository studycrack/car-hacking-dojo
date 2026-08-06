# ISO-TP로 8바이트보다 긴 진단 요청 주고받기

이 단계의 목표는 다음과 같습니다:
*  VIN 17자는 8바이트에 들어가지 않습니다.
*  **ISO-TP**(ISO 15765-2)가 그 위를 덮는 전송 계층입니다.
*  모든 진단 session이 이 위에서 돌아갑니다.
*  ISO-TP는 payload의 첫 바이트를 제어 필드로 씁니다.

| 첫 니블 | 종류 | 형식 |
| --- | --- | --- |
| `0` | Single Frame | `0L` 다음에 `L`바이트 |
| `1` | First Frame | `1LLL`, 12비트 전체 길이 + 첫 6바이트 |
| `2` | Consecutive Frame | `2N`, 순번 `1,2,…,F,0,…` + 최대 7바이트 |
| `3` | Flow Control | `30 BS ST`, 계속 · block size · 최소 간격 |

*  전송을 이끄는 쪽은 **수신자**입니다.
*  First Frame을 받으면 송신자는 멈춥니다. Flow Control이 올 때까지 기다립니다.
*  그 위에 **UDS**(ISO 14229)가 올라갑니다.
*  request는 service 바이트와 인자입니다. positive response는 service 바이트에 `0x40`을 더한 값입니다.

과제:
*  엔진 컨트롤러에 VIN을 요청하세요. request는 `0x7E0`, response는 `0x7E8`입니다.

        cansend vcan0 7E0#0322F19000000000

*  Flow Control을 직접 보내 나머지를 받아내세요.
*  같은 컨트롤러에서 DID `0xF1AB`를 읽으세요. 부트로더 unlock token입니다.

힌트:
*  위 request는 `22 F1 90` 세 바이트를 Single Frame(`03` 헤더)으로 감싼 것입니다.
*  response는 `62 F1 90` 뒤에 VIN 17바이트가 옵니다.
*  보내는 동안 `0x7E8`을 지켜보세요. First Frame이 온 뒤 멈춥니다.
*  ECU는 Flow Control을 30초 동안 기다립니다.
*  기다리는 동안에는 다른 request에 답하지 않습니다. 조용해졌다면 잠시 뒤 다시 요청하세요.

`0xF1AB` response 안에 플래그가 들어 있습니다!
