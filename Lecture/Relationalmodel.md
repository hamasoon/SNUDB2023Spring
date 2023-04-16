Relational Model
================

Terms
-----
1. Relation

2. Attribute Types

3. Relation Schema
- curre

4. Relation Instance
- current value of a relation

5. Keys
- Super key
    - set of attribute that sufficient enough to identify unique tuple
- Candidate key
    - minimal super key
- Primary key
    - representative candidate key &rarr; designer decide
- Foreign key
    - bridge key between two tables(kind of pointer)

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