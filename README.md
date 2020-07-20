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

df_samples = pd.read_csv('csvs/titanic.csv')
df_samples.head()
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>Survived</th>
      <th>Pclass</th>
      <th>Name</th>
      <th>Sex</th>
      <th>Age</th>
      <th>Siblings/Spouses Aboard</th>
      <th>Parents/Children Aboard</th>
      <th>Fare</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>0</td>
      <td>3</td>
      <td>Mr. Owen Harris Braund</td>
      <td>male</td>
      <td>22.0</td>
      <td>1</td>
      <td>0</td>
      <td>7.2500</td>
    </tr>
    <tr>
      <th>1</th>
      <td>1</td>
      <td>1</td>
      <td>Mrs. John Bradley (Florence Briggs Thayer) Cum...</td>
      <td>female</td>
      <td>38.0</td>
      <td>1</td>
      <td>0</td>
      <td>71.2833</td>
    </tr>
    <tr>
      <th>2</th>
      <td>1</td>
      <td>3</td>
      <td>Miss. Laina Heikkinen</td>
      <td>female</td>
      <td>26.0</td>
      <td>0</td>
      <td>0</td>
      <td>7.9250</td>
    </tr>
    <tr>
      <th>3</th>
      <td>1</td>
      <td>1</td>
      <td>Mrs. Jacques Heath (Lily May Peel) Futrelle</td>
      <td>female</td>
      <td>35.0</td>
      <td>1</td>
      <td>0</td>
      <td>53.1000</td>
    </tr>
    <tr>
      <th>4</th>
      <td>0</td>
      <td>3</td>
      <td>Mr. William Henry Allen</td>
      <td>male</td>
      <td>35.0</td>
      <td>0</td>
      <td>0</td>
      <td>8.0500</td>
    </tr>
  </tbody>
</table>
</div>



The conditions are given in a second dataframe, *df_cond_abs*. 
Each row of *df_cond_abs* is indexed by a *query* that can be applied to the df_samples (i.e. by using df_samples.query(query_string)). For each query the user specifies constraints supplied, regarding how many samples in the curated subset should satisfy the query. The constraints are given as a lower-bound and upper bound, as well as the penalty per violation (by default 1 if the penalty column not supplied). Ignore the *index_ref* column for now.

```python
# Get absolute numbers constraints 
df_cond_abs = pd.read_csv('csvs/curation_conditions_abs.csv').set_index('query')
df_cond_abs
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>id</th>
      <th>min</th>
      <th>max</th>
      <th>index_ref</th>
      <th>penalty_per_violation</th>
    </tr>
    <tr>
      <th>query</th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>Survived &gt;= 0</th>
      <td>0</td>
      <td>200</td>
      <td>200</td>
      <td>-1</td>
      <td>1</td>
    </tr>
    <tr>
      <th>Survived == 1</th>
      <td>1</td>
      <td>100</td>
      <td>100</td>
      <td>-1</td>
      <td>1</td>
    </tr>
    <tr>
      <th>Survived == 0</th>
      <td>2</td>
      <td>100</td>
      <td>100</td>
      <td>-1</td>
      <td>1</td>
    </tr>
    <tr>
      <th>Survived == 1 &amp; Sex == 'female'</th>
      <td>3</td>
      <td>48</td>
      <td>52</td>
      <td>-1</td>
      <td>1</td>
    </tr>
    <tr>
      <th>Survived == 0 &amp; Sex == 'female'</th>
      <td>4</td>
      <td>48</td>
      <td>52</td>
      <td>-1</td>
      <td>1</td>
    </tr>
    <tr>
      <th>Survived == 1 &amp; Pclass == 1</th>
      <td>5</td>
      <td>30</td>
      <td>35</td>
      <td>-1</td>
      <td>1</td>
    </tr>
    <tr>
      <th>Survived == 1 &amp; Pclass == 2</th>
      <td>6</td>
      <td>30</td>
      <td>35</td>
      <td>-1</td>
      <td>1</td>
    </tr>
    <tr>
      <th>Survived == 1 &amp; Pclass == 3</th>
      <td>7</td>
      <td>30</td>
      <td>35</td>
      <td>-1</td>
      <td>1</td>
    </tr>
    <tr>
      <th>Survived == 0 &amp; Pclass == 1</th>
      <td>8</td>
      <td>30</td>
      <td>35</td>
      <td>-1</td>
      <td>1</td>
    </tr>
    <tr>
      <th>Survived == 0 &amp; Pclass == 2</th>
      <td>9</td>
      <td>30</td>
      <td>35</td>
      <td>-1</td>
      <td>1</td>
    </tr>
    <tr>
      <th>Survived == 0 &amp; Pclass == 3</th>
      <td>10</td>
      <td>30</td>
      <td>35</td>
      <td>-1</td>
      <td>1</td>
    </tr>
    <tr>
      <th>Survived == 0 &amp; Pclass == 1 &amp; Sex == 'female'</th>
      <td>11</td>
      <td>8</td>
      <td>12</td>
      <td>-1</td>
      <td>1</td>
    </tr>
    <tr>
      <th>Age &lt; 20</th>
      <td>12</td>
      <td>48</td>
      <td>52</td>
      <td>-1</td>
      <td>1</td>
    </tr>
    <tr>
      <th>Age &lt; 30 &amp; Age &gt;= 20</th>
      <td>13</td>
      <td>48</td>
      <td>52</td>
      <td>-1</td>
      <td>1</td>
    </tr>
    <tr>
      <th>Age &lt; 40 &amp; Age &gt;= 30</th>
      <td>14</td>
      <td>48</td>
      <td>52</td>
      <td>-1</td>
      <td>1</td>
    </tr>
    <tr>
      <th>Age &gt;= 40</th>
      <td>15</td>
      <td>48</td>
      <td>52</td>
      <td>-1</td>
      <td>1</td>
    </tr>
  </tbody>
</table>
</div>



The function *get_query_features_df* applies all the queries on the *df_samples* dataframe, and we obtain df_bool, a boolean dataframe which has the samples as rows and the queries as columns. *df_bool* indicates which sample matches which query.

```python
df_bool = curator.get_query_features_df(df_samples, df_cond_abs.index)
df_bool.head()
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>Survived &gt;= 0</th>
      <th>Survived == 1</th>
      <th>Survived == 0</th>
      <th>Survived == 1 &amp; Sex == 'female'</th>
      <th>Survived == 0 &amp; Sex == 'female'</th>
      <th>Survived == 1 &amp; Pclass == 1</th>
      <th>Survived == 1 &amp; Pclass == 2</th>
      <th>Survived == 1 &amp; Pclass == 3</th>
      <th>Survived == 0 &amp; Pclass == 1</th>
      <th>Survived == 0 &amp; Pclass == 2</th>
      <th>Survived == 0 &amp; Pclass == 3</th>
      <th>Survived == 0 &amp; Pclass == 1 &amp; Sex == 'female'</th>
      <th>Age &lt; 20</th>
      <th>Age &lt; 30 &amp; Age &gt;= 20</th>
      <th>Age &lt; 40 &amp; Age &gt;= 30</th>
      <th>Age &gt;= 40</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>True</td>
      <td>False</td>
      <td>True</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>True</td>
      <td>False</td>
      <td>False</td>
      <td>True</td>
      <td>False</td>
      <td>False</td>
    </tr>
    <tr>
      <th>1</th>
      <td>True</td>
      <td>True</td>
      <td>False</td>
      <td>True</td>
      <td>False</td>
      <td>True</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>True</td>
      <td>False</td>
    </tr>
    <tr>
      <th>2</th>
      <td>True</td>
      <td>True</td>
      <td>False</td>
      <td>True</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>True</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>True</td>
      <td>False</td>
      <td>False</td>
    </tr>
    <tr>
      <th>3</th>
      <td>True</td>
      <td>True</td>
      <td>False</td>
      <td>True</td>
      <td>False</td>
      <td>True</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>True</td>
      <td>False</td>
    </tr>
    <tr>
      <th>4</th>
      <td>True</td>
      <td>False</td>
      <td>True</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>True</td>
      <td>False</td>
      <td>False</td>
      <td>False</td>
      <td>True</td>
      <td>False</td>
    </tr>
  </tbody>
</table>
</div>



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
summary
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





<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>cnt</th>
      <th>min</th>
      <th>max</th>
      <th>total</th>
      <th>violation</th>
    </tr>
    <tr>
      <th>query</th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>Survived &gt;= 0</th>
      <td>200</td>
      <td>200</td>
      <td>200</td>
      <td>887</td>
      <td>0</td>
    </tr>
    <tr>
      <th>Survived == 1</th>
      <td>100</td>
      <td>100</td>
      <td>100</td>
      <td>342</td>
      <td>0</td>
    </tr>
    <tr>
      <th>Survived == 0</th>
      <td>100</td>
      <td>100</td>
      <td>100</td>
      <td>545</td>
      <td>0</td>
    </tr>
    <tr>
      <th>Survived == 1 &amp; Sex == 'female'</th>
      <td>50</td>
      <td>48</td>
      <td>52</td>
      <td>233</td>
      <td>0</td>
    </tr>
    <tr>
      <th>Survived == 0 &amp; Sex == 'female'</th>
      <td>48</td>
      <td>48</td>
      <td>52</td>
      <td>81</td>
      <td>0</td>
    </tr>
    <tr>
      <th>Survived == 1 &amp; Pclass == 1</th>
      <td>33</td>
      <td>30</td>
      <td>35</td>
      <td>136</td>
      <td>0</td>
    </tr>
    <tr>
      <th>Survived == 1 &amp; Pclass == 2</th>
      <td>34</td>
      <td>30</td>
      <td>35</td>
      <td>87</td>
      <td>0</td>
    </tr>
    <tr>
      <th>Survived == 1 &amp; Pclass == 3</th>
      <td>33</td>
      <td>30</td>
      <td>35</td>
      <td>119</td>
      <td>0</td>
    </tr>
    <tr>
      <th>Survived == 0 &amp; Pclass == 1</th>
      <td>30</td>
      <td>30</td>
      <td>35</td>
      <td>80</td>
      <td>0</td>
    </tr>
    <tr>
      <th>Survived == 0 &amp; Pclass == 2</th>
      <td>31</td>
      <td>30</td>
      <td>35</td>
      <td>97</td>
      <td>0</td>
    </tr>
    <tr>
      <th>Survived == 0 &amp; Pclass == 3</th>
      <td>39</td>
      <td>30</td>
      <td>35</td>
      <td>368</td>
      <td>4</td>
    </tr>
    <tr>
      <th>Survived == 0 &amp; Pclass == 1 &amp; Sex == 'female'</th>
      <td>3</td>
      <td>8</td>
      <td>12</td>
      <td>3</td>
      <td>5</td>
    </tr>
    <tr>
      <th>Age &lt; 20</th>
      <td>49</td>
      <td>48</td>
      <td>52</td>
      <td>199</td>
      <td>0</td>
    </tr>
    <tr>
      <th>Age &lt; 30 &amp; Age &gt;= 20</th>
      <td>50</td>
      <td>48</td>
      <td>52</td>
      <td>293</td>
      <td>0</td>
    </tr>
    <tr>
      <th>Age &lt; 40 &amp; Age &gt;= 30</th>
      <td>51</td>
      <td>48</td>
      <td>52</td>
      <td>199</td>
      <td>0</td>
    </tr>
    <tr>
      <th>Age &gt;= 40</th>
      <td>50</td>
      <td>48</td>
      <td>52</td>
      <td>196</td>
      <td>0</td>
    </tr>
  </tbody>
</table>
</div>



As you can see above, the linear solver had 9 violations, but after we decoded the solution (round the $x_j$ values and decide which samples to include), there were 13 violations in total. The optimal LP target value is always going to be a lower bound on the *integer* progam target.  

We see that our pool has only 3 women from first-class (Pclass=1) who did not survive, so we are bound to have at least 5 violations there, since our condition on this set asks for 8 members. Our final curated set has 196 members instead of 200. 


We are also missing 4 non-surviving women in general. Let's see if we can fix up this amount.
We can tweak the optimization by giving a larger penalty for each violation of this constraint.  Say 5 penalty points vs. only 1 penalty for the other conditions.

```python
df_cond_abs['penalty_per_violation'] = 1
df_cond_abs.loc["Survived == 0 & Sex == 'female'", 'penalty_per_violation'] = 5

cc = curator.AbsBoundariesCurator(df_samples, df_cond_abs)
included, summary = cc.run(method='interior-point')

summary
```

    Theoretical penalty: 8.999999999971957
    Actual penalty: 9   Total violations: 9
    Included: 200





<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>cnt</th>
      <th>min</th>
      <th>max</th>
      <th>total</th>
      <th>violation</th>
    </tr>
    <tr>
      <th>query</th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>Survived &gt;= 0</th>
      <td>200</td>
      <td>200</td>
      <td>200</td>
      <td>887</td>
      <td>0</td>
    </tr>
    <tr>
      <th>Survived == 1</th>
      <td>100</td>
      <td>100</td>
      <td>100</td>
      <td>342</td>
      <td>0</td>
    </tr>
    <tr>
      <th>Survived == 0</th>
      <td>100</td>
      <td>100</td>
      <td>100</td>
      <td>545</td>
      <td>0</td>
    </tr>
    <tr>
      <th>Survived == 1 &amp; Sex == 'female'</th>
      <td>50</td>
      <td>48</td>
      <td>52</td>
      <td>233</td>
      <td>0</td>
    </tr>
    <tr>
      <th>Survived == 0 &amp; Sex == 'female'</th>
      <td>48</td>
      <td>48</td>
      <td>52</td>
      <td>81</td>
      <td>0</td>
    </tr>
    <tr>
      <th>Survived == 1 &amp; Pclass == 1</th>
      <td>33</td>
      <td>30</td>
      <td>35</td>
      <td>136</td>
      <td>0</td>
    </tr>
    <tr>
      <th>Survived == 1 &amp; Pclass == 2</th>
      <td>34</td>
      <td>30</td>
      <td>35</td>
      <td>87</td>
      <td>0</td>
    </tr>
    <tr>
      <th>Survived == 1 &amp; Pclass == 3</th>
      <td>33</td>
      <td>30</td>
      <td>35</td>
      <td>119</td>
      <td>0</td>
    </tr>
    <tr>
      <th>Survived == 0 &amp; Pclass == 1</th>
      <td>30</td>
      <td>30</td>
      <td>35</td>
      <td>80</td>
      <td>0</td>
    </tr>
    <tr>
      <th>Survived == 0 &amp; Pclass == 2</th>
      <td>31</td>
      <td>30</td>
      <td>35</td>
      <td>97</td>
      <td>0</td>
    </tr>
    <tr>
      <th>Survived == 0 &amp; Pclass == 3</th>
      <td>39</td>
      <td>30</td>
      <td>35</td>
      <td>368</td>
      <td>4</td>
    </tr>
    <tr>
      <th>Survived == 0 &amp; Pclass == 1 &amp; Sex == 'female'</th>
      <td>3</td>
      <td>8</td>
      <td>12</td>
      <td>3</td>
      <td>5</td>
    </tr>
    <tr>
      <th>Age &lt; 20</th>
      <td>49</td>
      <td>48</td>
      <td>52</td>
      <td>199</td>
      <td>0</td>
    </tr>
    <tr>
      <th>Age &lt; 30 &amp; Age &gt;= 20</th>
      <td>50</td>
      <td>48</td>
      <td>52</td>
      <td>293</td>
      <td>0</td>
    </tr>
    <tr>
      <th>Age &lt; 40 &amp; Age &gt;= 30</th>
      <td>51</td>
      <td>48</td>
      <td>52</td>
      <td>199</td>
      <td>0</td>
    </tr>
    <tr>
      <th>Age &gt;= 40</th>
      <td>50</td>
      <td>48</td>
      <td>52</td>
      <td>196</td>
      <td>0</td>
    </tr>
  </tbody>
</table>
</div>



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
df_cond_rel.reset_index()

```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>query</th>
      <th>id</th>
      <th>min</th>
      <th>max</th>
      <th>index_ref</th>
      <th>penalty_per_violation</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>Survived &gt;= 0</td>
      <td>0</td>
      <td>200.00</td>
      <td>200.00</td>
      <td>-1</td>
      <td>1</td>
    </tr>
    <tr>
      <th>1</th>
      <td>Survived == 1</td>
      <td>1</td>
      <td>0.45</td>
      <td>0.55</td>
      <td>0</td>
      <td>1</td>
    </tr>
    <tr>
      <th>2</th>
      <td>Survived == 0</td>
      <td>2</td>
      <td>0.45</td>
      <td>0.55</td>
      <td>0</td>
      <td>1</td>
    </tr>
    <tr>
      <th>3</th>
      <td>Survived == 1 &amp; Sex == 'female'</td>
      <td>3</td>
      <td>0.49</td>
      <td>0.51</td>
      <td>1</td>
      <td>1</td>
    </tr>
    <tr>
      <th>4</th>
      <td>Survived == 0 &amp; Sex == 'female'</td>
      <td>4</td>
      <td>0.49</td>
      <td>0.51</td>
      <td>2</td>
      <td>1</td>
    </tr>
    <tr>
      <th>5</th>
      <td>Survived == 1 &amp; Pclass == 1</td>
      <td>5</td>
      <td>0.30</td>
      <td>0.35</td>
      <td>1</td>
      <td>1</td>
    </tr>
    <tr>
      <th>6</th>
      <td>Survived == 1 &amp; Pclass == 2</td>
      <td>6</td>
      <td>0.30</td>
      <td>0.35</td>
      <td>1</td>
      <td>1</td>
    </tr>
    <tr>
      <th>7</th>
      <td>Survived == 1 &amp; Pclass == 3</td>
      <td>7</td>
      <td>0.30</td>
      <td>0.35</td>
      <td>1</td>
      <td>1</td>
    </tr>
    <tr>
      <th>8</th>
      <td>Survived == 0 &amp; Pclass == 1</td>
      <td>8</td>
      <td>0.30</td>
      <td>0.35</td>
      <td>2</td>
      <td>1</td>
    </tr>
    <tr>
      <th>9</th>
      <td>Survived == 0 &amp; Pclass == 2</td>
      <td>9</td>
      <td>0.30</td>
      <td>0.35</td>
      <td>2</td>
      <td>1</td>
    </tr>
    <tr>
      <th>10</th>
      <td>Survived == 0 &amp; Pclass == 3</td>
      <td>10</td>
      <td>0.30</td>
      <td>0.35</td>
      <td>2</td>
      <td>1</td>
    </tr>
    <tr>
      <th>11</th>
      <td>Survived == 0 &amp; Pclass == 1 &amp; Sex == 'female'</td>
      <td>11</td>
      <td>0.28</td>
      <td>0.35</td>
      <td>8</td>
      <td>1</td>
    </tr>
    <tr>
      <th>12</th>
      <td>Age &lt; 20</td>
      <td>12</td>
      <td>0.24</td>
      <td>0.26</td>
      <td>0</td>
      <td>1</td>
    </tr>
    <tr>
      <th>13</th>
      <td>Age &lt; 30 &amp; Age &gt;= 20</td>
      <td>13</td>
      <td>0.24</td>
      <td>0.26</td>
      <td>0</td>
      <td>1</td>
    </tr>
    <tr>
      <th>14</th>
      <td>Age &lt; 40 &amp; Age &gt;= 30</td>
      <td>14</td>
      <td>0.24</td>
      <td>0.26</td>
      <td>0</td>
      <td>1</td>
    </tr>
    <tr>
      <th>15</th>
      <td>Age &gt;= 40</td>
      <td>15</td>
      <td>0.24</td>
      <td>0.26</td>
      <td>0</td>
      <td>1</td>
    </tr>
  </tbody>
</table>
</div>



Here, *index_ref* column is referencing a previous constraint id.
For example, in line 4, we ask that the number of samples satisfying the query [*Survived == 0 & Sex == 'female'*] would be at least 49% and no more than 51% of the samples satisfying query 2 [*Survived == 0*]. This is how we were able to define a condition relevant to the negative set without knowing how many negative we'll have at the end!

We still have to ground the solution in some absolute number of desired sample, so we used integer boundaries for the first query above, simply by setting *index_ref=-1* (otherwise the solution is not well defined and the LP solver might not converge).

Let's run the *RelBoundariesCurator* to solve this (here with the simplex method):

```python
cc = curator.RelBoundariesCurator(df_samples, df_cond_rel)
included, summary = cc.run()
summary
```

    Theoretical penalty: 8.159999999999986
    Actual penalty: 10   Total violations: 10
    Included: 200





<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>cnt</th>
      <th>min</th>
      <th>max</th>
      <th>total</th>
      <th>violation</th>
    </tr>
    <tr>
      <th>query</th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>Survived &gt;= 0</th>
      <td>200</td>
      <td>200</td>
      <td>200</td>
      <td>887</td>
      <td>0</td>
    </tr>
    <tr>
      <th>Survived == 1</th>
      <td>110</td>
      <td>90</td>
      <td>110</td>
      <td>342</td>
      <td>0</td>
    </tr>
    <tr>
      <th>Survived == 0</th>
      <td>90</td>
      <td>90</td>
      <td>110</td>
      <td>545</td>
      <td>0</td>
    </tr>
    <tr>
      <th>Survived == 1 &amp; Sex == 'female'</th>
      <td>56</td>
      <td>54</td>
      <td>56</td>
      <td>233</td>
      <td>0</td>
    </tr>
    <tr>
      <th>Survived == 0 &amp; Sex == 'female'</th>
      <td>44</td>
      <td>44</td>
      <td>46</td>
      <td>81</td>
      <td>0</td>
    </tr>
    <tr>
      <th>Survived == 1 &amp; Pclass == 1</th>
      <td>38</td>
      <td>33</td>
      <td>38</td>
      <td>136</td>
      <td>0</td>
    </tr>
    <tr>
      <th>Survived == 1 &amp; Pclass == 2</th>
      <td>39</td>
      <td>33</td>
      <td>38</td>
      <td>87</td>
      <td>1</td>
    </tr>
    <tr>
      <th>Survived == 1 &amp; Pclass == 3</th>
      <td>33</td>
      <td>33</td>
      <td>38</td>
      <td>119</td>
      <td>0</td>
    </tr>
    <tr>
      <th>Survived == 0 &amp; Pclass == 1</th>
      <td>27</td>
      <td>27</td>
      <td>31</td>
      <td>80</td>
      <td>0</td>
    </tr>
    <tr>
      <th>Survived == 0 &amp; Pclass == 2</th>
      <td>28</td>
      <td>27</td>
      <td>31</td>
      <td>97</td>
      <td>0</td>
    </tr>
    <tr>
      <th>Survived == 0 &amp; Pclass == 3</th>
      <td>35</td>
      <td>27</td>
      <td>31</td>
      <td>368</td>
      <td>4</td>
    </tr>
    <tr>
      <th>Survived == 0 &amp; Pclass == 1 &amp; Sex == 'female'</th>
      <td>3</td>
      <td>8</td>
      <td>9</td>
      <td>3</td>
      <td>5</td>
    </tr>
    <tr>
      <th>Age &lt; 20</th>
      <td>52</td>
      <td>48</td>
      <td>52</td>
      <td>199</td>
      <td>0</td>
    </tr>
    <tr>
      <th>Age &lt; 30 &amp; Age &gt;= 20</th>
      <td>48</td>
      <td>48</td>
      <td>52</td>
      <td>293</td>
      <td>0</td>
    </tr>
    <tr>
      <th>Age &lt; 40 &amp; Age &gt;= 30</th>
      <td>52</td>
      <td>48</td>
      <td>52</td>
      <td>199</td>
      <td>0</td>
    </tr>
    <tr>
      <th>Age &gt;= 40</th>
      <td>48</td>
      <td>48</td>
      <td>52</td>
      <td>196</td>
      <td>0</td>
    </tr>
  </tbody>
</table>
</div>


