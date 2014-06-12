# -*- coding: utf-8 -*-
__author__ = 'D'

# Reduction ad Abdsurdum
# function for RAA

# reduction_eval return truth value (True/False/None) and degrees of freedom for True i False in given valuation (val)
#  returns -1 if evaluation is already determined

from utils import subtree_len,tree2str,all_subsets

def reductio_eval(f,val):
    allpv = f.allPV()
    freevar = allpv - set(val.keys())

    truevar=set([key for key, value in val.iteritems() if value == True])
    if len(freevar)>0:
        trueCount=0
        falseCount=0
        for ss in all_subsets(freevar):
            if f.evaluate(set(ss).union(truevar)): trueCount+=1
            else: falseCount+=1
    else:
        if f.evaluate(truevar):
            trueCount=-1
            falseCount=0
        else:
            falseCount=-1
            trueCount=0
    return((trueCount,falseCount))

def reductio_vals(f,val,truth):
    allpv = f.allPV()
    freevar = allpv - set(val.keys())
    truevar=set([key for key, value in val.iteritems() if value == True])
    vals = []
    for ss in all_subsets(freevar):
        if f.evaluate(set(ss).union(truevar))==truth:
            vals.add(set(ss).union(truevar))
    return vals

# n-torka - redni broj, formula tree, istinitost bool, zadano vrednovanje dict, sve s.v.
# steps - za prikazati postupak, lista listi [rbr, poz, istin. vrijed.], pos - pozicija u izvornoj formuli
# TO DO !!!!:
    # provjeriti radi li za duže - posebno račvanje
    # provjeriti steps - pozicije - dodati komentare ?
    # napraviti elegantnije
def reductio_do(rbr,f,truth,val,steps,pos,rbrtab):
    if f[0]=='(':
        pos2 = pos+1+subtree_len(f[1])
        steps.append([rbrtab,rbr,pos2,truth])
        (t1,f1) = reductio_eval(f[1],val)
        (t2,f2) = reductio_eval(f[3],val)
        val_copy={}
        if f[2]=='i':
            if not truth:

                if t1<f2: # lijeva strana više određena (manje stupnjeva slobode)
                    (ab_found,rbr2) = reductio_do(rbr+1,f[1],True,val,steps,pos+1,rbr+1)
                    rbr3=rbr2
                    if not ab_found:
                        (ab_found,rbr3) = reductio_do(rbr2+1,f[3],False,val,steps, pos2+1,rbr+1)
                else:
                    (ab_found,rbr2) = reductio_do(rbr+1,f[3],False,val,steps, pos2+1,rbr+1)
                    rbr3=rbr2
                    if not ab_found:
                        (ab_found,rbr3) = reductio_do(rbr2+1,f[1],True,val,steps,pos+1,rbr+1)
            else:
                if t1==-1 or f1==0: # konsekvens mora biti istinit
                    steps.append([rbr,rbr,pos+1,True])
                    (ab_found,rbr3) = reductio_do(rbr+1,f[3],True,val,steps,pos2+1,rbr+1)
                elif f2==-1 or t2==0: # antecedens mora biti neistinit
                    steps.append([rbr,rbr,pos2+1,False])
                    (ab_found,rbr3) = reductio_do(rbr+1,f[1],False,val,steps,pos+1,rbr+1)
                elif f1==-1 or t2==-1: # već istinit  !!!! isto dodati ostalim veznicima prije račvanja
                    steps.append([rbr,rbr,pos2+1,t2==-1])
                    steps.append([rbr,rbr,pos+1,f1!=-1])
                    return (False,rbr+1)
                else: #račvanje
                    steps.append([rbr,rbr,pos2,'?'])
                    val_copy=val.copy()
                    if f1<t2:
                        (ab_found,rbr2) = reductio_do(rbr+1,f[1],False,val,steps,pos+1,rbr+1)
                        if ab_found:
                            (ab_found,rbr3) = reductio_do(rbr2+1,f[3],True,val_copy,steps,pos2+1,rbr+1)
                        else: rbr3=rbr2
                    else:
                        (ab_found,rbr2) = reductio_do(rbr+1,f[3],True,val,steps,pos+1,rbr+1)
                        if ab_found:
                            (ab_found,rbr3) = reductio_do(rbr2+1,f[1],False,val_copy,steps,pos2+1,rbr+1)
                        else: rbr3=rbr2
        if f[2]=='k':
            if truth:
                if t1<t2:
                    (ab_found,rbr2) = reductio_do(rbr+1,f[1],True,val,steps,pos+1,rbr+1)
                    rbr3=rbr2
                    if not ab_found:
                        (ab_found,rbr3) = reductio_do(rbr2+1,f[3],True,val,steps, pos2+1,rbr+1)
                else:
                    (ab_found,rbr2) = reductio_do(rbr+1,f[3],True,val,steps,pos2+1,rbr+1)
                    rbr3=rbr2
                    if not ab_found:
                        (ab_found,rbr3) = reductio_do(rbr2+1,f[1],True,val,steps, pos+1,rbr+1)
            else:
                if t1==-1 or f1==0: # drugi konjunkt mora biti neistinit
                    (ab_found,rbr3) = reductio_do(rbr+1,f[3],False,val,steps,pos+1,rbr+1)
                elif t2==-1 or f2==0: # prvi mora biti neistinit
                    (ab_found,rbr3) = reductio_do(rbr+1,f[1],False,val,steps,pos+1,rbr+1)
                else: #račvanje
                    steps.append([rbrtab,rbr,pos2,'?'])
                    val_copy=val.copy()
                    (ab_found,rbr2) = reductio_do(rbr+1,f[1],False,val,steps,pos+1,rbr+1)
                    if ab_found:
                        (ab_found,rbr3) = reductio_do(rbr2+1,f[3],False,val_copy,steps,pos2+1,rbr+1)
                    else: rbr3=rbr2
        if f[2]=='d':
            if not truth:
                if f1<f2:
                    (ab_found,rbr2) = reductio_do(rbr+1,f[1],False,val,steps,pos+1,rbr+1)
                    rbr3=rbr2
                    if not ab_found:
                        (ab_found,rbr3) = reductio_do(rbr2+1,f[3],False,val,steps, pos2+1,rbr+1)
                else:
                    (ab_found,rbr2) = reductio_do(rbr+1,f[3],False,val,steps,pos2+1,rbr+1)
                    rbr3=rbr2
                    if not ab_found:
                        (ab_found,rbr3) = reductio_do(rbr2+1,f[1],False,val,steps, pos+1,rbr+1)
            else:
                if f1==-1 or t1==0: # drugi disjunkt mora biti istinit
                    steps.append([rbr,rbr,pos+1,False])
                    (ab_found,rbr3) = reductio_do(rbr+1,f[3],True,val,steps,pos+1,rbr+1)
                elif f2==-1 or t2==0: # prvi mora biti istinit
                    steps.append([rbr,rbr,pos2+1,False])
                    (ab_found,rbr3) = reductio_do(rbr+1,f[1],True,val,steps,pos+1,rbr+1)
                else: #račvanje
                    steps.append([rbrtab,rbr,pos2,'?'])
                    val_copy=val.copy()
                    if t1<t2:
                        (ab_found,rbr2) = reductio_do(rbr+1,f[1],True,val,steps,pos+1,rbr+1)
                        if ab_found:
                            (ab_found,rbr3) = reductio_do(rbr2+1,f[3],True,val_copy,steps,pos2+1,rbr+1)
                        else: rbr3=rbr2
                    else:
                        (ab_found,rbr2) = reductio_do(rbr+1,f[3],True,val,steps,pos+1,rbr+1)
                        if ab_found:
                            (ab_found,rbr3) = reductio_do(rbr2+1,f[1],True,val_copy,steps,pos2+1,rbr+1)
                        else: rbr3=rbr2
        if f[2]=='e':
            if truth:
                if f1==-1 or t1==0: # drugi mora biti neistinit
                    (ab_found,rbr3) = reductio_do(rbr+1,f[3],False,val,steps,pos+1,rbr+1)
                elif f2==-1 or t2==0: # prvi mora biti ne istinit
                    (ab_found,rbr3) = reductio_do(rbr+1,f[1],False,val,steps,pos+1,rbr+1)
                elif t1==-1 or f1==0: # drugi  mora biti istinit
                    (ab_found,rbr3) = reductio_do(rbr+1,f[3],True,val,steps,pos+1,rbr+1)
                elif t2==-1 or f2==0: # prvi mora biti istinit
                    (ab_found,rbr3) = reductio_do(rbr+1,f[1],True,val,steps,pos+1,rbr+1)
                else: #račvanje
                    steps.append([rbrtab,rbr,pos2,'?'])
                    val_copy=val.copy()
                    if t1<t2:
                        (ab_found,rbr2) = reductio_do(rbr+1,f[1],True,val,steps,pos+1,rbr+1)
                        if not ab_found:
                            (ab_found,rbr2) = reductio_do(rbr+1,f[3],True,val,steps,pos+1,rbr+1)
                        else: rbr3=rbr2
                    else:
                        (ab_found,rbr2) = reductio_do(rbr+1,f[3],True,val,steps,pos+1,rbr+1)
                        if not ab_found:
                            (ab_found,rbr2) = reductio_do(rbr+1,f[1],True,val,steps,pos+1,rbr+1)
                        else: rbr3=rbr2
                    if ab_found:
                        if f1<f2:
                            (ab_found,rbr3) = reductio_do(rbr2+1,f[1],False,val_copy,steps,pos2+1,rbr+1)
                            if not ab_found:
                                (ab_found,rbr3) = reductio_do(rbr2+1,f[3],False,val_copy,steps,pos2+1,rbr+1)
                        else:
                            (ab_found,rbr3) = reductio_do(rbr2+1,f[3],False,val_copy,steps,pos2+1,rbr+1)
                            if not ab_found:
                                (ab_found,rbr3) = reductio_do(rbr2+1,f[1],False,val_copy,steps,pos2+1,rbr+1)
                    else: rbr3=rbr2
            else:
                if t1==-1 or f1==0: # drugi mora biti neistinit
                    (ab_found,rbr3) = reductio_do(rbr+1,f[3],False,val,steps,pos2+1,rbr+1)
                elif t2==-1 or f2==0: # prvi mora biti ne istinit
                    (ab_found,rbr3) = reductio_do(rbr+1,f[1],False,val,steps,pos+1,rbr+1)
                elif f1==-1 or t1==0: # drugi  mora biti istinit
                    (ab_found,rbr3) = reductio_do(rbr+1,f[3],True,val,steps,pos2+1,rbr+1)
                elif f2==-1 or t2==0: # prvi mora biti istinit
                    (ab_found,rbr3) = reductio_do(rbr+1,f[1],True,val,steps,pos+1,rbr+1)
                else: #račvanje
                    steps.append([rbrtab,rbr,pos2,'?'])
                    val_copy=val.copy()
                    if t1<f2:
                        (ab_found,rbr2) = reductio_do(rbr+1,f[1],True,val,steps,pos+1,rbr+1)
                        if not ab_found:
                            (ab_found,rbr3) = reductio_do(rbr2+1,f[3],False,val,steps,pos2+1,rbr+1)
                        else: rbr3=rbr2
                    else:
                        (ab_found,rbr2) = reductio_do(rbr+1,f[3],True,val,steps,pos+1,rbr+1)
                        if not ab_found:
                            (ab_found,rbr3) = reductio_do(rbr2+1,f[1],False,val,steps,pos2+1,rbr+1)
                        else: rbr3=rbr2
                    if ab_found:
                        rbr=rbr3
                        if f1<t2:
                            (ab_found,rbr2) = reductio_do(rbr+1,f[1],False,val_copy,steps,pos+1,rbr+1)
                            if not ab_found:
                                (ab_found,rbr3) = reductio_do(rbr2+1,f[3],True,val_copy,steps,pos2+1,rbr+1)
                            else: rbr3=rbr2
                        else:
                            (ab_found,rbr2) = reductio_do(rbr+1,f[3],False,val_copy,steps,pos+1,rbr+1)
                            if not ab_found:
                                (ab_found,rbr3) = reductio_do(rbr2+1,f[1],True,val_copy,steps,pos2+1,rbr+1)
                            else: rbr3=rbr2
                    else: rbr3=rbr2
        return (ab_found, rbr3)

    elif f[0]=='n':
        steps.append([rbrtab,rbr,pos,truth])
        (ab_found,rbr2) = reductio_do(rbr+1,f[1],not truth,val,steps,pos+1,rbr+1)
        return (ab_found,rbr2)
    elif f[0] in f.allPV():
        steps.append([rbrtab,rbr,pos,truth])
        if f[0] in val:
            if val[f[0]]==truth:
                return (False,rbr)
            else:
                steps.append([rbrtab+1,rbr+1,pos,'x'+" ("+f[0]+"="+str(truth)+", "+f[0]+"="+str(val[f[0]])+")"])
                return (True,rbr+1)
        else:
            val[f[0]]=truth
            return (False,rbr)

