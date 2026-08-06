# confirmation을 보내며 indication 끝까지 받기

이 단계의 목표는 다음과 같습니다:
*  notification은 보내고 잊는 방식입니다. 도착하지 않아도 아무도 모릅니다.
*  중요한 것에는 그 거래가 맞지 않습니다.
*  그래서 ATT에는 두 번째 방식인 **indication**이 있습니다.
*  클라이언트가 Handle Value Confirmation으로 확인해야 다음 것이 옵니다.
*  한 번에 하나씩, 확인받으며, 순서대로입니다.
*  이 이모빌라이저는 audit log를 그 방식으로 보관합니다.

과제:
*  이 characteristic에 맞는 값으로 subscribe하세요.
*  도착하는 record마다 confirmation을 보내며 log를 끝까지 받아내세요.

힌트:
*  indication만 하는 characteristic에 notification으로 subscribe하면 아무 일도 일어나지 않습니다.
*  CCCD에 쓰는 값이 그 characteristic이 실제로 하는 일과 맞아야 합니다.
*  `0x0001`과 `0x0002`는 다릅니다.
*  record가 와도 confirmation을 하지 않으면 첫 번째에서 멈춥니다.
*  듣기만 하고 답하지 않으면 하나만 받고 나머지를 영영 기다립니다.

log를 전부 모으면 플래그가 됩니다!
