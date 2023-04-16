ER Model
========
ER Model
--------
1. Terms
    - Entity
    - Attributes
    - Entity set

Extended E-R Features
---------------------
1. Specialization : Top - down approach
    - From general group, subgrouping entity set with specific attributes
2. Generalization : Down - top approach
    - Combine common(sharing) attribute of each groups
    - disjoint / overlapping
        - disjoint : exclusive, ***cannot*** have multiple attributes at a same time
        - overlapping : ***can*** have multiple attributes at the same time.
    - total / partial
        - sub entity set have ***all*** attrs from high entity set
        - sub entity set have ***some*** attrs from high entity set

Logical Design
---------------
- Basic rules : one entity/relation set &rarr; unique table
1. Relation set
    -
2. Special case : 1-1, 1-m
    - 1-m : E1 &larr; R - E2
        - $E_2 = PK(E_1) \cup Attr(R)$
    - 1-1 : E1 &larr; R &rarr; E2
        - $R = PK(E_1) \cup PK(E_2)$
3. Specialization/Generalization to Relation schema
    - option 1
        - make difference table of each layer and make their relation by foreign key
    - option 2
        - include common attrs to all subgroups attrs

Design Issues
-------------
- Common Key Points : ***More Relation - Make it Entity***
- Key point is no matter model's type, just design model's that represent the real world, and extensive(flexible)
1. Entity VS Attributes

2. Entity VS Relationship

3. Binary VS n-ary relationships
