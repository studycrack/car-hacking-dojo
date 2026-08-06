# SecurityAccess 시도 제한 우회하고 key 무차별 대입하기 (SecurityAccess)

이 단계의 목표는 다음과 같습니다:
*  펌웨어 재기록, 액추에이터 테스트, 이모빌라이저 해제는 service `0x27` 뒤에 있습니다.
*  **SecurityAccess**는 challenge-response 방식입니다.
   1.  `10 03`으로 확장 session에 들어갑니다.
   2.  `27 01`로 seed를 요청하면 ECU가 `67 01`과 난수 4바이트로 답합니다.
   3.  그 seed로 key를 계산해 `27 02 <key>`로 보냅니다. 이 ECU는 **16비트 key**를 씁니다.
   4.  key가 맞으면 ECU가 `67 02`로 답합니다.
*  key 생성 알고리즘은 딜러 진단 소프트웨어 안에 있습니다. 여기서는 대신 추측합니다. 16비트면 65,536가지입니다.
*  다만 key를 세 번 틀리면 `7F 27 36`(exceedNumberOfAttempts)으로 답하고 10초 동안 보안 request를 거부합니다. 이대로면 전수 탐색에 며칠이 걸립니다.
*  시도 제한을 우회해 key를 찾고, 잠금이 풀린 뒤 routine `0xF00D`를 실행해야 합니다.

과제:
*  확장 session에 들어가 seed를 한 번 받아 두세요.

```
import sys
sys.path.insert(0, "/challenge")
import isotp, vcan

bus = vcan.Bus("vcan0")
print(isotp.request(bus, 0x7E0, 0x7E8, bytes.fromhex("1003")).hex())
```

*  key를 틀렸을 때 **무엇이 실패 counter를 초기화하는지** 찾으세요.
*  그것을 끼워 넣어 가며 16비트 전체를 탐색하세요.
   *  `7F 27 36`이 돌아오면 잠긴 것입니다.
   *  `67 02`가 돌아오면 뚫린 것입니다.
*  잠금이 풀린 뒤 routine을 실행하세요.

```
31 01 F0 0D
```

힌트:
*  진단 session 요청을 마음껏 보내세요. tester가 늘 하는 동작이라 거절당하지 않습니다.
*  이 ECU가 새 session을 어떻게 취급하는지 확인하세요. 실패 횟수도 잠금도 남지 않습니다.
*  seed는 한 번만 받아 두고 계속 쓰세요. 기본 session으로 돌아가지 않는 동안 유지됩니다.
*  매 시도마다 seed를 다시 받지 마세요. 계산 대상이 계속 바뀌어 탐색이 끝나지 않습니다.

routine 응답에 플래그가 담겨 옵니다!
