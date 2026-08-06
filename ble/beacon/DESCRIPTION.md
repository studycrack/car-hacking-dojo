# 연결하지 않고 advertising만으로 읽어내기

이 단계의 목표는 다음과 같습니다:
*  지금까지의 peripheral은 모두 연결해서 다뤘습니다. 이번에는 연결하지 않아도 됩니다.
*  찾아지고 싶은 장치는 **advertising**을 합니다.
*  payload를 특정 상대 없이 계속 broadcast합니다.
*  연결도 핸드셰이크도 없습니다. 누가 듣고 있는지 peripheral이 알 방법도 없습니다.
*  advertising payload는 **AD 구조**의 나열입니다.
*  각각 길이 바이트, 타입 바이트, 데이터로 이루어집니다.

        02 01 06        길이 2, 타입 0x01 (Flags), 값 06
        14 ff 99 04 ..  길이 20, 타입 0xFF (Manufacturer Specific Data)

*  타입 `0xFF`는 회사 식별자 2바이트 뒤에 제조사가 원하는 것을 담는 자리입니다.
*  **advertising payload는 모든 구조를 합쳐 31바이트**입니다.
*  이 센서가 할 말은 거기에 들어가지 않습니다.
*  그래서 조각을 하나씩 돌려가며 broadcast합니다. 조각마다 앞에 위치가 붙습니다.

과제:
*  advertising payload를 그대로 관찰하세요.

        hcidump --passive

*  조각을 모두 볼 때까지 지켜본 뒤 순서대로 맞추세요.

힌트:
*  `hcitool lescan`은 주소를 알려 줍니다. 이름을 advertising하면 이름도 보여줍니다.
*  이 장치는 이름을 advertising하지 않습니다. `(unknown)`으로 나옵니다.
*  `hcidump --passive -n`을 쓰면 여러 번 보고해 줍니다.

조각을 순서대로 합치면 플래그가 됩니다!
