# active scan으로 scan response 받아내기 (Scan Response)

이 단계의 목표는 다음과 같습니다:
*  31바이트는 넉넉하지 않아서, 규격은 31바이트를 한 번 더 줍니다. 대신 조건이 붙습니다.
*  advertising은 묻지 않아도 나가지만 **scan response**는 그렇지 않습니다. 스캐너가 scan request를 보내야 peripheral이 두 번째 payload로 답합니다.
*  그래서 스캔에는 두 종류가 있습니다.
   *  **passive scan**은 듣기만 하고, 보는 쪽을 드러내지 않습니다.
   *  **active scan**은 물어봅니다. 전파를 쏘므로 누군가 보고 있다는 것이 드러납니다.
*  이 키 포브는 필요한 것의 절반씩을 각각에 나눠 담았습니다.
*  양쪽을 다 모아 이어 붙여야 합니다.

과제:
*  먼저 passive scan으로 관찰해 절반을 모으세요.

```
hcidump --passive
```

*  드러나기를 감수하고 active scan으로 나머지를 받아내세요.

```
hcidump
```

*  두 출력을 비교해 무엇이 늘어났는지 확인하세요. 늘어난 쪽이 scan response입니다.
*  두 절반의 조각을 위치대로 이어 붙이세요.

힌트:
*  조각 번호를 이어서 세세요. scan response의 번호는 advertising에서 이어집니다.
*  passive만 돌리고 끝내지 마세요. 절반에서 번호가 끊깁니다.
*  `-n`을 붙여 여러 번 보고받으세요.

두 절반을 합치면 플래그가 됩니다!
