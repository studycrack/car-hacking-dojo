# characteristic 목록에 없는 descriptor 읽기

이 단계의 목표는 다음과 같습니다:
*  characteristic 하나는 최소 두 개의 attribute로 이루어집니다.
*  하나는 **declaration**입니다. 어떤 property를 가지며 값이 어디 있는지 말합니다.
*  다른 하나는 **값** 자체입니다.
*  여기에 **descriptor**가 더 붙을 수 있습니다. characteristic에 설명을 달아 주는 attribute입니다.
*  가장 흔한 것은 Characteristic User Description입니다. UUID는 `0x2901`입니다.
*  사람이 읽는 라벨이 들어가는 자리입니다.
*  펌웨어 개발자들이 주석처럼 쓰다 보니 남기지 말아야 할 것이 남곤 합니다.

과제:
*  attribute table을 handle 단위로 전부 확인하세요.

        gatttool -b <주소> --char-desc

*  descriptor를 읽어 보세요.

힌트:
*  `--characteristics`로는 descriptor가 보이지 않습니다. descriptor는 characteristic이 아닙니다.
*  `--char-desc` 출력은 characteristic 목록보다 줄이 훨씬 많습니다.
*  일부는 이미 아는 declaration이고, 일부는 값입니다.
*  나머지가 아무도 볼 거라 생각하지 않은 descriptor입니다.

descriptor 하나에 플래그가 들어 있습니다!
