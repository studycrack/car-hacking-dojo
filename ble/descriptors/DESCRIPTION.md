# characteristic 목록에 없는 descriptor 읽기 (Descriptors)

이 단계의 목표는 다음과 같습니다:
*  characteristic 하나는 최소 두 개의 attribute로 이루어집니다. 하나는 **declaration**(어떤 property를 가지며 값이 어디 있는지)이고, 다른 하나는 **값** 자체입니다.
*  여기에 **descriptor**가 더 붙을 수 있습니다. characteristic에 설명을 달아 주는 attribute입니다.
*  가장 흔한 것은 Characteristic User Description(UUID `0x2901`)입니다. 사람이 읽는 라벨이 들어가는 자리라서, 펌웨어 개발자들이 주석처럼 쓰다 보니 남기지 말아야 할 것이 남곤 합니다.
*  `--characteristics`로는 descriptor가 보이지 않습니다.
*  attribute table 전체를 열어 descriptor를 읽어야 합니다.

과제:
*  attribute table을 handle 단위로 전부 나열하세요.

```
gatttool -b <주소> --char-desc
```

*  출력을 세 종류로 나누세요.
   *  이미 아는 declaration
   *  그 값 handle
   *  나머지가 아무도 볼 거라 생각하지 않은 descriptor입니다.
*  descriptor handle을 읽으세요.

```
gatttool -b <주소> --char-read -a <descriptor handle>
```

힌트:
*  두 출력의 줄 수를 비교하세요. `--char-desc`가 characteristic 목록보다 훨씬 많고, 그 차이가 이 문제의 전부입니다.
*  UUID로 구분하세요. `0x2803`은 declaration, `0x2901`은 User Description입니다.
*  읽은 값이 hex로 나오면 ascii로 바꿔 보세요.

descriptor 하나에 플래그가 들어 있습니다!
