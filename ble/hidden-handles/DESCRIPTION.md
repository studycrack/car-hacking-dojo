# discovery 응답에 없는 handle 찾아내기

이 단계의 목표는 다음과 같습니다:
*  지금까지의 열거는 peripheral에게 스스로를 설명해 달라고 부탁하는 방식이었습니다.
*  그리고 그 답을 그대로 믿었습니다.
*  그 답은 펌웨어가 만듭니다.
*  Read By Type response는 장치가 **보내기로 선택한** 목록입니다.
*  장치는 원하는 것을 빼놓을 수 있습니다.
*  하지만 discovery 응답에서 빠져도 attribute table에서 사라지지는 않습니다.
*  **handle은 그대로 동작합니다.**
*  ATT에는 Read Request가 왔을 때 discovery 목록을 확인하는 절차가 없습니다.
*  handle을 찾아 그대로 내줄 뿐입니다.

과제:
*  `0x0001`부터 handle을 하나씩 올려 가며 읽어 보세요.
*  discovery 목록에 없던 attribute를 찾아내세요.

힌트:
*  `Invalid handle`이 오면 그 자리에는 아무것도 없습니다.
*  그 밖의 response가 오면 무언가 있습니다.
*  handle은 작은 정수이고 개수도 많지 않습니다. 반복문을 하나 짜세요.

숨어 있던 attribute 안에 플래그가 있습니다!
