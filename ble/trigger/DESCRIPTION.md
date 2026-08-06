# subscribe를 먼저 걸고 request 보내기

이 단계의 목표는 다음과 같습니다:
*  이제 subscribe도 해 봤고 쓰기도 해 봤습니다. 이 모듈은 둘 다 필요합니다.
*  **순서**가 중요합니다.
*  이 키리스 모듈은 request를 받으면 답을 돌려줍니다.
*  한 characteristic에 쓰면 다른 characteristic으로 답을 notification으로 밀어 줍니다.
*  그런데 그 답은 **그 순간 subscribe하고 있는 쪽**에게만 갑니다. 큐도 없습니다.
*  먼저 쓰면 답은 만들어져서 아무도 없는 쪽으로 밀려나고 사라집니다.

과제:
*  답이 오는 characteristic에 먼저 subscribe하세요.
*  그다음 request characteristic에 쓰세요.

힌트:
*  CAN 모듈에서 포브가 한 번만 전송했던 것과 같은 이야기입니다.
*  나중에 시작한 캡처는 아무것도 찾지 못했습니다.
*  한 가지가 더 있습니다. 이것이 어떤 도구로 풀 수 있는지를 결정합니다.
*  **답은 요청한 그 연결로 돌아옵니다.**
*  한 연결에서 subscribe하고 다른 연결에서 쓰면 똑같이 아무 소리도 듣지 못합니다.
*  하나의 연결을 열어 둔 채 그 안에서 두 가지를 모두 해야 합니다.
*  `/challenge/ble.py`의 클라이언트나 `bleak`을 쓰면 됩니다.

notification으로 도착한 답이 플래그입니다!
