> Consider the employee database of Figure 4.12. Give an SQL DDL definition of 
> this database. Identify referential-integrity constraints that should hold, and 
> include them in the DDL definition. 
>
> Employee database
> $employee (\underline{ID}, person\ name, street, city)$
> $works (\underline{ID}, company\ name, salary)$
> $company (\underline{company\ name}, city)$
> $manages (\underline{ID}, manager\ id)$

--------------------------------

```sql
CREATE TABLE employee(
    ID          INT,
    person_name VARCHAR(20),
    street      VARCHAR(20),
    city        VARCHAR(20),
    PRIMARY KEY (ID),
)
```