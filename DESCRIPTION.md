자동차의 컨트롤러들은 주소도, 인증도, 암호화도 없는 버스로 서로 대화합니다.
버스에 닿을 수 있으면 누구에게든 무엇이든 말할 수 있고, 누구인 척도 할 수
있습니다. 이 도장의 모든 공격이 그 사실에서 나옵니다.

달리는 차의 트래픽을 읽고, 모듈이 따르는 frame을 위조하고, 아무도 규격을
주지 않은 메시지 layout을 역공학합니다. 그다음은 정비 장비가 쓰는 진단
프로토콜 **UDS**, 그리고 진단 session과 ECU 내부 사이를 막고 선 인증입니다.
마지막은 차가 응답하는 Bluetooth이고, 여기에는 앞의 두 모듈에서 공격한 바로
그 버스에 연결된 애프터마켓 동글이 포함됩니다. 캡스톤이 그 bridge입니다.

여기 있는 것은 전부 시뮬레이션입니다. 워크스페이스에는 가상 CAN 인터페이스
`vcan0`과 advertising 중인 BLE peripheral들이 있고, 둘 다 시뮬레이션된 차량에
붙어 있습니다. 시뮬레이션한 것은 전선과 전파뿐이고, 도구와 frame 형식,
프로토콜과 공격 기법은 모두 실제 그대로입니다.

## 어디서 시작할까

모듈은 난이도가 아니라 인터페이스로 묶여 있고, 각 모듈 안에서는 문제들이 서로
이어집니다. 모듈을 따라 내려가면 경사는 이미 만들어져 있습니다.

아래는 다른 관점입니다. 같은 34문제를 무엇을 요구하는지에 따라 나눈 것입니다.

**시키는 대로 해 보기.** 설명이 명령을 알려 줍니다. 실행해 보고, 버스나
peripheral이 묻는 사람 누구에게나 내준다는 것을 확인하세요.

> `sniffing` · `discovery` · `descriptors` · `encoding` · `notify` · `beacon`

**두 가지를 엮기.** 무언가를 읽고, 그것을 씁니다. 돌아가는 session counter,
어느 조각이 어디로 가는지 알려 주는 index, 듣고 싶은 것을 유발하기 전에 먼저
있어야 하는 subscribe 같은 것들입니다.

> `filtering` · `fob-capture` · `injection` · `fragments` · `unlock` ·
> `sequence` · `stream` · `indicate` · `trigger` · `service-data` ·
> `scan-response` · `long-write` · `dbc`

**아무도 알려 주지 않은 것 찾기.** discovery 응답에는 없는데 대답은 하는
handle, 어느 규격에도 없는 service, 직접 알아내야 하는 scale 같은
것들입니다.

> `hidden-notify` · `hidden-handles` · `ecu-discovery` · `fault-memory` ·
> `iso-tp` · `firmware-dump` · `spoofing` · `odometer` · `gateway` ·
> `rolling-code`

**막으려고 만든 것을 뚫기.** 앞에 진짜 방어가 있고, 장식이 아닙니다. alive
counter와 checksum, 시도 제한, 위조할 수 없는 MAC입니다. 각각이 무엇을 덮고
있는지 정확히 이해한 뒤, 덮지 않은 곳으로 들어가야 통과합니다.

> `integrity` · `security-access` · `reflash` · `secoc` · `pivot`

처음이라면 `sniffing`이 첫 모듈의 첫 문제이고, 호기심 말고는 요구하는 것이
없습니다. 버스를 다뤄 본 적이 있다면 `spoofing`이나 `iso-tp`에서 시작하고,
낯선 것이 나오면 그때 돌아오세요.
