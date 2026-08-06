# confirmation을 보내며 indication 끝까지 받기 (Indicate)

이 단계의 목표는 다음과 같습니다:
*  notification은 보내고 잊는 방식이라 도착하지 않아도 아무도 모릅니다. 중요한 것에는 그 거래가 맞지 않습니다.
*  그래서 ATT에는 두 번째 방식인 **indication**이 있습니다. 클라이언트가 Handle Value Confirmation으로 확인해야 다음 것이 옵니다.
*  한 번에 하나씩, 확인받으며, 순서대로 옵니다.
*  이 이모빌라이저는 audit log를 그 방식으로 보관합니다.
*  indication에 맞는 값으로 subscribe하고, record마다 confirmation을 보내며 log를 끝까지 받아야 합니다.

과제:
*  이 characteristic의 CCCD를 찾으세요.
*  **indication에 맞는 값**으로 subscribe하세요. `0x0001`과 `0x0002`는 다릅니다.
*  도착하는 record마다 confirmation을 보내며 끝까지 받으세요.

```
import sys
sys.path.insert(0, "/challenge")
import ble

client = ble.Client("<주소>")
client.subscribe(<cccd handle>)
for handle, value in client.events_stream(timeout=5):
    print(hex(handle), value)
```

*  받은 record를 순서대로 이어 붙이세요.

힌트:
*  CCCD 값을 그 characteristic이 실제로 하는 일에 맞추세요. indication만 하는 쪽에 notification 값을 쓰면 아무 일도 일어나지 않습니다.
*  듣기만 하지 마세요. confirmation을 보내지 않으면 첫 번째에서 멈추고 나머지를 영영 기다립니다.
*  `/challenge/ble.py`의 클라이언트를 쓰세요. confirmation을 대신 보내 줍니다.
*  `bleak`을 쓰려면 `/usr/bin/python3`으로 실행하세요.

log를 전부 모으면 플래그가 됩니다!
