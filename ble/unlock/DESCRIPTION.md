# 권한 오류를 읽어 가며 characteristic에 쓰기

이 단계의 목표는 다음과 같습니다:
*  characteristic은 읽기만 하는 것이 아닙니다. 쓰기가 되는 것도 있습니다.
*  쓰면 동작이 바뀌는 peripheral은 관찰 대상이 아니라 조작 대상입니다.
*  이것은 바디 컨트롤 모듈의 Bluetooth 쪽입니다.
*  금고 characteristic은 `locked`를 돌려줍니다. 몇 번을 읽어도 그대로입니다.

과제:
*  쓰기가 가능한 characteristic이 무엇인지 알아내세요.
*  그 characteristic이 무엇을 요구하는지 알아내세요.
*  올바른 값을 써서 금고를 여세요.

힌트:
*  쓸 때는 값을 hex로 줍니다.

        gatttool -b <주소> --char-write-req -a <handle> -n d34dbeef

*  `-req`가 중요합니다. Write Request는 response를 받습니다. 성공 여부를 알 수 있습니다.
*  반대쪽인 Write Command는 보내고 잊는 방식입니다. 실패해도 조용합니다.
*  금고에 직접 써 보세요. peripheral이 어떻게 생각하는지 알려 줍니다.
*  attribute마다 권한이 있습니다. 돌아오는 오류가 어떤 권한을 어겼는지 말해 줍니다.
*  이 모듈을 설치한 사람이 attribute table에 메모를 남겼습니다.
*  characteristic 값이 아닌 부분을 읽는 방법은 이미 익혔습니다.

금고가 열리면 그 characteristic을 읽어 플래그를 확인하세요!
