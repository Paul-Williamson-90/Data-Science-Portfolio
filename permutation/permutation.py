#!/usr/bin/env python
# coding: utf-8

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.pyplot import cm
import pandas as pd
from scipy import stats
from scipy.stats import probplot



def bootstrap_statistic(data = None, statistic = 'mean', show = False):
    """
    Creates bootstrapped statistics for a given sample and statistic.
        - Original: The original statistic of choice for the given sample
        - Bias: How much the mean of the bootstrap distribution differs from the original statistic
        - Std. error: The standard error of the bootstrap statistic distribution
        - LCI: The 0.05 confidence interval found via empirical method
        - UCI: The 0.95 confidence interval found via empirical method
    """
    results = []
    try:
        data = np.array(data)
        sample_size = len(data)
    except Exception as e:
        raise TypeError(e)
    if statistic == 'mean':
        for i in range(3000):
            results.append(np.random.choice(data, sample_size, replace = True).mean())
        data_stat = data.mean()
        results = np.array(results)
    elif statistic == 'median':
        for i in range(3000):
            results.append(np.median(np.random.choice(data, sample_size, replace = True)))
        data_stat = np.median(data)
        results = np.array(results)
    else:
        raise TypeError("statistic not recognised, please choose either 'mean' or 'median'.")
    
    conf = np.array([x - data_stat for x in results])
    conf.sort()
    LCI = data_stat - conf[int(len(conf)*0.05)]
    UCI = data_stat - conf[int(len(conf)*0.95)]
    
    if show == True:
        fig, ax = plt.subplots(figsize=(10,6), facecolor='white')
        weights = np.ones_like(results)/float(len(results))
        y, x, _ = ax.hist(results, bins = 30, weights = weights, 
                label = 'bootstrap dist.', alpha = 0.5)
        
        ax.fill_between(x = [results.mean() - data_stat, results.mean() + data_stat], 
                        y1 = 0, y2 = y.max(), color = 'red', alpha = 0.05, 
                        label = 'bias')
        ax.fill_between(x = [LCI,UCI], y1 = 0, y2 = y.max(), color = 'grey', alpha = 0.2, 
                        label = 'confidence interval (95%)')
        ax.axvline(x = data_stat, ls = 'dashed', 
                label = f'observed {statistic}', color = 'red')
        ax.axvline(x = results.mean(), ls = 'dashed', 
                label = f'bootstrap mean', color = 'green')
        ax.grid()
        ax.legend()
        ax.set_xlabel('statistic value')
        ax.set_ylabel('density')
        ax.set_title(f'Bootstrap of {statistic} for sample.')
        plt.show()
    print(f'Original {statistic}: {data_stat}')
    print(f'Bias: {results.mean() - data_stat}')
    print(f'Std. error: {results.std()}')
    print(f'LCI: {LCI}, UCI: {UCI}')    
 
def check_dist(data = None, dist = 'norm', sparams = None):
    """
    Uses a QQ plot to check if a sample meets a specific distribution.
    """
    # Distribution checks
    dist_continu = [d.__str__() for d in dir(stats) if
                   isinstance(getattr(stats, d), stats.rv_continuous)]
    dist_discrete = [d.__str__() for d in dir(stats) if
                   isinstance(getattr(stats, d), stats.rv_discrete)]
    if dist not in dist_continu and dist not in dist_discrete:
        dist_continu = ', '.join(dist_continu)
        dist_discrete = ', '.join(dist_discrete)
        raise TypeError('Please choose a dist from: ',
                        'CONTINUOUS:','-',dist_continu,'-',
                       'DISCRETE:','-',dist_discrete)
    # Plot results
    fig, ax = plt.subplots(figsize=(6,6), facecolor = 'white')
    probplot(data, dist = dist, plot = ax, sparams = sparams, rvalue = True)
    ax.grid()
    plt.show()
    
def permutation_test_on_A(data = None, data_type = None):
    """
    Conducts a permutation test on a collection of samples to determine if they meet a null hypothesis
    of the differences between the first and other sample groups cannot be ruled out as random chance.
    
    The alternative hypothesis is that the difference between sample groups are statistically significant
    and unlikely due to random chance.
    
    data = list of sample groups (numpy.darray)
    data_type = 'continuous' or 'discrete'
    """
    def permute(data, group_sizes):
        """
        Conducts permutation on sample groups, used with permutation_test function.
        """
        bag = [list(x) for x in data]
        bag = np.array([x for xs in bag for x in xs])
        n = set(x for x in range(sum(group_sizes)))
        groups = []
        for size in group_sizes:
            g_idx = set(np.random.choice(list(n), size))
            groups.append(g_idx)
            n -= g_idx
        groups = [bag[list(gr)] for gr in groups]
        return [gr.mean() - groups[0].mean() for gr in groups[1:]]

    if not type(data) == list:
        raise TypeError('permutation_test() requires data as a list of sample groups in numpy.darray format.')
    for group in data:
        if type(group) is not np.ndarray:
            raise TypeError('permutation_test() requires data as a list of sample groups in numpy.darray format.')
    no_sample_groups = len(data)
    group_sizes = [len(x) for x in data]
    color = iter(cm.rainbow(np.linspace(0, 1, no_sample_groups)))
    
    if data_type == 'continuous':
        perm_diffs = [permute(data, group_sizes) for _ in range(3000)]

        mean_a = data[0].mean()
        p_values = []
        for e,diffs in enumerate(range(len(perm_diffs[0]))):
            mean_b = data[e+1].mean()
            p = round(np.mean([x[diffs] for x in perm_diffs] > mean_b - mean_a),2)
            p_values.append(p)

        fig, ax = plt.subplots(figsize = (10,6), facecolor = 'white')
        for i in range(len(perm_diffs[0])):
            ax.hist([item[i] for item in perm_diffs], bins = 30, label = f'group {i+2}+1', alpha = 0.3)

        for e,gr in enumerate(data[1:]):
            c = next(color)
            ax.axvline(x = gr.mean() - data[0].mean(), ls = 'dashed', color = c, lw = 3,
                       label = f'observed: group {e+2} on group 1 (p-value:{p_values[e]})')
        ax.set_xlabel('Differences')
        ax.set_ylabel('Frequency')
        ax.legend()
        ax.grid()
        plt.show()
    
    elif data_type == 'discrete':
        obs_perc_diffs = [data[0].mean() - data[i+1].mean() for i in range(no_sample_groups-1)]
        perm_diffs = [permute(data, group_sizes) for _ in range(3000)]
        
        mean_a = data[0].mean()
        p_values = [round(np.mean([diff[i] > obs_perc_diffs[i] 
                             for diff in perm_diffs]),2) for i in range(no_sample_groups-1)]
        
        fig, ax = plt.subplots(figsize = (10,6), facecolor = 'white')
        for i in range(len(perm_diffs[0])):
            ax.hist([item[i] for item in perm_diffs], bins = 30, label = f'group {i+2}+1', alpha = 0.3)
        
        for e,diff in enumerate(obs_perc_diffs):
            c = next(color)
            ax.axvline(x = diff, ls = 'dashed', color = c, lw = 3, 
                       label = f'observed: group {e+2} on group 1 (p-value:{p_values[e]})')
        ax.set_xlabel('Differences')
        ax.set_ylabel('Frequency')
        ax.legend()
        ax.grid()
        plt.show()
        
def ANOVA_permutation(data = None):
    """
    Conducts an ANOVA permutation test on a group of samples.
    
    data = list(np.darray)
    """
    def permute(data):
        group_sizes = [len(x) for x in data]
        group_idxs = [[x+inc for x in range(gs)] for (gs,inc) 
                      in zip(group_sizes,[0]+
                             [group_sizes[x]+sum(group_sizes[:x]) if x > 0 else group_sizes[x] 
                              for x in range(len(group_sizes[:]))])]
        bag = [list(x) for x in data]
        bag = np.array([x for xs in bag for x in xs])
        np.random.shuffle(bag)
        new_groups = [bag[idxs] for idxs in group_idxs]
        return np.array([np.mean(gr) for gr in new_groups]).var()
    
    obs_means = [np.mean(gr) for gr in data]
    obs_var = np.array(obs_means).var()
    print('Observed means:', obs_means)
    print('Variance:', obs_var)
    perm_var = [permute(data) for _ in range(3000)]
    print(f'P-value: {np.mean([ var > obs_var for var in perm_var])}')

def chi2_permutation(data = None):
    """
    Conducts a chi2 permutation test on a group of samples
    
    data = list(np.darray)
    """
    def chi2(observed, expected):
        pearson_residuals = []
        for row, expect in zip(observed, expected):
            pearson_residuals.append([(observe - expect) ** 2 / expect for observe in row])
        return np.sum(pearson_residuals)
    
    def permute(bag, group_sizes, classes, expected):
        sample = [np.random.choice(bag, g_size, replace = False) for g_size in group_sizes]
        sample = [[np.count_nonzero(gr == cl)/len(gr) for cl in classes]
               for gr in sample]
        return chi2(sample, expected)
    
    bag = [list(x) for x in data]
    bag = np.array([x for xs in bag for x in xs])
    np.random.shuffle(bag)
    
    no_sample_groups = len(data)
    group_sizes = [len(x) for x in data]
    classes = np.unique(bag)
    
    expected = [np.count_nonzero(bag == cl)/no_sample_groups for cl in classes]
    observed = [[np.count_nonzero(gr == cl)/len(gr) for cl in classes]
               for gr in data]
    
    chi2observed = chi2(observed, expected)
    perm_chi2 = [permute(bag, group_sizes, classes, expected) for _ in range(3000)]
    p_value = round(sum((perm_chi2 > chi2observed) / len(perm_chi2)),2)
    
    print(f'Observed chi2: {chi2observed}')
    print(f'P-value: {p_value}')    
    
    
def help_me():
    """
    Provides a list of available functions, their use cases, and requirements.
    """
    functions = {'bootstrap_statistic()':{'Function:':'bootstrap_statistic()',
                                       'Args:':"data = numpy.darray, statistic = 'mean' or 'median' (default = 'mean'), show = bool (default = False)",
                                       'Description:':"""
        Creates bootstrapped statistics for a given sample and statistic.
        
        Returns:
        - Original: The original statistic of choice for the given sample
        - Bias: How much the mean of the bootstrap distribution differs from the original statistic
        - Std. error: The standard error of the bootstrap statistic distribution
        - LCI: The 0.05 confidence interval found via empirical method
        - UCI: The 0.95 confidence interval found via empirical method""",
                                       'Assumptions:':'None'},
                 
                 'check_dist()':{'Function:':'check_dist()',
                                       'Args:':"data = numpy.darray, dist = str (default = 'norm'), sparams = tuple (default = None)",
                                       'Description:':"""
        Uses a QQ plot to check if a sample meets a specific distribution.
        Some distributions require a tuple sparams with specific values for that dist.""",
                                       'Assumptions:':'None'},
                 
                 'permutation_test_on_A()':{'Function:':'permutation_test_on_A()',
                                       'Args:':"data = list(numpy.darray), data_type = str (default = None)",
                                       'Description:':"""
        Conducts a permutation test on a collection of samples to determine if they meet a null hypothesis
        of the differences between the first sample group and other sample groups cannot be ruled out as 
        random chance.

        The alternative hypothesis is that the difference between sample groups are statistically 
        significant and unlikely due to random chance.

        data = list of sample groups (numpy.darray)
        data_type = 'continuous' or 'discrete'""",
                                       'Assumptions:':'None'},
                 
                 'ANOVA_permutation()':{'Function:':'ANOVA_permutation()',
                                       'Args:':"data = list(numpy.darray)",
                                       'Description:':"""
        Conducts an ANOVA permutation test on a collection of numerical samples to determine if they 
        meet a null hypothesis where the differences between sample groups cannot be ruled out as 
        random chance.

        The alternative hypothesis is that the difference between sample groups are statistically 
        significant and unlikely due to random chance.

        data = list of sample groups (numpy.darray)""",
                                       'Assumptions:':'None'},
                 
                 'chi2_permutation()':{'Function:':'chi2_permutation()',
                                       'Args:':"data = list(numpy.darray)",
                                       'Description:':"""
        Conducts an Chi2 permutation test on a collection of categorical samples to determine if they 
        meet a null hypothesis where the differences between sample groups cannot be ruled out as 
        random chance.

        The alternative hypothesis is that the difference between sample groups are statistically 
        significant and unlikely due to random chance.

        data = list of sample groups (numpy.darray)""",
                                       'Assumptions:':'None'}
                }
    for k in functions.keys():
        print('=========================================')
        for k1 in functions[k].keys():
            print(k1, functions[k][k1])
        print('')



if __name__ == '__main__':
    data = np.random.standard_normal(10000)
    bootstrap_statistic(data, 'median', show = True)
    bootstrap_statistic(data, 'mean', show = True)
    check_dist(data, dist = 'norm', sparams = None)
    
    data = [np.random.standard_normal(10000)+x/100 for x in range(3)]
    permutation_test_on_A(data, data_type = 'continuous')
    ANOVA_permutation(data)
    
    data = [np.random.choice([2,1,0],5000, replace = True, p = [0.25,0.25,0.5]),
           np.random.choice([2,1,0],1000, replace = True, p = [0.25,0.25,0.5]),
           np.random.choice([2,1,0],2000, replace = True, p = [0.25,0.25,0.5])]
    permutation_test_on_A(data, data_type = 'discrete')
    chi2_permutation(data)    
    
    help_me()

