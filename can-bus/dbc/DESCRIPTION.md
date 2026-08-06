# DBC 파일을 읽고 signal 만들어 보내기 (DBC)

이 단계의 목표는 다음과 같습니다:
*  **DBC 파일**은 버스 정의를 적어 두는 형식입니다. 메시지마다 한 항목, signal마다 한 줄이 있습니다.
*  각 signal에는 start bit, 길이, byte order, scale, offset이 적혀 있습니다.
*  이 차의 DBC가 `/challenge/vehicle.dbc`에 있습니다.
*  그 안의 `BCM_Command`는 손으로 계산하기 까다롭습니다. 실내 온도는 scale `0.5`에 offset `-20`, 팬은 4비트이고, byte order가 Motorola라 start bit를 세는 방식이 직관과 다릅니다.
*  실내 목표 온도 **30.5도**, 송풍 팬 **11**을 지시하는 frame을 보내야 합니다.

과제:
*  DBC 내용을 확인하세요.

```
cantools dump /challenge/vehicle.dbc
```

*  `BCM_Command`의 signal 이름과 비트 배치를 파악하세요.
*  `cantools`로 값을 인코딩하세요. 비트 packing까지 대신 해 줍니다.

```
#!/usr/bin/python3
import cantools
db = cantools.database.load_file("/challenge/vehicle.dbc")
message = db.get_message_by_name("BCM_Command")
data = message.encode({...})
```

*  인코딩한 8바이트를 `BCM_Command` ID로 전송하세요.

힌트:
*  `/usr/bin/python3`으로 실행하세요. 이 워크스페이스에는 파이썬이 두 개이고, `cantools`는 문제 이미지 쪽에만 있습니다.

```
/usr/bin/python3 -c 'import cantools; print(cantools.__version__)'
```

*  스크립트 첫 줄을 `#!/usr/bin/python3`으로 두세요.
*  `cantools dump` 출력에 있는 signal 이름을 모두 채우세요. `message.encode`는 지정하지 않은 것도 요구합니다.
*  손으로 비트를 맞추려 하지 마세요. Motorola 순서에서 어긋나기 쉽습니다. 라이브러리에 맡기세요.

지시가 받아들여지면 플래그가 버스로 나옵니다. `candump -a vcan0`으로 확인하세요!
