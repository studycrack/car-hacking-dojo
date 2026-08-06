# CCCD를 써서 notification 켜기

이 단계의 목표는 다음과 같습니다:
*  지금까지는 여러분이 묻고 peripheral이 답했습니다.
*  센서는 그렇게 동작하고 싶어 하지 않습니다.
*  BLE의 답은 **notification**입니다.
*  peripheral이 묻지도 않았는데 먼저 밀어 주는 PDU입니다.
*  다만 켜기 전에는 아무것도 보내지 않습니다.
*  notification을 보낼 수 있는 characteristic에는 CCCD가 붙어 있습니다. UUID는 `0x2902`입니다.
*  그냥 쓸 수 있는 attribute입니다.

        0x0001 을 쓰면 notification 활성화
        0x0002 를 쓰면 indication 활성화

*  기본값은 꺼짐입니다. 설정은 연결마다 따로 기억됩니다.

과제:
*  이 characteristic의 CCCD를 attribute table에서 찾으세요.
*  notification을 켜고 계속 듣고 있으세요.

힌트:
*  descriptor를 찾는 방법은 앞에서 익혔습니다.
*  peripheral은 자기가 준비됐을 때 말합니다.
*  할 말이 PDU 하나에 안 들어가 여러 번 나눠 옵니다. 한 번 받고 끊지 마세요.
*  `gatttool`로 계속 들으려면 `--listen`을 붙입니다.

notification을 이어 붙이면 플래그가 됩니다!
