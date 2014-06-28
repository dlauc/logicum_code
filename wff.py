# -*- coding: utf-8 -*-
__author__ = 'dl'

from nltk import Tree,parse_cfg,ShiftReduceParser
from utils import toTeX,subtree_len,tree2str,all_subsets,toHTML
from reductio import reductio_do

""" gramatika psf-a, izvan klase zbog brzine """
wff2 = parse_cfg("""
    WFF   -> 'p'
    WFF   -> 'q'
    WFF   -> 'r'
    WFF   -> 's'
    WFF  -> 'n' WFF
    WFF  -> '(' WFF 'i' WFF ')'
    WFF  -> '(' WFF 'k' WFF ')'
    WFF  -> '(' WFF 'd' WFF ')'
    WFF  -> '(' WFF 'e' WFF ')'
    """)

parser = ShiftReduceParser(wff2)
allPropsVar = [prod.rhs()[0] for prod in wff2.productions(wff2.start()) if len(prod.rhs())==1] # all prop. vars in grammar


class Wff(Tree):
    """ Wff represents well formed formula of prop. calculus in NLTK Tree structure
    """
    #
    def __init__(self,node_or_str, children=None,wffs=False):
        if wffs:
            t = parser.parse(node_or_str)
            for tr in t.subtrees():
                if tr.__class__== Tree:
                    tr.__class__ = Wff;

            super(Wff, self).__init__(t.node, t[0:len(t)])
        else:
            super(Wff, self).__init__(node_or_str, children)

    # wff string representation
    def __str__(self):
        f1= self.leaves()
        f2=[]
        for i in f1:
            if isinstance(i,list):
                f2.append(i[0])
            else:
                f2.append(i)
        return ''.join(f2)

    # return set of all propositional variables
    def allPV(self):
        allpv=set([])
        for a in self.leaves():
            if a in allPropsVar:  # to do - uopćiti na bilo koju gramatiku
                allpv.add(a)
        return allpv

    def subFormulas(self):
        rec=[]
        for a in self.subtrees():
            rec.append(tree2str(a))
        rec.remove(self.__str__())
        return list(set(rec))

    # wff as syntactic parsed tree as LaTeX
    def treeTeX(self,tl=None):
        jos=True
        if tl==None:
            tl=self.copy(True)
        while jos==True:
            jos=False
            for pr in tl.treepositions():
                if isinstance(tl[pr],Tree) and len(tl[pr])==1 and tl[pr].node=='WFF':
                   tl[pr] = toTeX(tl[pr][0])
                   jos=True
                   break
                if isinstance(tl[pr],Tree) and len(tl[pr]) ==5 and 'WFF' not in [(a.node if isinstance(a,Tree) else a) for a in tl[pr]]:
                   #tl[pr].node = ''.join([a for a in tl[pr]])
                   nod=''.join([(a.node if isinstance(a,Tree) else toTeX(a)) for a in tl[pr]])
                   if pr==(): tl=Tree(nod,[tl[pr][1],tl[pr][3]])
                   else: tl[pr]=Tree(nod,[tl[pr][1],tl[pr][3]])
                   jos=True
                   break
                if isinstance(tl[pr],Tree) and len(tl[pr])==2 and tl[pr][0]=='n' and (not isinstance(tl[pr][1],Tree) or tl[pr][1].node!='WFF'):
                   #tl[pr].node = ''.join([a for a in tl[pr]])
                   if pr==(): tl=Tree(toTeX('n')+tl[pr][1].node if isinstance(tl[pr][1],Tree) else toTeX('n')+tl[pr][1],[tl[pr][1]])
                   else: tl[pr]=Tree(toTeX('n')+tl[pr][1].node if isinstance(tl[pr][1],Tree) else toTeX('n')+tl[pr][1],[tl[pr][1]])
                   jos=True
                   break
        for pr in tl.treepositions():
            if isinstance(tl[pr],Tree): tl[pr].node='$'+tl[pr].node+'$'
            else: tl[pr]='$'+tl[pr]+'$'
        return tl.pprint_latex_qtree()

    # evoluation of formula in a model
    def evaluate(self,model):
        def e2(f):
            if f[0]=='(':
                if f[2]=='i':
                    return not e2(f[1]) or e2(f[3])
                elif f[2]=='k':
                    return e2(f[1]) and e2(f[3])
                elif f[2]=='d':
                    return e2(f[1]) or e2(f[3])
                elif f[2]=='e':
                    return (e2(f[1]) and e2(f[3])) or (not e2(f[1]) and not e2(f[3]))
            elif f[0]=='n':
                return not e2(f[1])
            elif f[0] in allPropsVar:
                return f[0] in model
            else:
                raise Exception("unknown pv: "+f.__str__()+': '+f[0])
        return e2(self)

    def truthTableLine(self,model):
        def e2(f,pos):
            if f[0]=='(':
                pos2 = pos+1+subtree_len(f[1])
                # !!! sve logičke izraze razbiti zbog lazy evaluacije
                if f[2]=='i':
                    v1 = not e2(f[1],pos+1)
                    v2 = e2(f[3],pos2+1)
                    v= v1 or v2
                elif f[2]=='k':
                    v1 = e2(f[1],pos+1)
                    v2 = e2(f[3],pos2+1)
                    v=v1 and v2
                elif f[2]=='d':
                    v1= e2(f[1],pos+1)
                    v2=e2(f[3],pos2+1)
                    v=v1 or v2
                elif f[2]=='e':
                    v1a= e2(f[1],pos+1)
                    v1b= e2(f[3],pos2+1)
                    v1=v1a and v1b
                    v2a= not e2(f[1],pos+1)
                    v2b= not e2(f[3],pos2+1)
                    v2=v2a and v2b
                    v=v1 or v2
                rec[pos2] = v
                return v
            elif f[0]=='n':
                v= not e2(f[1],pos+1)
                rec[pos]=v
                return v
            elif f[0] in allPropsVar:
                v= f[0] in model
                rec[pos]=v
                return v
            else:
                raise Exception("unknown pv: "+f[0]+";"+f[2])

        rec = [None] * len(self.__str__())
        e2(self,0)
        return rec

    def tableOrder(self,intr):
        return ''.join(['a' if a in intr else 'b' for a in ['p','q','r','s']])

    def truthTableTeX(self,boldMain=True):
        f = self.__str__()
        zag = '\\begin{tabular}{'+('c'*len(f))+'} \n'+''.join(['$'+toTeX(a)+'$ & ' for a in list(f)])
        zag = zag[:-3]+'\\\\ \n\r'

        t = self
        allpv = sorted(self.allPV())
        if len(t)>0 and t[0]=='(':
            mainPos = 1+len(tree2str(t[1]))
        else: mainPos=0

        allS = [a for a in all_subsets(allpv)]
        allS = sorted(allS,key=self.tableOrder)
        for subset in allS:
            tr = self.truthTableLine(subset)
            s= ['$'+toTeX('T',idx==mainPos)+'$ & ' if f==True else '$'+toTeX('F',idx==mainPos)+'$ & ' if f==False else ' & ' for idx, f in enumerate(tr)]
            zag= zag+''.join(s)[:-3]+'\\\\ \n\r'
        zag += '\n\r\\end{tabular}'
        return zag

    # classify formula: 't' - tautology, 'k' - contradiction, 'o' - other
    def classify(self):
        taut = True
        cont = True
        allpv = self.allPV()
        for subset in all_subsets(allpv):
            a = self.evaluate(subset)
            if a==True: cont=False
            if a==False: taut=False
            if not cont and not taut: break
        if taut: return 'T'
        elif cont: return 'K'
        else: return 'O'

    def reductio(self):
        steps = []
        rec = reductio_do(1,self,False,{},steps,0,1)
        return rec[0], steps

    def reductio2TeX(self,rec,stepbystep=True):
        f = self.__str__()
        zag1 = '\\begin{tabular}{'+'l'+('c'*len(f))+'} \n'+''.join(['$'+toTeX(a)+'$ & ' for a in list(f)])
        zag1 = zag1[:-3]+'\\\\ \n\r'
        ra = rec[1]
        rbrs = list(set([c[0] for c in ra]))

        # matrica
        m=[]
        for j in range(len(rbrs)):
            l = []
            for k in range(len(f)): l.append('')
            m.append(l)
        for i in ra:
            m[rbrs.index(i[0])][i[2]-1] = ('$'+toTeX('T')+'$' if i[3]==True else '$'+toTeX('F')+'$' if i[3]==False else 'x')

        i=1
        zag=zag1
        for j in m:
            zag=zag+'('+str(i)+')'
            for k in j:
                zag = zag + '&'+k
            i+=1
            zag= zag+'\\\\ \n'
        zag += '\n\\end{tabular}'

        # sve u istom redu
        m=[]
        for j in range(0,2):
            l = []
            for k in range(len(f)): l.append('')
            m.append(l)
        for i in ra:
            if i[3] in (True,False):
                m[0][i[2]-1]= '$'+toTeX('T')+'$' if i[3]==True else '$'+toTeX('F')+'$'
            else:
                m[1][i[2]-1]='x'
        i=1
        zag2=zag1
        for j in m:
            zag2=zag2+'('+str(i)+')'
            for k in j:
                zag2 = zag2 + '&'+k
            i+=1
            zag2= zag2+'\\\\ \n'
        zag2 += '\n\\end{tabular}'

        return zag+'\n\r'+zag2

    def reductio2HTML(self,rec,stepbystep=True):
        f = self.__str__()
        zag1 = '<table><th>'+''.join(['<td>\('+toHTML(a)+'\)</td>' for a in list(f)])+'</th>\n\r'
        ra = rec[1]
        rbrs = list(set([c[0] for c in ra]))

        return zag1
        # matrica
        m=[]
        for j in range(len(rbrs)):
            l = []
            for k in range(len(f)): l.append('')
            m.append(l)
        for i in ra:
            m[rbrs.index(i[0])][i[2]-1] = '<td>'+('\('+toHTML('T')+'\)' if i[3]==True else '\('+toHTML('F')+'\)' if i[3]==False else 'x')+'</td>'

        i=1
        zag=zag1
        for j in m:
            zag=zag+'('+str(i)+')'
            for k in j:
                zag = zag + '<td>'+k+'</td>'
            i+=1
            zag= '<tr>'+zag+'</tr> \n'
        zag += '\n</table>'

        # sve u istom redu
        m=[]
        for j in range(0,2):
            l = []
            for k in range(len(f)): l.append('')
            m.append(l)
        for i in ra:
            if i[3] in (True,False):
                m[0][i[2]-1]= '\('+toHTML('T')+'\)' if i[3]==True else '\('+toHTML('F')+'\)'
            else:
                m[1][i[2]-1]='x'
        i=1
        zag2=zag1
        for j in m:
            zag2=zag2+'('+str(i)+')'
            for k in j:
                zag2 = zag2 + '<td>'+k+'</td>'
            i+=1
            zag2= '<tr>'+zag2+'</tr> \n'
        zag2 += '\n</table>'

        return zag+'\n\r'+zag2

if __name__ == "__main__":
    # tests
    wff1 = Wff('((piq)i(nqinp))',wffs=True)
    rec = wff1.reductio()
    print(wff1.reductio2HTML(rec))
    exit()
    print(wff1)
    print('Synthatic tree',wff1.treeTeX())
    print('evaluate',wff1.evaluate('p'))
    print('truth table',wff1.truthTableTeX())
    print('semantic class',wff1.classify())
    rec = wff1.reductio()
    print('reductio',rec)
    print('reductio',wff1.reductio2TeX(rec))