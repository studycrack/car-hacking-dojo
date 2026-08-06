# BLE peripheral 찾아서 GATT attribute table 훑기 (Discovery)

이 단계의 목표는 다음과 같습니다:
*  누군가 이 차의 OBD-II 포트에 동글을 꽂아 두고 잊었습니다.
*  그 동글은 앞의 두 모듈에서 공격한 진단 버스에 직접 연결되어 있고, 동시에 Bluetooth로도 말을 합니다. 휴대폰 앱과 대화해야 하기 때문입니다.
*  BLE의 데이터 모델은 **GATT**입니다. attribute가 나란히 늘어선 표이고, service가 묶고 characteristic이 값을 담으며, 각각 16비트 handle을 가집니다.
*  이 동글은 페어링도 비밀번호도 요구하지 않습니다.
*  연결해서 attribute table을 훑고, 제조사가 남기지 말았어야 할 값을 찾아야 합니다.

과제:
*  advertising 중인 peripheral을 찾아 주소를 확인하세요.

```
hcitool lescan
```

*  연결해서 무엇을 노출하는지 확인하세요.

```
gatttool -b <주소> --primary
gatttool -b <주소> --characteristics
```

*  읽을 수 있는 characteristic을 모두 읽으세요.

```
gatttool -b <주소> --char-read -a <값 handle>
```

힌트:
*  `--characteristics` 출력에서 **declaration handle**과 **값 handle**을 구분하세요. 둘은 서로 다른 attribute입니다.
*  값 handle을 읽으세요. declaration을 읽으면 property 정보만 나오고 데이터는 나오지 않습니다.
*  `char value handle` 열에 적힌 값을 쓰세요.
*  셸이 편하면 `bluetoothctl`을 쓰세요. `scan on` 다음 `connect`, 그리고 `gatt` 메뉴 순서입니다.

읽힌 값 하나가 플래그입니다!
