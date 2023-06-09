## Discussion

#### 17-3
> For each of the following cases, determine which of the five states of a transactions T<sub>1</sub> is in.
> 1. T<sub>1</sub> has just started and accessing its first database item X.
> 2. T<sub>1</sub> is currently on hold waiting for a certain resource to be available for tis next instruction to proceed.
> 3. It has been determined that T<sub>1</sub> cannot proceed to complete its task.

1. Active : T<sub>1</sub> has just started and accessing its first database item X.
2. Active : T<sub>1</sub> just wait &rarr; still working on transaction
3. Failed

#### 17-6
> Determine follwing schedules are conflict serializable or not.
> if not, find all conflict insturctions pairs

|         T1         |   T2    |  T3   |  T4   |                T5                 |
| :----------------: | :-----: | :---: | :---: | :-------------------------------: |
|                    | read(X) |       |       |                                   |
| read(Y)<br>read(Z) |         |       |       |                                   |
|                    |         |       |       | read(V) <br> read(W) <br> read(W) |
|| ||||

## Practice

#### 17.1
> What is a cascadeless schedule?
- All updated(written) data allow to read/write only after commit


## Exercise
