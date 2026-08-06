# active scan으로 scan response 받아내기

이 단계의 목표는 다음과 같습니다:
*  31바이트는 넉넉하지 않습니다. 그래서 규격은 31바이트를 한 번 더 줍니다.
*  대신 조건이 붙습니다.
*  advertising은 묻지 않아도 나갑니다. **scan response**는 그렇지 않습니다.
*  받고 싶은 스캐너가 scan request를 보내야 peripheral이 두 번째 payload로 답합니다.
*  그래서 스캔에는 두 종류가 있습니다.
   *  **passive scan**은 듣기만 합니다. 보는 쪽을 드러내지 않습니다.
   *  **active scan**은 물어봅니다. 전파를 쏘므로 누군가 보고 있다는 것이 드러납니다.
*  이 키 포브는 원하는 것의 절반씩을 각각에 나눠 담았습니다.

과제:
*  먼저 passive scan으로 관찰해 절반을 모으세요.

        hcidump --passive

*  드러나기를 감수하고 active scan으로 나머지를 받아내세요.

        hcidump

*  두 절반을 순서대로 이어 붙이세요.

힌트:
*  두 출력을 비교하면 무엇이 늘어났는지 보입니다.
*  scan response의 조각 번호는 advertising에서 이어집니다.
*  양쪽을 다 모으면 순서가 저절로 정해집니다.

두 절반을 합치면 플래그가 됩니다!
