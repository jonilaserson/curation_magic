# Curation Magic
> Automagically curate test sets based on user given constraints


Did you ever need to sub-sample a pool of samples according to a strict set of conditions? Perhaps when designing a test set for an experiment?  This package provides an easy way to sub-sample a dataframe.

The user provides two dataframes: the first has the sample pool, and the second has queries over these samples, with the specification of the intended amount of samples that should satisfy each query in the curated set.

## Install

`pip install curation_magic`

## Problem Definition
Our goal is to curate a subset from a general pool of samples, that will satisfy a list of conditions as close as possible.

The pool of samples is given in a dataframe, which we'll call *df_samples*, it has one row per sample, and the columns represent all sort of meta data and features of the samples.

Let's see an example, where our general pool is the list of passengers on board the titanic (originally published by Kaggle):

```python
# Load dataframe from file.
import pandas as pd

df_samples = pd.read_csv('csvs/titanic.csv').drop(columns='Name')
print(df_samples.head().to_markdown())
```

    |    |   Survived |   Pclass | Sex    |   Age |   Siblings/Spouses Aboard |   Parents/Children Aboard |    Fare |
    |---:|-----------:|---------:|:-------|------:|--------------------------:|--------------------------:|--------:|
    |  0 |          0 |        3 | male   |    22 |                         1 |                         0 |  7.25   |
    |  1 |          1 |        1 | female |    38 |                         1 |                         0 | 71.2833 |
    |  2 |          1 |        3 | female |    26 |                         0 |                         0 |  7.925  |
    |  3 |          1 |        1 | female |    35 |                         1 |                         0 | 53.1    |
    |  4 |          0 |        3 | male   |    35 |                         0 |                         0 |  8.05   |


The conditions are given in a second dataframe, *df_cond_abs*. 
Each row of *df_cond_abs* is indexed by a *query* that can be applied to the df_samples (i.e. by using df_samples.query(query_string)). For each query the user specifies constraints supplied, regarding how many samples in the curated subset should satisfy the query. The constraints are given as a lower-bound and upper bound, as well as the penalty per violation (by default 1 if the penalty column not supplied). Ignore the *index_ref* column for now.

```python
# Get absolute numbers constraints 
df_cond_abs = pd.read_csv('csvs/curation_conditions_abs.csv').set_index('query')
print(df_cond_abs.to_markdown())
```

    | query                                         |   id |   min |   max |   index_ref |   penalty_per_violation |
    |:----------------------------------------------|-----:|------:|------:|------------:|------------------------:|
    | Survived >= 0                                 |    0 |   200 |   200 |          -1 |                       1 |
    | Survived == 1                                 |    1 |   100 |   100 |          -1 |                       1 |
    | Survived == 0                                 |    2 |   100 |   100 |          -1 |                       1 |
    | Survived == 1 & Sex == 'female'               |    3 |    48 |    52 |          -1 |                       1 |
    | Survived == 0 & Sex == 'female'               |    4 |    48 |    52 |          -1 |                       1 |
    | Survived == 1 & Pclass == 1                   |    5 |    30 |    35 |          -1 |                       1 |
    | Survived == 1 & Pclass == 2                   |    6 |    30 |    35 |          -1 |                       1 |
    | Survived == 1 & Pclass == 3                   |    7 |    30 |    35 |          -1 |                       1 |
    | Survived == 0 & Pclass == 1                   |    8 |    30 |    35 |          -1 |                       1 |
    | Survived == 0 & Pclass == 2                   |    9 |    30 |    35 |          -1 |                       1 |
    | Survived == 0 & Pclass == 3                   |   10 |    30 |    35 |          -1 |                       1 |
    | Survived == 0 & Pclass == 1 & Sex == 'female' |   11 |     8 |    12 |          -1 |                       1 |
    | Age < 20                                      |   12 |    48 |    52 |          -1 |                       1 |
    | Age < 30 & Age >= 20                          |   13 |    48 |    52 |          -1 |                       1 |
    | Age < 40 & Age >= 30                          |   14 |    48 |    52 |          -1 |                       1 |
    | Age >= 40                                     |   15 |    48 |    52 |          -1 |                       1 |


The function *get_query_features_df* applies all the queries on the *df_samples* dataframe, and we obtain df_bool, a boolean dataframe which has the samples as rows and the queries as columns. *df_bool* indicates which sample matches which query.

```python
df_bool = curator.get_query_features_df(df_samples, df_cond_abs.index)
print(df_bool.head().to_markdown())
```

    |    |   Survived >= 0 |   Survived == 1 |   Survived == 0 |   Survived == 1 & Sex == 'female' |   Survived == 0 & Sex == 'female' |   Survived == 1 & Pclass == 1 |   Survived == 1 & Pclass == 2 |   Survived == 1 & Pclass == 3 |   Survived == 0 & Pclass == 1 |   Survived == 0 & Pclass == 2 |   Survived == 0 & Pclass == 3 |   Survived == 0 & Pclass == 1 & Sex == 'female' |   Age < 20 |   Age < 30 & Age >= 20 |   Age < 40 & Age >= 30 |   Age >= 40 |
    |---:|----------------:|----------------:|----------------:|----------------------------------:|----------------------------------:|------------------------------:|------------------------------:|------------------------------:|------------------------------:|------------------------------:|------------------------------:|------------------------------------------------:|-----------:|-----------------------:|-----------------------:|------------:|
    |  0 |               1 |               0 |               1 |                                 0 |                                 0 |                             0 |                             0 |                             0 |                             0 |                             0 |                             1 |                                               0 |          0 |                      1 |                      0 |           0 |
    |  1 |               1 |               1 |               0 |                                 1 |                                 0 |                             1 |                             0 |                             0 |                             0 |                             0 |                             0 |                                               0 |          0 |                      0 |                      1 |           0 |
    |  2 |               1 |               1 |               0 |                                 1 |                                 0 |                             0 |                             0 |                             1 |                             0 |                             0 |                             0 |                                               0 |          0 |                      1 |                      0 |           0 |
    |  3 |               1 |               1 |               0 |                                 1 |                                 0 |                             1 |                             0 |                             0 |                             0 |                             0 |                             0 |                                               0 |          0 |                      0 |                      1 |           0 |
    |  4 |               1 |               0 |               1 |                                 0 |                                 0 |                             0 |                             0 |                             0 |                             0 |                             0 |                             1 |                                               0 |          0 |                      0 |                      1 |           0 |


We can use this table to quickly see how many samples in our pool satisfy each query:

```python
df_bool.sum()
```




    Survived >= 0                                    887
    Survived == 1                                    342
    Survived == 0                                    545
    Survived == 1 & Sex == 'female'                  233
    Survived == 0 & Sex == 'female'                   81
    Survived == 1 & Pclass == 1                      136
    Survived == 1 & Pclass == 2                       87
    Survived == 1 & Pclass == 3                      119
    Survived == 0 & Pclass == 1                       80
    Survived == 0 & Pclass == 2                       97
    Survived == 0 & Pclass == 3                      368
    Survived == 0 & Pclass == 1 & Sex == 'female'      3
    Age < 20                                         199
    Age < 30 & Age >= 20                             293
    Age < 40 & Age >= 30                             199
    Age >= 40                                        196
    dtype: int64



### Curate a subset using absolute bounds
Let's use the *AbsBoundariesCurator* to build a curated set that satisfies all the conditions as much as possible:

```python
abc = curator.AbsBoundariesCurator(df_samples, df_cond_abs)

# Note, we are using here the interior-point solver which is
# faster but less accurate than the default simplex solver.
included, summary = abc.run(method='interior-point')

# The summary shows how many were included from every query,
# and the total number of violations.
print(summary.to_markdown())
```

    Theoretical penalty: 8.99999970164261
    Actual penalty: 13   Total violations: 13
    Included: 198
    | query                                         |   cnt |   min |   max |   total |   violation |
    |:----------------------------------------------|------:|------:|------:|--------:|------------:|
    | Survived >= 0                                 |   198 |   200 |   200 |     887 |           2 |
    | Survived == 1                                 |    99 |   100 |   100 |     342 |           1 |
    | Survived == 0                                 |    99 |   100 |   100 |     545 |           1 |
    | Survived == 1 & Sex == 'female'               |    49 |    48 |    52 |     233 |           0 |
    | Survived == 0 & Sex == 'female'               |    44 |    48 |    52 |      81 |           4 |
    | Survived == 1 & Pclass == 1                   |    33 |    30 |    35 |     136 |           0 |
    | Survived == 1 & Pclass == 2                   |    33 |    30 |    35 |      87 |           0 |
    | Survived == 1 & Pclass == 3                   |    33 |    30 |    35 |     119 |           0 |
    | Survived == 0 & Pclass == 1                   |    32 |    30 |    35 |      80 |           0 |
    | Survived == 0 & Pclass == 2                   |    32 |    30 |    35 |      97 |           0 |
    | Survived == 0 & Pclass == 3                   |    35 |    30 |    35 |     368 |           0 |
    | Survived == 0 & Pclass == 1 & Sex == 'female' |     3 |     8 |    12 |       3 |           5 |
    | Age < 20                                      |    50 |    48 |    52 |     199 |           0 |
    | Age < 30 & Age >= 20                          |    50 |    48 |    52 |     293 |           0 |
    | Age < 40 & Age >= 30                          |    49 |    48 |    52 |     199 |           0 |
    | Age >= 40                                     |    49 |    48 |    52 |     196 |           0 |


As you can see above, the linear solver had 9 violations, but after we decoded the solution (round the $x_j$ values and decide which samples to include), there were 13 violations in total. The optimal LP target value is always going to be a lower bound on the *integer* progam target.  

We see that our pool has only 3 women from first-class (Pclass=1) who did not survive, so we are bound to have at least 5 violations there, since our condition on this set asks for 8 members. Our final curated set has 196 members instead of 200. 


We are also missing 4 non-surviving women in general. Let's see if we can fix up this amount.
We can tweak the optimization by giving a larger penalty for each violation of this constraint.  Say 5 penalty points vs. only 1 penalty for the other conditions.

```python
df_cond_abs['penalty_per_violation'] = 1
df_cond_abs.loc["Survived == 0 & Sex == 'female'", 'penalty_per_violation'] = 5

cc = curator.AbsBoundariesCurator(df_samples, df_cond_abs)
included, summary = cc.run(method='interior-point')

print(summary.to_markdown())
```

    /cached_data/projects/mammo_v2/jonil/code/curation_magic/curation_magic/curator.py:153: OptimizeWarning: Solving system with option 'cholesky':True failed. It is normal for this to happen occasionally, especially as the solution is approached. However, if you see this frequently, consider setting option 'cholesky' to False.
      self.solution = linprog(method=method, **self.linprog_params)
    /cached_data/projects/mammo_v2/jonil/code/curation_magic/curation_magic/curator.py:153: OptimizeWarning: Solving system with option 'sym_pos':True failed. It is normal for this to happen occasionally, especially as the solution is approached. However, if you see this frequently, consider setting option 'sym_pos' to False.
      self.solution = linprog(method=method, **self.linprog_params)
    /cached_data/projects/mammo_v2/jonil/code/curation_magic/curation_magic/curator.py:153: OptimizeWarning: Solving system with option 'sym_pos':False failed. This may happen occasionally, especially as the solution is approached. However, if you see this frequently, your problem may be numerically challenging. If you cannot improve the formulation, consider setting 'lstsq' to True. Consider also setting `presolve` to True, if it is not already.
      self.solution = linprog(method=method, **self.linprog_params)


    Theoretical penalty: 8.999999999971957
    Actual penalty: 9   Total violations: 9
    Included: 200
    | query                                         |   cnt |   min |   max |   total |   violation |
    |:----------------------------------------------|------:|------:|------:|--------:|------------:|
    | Survived >= 0                                 |   200 |   200 |   200 |     887 |           0 |
    | Survived == 1                                 |   100 |   100 |   100 |     342 |           0 |
    | Survived == 0                                 |   100 |   100 |   100 |     545 |           0 |
    | Survived == 1 & Sex == 'female'               |    50 |    48 |    52 |     233 |           0 |
    | Survived == 0 & Sex == 'female'               |    48 |    48 |    52 |      81 |           0 |
    | Survived == 1 & Pclass == 1                   |    33 |    30 |    35 |     136 |           0 |
    | Survived == 1 & Pclass == 2                   |    34 |    30 |    35 |      87 |           0 |
    | Survived == 1 & Pclass == 3                   |    33 |    30 |    35 |     119 |           0 |
    | Survived == 0 & Pclass == 1                   |    30 |    30 |    35 |      80 |           0 |
    | Survived == 0 & Pclass == 2                   |    31 |    30 |    35 |      97 |           0 |
    | Survived == 0 & Pclass == 3                   |    39 |    30 |    35 |     368 |           4 |
    | Survived == 0 & Pclass == 1 & Sex == 'female' |     3 |     8 |    12 |       3 |           5 |
    | Age < 20                                      |    49 |    48 |    52 |     199 |           0 |
    | Age < 30 & Age >= 20                          |    50 |    48 |    52 |     293 |           0 |
    | Age < 40 & Age >= 30                          |    51 |    48 |    52 |     199 |           0 |
    | Age >= 40                                     |    50 |    48 |    52 |     196 |           0 |


Goodie!  This constraing is now satisfied, and we reduced the integral gap to 0 (since the actual penalty = theoretical penalty), which means we are at the optimal solution!

Now we can go back to the original samples dataframe, and add a new column indicating which samples would participate in the final set:

```python
df_subset = df_samples[included]
print(len(df_subset))
```

    200


### Curate a subset using relative bounds

The fact that the condition boundaties are given in absolute integer numbers is actually a limitation:
Say we are willing to have some flexibility with regard to the number of negatives we curate (i.e. anything in the range 90-110 is fine), but within the chosen set of negatives, we would like 49-51% to be females. Since we don't know how many negatives we'll turn up with, there is no way to put a tight bound (in absolute numbers) on the number of negative female samples.

What we want is to be able to bound a query relative to the (yet unknown) number of samples that satisfy a previous query.  So an alternative way to provide boundaries is in the form of a *fraction* relative to the resulting set satisfying a different query.


```python
# Get relative fraction constraints
df_cond_rel = pd.read_csv('csvs/curation_conditions_rel.csv').set_index('query')
print(df_cond_rel.reset_index().to_markdown())

```

    |    | query                                         |   id |    min |    max |   index_ref |   penalty_per_violation |
    |---:|:----------------------------------------------|-----:|-------:|-------:|------------:|------------------------:|
    |  0 | Survived >= 0                                 |    0 | 200    | 200    |          -1 |                       1 |
    |  1 | Survived == 1                                 |    1 |   0.45 |   0.55 |           0 |                       1 |
    |  2 | Survived == 0                                 |    2 |   0.45 |   0.55 |           0 |                       1 |
    |  3 | Survived == 1 & Sex == 'female'               |    3 |   0.49 |   0.51 |           1 |                       1 |
    |  4 | Survived == 0 & Sex == 'female'               |    4 |   0.49 |   0.51 |           2 |                       1 |
    |  5 | Survived == 1 & Pclass == 1                   |    5 |   0.3  |   0.35 |           1 |                       1 |
    |  6 | Survived == 1 & Pclass == 2                   |    6 |   0.3  |   0.35 |           1 |                       1 |
    |  7 | Survived == 1 & Pclass == 3                   |    7 |   0.3  |   0.35 |           1 |                       1 |
    |  8 | Survived == 0 & Pclass == 1                   |    8 |   0.3  |   0.35 |           2 |                       1 |
    |  9 | Survived == 0 & Pclass == 2                   |    9 |   0.3  |   0.35 |           2 |                       1 |
    | 10 | Survived == 0 & Pclass == 3                   |   10 |   0.3  |   0.35 |           2 |                       1 |
    | 11 | Survived == 0 & Pclass == 1 & Sex == 'female' |   11 |   0.28 |   0.35 |           8 |                       1 |
    | 12 | Age < 20                                      |   12 |   0.24 |   0.26 |           0 |                       1 |
    | 13 | Age < 30 & Age >= 20                          |   13 |   0.24 |   0.26 |           0 |                       1 |
    | 14 | Age < 40 & Age >= 30                          |   14 |   0.24 |   0.26 |           0 |                       1 |
    | 15 | Age >= 40                                     |   15 |   0.24 |   0.26 |           0 |                       1 |


Here, *index_ref* column is referencing a previous constraint id.
For example, in line 4, we ask that the number of samples satisfying the query [*Survived == 0 & Sex == 'female'*] would be at least 49% and no more than 51% of the samples satisfying query 2 [*Survived == 0*]. This is how we were able to define a condition relevant to the negative set without knowing how many negative we'll have at the end!

We still have to ground the solution in some absolute number of desired sample, so we used integer boundaries for the first query above, simply by setting *index_ref=-1* (otherwise the solution is not well defined and the LP solver might not converge).

Let's run the *RelBoundariesCurator* to solve this (here with the simplex method):

```python
cc = curator.RelBoundariesCurator(df_samples, df_cond_rel)
included, summary = cc.run()
print(summary.to_markdown())
```

    Theoretical penalty: 8.160000000000009
    Actual penalty: 10   Total violations: 10
    Included: 200
    | query                                         |   cnt |   min |   max |   total |   violation |
    |:----------------------------------------------|------:|------:|------:|--------:|------------:|
    | Survived >= 0                                 |   200 |   200 |   200 |     887 |           0 |
    | Survived == 1                                 |   110 |    90 |   110 |     342 |           0 |
    | Survived == 0                                 |    90 |    90 |   110 |     545 |           0 |
    | Survived == 1 & Sex == 'female'               |    56 |    54 |    56 |     233 |           0 |
    | Survived == 0 & Sex == 'female'               |    44 |    44 |    46 |      81 |           0 |
    | Survived == 1 & Pclass == 1                   |    38 |    33 |    38 |     136 |           0 |
    | Survived == 1 & Pclass == 2                   |    39 |    33 |    38 |      87 |           1 |
    | Survived == 1 & Pclass == 3                   |    33 |    33 |    38 |     119 |           0 |
    | Survived == 0 & Pclass == 1                   |    27 |    27 |    31 |      80 |           0 |
    | Survived == 0 & Pclass == 2                   |    28 |    27 |    31 |      97 |           0 |
    | Survived == 0 & Pclass == 3                   |    35 |    27 |    31 |     368 |           4 |
    | Survived == 0 & Pclass == 1 & Sex == 'female' |     3 |     8 |     9 |       3 |           5 |
    | Age < 20                                      |    52 |    48 |    52 |     199 |           0 |
    | Age < 30 & Age >= 20                          |    48 |    48 |    52 |     293 |           0 |
    | Age < 40 & Age >= 30                          |    52 |    48 |    52 |     199 |           0 |
    | Age >= 40                                     |    48 |    48 |    52 |     196 |           0 |

