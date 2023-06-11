## Discussion 18.2
> What is starvation? and show example
- starvation is a situation where a transaction continously deferred due to other transaction get S-lock or X-lock

example
|    T1     |        T2        |    T3     |    T4     |
| :-------: | :--------------: | :-------: | :-------: |
| lock-S(A) |                  |           |           |
|           | lock-X(A) denied |           |           |
|           |                  | lock-S(A) |           |
| unlock(A) |                  |           |           |
|           |                  |           | lock-S(A) |
|           |                  | unlock(A) |           |

- T2 is starvation due to other transaction keep get S-lock

## Exercise 18.1
> Show 2PL protocol ensure conflict serializable

- 2PL protocol : divide transaction into 2 phase
  - Locking phase
    - Acquire all locks
    - Upgrade S to X Lock
  - Unlocking phase : release all locks
    - Release all locks
    - Downgrade X to S Lock

2PL은 다음과 같은 규칙에 따라 잠금을 부여하고 해제함으로써 충돌을 방지합니다:

읽기 잠금 (shared lock)은 여러 트랜잭션이 동시에 가질 수 있지만, 쓰기 잠금 (exclusive lock)은 트랜잭션이 가질 때 다른 트랜잭션은 접근할 수 없습니다.
트랜잭션은 데이터를 수정하기 위해 쓰기 잠금을 획득하기 전까지는 읽기 잠금만 획득하게 되므로 충돌이 발생하지 않습니다.
트랜잭션이 쓰기 잠금을 획득하면 다른 트랜잭션들은 해당 데이터에 대한 읽기와 쓰기 잠금을 요청할 수 없으므로 충돌이 발생하지 않습니다.
2PL 프로토콜은 다음과 같은 특성을 가지므로 conflict serializability를 보장합니다:

## Exercise 18.2
> Insert Lock and Unlock command to schedule properly for 2PL protocol
```
T34 read(A);
    read(B);
    if A = 0 then B := B + 1;
    write(B);
T35 read(B);
    read(A);
    if B = 0 then A := A + 1;
    write(A);
```

Answer
```
T34 S-lock(A);
    read(A);
    X-lock(B);
    read(B);
    if A = 0 then B := B + 1;
    unlock(A);
    write(B);
    unlock(B);
T35 S-lock(B);
    read(B);
    X-lock(A);
    read(A);
    if B = 0 then A := A + 1;
    unlock(B);
    write(A);
    unlock(A);
```

#### 18.2.2
> Is above schedule could be deadlock?

|         T34         |         T35         |
| :-----------------: | :-----------------: |
|      S-lock(A)      |                     |
|       read(A)       |                     |
|                     |      S-lock(B)      |
|                     |       read(B)       |
| X-lock(B) : Denied! |                     |
|                     | X-lock(A) : Denied! |

Yes, it could be deadlock

## Exercise 18.3
> What is the difference between strict 2PL and rigorous 2PL?

- Strict 2PL : maintain X-lock until commit or abort
  - Avoid Cascading Rollback
- Rigoous 2PL : maintain all lock until commit or abort

## Exercise 18.18
> 1. What is strict 2PL? and what is it's advantage and disadvantage?
> 2. Why many DBMS use strict 2PL despite it's disadvantage?

1. strict 2PL : maintain X-lock utill commit or abort
  - Advantage : Avoid Cascading Rollback
    - Proof : due to some transaction keep X-lcoak until commit or abort, other transaction can't get any lock before it's commit
    - So, any operation after x-lock can't be occured so, it can't be cascading rollback
  - Disadvantage : Starvation
    - Bad concurrency
  
2. s
  - Prevent cascading abort(rollback)
  - Only maintain X-lock until commit or abort
    - Better concurrency performance than rigorous 2PL