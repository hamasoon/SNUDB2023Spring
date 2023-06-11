## Discussion

#### 19-1
> Difference between non-volatile storage and stable storage

- non-volatile storage : data is not lost when power is off
  - but can't ensure data is not lost when system crash
- stable storage : data doesn't lost for any reason
  - but it's just concept, not exist in real world
  - to implement this storage, we use redundant storage and recovery algorithm

#### 19-5
> Suppose the log after crash is as shown. Determine which transactions must be redone and which must be undone.
```
T0 start
T0, A, 0, 10
T0 commit
T1 start
T1, B, 0, 10
T2 start
T2, C, 0, 10
T2, C, 10, 20
T3 start
T3, A, 10, 20
T1, D, 5, 0
T3 commit
```

##### Analysis
1. Redo Phase
  - T0 start : add to undo-list
  - T0, A, 0, 10 : redo
  - T0 commit : remove from undo-list
  - T1 start : add to undo-list
  - T1, B, 0, 10 : redo
  - T2 start : add to undo-list
  - T2, C, 0, 10 : redo
  - T2, C, 10, 20 : redo
  - T3 start : add to undo-list
  - T3, A, 10, 20 : redo
  - T1, D, 5, 0 : redo
  - T3 commit : remove from undo-list
2. Undo Phase
  - T1 start : remove from undo-lists
  - T1, B, 0, 10 : undo - leave redo-only log (T1, B, 0)
  - T2 start : remove from undo-list
  - T2, C, 0, 10 : undo - leave redo-only log (T2, C, 0)
  - T2, C, 10, 20 : undo - leave redo-only log (T2, C, 10)
  - T3 start : skip - not in undo-list
  - T3, A, 10, 20 : skip - not in undo-list
  - T1, D, 5, 0 : undo - leave redo-only log (T1, D, 5)
  - T3 commit : skip - not in undo-list
  
#### 19-7
```
T0 start
T0, A, 0, 10
T0 commit
T1 start
T1, B, 0, 10
T2 start
T2, C, 0, 10
T2, C, 10, 20
check point {T1, T2}
T3 start
T3, A, 10, 20
T3, A, 10
T3 abort
```
##### Analysis
1. Redo Phase : start from check point
  - check point {T1, T2} : add to undo-list
  - T3 start : add to undo-list
  - T3, A, 10, 20 : redo
  - T3, A, 10 : redo
  - T3 abort : remove from undo-list
2. Undo Phase
  - T2, C, 10, 20 : undo - leave redo-only log (T2, C, 10)
  - T2, C, 0, 10 : undo - leave redo-only log (T2, C, 0)
  - T2 start : remove from undo-list
  - T1, B, 0, 10 : undo - leave redo-only log (T1, B, 0)
  - T1 start : remove from undo-list