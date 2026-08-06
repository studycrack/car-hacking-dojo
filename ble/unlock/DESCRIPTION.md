# 권한 오류를 읽어 가며 characteristic에 쓰기 (Write)

이 단계의 목표는 다음과 같습니다:
*  characteristic은 읽기만 하는 것이 아닙니다. 쓰기가 되는 것도 있고, 쓰면 동작이 바뀌는 peripheral은 관찰 대상이 아니라 조작 대상입니다.
*  이것은 바디 컨트롤 모듈의 Bluetooth 쪽입니다.
*  금고 characteristic은 `locked`를 돌려주고, 몇 번을 읽어도 그대로입니다.
*  그 값은 attribute table 안에 적혀 있습니다.
*  올바른 값을 써서 금고를 열어야 합니다.

과제:
*  쓰기가 가능한 characteristic을 확인하세요. property 열에 `write`가 있는 것입니다.

```
gatttool -b <주소> --characteristics
```

*  금고에 아무 값이나 써 보세요. peripheral이 무엇을 요구하는지 오류로 알려 줍니다.

```
gatttool -b <주소> --char-write-req -a <handle> -n d34dbeef
```

*  attribute table을 훑어 설치한 사람이 남긴 메모를 찾으세요.

```
gatttool -b <주소> --char-desc
```

*  메모가 말하는 값을 써서 금고를 여세요.
*  금고 characteristic을 다시 읽어 `locked`가 아닌 값이 나오는지 확인하세요.

힌트:
*  `-req`를 쓰세요. Write Request는 response를 받아서 성공 여부를 알 수 있습니다.
*  `--char-write-cmd`는 쓰지 마세요. Write Command는 보내고 잊는 방식이라 실패해도 조용합니다.
*  돌아오는 오류를 읽으세요. 어떤 권한을 어겼는지 말해 줍니다.
*  값은 hex로 주세요. ascii 문자열이라면 먼저 hex로 바꿔야 합니다.

금고가 열리면 그 characteristic을 읽어 플래그를 확인하세요!
