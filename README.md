# Curation Magic
> Automagically curate test sets based on user given constraints


Did you ever need to sub-sample a pool of samples according to a strict set of conditions? Perhaps when designing a test set for an experiment?  This package provides an easy way to sub-sample a dataframe.

The user provides two dataframes: the first has the sample pool, and the second has queries over these samples, with the specification of the intended amount of samples that should satisfy each query in the curated set.

## Install

`pip install curation_magic`

## Instructions
Our goal is to curate a subset from a general pool of samples, that will satisfy a list of conditions as close as possible.

The pool of samples is given in a dataframe, which we'll call *df_samples*, it has one row per sample, and the columns represent all sort of meta data and features of the samples.

Let's see an example:

```python
# Load dataframe from file.
import pandas as pd

df_samples = pd.read_csv('csvs/curation_pool.csv', 
                         converters={'age':int, 'birad':int})
df_samples = df_samples.set_index('study_id')
df_samples.head(10)
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
      <th>exists</th>
      <th>data_source</th>
      <th>age</th>
      <th>density</th>
      <th>birad</th>
      <th>lesion_type</th>
      <th>largest_mass</th>
      <th>is_pos</th>
    </tr>
    <tr>
      <th>study_id</th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>1</td>
      <td>optimam</td>
      <td>56</td>
      <td>2</td>
      <td>0</td>
      <td>calcification</td>
      <td>NaN</td>
      <td>1</td>
    </tr>
    <tr>
      <th>1</th>
      <td>1</td>
      <td>optimam</td>
      <td>70</td>
      <td>4</td>
      <td>0</td>
      <td>mass</td>
      <td>16.87</td>
      <td>1</td>
    </tr>
    <tr>
      <th>2</th>
      <td>1</td>
      <td>optimam</td>
      <td>70</td>
      <td>2</td>
      <td>0</td>
      <td>mass</td>
      <td>10.15</td>
      <td>1</td>
    </tr>
    <tr>
      <th>3</th>
      <td>1</td>
      <td>optimam</td>
      <td>66</td>
      <td>2</td>
      <td>0</td>
      <td>mass</td>
      <td>10.71</td>
      <td>1</td>
    </tr>
    <tr>
      <th>4</th>
      <td>1</td>
      <td>imh</td>
      <td>49</td>
      <td>3</td>
      <td>0</td>
      <td>distortion</td>
      <td>NaN</td>
      <td>1</td>
    </tr>
    <tr>
      <th>5</th>
      <td>1</td>
      <td>optimam</td>
      <td>67</td>
      <td>2</td>
      <td>0</td>
      <td>mass</td>
      <td>9.24</td>
      <td>1</td>
    </tr>
    <tr>
      <th>6</th>
      <td>1</td>
      <td>optimam</td>
      <td>47</td>
      <td>4</td>
      <td>0</td>
      <td>mass</td>
      <td>14.35</td>
      <td>1</td>
    </tr>
    <tr>
      <th>7</th>
      <td>1</td>
      <td>optimam</td>
      <td>51</td>
      <td>3</td>
      <td>0</td>
      <td>calcification</td>
      <td>NaN</td>
      <td>1</td>
    </tr>
    <tr>
      <th>8</th>
      <td>1</td>
      <td>optimam</td>
      <td>50</td>
      <td>4</td>
      <td>0</td>
      <td>calcification</td>
      <td>NaN</td>
      <td>1</td>
    </tr>
    <tr>
      <th>9</th>
      <td>1</td>
      <td>optimam</td>
      <td>59</td>
      <td>3</td>
      <td>0</td>
      <td>calcification</td>
      <td>NaN</td>
      <td>1</td>
    </tr>
  </tbody>
</table>
</div>



The conditions are given in a second dataframe, *df_cond_abs*. 
Each row of *df_cond_abs* is indexed by a *query* that can be applied to the df_samples (i.e. by using df_samples.query(query_string)). For each query the user specifies constraints supplied, regarding how many samples in the curated subset should satisfy the query. The constraints are given as a lower-bound and upper bound (ignore the *index_ref* column).

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
      <th>min</th>
      <th>max</th>
      <th>index_ref</th>
    </tr>
    <tr>
      <th>query</th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>is_pos == "1"</th>
      <td>400</td>
      <td>400</td>
      <td>-1</td>
    </tr>
    <tr>
      <th>is_pos == "0"</th>
      <td>400</td>
      <td>400</td>
      <td>-1</td>
    </tr>
    <tr>
      <th>data_source == "optimam" &amp; is_pos == "0"</th>
      <td>160</td>
      <td>240</td>
      <td>-1</td>
    </tr>
    <tr>
      <th>data_source == "imh" &amp; is_pos == "0"</th>
      <td>160</td>
      <td>240</td>
      <td>-1</td>
    </tr>
    <tr>
      <th>data_source == "optimam" &amp; is_pos == "1"</th>
      <td>160</td>
      <td>240</td>
      <td>-1</td>
    </tr>
    <tr>
      <th>data_source == "imh" &amp; is_pos == "1"</th>
      <td>160</td>
      <td>240</td>
      <td>-1</td>
    </tr>
    <tr>
      <th>lesion_type == "mass" &amp; is_pos == "1"</th>
      <td>270</td>
      <td>300</td>
      <td>-1</td>
    </tr>
    <tr>
      <th>lesion_type == "calcification" &amp; is_pos == "1"</th>
      <td>110</td>
      <td>140</td>
      <td>-1</td>
    </tr>
    <tr>
      <th>birad == "1" &amp; is_pos == "0"</th>
      <td>300</td>
      <td>320</td>
      <td>-1</td>
    </tr>
    <tr>
      <th>birad == "2" &amp; is_pos == "0"</th>
      <td>80</td>
      <td>100</td>
      <td>-1</td>
    </tr>
    <tr>
      <th>lesion_type == "mass" &amp; largest_mass&lt;=10</th>
      <td>30</td>
      <td>40</td>
      <td>-1</td>
    </tr>
    <tr>
      <th>lesion_type == "mass" &amp; largest_mass&gt;10 &amp; largest_mass&lt;=20</th>
      <td>140</td>
      <td>180</td>
      <td>-1</td>
    </tr>
    <tr>
      <th>lesion_type == "mass" &amp; largest_mass&gt;20 &amp; largest_mass&lt;=50</th>
      <td>75</td>
      <td>110</td>
      <td>-1</td>
    </tr>
    <tr>
      <th>age&lt;50</th>
      <td>200</td>
      <td>240</td>
      <td>-1</td>
    </tr>
    <tr>
      <th>age&lt;60 &amp; age&gt;=50</th>
      <td>216</td>
      <td>264</td>
      <td>-1</td>
    </tr>
    <tr>
      <th>age&lt;70 &amp; age&gt;=60</th>
      <td>176</td>
      <td>208</td>
      <td>-1</td>
    </tr>
    <tr>
      <th>age&gt;=70</th>
      <td>120</td>
      <td>160</td>
      <td>-1</td>
    </tr>
  </tbody>
</table>
</div>



Let's use the *AbsBoundariesCurator* to find a curated set:

```python
abc = curator.AbsBoundariesCurator(df_samples, df_cond_abs)

# Note, we are using here the interior-point solver which is
# faster but less accurate than the default simplex solver.
included, summary = abc.run(method='interior-point')

# The summary shows how many were included from every query,
# and the total number of violations.
summary
```

    Theoretical violations: 4.000000001349921
    included: 799
    actual violations: 5





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
      <th>violation</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>is_pos == "1"</th>
      <td>399</td>
      <td>400</td>
      <td>400</td>
      <td>1</td>
    </tr>
    <tr>
      <th>is_pos == "0"</th>
      <td>400</td>
      <td>400</td>
      <td>400</td>
      <td>0</td>
    </tr>
    <tr>
      <th>data_source == "optimam" &amp; is_pos == "0"</th>
      <td>161</td>
      <td>160</td>
      <td>240</td>
      <td>0</td>
    </tr>
    <tr>
      <th>data_source == "imh" &amp; is_pos == "0"</th>
      <td>239</td>
      <td>160</td>
      <td>240</td>
      <td>0</td>
    </tr>
    <tr>
      <th>data_source == "optimam" &amp; is_pos == "1"</th>
      <td>241</td>
      <td>160</td>
      <td>240</td>
      <td>1</td>
    </tr>
    <tr>
      <th>data_source == "imh" &amp; is_pos == "1"</th>
      <td>158</td>
      <td>160</td>
      <td>240</td>
      <td>2</td>
    </tr>
    <tr>
      <th>lesion_type == "mass" &amp; is_pos == "1"</th>
      <td>269</td>
      <td>270</td>
      <td>300</td>
      <td>1</td>
    </tr>
    <tr>
      <th>lesion_type == "calcification" &amp; is_pos == "1"</th>
      <td>111</td>
      <td>110</td>
      <td>140</td>
      <td>0</td>
    </tr>
    <tr>
      <th>birad == "1" &amp; is_pos == "0"</th>
      <td>303</td>
      <td>300</td>
      <td>320</td>
      <td>0</td>
    </tr>
    <tr>
      <th>birad == "2" &amp; is_pos == "0"</th>
      <td>85</td>
      <td>80</td>
      <td>100</td>
      <td>0</td>
    </tr>
    <tr>
      <th>lesion_type == "mass" &amp; largest_mass&lt;=10</th>
      <td>34</td>
      <td>30</td>
      <td>40</td>
      <td>0</td>
    </tr>
    <tr>
      <th>lesion_type == "mass" &amp; largest_mass&gt;10 &amp; largest_mass&lt;=20</th>
      <td>147</td>
      <td>140</td>
      <td>180</td>
      <td>0</td>
    </tr>
    <tr>
      <th>lesion_type == "mass" &amp; largest_mass&gt;20 &amp; largest_mass&lt;=50</th>
      <td>84</td>
      <td>75</td>
      <td>110</td>
      <td>0</td>
    </tr>
    <tr>
      <th>age&lt;50</th>
      <td>212</td>
      <td>200</td>
      <td>240</td>
      <td>0</td>
    </tr>
    <tr>
      <th>age&lt;60 &amp; age&gt;=50</th>
      <td>249</td>
      <td>216</td>
      <td>264</td>
      <td>0</td>
    </tr>
    <tr>
      <th>age&lt;70 &amp; age&gt;=60</th>
      <td>198</td>
      <td>176</td>
      <td>208</td>
      <td>0</td>
    </tr>
    <tr>
      <th>age&gt;=70</th>
      <td>140</td>
      <td>120</td>
      <td>160</td>
      <td>0</td>
    </tr>
  </tbody>
</table>
</div>



As you can see above, the linear solver had 4 violations, but after we decoded the solution (round the $x_j$ values and decide which samples to include), there were 10 violations in total. Our curated set has 802 members instead of 800, specifically two extra positives. Also, we have 3 too many positive studies from optimam, and 3 too few studies from imh.

Now we can go back to the original samples dataframe, and add a new column indicating which samples would participate in the final set:

```python
df_samples['included'] = included
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
      <th>exists</th>
      <th>data_source</th>
      <th>age</th>
      <th>density</th>
      <th>birad</th>
      <th>lesion_type</th>
      <th>largest_mass</th>
      <th>is_pos</th>
      <th>included</th>
    </tr>
    <tr>
      <th>study_id</th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>1</td>
      <td>optimam</td>
      <td>56</td>
      <td>2</td>
      <td>0</td>
      <td>calcification</td>
      <td>NaN</td>
      <td>1</td>
      <td>True</td>
    </tr>
    <tr>
      <th>1</th>
      <td>1</td>
      <td>optimam</td>
      <td>70</td>
      <td>4</td>
      <td>0</td>
      <td>mass</td>
      <td>16.87</td>
      <td>1</td>
      <td>True</td>
    </tr>
    <tr>
      <th>2</th>
      <td>1</td>
      <td>optimam</td>
      <td>70</td>
      <td>2</td>
      <td>0</td>
      <td>mass</td>
      <td>10.15</td>
      <td>1</td>
      <td>True</td>
    </tr>
    <tr>
      <th>3</th>
      <td>1</td>
      <td>optimam</td>
      <td>66</td>
      <td>2</td>
      <td>0</td>
      <td>mass</td>
      <td>10.71</td>
      <td>1</td>
      <td>False</td>
    </tr>
    <tr>
      <th>4</th>
      <td>1</td>
      <td>imh</td>
      <td>49</td>
      <td>3</td>
      <td>0</td>
      <td>distortion</td>
      <td>NaN</td>
      <td>1</td>
      <td>True</td>
    </tr>
  </tbody>
</table>
</div>



### Using Relative bounds for the constraints

The fact that the condition boundaties are given in absolute integer numbers is actually a limitation:
Say we are willing to have some flexibility with regard to the number of negatives we curate (i.e. anything in the range 350-450 is fine), but within the chosen set of negatives, we would like 25% to be with birad=2. Since we don't know how many negatives we'll turn up with, there is no way to put a tight bound (in absolute numbers) on the number of birad=2 samples.

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
      <th>min</th>
      <th>max</th>
      <th>index_ref</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>exists == "1"</td>
      <td>800.00</td>
      <td>800.00</td>
      <td>-1</td>
    </tr>
    <tr>
      <th>1</th>
      <td>is_pos == "1"</td>
      <td>0.50</td>
      <td>0.50</td>
      <td>0</td>
    </tr>
    <tr>
      <th>2</th>
      <td>is_pos == "0"</td>
      <td>0.50</td>
      <td>0.50</td>
      <td>0</td>
    </tr>
    <tr>
      <th>3</th>
      <td>data_source == "optimam" &amp; is_pos == "0"</td>
      <td>0.40</td>
      <td>0.60</td>
      <td>2</td>
    </tr>
    <tr>
      <th>4</th>
      <td>data_source == "imh" &amp; is_pos == "0"</td>
      <td>0.40</td>
      <td>0.60</td>
      <td>2</td>
    </tr>
    <tr>
      <th>5</th>
      <td>data_source == "optimam" &amp; is_pos == "1"</td>
      <td>0.40</td>
      <td>0.60</td>
      <td>1</td>
    </tr>
    <tr>
      <th>6</th>
      <td>data_source == "imh" &amp; is_pos == "1"</td>
      <td>0.40</td>
      <td>0.60</td>
      <td>1</td>
    </tr>
    <tr>
      <th>7</th>
      <td>lesion_type == "mass" &amp; is_pos == "1"</td>
      <td>0.65</td>
      <td>0.70</td>
      <td>1</td>
    </tr>
    <tr>
      <th>8</th>
      <td>lesion_type == "calcification" &amp; is_pos == "1"</td>
      <td>0.30</td>
      <td>0.35</td>
      <td>1</td>
    </tr>
    <tr>
      <th>9</th>
      <td>birad == "1" &amp; is_pos == "0"</td>
      <td>0.75</td>
      <td>0.80</td>
      <td>2</td>
    </tr>
    <tr>
      <th>10</th>
      <td>birad == "2" &amp; is_pos == "0"</td>
      <td>0.20</td>
      <td>0.25</td>
      <td>2</td>
    </tr>
    <tr>
      <th>11</th>
      <td>lesion_type == "mass" &amp; largest_mass&lt;=10</td>
      <td>0.10</td>
      <td>0.15</td>
      <td>7</td>
    </tr>
    <tr>
      <th>12</th>
      <td>lesion_type == "mass" &amp; largest_mass&gt;10 &amp; larg...</td>
      <td>0.50</td>
      <td>0.60</td>
      <td>7</td>
    </tr>
    <tr>
      <th>13</th>
      <td>lesion_type == "mass" &amp; largest_mass&gt;20 &amp; larg...</td>
      <td>0.25</td>
      <td>0.30</td>
      <td>7</td>
    </tr>
    <tr>
      <th>14</th>
      <td>age&lt;50</td>
      <td>0.25</td>
      <td>0.30</td>
      <td>0</td>
    </tr>
    <tr>
      <th>15</th>
      <td>age&lt;60 &amp; age&gt;=50</td>
      <td>0.27</td>
      <td>0.33</td>
      <td>0</td>
    </tr>
    <tr>
      <th>16</th>
      <td>age&lt;70 &amp; age&gt;=60</td>
      <td>0.22</td>
      <td>0.26</td>
      <td>0</td>
    </tr>
    <tr>
      <th>17</th>
      <td>age&gt;=70</td>
      <td>0.15</td>
      <td>0.20</td>
      <td>0</td>
    </tr>
  </tbody>
</table>
</div>



Here, in line 10, we ask that the number of samples satisfying the query [*birad == "2" & is_pos == "0"*] would be at least 20% and no more than 25% of the samples satisfying query 2 [*is_pos == "0"*], as indicated by the column *index_ref*. This is how we were able to define a condition relevant to the negative set without knowing how many negative we'll have at the end!

We still have to ground the solution in some absolute number of desired sample, so we used integer boundaries for the first query above, simply by setting *index_ref=-1* (otherwise the solution is not well defined and the LP solver might not converge).

Let's run the *RelBoundariesCurator* to solve this (here with the simplex method):

```python
cc = curator.RelBoundariesCurator(df_samples, df_cond_rel)
included, summary = cc.run()
df_samples['included'] = included
summary
```

    Theoretical violations: 4.000000000000157
    included: 800
    actual violations: 4





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
      <th>violation</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>exists == "1"</th>
      <td>800</td>
      <td>800</td>
      <td>800</td>
      <td>0</td>
    </tr>
    <tr>
      <th>is_pos == "1"</th>
      <td>400</td>
      <td>400</td>
      <td>400</td>
      <td>0</td>
    </tr>
    <tr>
      <th>is_pos == "0"</th>
      <td>400</td>
      <td>400</td>
      <td>400</td>
      <td>0</td>
    </tr>
    <tr>
      <th>data_source == "optimam" &amp; is_pos == "0"</th>
      <td>160</td>
      <td>160</td>
      <td>240</td>
      <td>0</td>
    </tr>
    <tr>
      <th>data_source == "imh" &amp; is_pos == "0"</th>
      <td>240</td>
      <td>160</td>
      <td>240</td>
      <td>0</td>
    </tr>
    <tr>
      <th>data_source == "optimam" &amp; is_pos == "1"</th>
      <td>242</td>
      <td>160</td>
      <td>240</td>
      <td>2</td>
    </tr>
    <tr>
      <th>data_source == "imh" &amp; is_pos == "1"</th>
      <td>158</td>
      <td>160</td>
      <td>240</td>
      <td>2</td>
    </tr>
    <tr>
      <th>lesion_type == "mass" &amp; is_pos == "1"</th>
      <td>263</td>
      <td>260</td>
      <td>280</td>
      <td>0</td>
    </tr>
    <tr>
      <th>lesion_type == "calcification" &amp; is_pos == "1"</th>
      <td>120</td>
      <td>120</td>
      <td>140</td>
      <td>0</td>
    </tr>
    <tr>
      <th>birad == "1" &amp; is_pos == "0"</th>
      <td>300</td>
      <td>300</td>
      <td>320</td>
      <td>0</td>
    </tr>
    <tr>
      <th>birad == "2" &amp; is_pos == "0"</th>
      <td>80</td>
      <td>80</td>
      <td>100</td>
      <td>0</td>
    </tr>
    <tr>
      <th>lesion_type == "mass" &amp; largest_mass&lt;=10</th>
      <td>39</td>
      <td>26</td>
      <td>39</td>
      <td>0</td>
    </tr>
    <tr>
      <th>lesion_type == "mass" &amp; largest_mass&gt;10 &amp; largest_mass&lt;=20</th>
      <td>135</td>
      <td>132</td>
      <td>158</td>
      <td>0</td>
    </tr>
    <tr>
      <th>lesion_type == "mass" &amp; largest_mass&gt;20 &amp; largest_mass&lt;=50</th>
      <td>79</td>
      <td>66</td>
      <td>79</td>
      <td>0</td>
    </tr>
    <tr>
      <th>age&lt;50</th>
      <td>240</td>
      <td>200</td>
      <td>240</td>
      <td>0</td>
    </tr>
    <tr>
      <th>age&lt;60 &amp; age&gt;=50</th>
      <td>264</td>
      <td>216</td>
      <td>264</td>
      <td>0</td>
    </tr>
    <tr>
      <th>age&lt;70 &amp; age&gt;=60</th>
      <td>176</td>
      <td>176</td>
      <td>208</td>
      <td>0</td>
    </tr>
    <tr>
      <th>age&gt;=70</th>
      <td>120</td>
      <td>120</td>
      <td>160</td>
      <td>0</td>
    </tr>
  </tbody>
</table>
</div>



In our decoded solution, the total number of violations was 4, exactly the same as in the optimal LP solution. This means that our solution is indeed optimal, since the optimal LP target value is always a lower bound on the *integer* progam target.
