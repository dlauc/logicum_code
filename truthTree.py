__author__ = 'D'
# -*- coding: utf-8 -*-

import wff
from nltk import Tree
from utils import tree2str,toTeXs

## TO DO - prevesti komentare, pripremiti u novom formatu
# zatvara grane (x) i vraća pozicije otvorenih
def treePathsPV(t):
    rec = []
    bran = t.treepositions('leaves')
    for pr in bran:
        if t[pr]=='o':
            lst=[t[pr[0:i]].node[0] for i in range(len(pr)) if len(t[pr[0:i]].node[0])<=2]
            k = [1 for a in lst if ('n'+a if len(a)==1 else a[0]) in lst]
            if len(k)>0:
                t[pr]='x'
            else: rec.append(pr)
    return rec

# nalazi formulu za obraditi,
def treeFindNBF(t):
    # prvo sve negranajuće formule
    for pr in t.treepositions():
        if isinstance(t[pr],Tree) and t[pr].node[1]==False:
            f = wff.parser.parse(t[pr].node[0])
            if   f[0]=='n' and f[1][0]=='n': return pr
            elif f[0]=='(' and f[2]=='k': return pr
            elif f[0]=='n' and f[1][0]=='(' and f[1][2] in ['d','i']: return pr
    # inače prvu
    for pr in t.treepositions():
        if isinstance(t[pr],Tree) and t[pr].node[1]==False: return pr
    return None

# pretvara string list u tree
def Strl2Tree(fs):
    if len(fs)>0:
        ttree=Tree([fs[0],False if len(fs[0])>2 else True],['o'])
        for f in fs[1:]:
            ttree[ttree.treepositions('leaves')] = Tree([f,False if len(f)>2 else True],['o'])
    else: ttree=None
    return ttree

# fs - popis psf-a, već negirana konkluzija
def truthTreeDo(fs):
    # 'o' otvoren 'x', zatvoren
    # dodavanje inicijalnih formula
    ttree = Strl2Tree(fs)

    completed = False
    while not completed:
        # zatvori kontradiktorne grane i vrati otvorene
        c = treePathsPV(ttree)
        if len(c)==0: break
        # uzmi formulu za obradu
        fp = treeFindNBF(ttree)
        if fp==None: break
        # primjeni pravila na odabranu formulu
        fs = ttree[fp].node[0]
        ft = wff.parser.parse(fs)
        ttree[fp].node[1] = True # formula obrađena
        nfs = []; nfs2 = [] # popisi formula (stringova) koje se dodaju na kraju svake otvorene grane
        #nn A -> A
        if fs[0:2]=='nn': nfs.append(fs[2:])
        elif ft[0]=='(' and ft[2]=='k':
            nfs.append(tree2str(ft[1]))
            nfs.append(tree2str(ft[3]))
        elif ft[0]=='(' and ft[2]=='d':
            nfs.append(tree2str(ft[1]))
            nfs2.append(tree2str(ft[3]))
        elif ft[0]=='(' and ft[2]=='i':
            nfs.append('n'+tree2str(ft[1]))
            nfs2.append(tree2str(ft[3]))
        elif fs[0:2]=='n(' and ft[1][2]=='k':
            nfs.append('n'+tree2str(ft[1][1]))
            nfs2.append('n'+tree2str(ft[1][3]))
        elif fs[0:2]=='n(' and ft[1][2]=='d':
            nfs.append('n'+tree2str(ft[1][1]))
            nfs.append('n'+tree2str(ft[1][3]))
        elif fs[0:2]=='n(' and ft[1][2]=='i':
            nfs.append(tree2str(ft[1][1]))
            nfs.append('n'+tree2str(ft[1][3]))

        if len(nfs)==0: raise Exception("Error handling formula: "+fs)
        ntree = Strl2Tree(nfs)
        if len(nfs2)>0: ntree2 = Strl2Tree(nfs2)

        for path in c:
            if path[0:len(fp)]==fp: # reduciraj c na one ispod odabrane formule
                ttree[path]=ntree.copy(True)
                if len(nfs2): ttree[path[0:-1]].append(ntree2.copy(True))
    return (len(c)==0,ttree)

def TruthTree2Tex(tl):
    for pr in tl.treepositions():
        if isinstance(tl[pr],Tree) and len(tl[pr].node)==2:
            tl[pr].node = '$'+toTeXs(tl[pr].node[0])+('\checkmark ' if len(tl[pr].node[0])>2 else'')+ '$'
        elif not isinstance(tl[pr],Tree) :
            tl[pr] = '$'+toTeXs(tl[pr])+'$'
    return tl.pprint_latex_qtree()


def testTruthTreeDo(fs):
    r=truthTreeDo(['n'+fs])
    if r[0]: print("yes")
    else: print("no")
#    r[1].draw()
    print(TruthTree2Tex(r[1]))


if __name__ == "__main__":
    # tests
    r=truthTreeDo(['(piq)','nq','nnp'])
    if r[0]: print("yes")
    else: print("no")
#    r[1].draw()
    print(TruthTree2Tex(r[1]))
