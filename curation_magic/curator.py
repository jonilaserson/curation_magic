# AUTOGENERATED! DO NOT EDIT! File to edit: 00_core.ipynb (unless otherwise specified).

__all__ = ['logger', 'tc', 'get_query_features_df', 'Curator', 'AbsBoundariesCurator', 'RelBoundariesCurator']

# Cell
import pandas as pd
import numpy as np
from scipy.optimize import linprog

import logging
logger = logging.getLogger(__name__)

import unittest
tc = unittest.TestCase('__init__')


# Cell
def get_query_features_df(df_samples, queries):
    """Apply queries on df_samples and return a boolean feature dataframe.

    If X = df_bool.values, then X[i, j] is True iff condition j is true for sample i
    """
    df_bool = df_samples[[]].copy()
    for query in queries:
        try:
            df_bool[query] = df_samples.eval(query)
        except Exception as e:
            print(query, e)
            raise
    return df_bool


# Cell
class Curator(object):
    def __init__(self, df, df_cond, dedup=True, allow_violations=True):
        """Init a curator object.
        :param df: dataframe of samples (one row per samples).
        :param df_cond: dataframe of indexed by queries that can be applied to df,
                        and the columns 'min', 'max', and 'index_ref' representing
                        the required number of samples that should satisfy each query.
                        The column 'penalty_per_violation', if exist, indicates how much
                        violation penalty would a single unit of violation in each query
                        will cost (by default, 1)
        :param dedup: whether to combine rows that match the same set of queries.
                      If True (default), works faster, but slightly less accurate.
        :param allow_violations: Allow infeasible solutions (should generally be True).
        """

        self.df_bool = get_query_features_df(df, df_cond.index)
        self.df_cond = df_cond.copy()
        self.dedup = dedup
        self.allow_violations = allow_violations

        if 'penalty_per_violation' not in self.df_cond:
            self.df_cond['penalty_per_violation'] = 1
        self.df_cond['index_ref'] = self.df_cond['index_ref'].astype('int')

        A = self.df_bool.values.astype('float').T # A.shape = [queries, samples]

        if dedup:
            A, self.ix, self.cnt = np.unique(A, return_inverse=True, return_counts=True, axis=1)
            # Multiply each (binary) column of A by the number of samples with those features.
            A = A * self.cnt
            #self.df_bool = pd.DataFrame(data=A.T, columns=df_bool.columns)

        self.n_constraints, self.n_samples = A.shape
        logger.info('#constraints=%d, #samples=%d' % A.shape)

        self.linprog_params = self.get_LP_params(A, self.df_cond)

        for key, val in self.linprog_params.items():
            logger.debug(key, np.shape(val))


    @staticmethod
    def get_abs_bounds(df_cond, cnt=None):
        """Convert bounds from relative fractions to absolute quantities.

           :param b: a matrix of shape (n_constraints, 3) where each row (l, u, j)
                     if j = -1:  the constraint is    "between l and u"
                     otherwise:  the constraint is    "between l*y_j and u*y_j"
                                 where y_j is the number of *included* samples that satisfy query j,
                                 given by the cnt parameter.

           :param cnt: how many *currently included* samples are satisfy each query.
                       if cnt is not None, y_j = cnt[j]. Otherwise, infer the bounds by looking
                       at the l and u values of b[j, :].
        """
        df_cond = df_cond.copy()
        cond_min = df_cond['min']
        cond_max = df_cond['max']
        for i, j in enumerate(df_cond['index_ref']):
            if j != -1:
                cond_min.iat[i] *= (cond_min.iat[j] if cnt is None else cnt[j])
                cond_max.iat[i] *= (cond_max.iat[j] if cnt is None else cnt[j])

        df_cond[['min', 'max']] = df_cond[['min', 'max']].round().astype('int')
        return df_cond

    def get_LP_params(self, A, df_cond):
        """Returns a dictionary with the arguments to scipy.optimize.linprog"""
        raise NotImplementedError

    def decode_solution(self):
        """Returns a boolean vector of size n_samples, indicating chosen samples."""

        if not self.dedup:
            # Original samples, just round.
            included = self.solution.x[:self.n_samples].round().astype('int')
        else:
            # Original x counts fraction (between 0-1) of samples to take from each group.
            # Convert it to (integer) number of samples to take from each group:
            x = (self.solution.x[:self.n_samples] * self.cnt).round().astype('int')

            # Randomly choose from each group:
            included = np.zeros((len(self.ix),), dtype='bool')
            for g, cnt_g in enumerate(x):
                all_members = (self.ix == g).nonzero()[0]
                included_members = np.random.choice(all_members, cnt_g, replace=False)
                included[included_members] = True

        self.included = included
        print('included:', included.sum())
        return included

    def get_summary(self, included):
        """Get summary of the queries, boundaries, and the violations."""

        cnt = self.df_bool[included.astype('bool')].sum()

        summary_df = self.get_abs_bounds(self.df_cond, cnt=cnt)
        summary_df['cnt'] = cnt
        summary_df['violation'] = pd.DataFrame([summary_df['min'] - summary_df['cnt'],
                                                summary_df['cnt'] - summary_df['max']]).max().clip(0, None)
        print('actual violations:', summary_df['violation'].sum())
        return summary_df[['cnt', 'min', 'max', 'violation']]

    def run(self, method='revised simplex'):
        """Apply the LP. Use method='interior-point' for faster and less accurate solution."""

        included = summary_df = None
        self.solution = linprog(method=method, **self.linprog_params)
        logger.info(self.solution.message)

        if self.solution.success:
            print("Theoretical violations:", self.solution.fun)
            included = self.decode_solution()
            summary_df = self.get_summary(included)
        else:
            logger.error("Could not find solution.")

        return included, summary_df

# Cell
class AbsBoundariesCurator(Curator):
    def get_LP_params(self, A, df_cond):
        n_constraints, n_samples = A.shape
        df_cond = self.get_abs_bounds(df_cond) # In case the user supplied relative bounds

        bounds = [(0, 1)] * n_samples
        c = [0] * n_samples

        # Upper bound
        b_ub = df_cond['max'].values
        b_lb = df_cond['min'].values
        b_ub = np.hstack((b_ub, -b_lb))

        A_ub = np.vstack([A, # A * x <= ub
                         -A])# A * x >= lb ==> -A * x <= -lb

        if self.allow_violations: # Support non-feasible scenarios (pay penalty)
            # Add a new variable for every constraint, representing the violation.
            bounds += [(0, None)] * n_constraints
            c += df_cond['penalty_per_violation'].tolist()

            # Update the constraints to allow violations by c
            C = np.eye(n_constraints)
            A_ub = np.hstack((A_ub, np.vstack((-C, -C))))

        return dict(c=c, A_ub=A_ub, b_ub=b_ub, bounds=bounds)


# Cell
class RelBoundariesCurator(Curator):
    def get_LP_params(self, A, df_cond):
        b = df_cond[['min', 'max', 'index_ref']].values
        n_constraints, n_samples = A.shape

        #             X's                          Y's
        bounds = [(0, 1)] * n_samples + [(0, None)] * n_constraints
        c = [0] * (n_samples          +    n_constraints)

        # Equalities
        Y = np.eye(n_constraints)
        A_eq = np.hstack((A, -Y))
        b_eq = np.zeros((n_constraints,))

        # Upper bounds
        Y_ub = Y.copy()
        Y_lb = Y.copy()

        b_ub = df_cond['max'].values.copy()
        b_lb = df_cond['min'].values.copy()
        for i, j in enumerate(df_cond['index_ref']):
            if j != -1:
                Y_ub[i, j] = -b_ub[i]
                Y_lb[i, j] = -b_lb[i]
                b_ub[i] = b_lb[i] = 0
        b_ub = np.hstack((b_ub, -b_lb))

        A_ub = np.zeros((n_constraints*2, n_samples))
        A_ub = np.hstack((A_ub, np.vstack((Y_ub, -Y_lb))))


        if self.allow_violations: # Support non-feasible scenarios (pay penalty)
            # Add a new variable for every constraint, representing the violation.
            bounds += [(0, None)] * n_constraints
            c += df_cond['penalty_per_violation'].tolist()

            # Update the constraints to allow violations by c
            C = np.eye(n_constraints)
            A_ub = np.hstack((A_ub, np.vstack((-C, -C))))
            A_eq = np.hstack((A_eq, np.zeros((n_constraints, n_constraints))))

        return dict(c=c, A_eq=A_eq, b_eq=b_eq, A_ub=A_ub, b_ub=b_ub, bounds=bounds)
