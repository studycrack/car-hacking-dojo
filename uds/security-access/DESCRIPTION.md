# SecurityAccess 시도 제한 우회하고 key 무차별 대입하기

이 단계의 목표는 다음과 같습니다:
*  펌웨어 재기록, 액추에이터 테스트, 이모빌라이저 해제는 service `0x27` 뒤에 있습니다.
*  **SecurityAccess**는 challenge-response 방식입니다.
   1.  `10 03`으로 확장 session에 들어갑니다.
   2.  `27 01`로 seed를 요청합니다. ECU가 `67 01`과 난수 4바이트로 답합니다.
   3.  그 seed로 key를 계산해 `27 02 <key>`로 보냅니다. 이 ECU는 16비트 key를 씁니다.
   4.  key가 맞으면 ECU가 `67 02`로 답합니다.
*  key 생성 알고리즘은 딜러 진단 소프트웨어 안에 있습니다.
*  여기서는 대신 추측합니다. 16비트면 65,536가지입니다.
*  이 ECU에는 시도 제한이 있습니다.
*  key를 세 번 틀리면 `7F 27 36`(exceedNumberOfAttempts)으로 답합니다.
*  그리고 10초 동안 보안 request를 거부합니다. 이대로면 전수 탐색에 며칠이 걸립니다.

과제:
*  시도 제한을 우회해 16비트 key를 찾아내세요.
*  잠금이 풀린 뒤 routine `0xF00D`를 실행하세요.

        31 01 F0 0D

힌트:
*  **무엇이 그 counter를 초기화하는지** 보세요.
*  진단 session을 요청하는 것은 tester가 늘 하는 동작입니다.
*  이 ECU는 새 session을 새 출발로 취급합니다. 실패 횟수도 잠금도 남지 않습니다.
*  다만 seed는 기본 session으로 돌아가지 않는 동안에만 유지됩니다. 한 번 받아 두고 계속 쓰세요.
*  `vcan.py`와 `isotp.py`를 `/challenge`에서 가져다 쓸 수 있습니다.

        import sys
        sys.path.insert(0, "/challenge")
        import isotp, vcan

        bus = vcan.Bus("vcan0")
        print(isotp.request(bus, 0x7E0, 0x7E8, bytes.fromhex("1003")).hex())

routine response에 플래그가 담겨 옵니다!
