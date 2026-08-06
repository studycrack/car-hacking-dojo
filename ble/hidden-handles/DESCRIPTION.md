# discovery 응답에 없는 handle 찾아내기 (Handle Walking)

이 단계의 목표는 다음과 같습니다:
*  지금까지의 열거는 peripheral에게 스스로를 설명해 달라고 부탁하고, 그 답을 그대로 믿는 방식이었습니다.
*  그런데 그 답은 펌웨어가 만듭니다. Read By Type 응답은 장치가 **보내기로 선택한** 목록이고, 장치는 원하는 것을 빼놓을 수 있습니다.
*  하지만 discovery 응답에서 빠져도 attribute table에서 사라지지는 않습니다. **handle은 그대로 동작합니다.**
*  ATT에는 Read Request가 왔을 때 discovery 목록을 확인하는 절차가 없습니다. handle을 찾아 그대로 내줄 뿐입니다.
*  handle을 하나씩 올려 가며 읽어 목록에 없던 attribute를 찾아야 합니다.

과제:
*  먼저 discovery로 알려진 handle 목록을 확보하세요.

```
gatttool -b <주소> --char-desc
```

*  `0x0001`부터 handle을 하나씩 올려 가며 직접 읽으세요.

```
gatttool -b <주소> --char-read -a 0x0001
```

*  응답을 두 종류로 나누세요.
   *  `Invalid handle`이면 그 자리에는 아무것도 없습니다.
   *  그 밖의 응답이 오면 무언가 있습니다.
*  응답은 왔는데 목록에는 없던 handle을 찾아 읽으세요.

힌트:
*  반복문을 하나 짜세요. handle은 작은 정수이고 개수도 많지 않습니다.

```
for h in $(seq 1 60); do
  printf '%04x ' $h
  gatttool -b <주소> --char-read -a $h
done
```

*  느리면 `/challenge/ble.py`의 클라이언트를 쓰세요. 연결을 한 번만 열고 전부 돌 수 있습니다.
*  두 목록을 나란히 놓고 비교하세요. 대조하지 않으면 무엇이 숨어 있었는지 알 수 없습니다.

숨어 있던 attribute 안에 플래그가 있습니다!
