> Consider the relational database employee where the primary keys are 
> underlined. Give an expression in SQL for each of the following queries.<br> 
> employee (ID, person_name, street, city)
> works (ID, company_name, salary)
> company (company_name, city)
> manages (ID, manager_id)
--------------------------------


a. Find the ID, name, and city of residence of each employee who works for "First Bank Corporation".

```sql
SELECT E.ID, person_name, city
FROM employee AS E, wroks AS W
WHERE E.ID = W.ID AND
    W.company_name = "First Bank Corporation"
```

b. Find the ID, name, and city of residence of each employee who works for "First Bank Corporation"
and earns more than $10000.

```sql 
SELECT E.ID, person_name, city
FROM employee AS E, wroks AS W
WHERE E.ID = W.ID AND
    W.company_name = "First Bank Corporation"
    W.salary > 10000
```

This could be written also in the style of the answer to part a, as follows: 

```sql
SELECT ID, person_name, city
FROM employee 
WHERE ID IN (
    SELECT ID
    FROM works
    WHERE company_name = 'First Bank Corporation' AND salary > 10000
) 
```

c. Find the ID of each employee who does not work for "First Bank Corporation".

```sql
SELECT ID
FROM employee
WHERE ID NOT IN (
    SELECT ID
    FROM works
    WHERE company_name = 'First Bank Corporation'
)
```

If one allows people to appear in _employee_ without appearing also in 
_works_, the solution is slightly more complicated. An outer join as discussed
in Chapter 4 could be used as well. 

```sql 
SELECT ID
FROM works
WHERE company_name <> 'First Bank Corporation' 
```

d. Find the ID of each employee who earns more than every employee of "Small Bank Corporation".

```sql
SELECT ID
FROM works
WHERE salary > ALL (
    SELECT salary
    FROM works
    WHERE company_name = 'First Bank Corporation' 
)
```

If people may work for several companies and we wish to consider the _total_ earnings of 
each person, the is more complex. But note that the fact that ID is the primary key for 
_works_ implies that this cannot be the case. 

e. **Assume that companies may be located in several cities**. Find the name of each company that 
is located in every city in which "Small Bank Corporation" is located.

```sql 
SELECT S.company_name 
FROM company AS S 
WHERE NOT EXISTS (
    (
        SELECT city
        FROM company
        WHERE company_name = 'Small Bank Corporation'
    )
    EXCEPT
    (
        SELECT city
        FROM company AS T
        WHERE T.company_name = S.company_name
    )
)
```

f. Find the name of the company that has the most employees (or companies, in the case where 
there is a tie for the most).

```sql
SELECT company_name 
FROM works
GROUP BY company_name
HAVING COUNT(DISTINCT ID) >= ALL (
    SELECT COUNT(DISTINCT ID)
    FROM works
    GROUP BY company_name
)
```

g. Find the name of each company whose employees earn a higher salary, on average, than the 
average salary at "First Bank Corporation".

```sql
SELECT company_name
FROM works
GROUP BY company_name 
HAVING AVG(salary) >  (
    SELECT AVG(salary)
    FROM works
    WHERE company_name = 'First Bank Corporation'
)
```