Terms
-----
#### 1. Integrity Constraints
- By ensuring quthorized changes to database do not result a inconsistency(guarding accidental damage)
    - set data type
    - unique
    - not null
    - primary key : unique + not null
    - foreign key : referential integrity
        - 어떤 foreign key던지 항상 연결되어 있는 다른 테이블의 primary key(즉, 레퍼런스)가 제대로 존재해야 한다는 뜻입니다. 따라서 업데이트나 삭제가 일어나도 연결된 두테이블이 항상 synchronized 되게 해주는 법칙입니다. 

Operartions
-----------
- Create Table
```sql
CREATE TABLE student(
    ID          CHAR(5),
    name        VARCHAR(20) NOT NULL,
    dept_name   VARCHAR(20),
    salary      NUMERIC(8, 2),
    PRIMARY KEY(ID),
    FOREIGN KEY(dept_name) REFERENCES department
)

CREATE TABLE movie_revenue (
    mov_id    INT,
    revenue   INT,
    FOREIGN KEY (mov_id) REFERENCES movie(mov_id)
)

CREATE TABLE teaches(
    ID	    		varchar(5), 
	course_id		varchar(8),
	sec_id			varchar(8), 
	semester		varchar(6),
	year			numeric(4,0),
	primary key (ID, course_id, sec_id, semester, year),
	foreign key (course_id,sec_id, semester, year) references section
		on delete cascade,
	foreign key (ID) references instructor
	    on delete cascade
)
```
- select, from, where, rename - so used to... i will skip this
- 

2. aggregation
- 데이터베이스에서 집계(Aggregation)는 여러 개의 데이터 행(row)을 하나의 그룹으로 묶어서 새로운 결과를 만드는 연산입니다. 집계 함수는 합계, 평균, 최대, 최소 등이 있으며, 이러한 함수를 사용하여 그룹화된 데이터에 대한 정보를 분석할 수 있습니다.
- Aggregation 함수들은 기본적으로 null value를 무시한다

3. Referential integrity
- 관계형 데이터베이스에서 두 개 이상의 테이블 간에 관계가 있는 경우, 이러한 관계가 항상 일관되고 유지되도록 보장하는 기능입니다.

