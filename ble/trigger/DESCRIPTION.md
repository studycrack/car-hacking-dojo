# subscribe를 먼저 걸고 request 보내기 (Trigger)

이 단계의 목표는 다음과 같습니다:
*  이제 subscribe도 해 봤고 쓰기도 해 봤습니다. 이 모듈은 둘 다 필요하고, **순서**가 중요합니다.
*  이 키리스 모듈은 한 characteristic에 쓰면 다른 characteristic으로 답을 notification으로 밀어 줍니다.
*  그 답은 **그 순간 subscribe하고 있는 쪽**에게만 갑니다. 큐도 없어서, 먼저 쓰면 답은 만들어져서 아무도 없는 쪽으로 밀려나고 사라집니다.
*  게다가 **답은 요청한 그 연결로 돌아옵니다.**
*  하나의 연결을 열어 둔 채 그 안에서 subscribe와 쓰기를 모두 해야 합니다.

과제:
*  답이 오는 characteristic과 request를 받는 characteristic을 각각 찾으세요.
*  하나의 연결을 열고, **먼저 subscribe**하세요.
*  같은 연결에서 request characteristic에 쓰세요.
*  그 연결로 도착하는 notification을 받으세요.

```
import sys
sys.path.insert(0, "/challenge")
import ble

client = ble.Client("<주소>")
client.subscribe(<cccd handle>)
client.write(<request handle>, b"\x01")
for handle, value in client.events_stream(timeout=5):
    print(hex(handle), value)
```

힌트:
*  순서를 뒤집지 마세요. CAN 모듈에서 포브가 한 번만 전송했던 것과 같은 이야기입니다.
*  `gatttool`을 두 번 실행하지 마세요. 연결이 둘로 갈라져서 답을 받을 수 없습니다.
*  `/challenge/ble.py`의 클라이언트나 `bleak`을 쓰세요. 한 연결 안에서 둘 다 됩니다.
*  `bleak`을 쓰려면 `/usr/bin/python3`으로 실행하세요.

notification으로 도착한 답이 플래그입니다!
