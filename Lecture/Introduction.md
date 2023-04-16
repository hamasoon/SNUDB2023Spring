Terms
=====
1. Data : formal description of entity, event, phenomena, idea

2. Database
    - integrated collection of persistent data
        - Persistent data(영속적 데이터)란, 컴퓨터 시스템이 종료되거나 프로그램이 종료되더라도 유지되는 데이터를 의미합니다. 즉, 메모리에 저장되지 않고 디스크, SSD 등의 저장장치에 저장되는 데이터를 말합니다.
    - representing the information of interest
    - for various programs that compose the compterized information system of an organization

3. DBMS : Database Management System
    - Why we need it?   

    1. 데이터 중복(redundancy) 최소화: DBMS는 중복 데이터를 최소화하고 데이터 일관성을 유지합니다. 이를 통해 데이터의 정확성과 일관성을 높일 수 있습니다.

    2. 데이터 무결성 보장: DBMS는 데이터 무결성을 보장합니다. 이는 데이터의 정확성과 일관성을 유지하고 데이터의 무결성을 위반하는 작업을 방지합니다.
        - 데이터 무결성은 데이터베이스에 저장된 데이터의 정확성, 일관성, 유효성을 지키는 것이다. 보통 데이터 무결성은 제약조건으로 데이터베이스 시스템이 강제한다.

    3. 데이터 보안 강화: DBMS는 데이터 보안을 강화합니다. 사용자 권한을 관리하고 데이터 접근 권한을 제한하여 데이터 유출과 같은 보안 위협을 방지합니다.

    4. 데이터의 공유 및 동시 접근: DBMS는 데이터의 공유와 동시 접근을 지원합니다. 이를 통해 여러 사용자가 동시에 데이터에 접근하여 업무 효율성을 높일 수 있습니다.

    5. 데이터 백업 및 복구: DBMS는 데이터 백업과 복구를 지원합니다. 이를 통해 데이터 손실 및 장애 상황에서도 데이터를 보호하고 복구할 수 있습니다.

    6. 데이터 일관성 유지(inconsistency): DBMS는 데이터 일관성을 유지하며 데이터간의 관계를 유지합니다. 이를 통해 데이터의 정확성과 일관성을 유지할 수 있습니다.

    - Integrity : details in 4th chapter

4. Abstraction
    - physical - actual storage/ logical - data relationship/ view - data usage
    - each layer doesn't needed to understand implementation of each layer(Key point!)
    - Data independence : modifying each levels implementation must not affect to usage of higher levels, 

5. Schema / Instances - Concepts / Contents - Type / Variables

6. Data Models
    - a collection of conceptual tools for describing data, data relationships, data semantics, and consistency constraints.
    - The framework/formalism for representing data and their relationships

7. DDL, DML, Query
    - DDL(Data Definition Language) : Operation defining DB schema
        - Create Table
        - Drop Table
        - Alter
    - DML(Data Manipulation Language)
        - Insert
        - Retrieve(Select)
        - Delete
        - Update
    - Query
        - a statement requesting the retrieval of information(part of DML)
        - 데이터베이스에서 데이터를 검색하거나 조작하는데 사용되는 명령어 집합을 말합니다. 쿼리는 데이터베이스 내의 테이블, 뷰, 프로시저 등의 개체에 대한 검색, 삽입, 수정, 삭제 등을 수행할 수 있습니다.