# CCCD를 써서 notification 켜기 (Notify)

이 단계의 목표는 다음과 같습니다:
*  지금까지는 여러분이 묻고 peripheral이 답했지만, 센서는 그렇게 동작하고 싶어 하지 않습니다.
*  BLE의 답은 **notification**입니다. peripheral이 묻지도 않았는데 먼저 밀어 주는 PDU입니다.
*  다만 켜기 전에는 아무것도 보내지 않습니다. notification을 보낼 수 있는 characteristic에는 CCCD(UUID `0x2902`)가 붙어 있고, 그냥 쓸 수 있는 attribute입니다.

```
0x0001 을 쓰면 notification 활성화
0x0002 를 쓰면 indication 활성화
```

*  기본값은 꺼짐이고, 설정은 연결마다 따로 기억됩니다.
*  할 말이 PDU 하나에 안 들어가 여러 번 나눠 옵니다.
*  CCCD를 켜고 끝까지 들어야 합니다.

과제:
*  이 characteristic의 CCCD handle을 attribute table에서 찾으세요. UUID가 `0x2902`인 줄입니다.

```
gatttool -b <주소> --char-desc
```

*  CCCD에 `0100`을 쓰고 연결을 유지한 채 들으세요.

```
gatttool -b <주소> --char-write-req -a <cccd handle> -n 0100 --listen
```

*  도착하는 notification을 모두 모아 순서대로 이어 붙이세요.

힌트:
*  `--listen`을 빠뜨리지 마세요. 없으면 쓰기만 하고 끊어져서 아무것도 받지 못합니다.
*  한 번 받고 끊지 마세요. peripheral은 자기가 준비됐을 때 말합니다.
*  CCCD 값은 little-endian으로 쓰세요. `0x0001`은 `0100`입니다.
*  descriptor를 찾는 방법은 앞 문제에서 익힌 것을 그대로 쓰세요.

notification을 이어 붙이면 플래그가 됩니다!
