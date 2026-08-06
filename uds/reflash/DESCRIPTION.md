# calibration block을 다시 써서 이모빌라이저 해제하기

이 단계의 목표는 다음과 같습니다:
*  컨트롤러 메모리를 읽는 것이 정찰이라면, 쓰는 것은 공격입니다.
*  UDS의 재기록 절차는 세 단계로 정해져 있습니다.

| request | 뜻 |
| --- | --- |
| `34 <fmt> <ALFI> <주소> <크기>` | RequestDownload, 어디에 얼마나 쓸지 알린다 |
| `36 <n> <데이터...>` | TransferData, block 하나. `n`은 `01, 02, 03, ...` |
| `37 <checksum>` | RequestTransferExit, 마치고 바이트가 온전함을 증명한다 |

*  `RequestDownload`는 `74`와 길이 형식 바이트, 받아 줄 최대 block size로 답합니다.
*  `TransferData`는 반드시 **다음** block 번호를 실어야 합니다.
*  반복하거나 건너뛰면 `requestSequenceError`입니다.
*  `RequestTransferExit`은 알린 길이가 전부 도착하고 checksum이 맞을 때만 기록합니다.
*  calibration 영역은 `0x08010000`에 있습니다.
*  그 안에 이모빌라이저 무장 여부를 결정하는 4바이트 필드가 있습니다.
*  그 값이 `DE AD BE EF`이면 해제된 것으로 봅니다.

과제:
*  calibration 영역을 먼저 읽어 구조를 파악하세요. `0x23`이 여기서도 동작합니다.
*  이모빌라이저가 해제되도록 calibration block을 다시 쓰세요.

힌트:
*  이 절차는 **programming session** 밖에서는 동작하지 않습니다.
*  checksum은 부트로더가 오래 써 온 방식입니다.
*  바이트를 모두 더한 뒤 2의 보수를 취하고 1바이트로 자릅니다.
*  구조체 안에 필드 layout이 적혀 있습니다. 덮어쓰기 전에 읽어서 확인하세요.

기록이 반영되면 컨트롤러가 결과를 알려 줍니다. 거기에 플래그가 담겨 옵니다!
