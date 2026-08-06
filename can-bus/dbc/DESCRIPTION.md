# DBC 파일을 읽고 signal 만들어 보내기

이 단계의 목표는 다음과 같습니다:
*  **DBC 파일**은 버스 정의를 적어 두는 형식입니다.
*  메시지마다 한 항목, signal마다 한 줄이 있습니다.
*  각 signal에는 start bit, 길이, byte order, scale, offset이 적혀 있습니다.
*  이 차의 DBC가 `/challenge/vehicle.dbc`에 있습니다.
*  그 안의 comfort 메시지는 손으로 계산하기 까다롭습니다.
*  실내 온도는 scale `0.5`에 offset `-20`입니다. 팬은 4비트입니다.
*  byte order는 Motorola입니다. start bit를 세는 방식이 직관과 다릅니다.

과제:
*  `/challenge/vehicle.dbc`를 읽고 comfort 메시지 구조를 파악하세요.
*  실내 목표 온도 **30.5도**, 송풍 팬 **11**을 지시하는 frame을 보내세요.

힌트:
*  `cantools`가 DBC를 읽고 bit packing까지 해 줍니다.

        cantools dump /challenge/vehicle.dbc

*  이 워크스페이스에는 파이썬이 두 개입니다.
*  `python3`는 도장 것입니다. `cantools`는 문제 이미지 쪽에 설치되어 있습니다.

        /usr/bin/python3 -c 'import cantools; print(cantools.__version__)'

*  스크립트도 그쪽 인터프리터로 작성하세요.

        #!/usr/bin/python3
        import cantools
        db = cantools.database.load_file("/challenge/vehicle.dbc")
        message = db.get_message_by_name("BCM_Command")
        data = message.encode({...})

지시가 받아들여지면 플래그가 버스로 나옵니다!
