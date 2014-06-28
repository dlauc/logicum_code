# -*- coding: utf-8 -*-
__author__ = 'D'

from itertools import chain, combinations
from nltk import Tree

def toTeX(s,bold=False):
    if s=='i': r= '\\kond '
    elif s=='k': r='\\wedge '
    elif s=='d': r='\\vee '
    elif s=='e': r='\\bi '
    elif s=='n': r='\\lnot '
    elif s=='T': r='\\top '
    elif s=='F': r='\\bot '
    else: r=str(s)
    if bold: r='\\boldsymbol{'+r+'}'
    return r

def toHTML(s,bold=False):
    if s=='i': r= '\\to '
    elif s=='k': r='\\wedge '
    elif s=='d': r='\\vee '
    elif s=='e': r='\\iff '
    elif s=='n': r='\\neg '
    elif s=='T': r='\\top '
    elif s=='F': r='\\bot '
    else: r=str(s)
    if bold: r='\boldsymbol{'+r+'}'
    return r

def toTeXs(s,rem_out_p=True):
    s= ''.join([toTeX(a) for a in list(s)])
    if rem_out_p and s[0]=='(': s=s[1:-1]
    return s

def all_subsets(ss):
  return chain(*map(lambda x: combinations(ss, x), range(0, len(ss)+1)))

def subtree_len(a):
    if isinstance(a, Tree):
        return len(a.leaves())
    else: return 1

def tree2str(t):
    if not isinstance(t,Tree):
        return t
    f1= t.leaves()
    f2=[]
    for i in f1:
        if isinstance(i,list):
            f2.append(i[0])
        else:
            f2.append(i)
    return ''.join(f2)

