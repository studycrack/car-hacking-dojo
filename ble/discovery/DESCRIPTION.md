# BLE peripheral 찾아서 GATT attribute table 훑기

이 단계의 목표는 다음과 같습니다:
*  누군가 이 차의 OBD-II 포트에 동글을 꽂아 두고 잊었습니다.
*  그 동글은 앞의 두 모듈에서 공격한 진단 버스에 직접 연결되어 있습니다.
*  동시에 Bluetooth로도 말을 합니다. 휴대폰 앱과 대화해야 하기 때문입니다.
*  BLE의 데이터 모델은 **GATT**입니다. attribute가 나란히 늘어선 표입니다.
*  service가 묶고, characteristic이 값을 담습니다. 각각 16비트 handle을 가집니다.

과제:
*  advertising 중인 peripheral을 찾으세요.

        hcitool lescan

*  연결해서 무엇을 노출하는지 확인하세요.

        gatttool -b <주소> --primary
        gatttool -b <주소> --characteristics

*  읽을 수 있는 characteristic을 모두 읽어 보세요.

        gatttool -b <주소> --char-read -a <값 handle>

힌트:
*  `--characteristics` 출력에는 **declaration handle**과 **값 handle**이 따로 나옵니다.
*  둘은 서로 다른 attribute입니다.
*  declaration을 읽으면 property 정보가 나옵니다. 데이터는 나오지 않습니다.
*  읽어야 하는 것은 값 handle입니다.
*  여기서는 key도 페어링도 비밀번호도 요구하지 않습니다.

characteristic 하나가 제조사가 남기지 말았어야 할 것을 들고 있습니다. 그것이 플래그입니다!
