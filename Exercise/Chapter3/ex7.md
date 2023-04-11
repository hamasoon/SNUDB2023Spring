> Consider the SQL query 
```sql
SELECT p.a1
FROM p, r1, r2
WHERE p.a1 = r1.a1 OR p.a1 = r2.a1
```
> Under what conditions does the preceding query select values of _p.a1_ that are 
> either in _r1_ or in _r2_ ? Examine carefully the cases where either _r1_ or _r2_ 
> may be empty. 

--------------------------------

