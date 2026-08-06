# declaration에 없는 기능 쓰기

이 단계의 목표는 다음과 같습니다:
*  이 동글을 열거하면 디버그 characteristic이 `debug channel idle`을 돌려줍니다.
*  그 declaration에는 `READ`만 있습니다.
*  notify property가 없으니 subscribe할 것도 없어 보입니다.
*  declaration을 보고 화면을 만드는 도구는 그 선택지를 아예 보여주지 않습니다.
*  하지만 characteristic 목록 말고 **attribute table**을 보세요.
*  그 characteristic 아래에 `0x2902`가 앉아 있습니다.
*  CCCD는 notification을 켜기 위한 것입니다. notification을 못 보내는 characteristic에 있을 이유가 없습니다.

과제:
*  attribute table에서 그 CCCD를 찾으세요.
*  있으면 안 될 그 descriptor에 값을 쓰고, 들으세요.

힌트:
*  declaration의 property 바이트는 **펌웨어가 밝힌 의도**입니다. 스택이 강제하는 권한이 아닙니다.
*  CCCD에 쓰기가 들어올 때 그것을 확인하는 코드는 없습니다.
*  펌웨어가 notification을 보낼 때 확인하는 코드도 없습니다.
*  누군가 화면을 정리하려고 notify property만 껐습니다.
*  실제로 notification을 보내는 코드는 그대로 두었습니다.

subscribe가 켜지면 notification으로 플래그가 도착합니다!
