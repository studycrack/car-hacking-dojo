# declaration에 없는 기능 쓰기 (Hidden Notify)

이 단계의 목표는 다음과 같습니다:
*  이 동글을 열거하면 디버그 characteristic이 `debug channel idle`을 돌려줍니다.
*  그 declaration에는 `READ`만 있습니다. notify property가 없으니 subscribe할 것도 없어 보이고, declaration을 보고 화면을 만드는 도구는 그 선택지를 아예 보여주지 않습니다.
*  하지만 attribute table을 보면 그 characteristic 아래에 `0x2902`가 앉아 있습니다.
*  CCCD는 notification을 켜기 위한 것입니다. notification을 못 보내는 characteristic에 있을 이유가 없습니다.
*  있으면 안 될 그 CCCD에 값을 써서 notification을 받아내야 합니다.

과제:
*  characteristic 목록에서 디버그 characteristic의 property를 확인하세요. `READ`만 있습니다.

```
gatttool -b <주소> --characteristics
```

*  attribute table을 열어 그 아래에 `0x2902`가 있는지 확인하세요.

```
gatttool -b <주소> --char-desc
```

*  그 CCCD에 값을 쓰고, 연결을 유지한 채 들으세요.

```
gatttool -b <주소> --char-write-req -a <cccd handle> -n 0100 --listen
```

힌트:
*  declaration의 property 바이트를 권한으로 믿지 마세요. **펌웨어가 밝힌 의도**일 뿐이고 스택이 강제하지 않습니다.
*  CCCD에 그냥 쓰세요. 쓰기가 들어올 때 property를 확인하는 코드는 없습니다.
*  characteristic 값을 다시 읽지 마세요. 여전히 `debug channel idle`입니다. 값이 아니라 CCCD를 건드려야 합니다.

subscribe가 켜지면 notification으로 플래그가 도착합니다!
