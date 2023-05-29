Relational Model
================
#### - Pro
- 일관성: 관계형 데이터베이스 모델은 데이터의 논리적 일관성을 유지하기 위해 정규화(Normalization)를 사용합니다. 이를 통해 중복 데이터를 제거하고 데이터의 일관성을 유지할 수 있습니다.

- 유연성: 관계형 데이터베이스 모델은 데이터의 유형이나 크기에 관계없이 처리할 수 있습니다. 또한, 데이터의 추가, 수정, 삭제에 대한 처리가 쉽고 빠릅니다.

- 보안성: 관계형 데이터베이스 모델은 보안성이 높습니다. 액세스 제어, 권한 관리 등의 보안 기능을 제공합니다.

- 쿼리 언어: SQL을 사용하여 데이터를 쉽게 검색하고 필요한 정보를 추출할 수 있습니다.

- 확장성: 관계형 데이터베이스 모델은 대규모 데이터베이스 시스템에 적합합니다. 데이터의 양이 증가해도 성능이 유지됩니다.

#### - Con
- 복잡성: 대규모 시스템에서는 데이터의 일관성을 유지하기 위한 정규화 과정이 복잡해질 수 있습니다.

- 성능: 조인 연산 등의 처리가 느릴 수 있습니다. 따라서 대규모 데이터베이스에서는 성능이 저하될 수 있습니다.

- 비용: 관계형 데이터베이스는 대부분 상용 데이터베이스 시스템으로 구성되어 있기 때문에 구축 및 유지보수 비용이 높을 수 있습니다.

- 제약사항: 관계형 데이터베이스 모델에서는 데이터베이스 스키마가 미리 정의되어 있어야 합니다. 따라서 스키마 변경에 대한 제약사항이 있을 수 있습니다.

- 데이터 일관성 문제: 관계형 데이터베이스 모델에서는 외래키(Foreign Key) 등의 제약 조건을 사용하여 데이터 일관성을 유지합니다. 그러나 이러한 제약 조건이 잘못된 경우 데이터 일관성 문제가 발생할 수 있습니다.

Terms
-----
1. Relation : Single file or table of database(Relation = Relation Schema + Relation Instance)

2. Relation Schema : Define structure of relation

3. Relation Instance : Data inside relation

4. Attribute Types
    - Atomic : must be minimal unit 
        - exception : composite attribute, multi-valued attribute

5. Keys
    - Super key
        - set of attribute that sufficient enough to identify unique tuple
    - Candidate key
        - minimal super key
    - Primary key
        - representative candidate key &rarr; designer decide
        - Not null & unique
    - Foreign key
        - bridge key between two tables(kind of pointer)
        - type equality
        - Referential integrity
            - 특히, 참조하는 테이블의 primary key 값이 변경되거나 삭제될 때, 이에 의존하는 다른 테이블의 foreign key 값도 함께 변경되거나 삭제되는 것을 의미합니다.

6. Query Languages
    - procedural : how to get data?
    - non procedural : what data are needed?(SQL)

Relational Algebra
------------------
1. Select : get tuples from relation satisfying condition
    - form : $\sigma_{condition}(R)$
2. Project : get specific attribute from relation
    - form : $\Pi_{attribute-list}(R)$
3. Set operation : Union, Difference, Intersection
    - form : $r \cup s, r - s, r \cap s$
4. Cartesion-Product : ***all possible combination*** list of two relation
    - form : $r \times s$
    - So, normally using select operation to get valid combination
        - form : $\sigma_{condition}(r \times s )$
5. Rename
    - form : $\rho_{newattrnames}(R)$
6. Natural Join
    - from : $r \triangleright\triangleleft_{condition} s$

cf) what is ***basic*** operation?