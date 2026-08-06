# 순서 없이 도착하는 notification 재조립하기 (Stream)

이 단계의 목표는 다음과 같습니다:
*  notification 하나가 실을 수 있는 것은 최대 20바이트입니다. ATT PDU가 23바이트인데 opcode와 handle이 3바이트를 가져가기 때문입니다.
*  그보다 긴 것은 여러 조각으로 흘러옵니다. 이 텔레매틱스 유닛의 주행 log가 그렇습니다.
*  subscribe하면 peripheral이 밀어낼 수 있는 속도로 조각이 쏟아지는데, **순서대로 오지 않습니다.**
*  ATT 자체에는 순서 개념이 없어서, peripheral이 순서를 **payload 안에** 넣습니다. 이 장치는 조각마다 첫 바이트를 그 조각의 위치로 씁니다.
*  조각을 모두 모아 위치대로 되돌려야 합니다.

과제:
*  이 characteristic의 CCCD를 찾아 subscribe하세요.
*  조각이 더 오지 않을 때까지 모두 모으세요.

```
import sys
sys.path.insert(0, "/challenge")
import ble

client = ble.Client("<주소>")
client.subscribe(<cccd handle>)
chunks = [value for handle, value in client.events_stream(timeout=5)]
```

*  모은 조각을 첫 바이트로 정렬하세요.
*  **이어 붙이기 전에 그 첫 바이트를 떼어내세요.**

힌트:
*  받은 순서대로 붙이지 마세요. 프로토콜은 무엇이 먼저 왔는지 따지지 않습니다.
*  위치 바이트를 반드시 떼세요. 그대로 두면 조각 사이사이에 알 수 없는 문자가 끼어듭니다.
*  조각 번호가 연속인지 확인하세요. 중간이 비면 아직 다 받지 못한 것입니다.

조각을 순서대로 합치면 플래그가 됩니다!
