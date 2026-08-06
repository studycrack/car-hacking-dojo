# Prepare / Execute Write로 긴 값 쓰기 (Long Write)

이 단계의 목표는 다음과 같습니다:
*  읽기에도 같은 문제가 있었지만 눈치챌 필요가 없었습니다. Read Response는 최대 MTU-1 바이트를 싣고, 그보다 긴 값은 클라이언트가 Read Blob request를 대신 보내 모았습니다.
*  쓰기도 같은 문제를 갖지만 해결 방식이 다릅니다. `Write Blob` 같은 것은 없고, 클라이언트가 조각을 쌓아 두었다가 한 번에 반영합니다.

| request | 뜻 |
| --- | --- |
| `16` Prepare Write | 조각 하나와 그 조각이 들어갈 offset |
| `18` Execute Write | 쌓아 둔 것을 반영(`01`) 또는 폐기(`00`) |

*  Execute 전까지는 아무것도 기록되지 않습니다. peripheral이 조각을 들고 있다가 offset 순서로 재조립해 하나의 값으로 반영합니다.
*  이 바디 컨트롤 모듈에는 서비스 모드가 있고, **36바이트짜리 명령**에 열립니다.
*  평범한 Write Request로는 실어 나를 수 없으니, Prepare / Execute Write로 넣어야 합니다.

과제:
*  attribute table에서 그 36바이트 명령을 찾으세요. 정비 도구를 설치한 사람이 그대로 남겨 두었습니다.

```
gatttool -b <주소> --char-desc
```

*  평범한 쓰기로 한번 보내 보세요. 길이가 잘못됐다는 오류가 돌아옵니다.
*  Prepare Write로 조각을 쌓고 Execute Write로 반영하세요.

```
import sys
sys.path.insert(0, "/challenge")
import ble

client = ble.Client("<주소>")
client.write_long(<handle>, b"...36 bytes...")
```

*  서비스 모드가 열리면 해당 characteristic을 읽으세요.

힌트:
*  명령을 찾는 데 시간을 쓰지 마세요. 비밀이 아니고, 그것을 **집어넣는 것**이 이 문제입니다.
*  조각마다 offset을 정확히 매기세요. 어긋나면 재조립된 값이 달라져 서비스 모드가 열리지 않습니다.
*  한 번에 실을 수 있는 크기를 MTU에서 헤더를 뺀 만큼으로 잡으세요.
*  `client.write_long`을 쓰세요. 분할과 Execute까지 대신 해 줍니다.

서비스 모드가 열리면 해당 characteristic을 읽어 플래그를 확인하세요!
