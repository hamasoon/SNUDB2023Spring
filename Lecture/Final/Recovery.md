# Recovery System

## Recovery Alogrithm
- **Recovery Algorithm** : Algorithm that ensure atomicity and durability of transaction
    - **Atomicity** : All or nothing
    - **Durability** : Safe save
- 2 parts
    - **Analysis** : phase *during normal transaction* - Check which transaction need to be redone or undone and log enough information for recovery
    - **Redo** : phase *after failure* - Redo all transaction that need to be redone to ensure atomicity, durability and *consistency*

## Log-based Recovery
- Assumption
    - serial transaction
    - log is stored in stable storage directly

- **Log** : Sequence of **log records**
    - log must be stored in *stable storage*
    - 
- **Log record** : Record that contain information about transaction
    - Start of transaction : <*T<sub>i</sub>* Start>
    - Before <*T<sub>i</sub>*> executes write(*X*) : <*T<sub>i</sub>*,  *X*, *V<sub>old</sub>*, *V<sub>new</sub>*>
    - Finish of last statement : <*T<sub>i</sub>* Commit>
    - Rollback : <*T<sub>i</sub>* Abort>

#### Immediate Database Modification
- Reflect all update to database immediately **during transaction executed**
    - Log record is written **before** data is updated
- Logging for Immediate Database Modification
    - Transaction start : <*T<sub>i</sub>* Start>
    - Write(X) opeartion results in
        - write log : <*T<sub>i</sub>*, *X*, *V<sub>old</sub>*, *V<sub>new</sub>*>
        - update data(log is *prior* to data writing)
    - When *T<sub>i</sub>*

- Example : (B<sub>X</sub> denotes write block containing *X* from buffer to disk )
    | Log                              | Write    | Output/Remarks               |
    | -------------------------------- | -------- | ---------------------------- |
    | <*T<sub>0</sub>* Start>          |          |                              |
    | <*T<sub>0</sub>*, A, 1000, 2000> |          |                              |
    |                                  | A = 2000 | Update A in *bufferd* block  |
    | <*T<sub>0</sub>*, B, 2000, 2050> |          |                              |
    |                                  | B = 2050 | Update B in *bufferd* block  |
    | <*T<sub>0</sub>* Commit>         |          | Commit but not write to disk |
    | <*T<sub>1</sub>* Start>          |          |                              |
    | <*T<sub>1</sub>*, C, 700, 600>   |          |                              |
    |                                  | C = 600  | Update C in *bufferd* block  |
    |                                  |          | B<sub>B</sub>, B<sub>C</sub> |
    | T<sub>1</sub> Commit             |          |                              |
    |                                  |          | B<sub>A</sub>                |
    - Note that **disk write sequence is not same as log sequence**
        - Because log is written before data is updated
        - So, log sequence is not same as data update sequence

#### Redo and Undo : Based on Log
- **Redo** : Re-execute transaction that is not completed(to enusre durability)
    - **Redo** is needed when transaction is committed/aborted but not written to disk
    - Start from the **first** log record of transaction

- **Undo** : Rollback transaction that is not completed(to ensure atomicity)
    - **Undo** is needed when transaction is not committed/aborted
    - Start from the **last** log record of transaction

- Both **Redo** and **Undo** must be idempotent
    - **Idempotent** : Operation that can be applied multiple times without changing result
    - **Redo** and **Undo** must be idempotent because
        - **Redo** and **Undo** may be applied multiple times
        - Becuase of failure during **Redo** and **Undo** is possible

- Example
    | Case1                            | Case2                            | Case3                            |
    | -------------------------------- | -------------------------------- | -------------------------------- |
    | <*T<sub>0</sub>* Start>          | <*T<sub>0</sub>* Start>          | <*T<sub>0</sub>* Start>          |
    | <*T<sub>0</sub>*, A, 1000, 950>  | <*T<sub>0</sub>*, A, 1000, 950>  | <*T<sub>0</sub>*, A, 1000, 950>  |
    | <*T<sub>0</sub>*, B, 2000, 2050> | <*T<sub>0</sub>*, B, 2000, 2050> | <*T<sub>0</sub>*, B, 2000, 2050> |
    |                                  | <*T<sub>0</sub>* Commit>         | <*T<sub>0</sub>* Commit>         |
    |                                  | <*T<sub>1</sub>* Start>          | <*T<sub>1</sub>* Start>          |
    |                                  | <*T<sub>1</sub>*, C, 700, 600>   | <*T<sub>1</sub>*, C, 700, 600>   |
    |                                  |                                  | <*T<sub>1</sub>* Commit>         |
    - Case1 : Fail during *T<sub>0</sub>*
        - Undo <*T<sub>0</sub>*
    - Case2 : Commit *T<sub>0</sub>* but fail during *T<sub>1</sub>*
        - Redo <*T<sub>0</sub>*
        - Undo <*T<sub>1</sub>*
    - Case3 : Commit *T<sub>0</sub>* and *T<sub>1</sub>*
        - Redo <*T<sub>0</sub>*, <*T<sub>1</sub>*>

#### Checkpoint
- Problem of **Log-based Recovery**
    - **Redo** and **Undo** is time consuming
    - **Log** is large
        - searching entire log is time consuming
        - storing entire log is space consuming
    - To solve this problem, **Checkpoint** is used

- **Checkpoint** : Point in time that all buffered data(include **log**) is written to disk
    - Sequence
        - Write all log reocrds in main memory to disk
        - Write all modified buffer block to disk
        - Write **Checkpoint** record to log
    - Checkpoint is used to reduce **Redo** and **Undo** time
    - Checkpoint is used to reduce **log size**

#### Transaction Rollback - during normal execution
- Rollback is Undo of transaction

- Rollback of transaction *T<sub>i</sub>*
    - Search log from the end(for undo)
    - For each log record <*T<sub>i</sub>*, *X*, *V<sub>old</sub>*, *V<sub>new</sub>*>
        - Write *V<sub>old</sub>* to *X*
        - Write <*T<sub>i</sub>*, *X*, *V<sub>old</sub>*> : *redo-only log record*
    - Search until <*T<sub>i</sub>* Start> is found
        - Write <*T<sub>i</sub>* Abort> to log
        - *T<sub>i</sub>* enters **abort** state
            - Note that abort need **redo** operation not undo

## Recovery in Concurrent Transactions
- Extend the log-based recovery schemes
    - All transactions share a single disk buffer and a **single log**
    - log records of different transactions may be interspersed in the log
    - Buffer block may contain updated data of different transactions

- Assume using strict 2PL
    - **Strict 2PL** : Transaction holds all locks until it commits/aborts
    - **Strict 2PL** is used to ensure **serializability**
    - **Strict 2PL** is used to ensure **recoverability**

#### Checkpoint and Crash
- Decide Redo or Undo using Checkpoint time, Crash time, Committed time
    - Before Checkpoint : Nothing to do
    - After Checkpoint, Before Crash : Redo
    - After Crash : Undo

#### Recovery after System Crash
1. Redo Phase(repeating history)
    - Scan log *forward* from the beginning(last checkpoint)
    - Redo Operation
        - <*T<sub>i</sub>*, *X*, *V<sub>old</sub>*, *V<sub>new</sub>*> : Write *V<sub>new</sub>* to *X*
        - Write <*T<sub>i</sub>*, *X*, *V<sub>old</sub>*> : *redo-only log record*
    - Add to undo-list  
        - <*T<sub>i</sub>*, start>
    - Remove from undo-list
        - <*T<sub>i</sub>*, abort> or <*T<sub>i</sub>*, commit>

2. Undo Phase
   - Scan log *backward* from the end
   - Undo operation
       - Perform undo action and write redo-only log record(same as rollback)
   - Meet <*T<sub>i</sub>*, start>
       - Write <*T<sub>i</sub>*, abort> to log
       - remove from undo-list
   - Terminate when undo-list is empty

#### Recovery after System Crash : Example
```
<T0, start>
<T0, B, 2000, 2050>
<T1, start>
<checkpoint {T0, T1}>
<T1, C, 700, 600>
<T1, commit>
<T2, start>
<T2, A, 500, 400>
<T0, B, 2000>
<T0, abort>
CRASH!
<T2, A, 500>
<T2, abort>
```
- Analysis
    - Rollback operation of *T<sub>0</sub>*
        - Undo <*T<sub>0</sub>*, B, 2000, 2050>
        - Write <*T<sub>0</sub>*, B, 2000> : Redo-only log record
        - Write <*T<sub>0</sub>*, abort>
    - Redo Phase : start from the check point
        - <Checkpoint> : add *T<sub>0</sub>*, *T<sub>1</sub>* to undo-list
        - <*T<sub>1</sub>*, C, 700, 600> : Redo
        - <*T<sub>1</sub>*, commit> : Remove from undo-list
        - <*T<sub>2</sub>*, start> : Add to undo-list
        - <*T<sub>2</sub>*, A, 500, 400> : Redo
        - <*T<sub>0</sub>*, B, 2000> : Redo
        - <*T<sub>0</sub>*, abort> : Remove from undo-list
    - Undo Phase : start from the end(only check *T<sub>2</sub>*)
        - <*T<sub>2</sub>*, A, 500, 400> : Undo the redo operation
            - Write <*T<sub>2</sub>*, A, 500> : Redo-only log record
        - <*T<sub>2</sub>*, start> : Remove from undo-list
            - Write <*T<sub>2</sub>*, abort>

#### Recovery after System Crash : Example2
```
<T0, start>
<T0, A, 0, 10>
<T0, commit>
<T1, start>
<T1, B, 0, 10>
<T2, start>
<T2, C, 0, 10>
<T2, C, 10, 20>
<checkpoint {T1, T2}>
<T3, start>
<T3, A, 10, 20>
<T4, start>
<T4, D, 0, 10>
<T3, commit>
CRASH!
```
- Analysis
    - Redo : start from the check point
        - <Checkpoint> : Add *T<sub>1</sub>*, *T<sub>2</sub>* to undo-list
        - <*T<sub>3</sub>*, start> : Add to undo-list
        - <*T<sub>3</sub>*, A, 10, 20> : Redo
        - <*T<sub>4</sub>*, start> : Add to undo-list
        - <*T<sub>4</sub>*, D, 0, 10> : Redo
        - <*T<sub>3</sub>*, commit> : Remove from undo-list
    - Undo : start from the end
        - Only *T<sub>4</sub>* in undo-list
        - <*T<sub>4</sub>*, D, 0, 10> : Undo
            - Write <*T<sub>4</sub>*, D, 0> : Redo-only log record
        - <*T<sub>4</sub>*, start> : Remove from undo-list
            - Write <*T<sub>4</sub>*, abort>
        - <*T<sub>2</sub>*, C, 10, 20> : Undo
            - Write <*T<sub>2</sub>*, C, 10> : Redo-only log record
        - <*T<sub>2</sub>*, C, 0, 10> : Undo
            - Write <*T<sub>2</sub>*, C, 0> : Redo-only log record
        - <*T<sub>2</sub>*, start> : Remove from undo-list
            - Write <*T<sub>2</sub>*, abort>
        - <*T<sub>1</sub>*, B, 0, 10> : Undo
            - Write <*T<sub>1</sub>*, B, 0> : Redo-only log record
        - <*T<sub>1</sub>*, start> : Remove from undo-list
            - Write <*T<sub>1</sub>*, abort>

#### Log Record Buffering
- **Log Record Buffering** : Buffer log records in main memory
    - Normally, not directly written to disk
- Write log records to disk when
    - Buffer is full
    - **Log force** : Write all log records in buffer to disk
        - After commit

## Write-Ahead Logging(WAL)
- **Write-Ahead Logging(WAL)** : Write log records before writing data
    - Write log records to disk before writing data to disk
    - Guarantee atomicity and durability

- Rules
    1. Log record saved in stable storage in order in which they are written
    2. *T<sub>i</sub>* can only enter to commit state after all log records for *T<sub>i</sub>* have been written to stable storage
    3. Before a data item is written to disk, the log record for the write must be written to stable storage