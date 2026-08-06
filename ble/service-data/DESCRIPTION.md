# AD 구조는 타입마다 layout이 다르다

이 단계의 목표는 다음과 같습니다:
*  Manufacturer Specific Data는 회사 식별자 2바이트 뒤가 자유였습니다.
*  advertising에는 더 구조적인 것도 있습니다.
*  **Service Data**(AD 타입 `0x16`)는 데이터가 어느 service의 것인지 지정합니다.
*  구조는 16비트 service UUID로 시작하고, 그 뒤에 payload가 옵니다.

```
12 16 6f fd 00 70 77 6e ...
^  ^  ^^^^^ ^^^^^^^^^^^^^
|  |  UUID  실제 데이터
|  타입 0x16
길이
```

*  이 트래커도 앞의 beacon처럼 조각을 돌려가며 broadcast합니다.

과제:
*  advertising을 관찰해 Service Data 구조를 찾으세요.
*  타입에 맞게 payload가 시작하는 위치를 잡으세요.
*  조각만 뽑아 순서대로 맞추세요.

힌트:
*  구조 전체를 데이터로 취급하면 조각마다 앞에 UUID 2바이트가 붙습니다.
*  거의 맞아 보이는데 틀린 상태가 됩니다. 완전히 틀린 것보다 알아채기 어렵습니다.
*  AD 구조는 **타입이 있고**, 타입마다 layout이 정해져 있습니다.
*  이 payload가 Service Data라는 것을 알면 데이터가 어디서 시작하는지도 압니다.

UUID를 걷어내고 순서대로 합치면 플래그가 됩니다!
