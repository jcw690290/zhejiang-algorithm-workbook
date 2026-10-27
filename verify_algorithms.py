"""Independent checks of the supplied answers and data for interactive traces."""
from pathlib import Path
import random, itertools, json
R=random.Random(20261026)
checks=[]; traces={}
def ok(name, condition):
    assert condition, name
    checks.append(name)
def trace(qid, columns, rows, caption='按题目数据执行；可逐步查看变量变化。'):
    traces[qid]={'columns':columns,'rows':[[str(x) for x in row] for row in rows],'caption':caption}

# 2023 January
for _ in range(100):
    a=R.sample(range(100),8); old=a[:]
    for i in range(1,7):
        for j in range(1,8-i-1):
            if a[j]>a[j-1]: a[j],a[j-1]=a[j-1],a[j]
    assert a[:6]==sorted(old[:6],reverse=True) and a[6:]==old[6:]
ok('202301-Q10：排序边界与降序，100组',True)
calls=[]
def rf(n):
    calls.append(n)
    return n if n<3 else rf(n-1)+rf(n-3)
rf(5); ok('202301-Q11：递归调用7次',len(calls)==7)
trace('202301-Q11',['调用序号','参数n','是否继续递归'],[(i+1,n,'否，直接返回' if n<3 else '是，分别调用n-1和n-3') for i,n in enumerate(calls)])
outcomes=set()
for ops in itertools.product([0,1],repeat=7):
    a=list('AB##CD#'); stk=[]
    for i,op in enumerate(ops):
        if op==1 and a[i]!='#': stk.append(a[i]); a[i]='#'
        elif op==0 and stk and a[i]=='#': a[i]=stk.pop()
    outcomes.add(''.join(a))
ok('202301-Q12：穷举128条操作路径',all(x in outcomes for x in ['AB##CD#','#######','#B##CDA']) and '##ABCD#' not in outcomes)
def merge(a,b):
    i=len(a)-1; j=len(b)-1; a.extend([[0,0,0] for _ in b]); k=len(a)-1; count=0
    while j>=0:
        count+=1
        if i>=0 and a[i][0]>b[j][0]: a[k]=a[i]; i-=1
        else: a[k]=b[j]; j-=1
        k-=1
    return a,count
a,c=merge([[0,3,2],[1,1,2],[12,2,2]],[[2,1,1],[4,3,0],[11,3,2]])
ok('202301-Q15：归并循环4次',c==4 and [x[0] for x in a]==[0,1,2,4,11,12])
def queue_proc(records,m):
    data=[x+[-1] for x in records]; n=len(data); qi=[[-1,-1] for _ in range(m)]
    cur=wait=i=total=0; rows=[]
    while i<n or wait>0:
        if i<n and data[i][0]<=cur:
            k=data[i][2]
            if qi[k][0]==-1: qi[k][0]=i
            else:
                p=qi[k][1]; data[p][3]=i
            qi[k][1]=i; wait+=1; i+=1
        elif wait>0:
            k=0
            while qi[k][0]==-1: k+=1
            p=qi[k][0]; start=cur; total+=cur-data[p][0]; cur+=data[p][1]
            rows.append([p,start,cur,start-data[p][0],k])
            qi[k][0]=data[p][3]; wait-=1
        else: cur=data[i][0]
    return total/n,rows
avg,rows=queue_proc(a,3)
ok('202301-Q15：B等待6秒',rows[3][0]==1 and rows[3][3]==6)
trace('202301-Q15',['器件下标','开始时刻','结束时刻','等待时长','优先级'],rows)
for _ in range(100):
    times=sorted(R.sample(range(80),R.randrange(1,20)))
    records=[[t,R.randrange(1,8),R.randrange(3)] for t in times]
    value,actual=queue_proc(records,3)
    remaining=list(range(len(records))); cur=total=0; expected=[]
    while remaining:
        ready=[i for i in remaining if records[i][0]<=cur]
        if not ready: cur=records[remaining[0]][0]; continue
        p=min(ready,key=lambda x:(records[x][2],records[x][0]))
        total+=cur-records[p][0]; expected.append(p); cur+=records[p][1]; remaining.remove(p)
    assert [r[0] for r in actual]==expected and value==total/len(records)
ok('202301-Q15：链式队列对照直接调度100组',True)

# 2023 June
pairs=[]
def f(a,s):
    pairs.append((a,s)); return a if a>=s else f(a+1,s-a)
ok('202306-Q10：返回8',f(6,21)==8)
trace('202306-Q10',['a','s','动作'],[(a,s,'返回'+str(a) if a>=s else '继续递归') for a,s in pairs])
q=list('print')+[None]*15; h,t=0,5; output=[]; rows=[]
while h<t:
    char=q[h]
    if h%3==0: output.append(char); action='输出'
    else: q[t]=char; t+=1; action='移到队尾'
    rows.append([h,char,action,t]); h+=1
ok('202306-Q11：最后输出r',''.join(output)=='pnitr')
trace('202306-Q11',['head','当前字符','动作','动作后tail'],rows)
def mode(a):
    c=m=1; v=0
    for i in range(1,len(a)):
        if a[i]==a[i-1]:
            c+=1
            if c>m: m=c; v=i
        else: c=1
    return a[v]
for _ in range(100):
    a=sorted(R.choices(range(8),k=R.randrange(1,20)))
    assert mode(a)==max(dict.fromkeys(a),key=a.count)
ok('202306-Q12：末段与并列模式100组',True)
task=[[2,-1],[1,4],[3,1],[5,-1],[1,-1],[6,0]]
days=8; c=[2,1,4,3,5,0]; w=[0]*6
for k in reversed(c): w[k]=days-task[k][0]+1 if task[k][1]==-1 else w[task[k][1]]-task[k][0]
ok('202306-Q15：最晚开始时间',w==[7,7,4,4,8,1])
trace('202306-Q15',['任务k','工期','后继','最晚开始w[k]'],[[k,task[k][0],task[k][1],w[k]] for k in reversed(c)])

# 2024 January
trace('202401-Q10',['i','j','m','a[m]','本轮动作','c'],[[0,6,3,36,'向右，i=4',1],[4,6,5,78,'命中退出',1]])
def pick(s):
    if not s: return {''}
    return {s[0]+r for r in pick(s[1:])}|{s[-1]+r for r in pick(s[:-1])}
res=pick('abcde')
ok('202401-Q11：穷举两端取字符','aecbd' not in res and all(s in res for s in ['abced','aedbc','edcba']))
def head_tail(values):
    d=[[v,i+1] for i,v in enumerate(values)]; d[-1][1]=-1; h=t=0; p=d[h][1]
    while p!=-1:
        q=d[p][1]
        if d[p][0]>0: d[t][1]=p; t=p
        else: d[p][1]=h; h=p
        p=q
    d[t][1]=-1; result=[]
    while h!=-1: result.append(d[h][0]); h=d[h][1]
    return result
for _ in range(100):
    values=sorted(R.sample(range(-100,101),15),key=abs)
    assert head_tail(values)==sorted(values)
ok('202401-Q12：头尾插100组',True)
def group(data,m):
    a=[[] for _ in range(len(data)+1)]; g=0
    for k,row in enumerate(data):
        while row[1]>=m:
            g+=1; a[row[0]].append(g); row[1]-=m
    data.sort(key=lambda x:-x[1]); b=[[] for _ in range(m)]
    for unit,num in data:
        if num==0: break
        j=num
        while j<m and not b[j]: j+=1
        if j<m: v=b[j].pop()
        else: g+=1; v=g
        a[unit].append(v); b[j-num].append(v)
    return a
ok('202401-Q15：修改样例分组',group([[1,25],[2,17],[3,54],[4,20],[5,38]],20)[1]==[1,8])

# 2024 June
def bcount(d,key):
    i,j=0,len(d)-1; n=0; ms=[]
    while i<=j:
        m=(i+j)//2; n+=1; ms.append(d[m])
        if key==d[m]: break
        elif key<d[m]: j=m-1
        else: i=m+1
    return n,ms
old=[6,12,15,18,22,25,28,35,46]; new=old+[58]
counts={bcount(new,key)[0] for key in range(-100,200) if bcount(old,key)[0]<=2}
ok('202406-Q10：穷举key含未命中情况',counts=={1,2,4})
trace('202406-Q10',['key','旧中点轨迹','新中点轨迹','新次数'],[[x,'→'.join(map(str,bcount(old,x)[1])),'→'.join(map(str,bcount(new,x)[1])),bcount(new,x)[0]] for x in [22,12,28]])
def peaks(a):
    for i in range(0,len(a)-1,2):
        if i>0 and a[i]<a[i-1]: a[i],a[i-1]=a[i-1],a[i]
        if a[i]<a[i+1]: a[i],a[i+1]=a[i+1],a[i]
    return a
ok('202406-Q11：D确实可达',peaks([6,3,9,2,9,8])==[6,3,9,2,9,8])
def relocate(order):
    n=len(order); d=[[v,-1] for v in range(n)]
    for p,q in zip(order,order[1:]): d[p][1]=q
    p=order[0]; i=0; steps=0
    while p!=-1:
        steps+=1; assert steps<1000
        tp=d[p][1]
        if p==i: i+=1
        elif p>i:
            d[i][0],d[p][0]=d[p][0],d[i][0]
            d[p][1]=d[i][1]; d[i][1]=p; i+=1
        p=tp
    return [x[0] for x in d]
for order in itertools.permutations(range(6)): assert relocate(order)==list(order)
ok('202406-Q12：6节点720种逻辑排列',True)
def compare(data,i,r):
    j=0
    while j<len(r) and i+j<len(data):
        if data[i+j]!=r[j]: break
        j+=1
    return j
def trans(data,r,segs):
    ns=[]
    for s in segs:
        if s[0]==0:
            h=i=s[1]; m=len(r)
            while i+m<=s[2]+1:
                if compare(data,i,r)==m:
                    if i>h: ns.append([0,h,i-1])
                    ns.append([m,i,i+m-1]); i+=m; h=i
                else: i+=1
            if h<=s[2]: ns.append([0,h,s[2]])
        else: ns.append(s)
    return ns
def transform(data,rs):
    data=data[:]; segs=[[0,0,len(data)-1]]
    for r in rs: segs=trans(data,r,segs)
    data.extend([0]*sum(s[0]>0 for s in segs)); p=len(data)-1
    for i in range(len(segs)-1,-1,-1):
        for j in range(segs[i][2],segs[i][1]-1,-1): data[p]=data[j]+segs[i][0]; p-=1
        if segs[i][0]>0: data[p]=127+segs[i][0]; p-=1
    return data,segs
value,segs=transform([3,5,1,6,3,8,7,5,1,8,7],[[5,1],[8,7]])
ok('202406-Q15：标记数及变换结果',sum(s[0]>0 for s in segs)==4 and value==[3,129,7,3,6,3,129,10,9,129,7,3,129,10,9])
trace('202406-Q15',['段状态/增加值','原起点','原终点'],segs,'第（1）问的分段描述；状态为2的每一段都会增加一个标记元素。')

# 2025 January
for _ in range(100):
    a=sorted(R.choices(range(10),k=10)); p=R.randrange(10); target=a[:]; target[p]+=1; target.sort()
    t=a[p]+1; i=p
    while i<len(a)-1 and t>a[i+1]: a[i]=a[i+1]; i+=1
    a[i]=t; assert a==target
ok('202501-Q10：有序插入100组',True)
def recursive_string(s,t): return s[t] if t>=len(s)-2 else recursive_string(s,t+2)+s[t]
for n in range(1,20):
    s='abcdefghijklmnopqrst'[:n]; r=''
    for i in range(0,n,2): r=s[i]+r
    assert r==recursive_string(s,0)
ok('202501-Q11：奇偶长度与单字符',True)
last=[]
for _ in range(30):
    c=[1,1,1,1,2,3,2,3,2,3]+[R.randint(1,10) for _ in range(80)]+[2,3,2,2,2,2,1,1,1,1]
    qa=[0]*5; qb=[0]*5; h,t=0,4; temp=0; rows=[]
    for k in range(100):
        qa[t]=c[k]; qb[t]=temp+qa[t]-qa[h]
        assert qb[t]==sum(c[max(0,k-3):k+1])
        rows.append([k,h,t,qb[h],qb[t]])
        last=[qb[h],qb[t]]; temp=qb[t]; t=(t+1)%5; h=(h+1)%5
    assert last==[8,4]
ok('202501-Q12：30组随机中段均输出8、4',True)
trace('202501-Q12',['k','h','t','qb[h]','qb[t]'],rows[-5:],'只展示最后5轮；演示中的随机中段取固定随机种子，最后结果与中段无关。')
def selection(data,n,s,w):
    r=[[0,0,201] for _ in range(n)]; heads=[-1,-1]; tails=[-1,-1]; cnt=0
    for i in range(len(data)):
        k=data[i][0]; r[k][1]+=1
        if data[i][2]<r[k][2]: r[k][2]=data[i][2]; r[k][0]=r[k][1]
        data[i][3]=r[k][0]; data[i].append(-1); v=1
        if data[i][3]<=w: data[i][4]=True; cnt+=1; v=0
        if heads[v]==-1: heads[v]=i
        else: data[tails[v]][5]=i
        tails[v]=i
    p,q=heads; result=[]
    while cnt<s and q!=-1:
        tmp=data[q][2]
        while q!=-1 and data[q][2]==tmp:
            while p!=-1 and p<q: result.append(data[p][1]); p=data[p][5]
            result.append(data[q][1]); data[q][4]=True; cnt+=1; q=data[q][5]
    while p!=-1: result.append(data[p][1]); p=data[p][5]
    return result
sample=[[k,sid,sc,0,False] for k,sid,sc in zip([0,2,2,0,0,2,2,0,1,1,1,1],['0002','2027','2002','0072','0182','2071','2128','0012','1081','1002','1008','1208'],[198,185,183,182,182,177,177,176,175,163,161,161])]
chosen=selection([x[:] for x in sample],3,5,1)
ok('202501-Q15：同分补选与原表顺序',chosen==['0002','2027','2002','0072','0182','1081'])
for _ in range(100):
    rows=sorted([[R.randrange(3),str(i),R.randrange(8),0,False] for i in range(20)],key=lambda x:-x[2]); s=R.randrange(1,22); w=R.randrange(1,4)
    selected={i for i,row in enumerate(rows) if 1+sum(x[0]==row[0] and x[2]>row[2] for x in rows)<=w}
    others=[i for i in range(len(rows)) if i not in selected]
    for score,g in itertools.groupby(others,key=lambda i:rows[i][2]):
        if len(selected)>=s: break
        selected.update(g)
    expected=[row[1] for i,row in enumerate(rows) if i in selected]
    assert selection([x[:] for x in rows],3,s,w)==expected
ok('202501-Q15：链表补选对照直接规则100组',True)

# 2025 June
s='abcdefghi'; n=2; i=n; r=''; rows=[]
while i<len(s):
    old=i; r+=s[i]; i+=1
    if i%5==0: i+=n
    rows.append([old,s[old],i,r])
ok('202506-Q10：cdehi',r=='cdehi')
trace('202506-Q10',['读取下标','字符','下一次下标','r'],rows)
data=[[11,3],[23,-1],[15,0],[26,1],[63,2]]; tag=[0]*5; p=i=0; rows=[]
while i<len(data):
    if tag[p]==0 and data[p][1]!=-1: tag[i]+=1; p=data[p][1]
    else: tag[i]+=tag[p]; rows.append([i,tag[i],tag[:]]); i+=1; p=i
ok('202506-Q11：距离为边数',tag==[2,0,3,1,4])
trace('202506-Q11',['已算完的起点i','tag[i]','当前tag'],rows)
def bsearch(data,key):
    i,j=0,len(data)-1
    while i<=j:
        m=(i+j)//2
        for k in range(m-1,m+2):
            if i<=k<=j and data[k]==key: return k
        if data[m]<key: i=m+2
        else: j=m-2
    return -1
options=[[16,19,18,22,20,29,25],[16,19,20,18,22,25,29],[18,16,19,20,22,29,25],[18,16,20,19,25,22,29]]
bad=[j for j,a in enumerate(options) if any(bsearch(a,key)!=a.index(key) for key in a)]
ok('202506-Q12：仅B存在查找失败',bad==[1] and bsearch(options[1],19)==-1)
def reserve(data,m):
    a=[]; result=[]
    for start,end in data:
        flag=True; p1=0
        while p1<len(a) and a[p1][0]<=start: p1+=1
        p2=p1-1 if p1>0 else 0
        while p2<len(a) and a[p2][0]<end:
            if a[p2][1]==m: flag=False; break
            p2+=1
        if flag:
            for j in range(p1,p2): a[j][1]+=1
            a.insert(p2,[end,0]); a.insert(p1,[start,1])
            if p1>0: a[p1][1]=a[p1-1][1]+1
            a[p2+1][1]=a[p2][1]-1
        result.append(flag)
    return result
for _ in range(200):
    requests=[]
    for _ in range(20):
        start=R.randrange(20); requests.append((start,R.randrange(start+1,25)))
    m=R.randrange(1,5); accepted=[]; expected=[]
    for start,end in requests:
        can=all(sum(x<=t<y for x,y in accepted)<m for t in range(start,end))
        expected.append(can)
        if can: accepted.append((start,end))
    assert reserve(requests,m)==expected
ok('202506-Q15：时间轴对照逐分钟容量200组，含同刻端点',True)

# 2026 January
s='keeper'; t=2; c=''; i=0; rows=[]
while i<len(s) and t>=0:
    if s[i]=='e': t-=1
    else: c+=s[i]
    rows.append([i,s[i],t,c]); i+=1
ok('202601-Q10：kp',c=='kp'); trace('202601-Q10',['i','字符','t','c'],rows)
a=[6,0,0,0,0,0]; ta=0; b=[2,7,2,1,5]; tb=4; total=0; rows=[]
while ta!=-1:
    while tb!=-1 and a[ta]>b[tb]:
        if (a[ta]+b[tb])%2==1: ta+=1; a[ta]=b[tb]
        tb-=1
    if tb!=-1: tb-=1
    value=a[ta]; total+=value; ta-=1
    rows.append([a[:ta+1],b[:tb+1],value,total])
ok('202601-Q11：栈和15',total==15)
trace('202601-Q11',['本轮结束a有效栈','b有效栈','本轮计入','累计s'],rows)
target=[2,4,3,5,6,9,7]; possible=set()
for perm in itertools.permutations(target):
    a=list(perm); i=1
    for j in range(1,len(a)):
        if a[j]<a[0]: a[i],a[j]=a[j],a[i]; i+=1
    a[0],a[i-1]=a[i-1],a[0]
    if a==target: possible.add(perm[0])
ok('202601-Q12：穷举7!初始排列',possible=={2,5,6})
def window(reqs,m):
    i=j=s=loops=0; rows=[]
    while j<len(reqs):
        loops+=1
        if reqs[j][0]-reqs[i][0]<60:
            s+=reqs[j][1]; rows.append([i,j,'加入',s])
            if s>m: return True,loops,rows
            j+=1
        else: s-=reqs[i][1]; rows.append([i,j,'移除左端',s]); i+=1
    return False,loops,rows
res,_,rows=window([[6,1],[19,13],[35,3],[70,2],[75,7]],20)
ok('202601-Q15：True与最大199次',res and window([[60*i,1] for i in range(100)],2)[1]==199)
trace('202601-Q15',['i','j','动作','窗口和s'],rows)
def transport(reqs,items):
    available=set(); idx=0; result=[]
    for qi,(cur,need) in enumerate(reqs):
        while idx<len(items) and items[idx][0]<cur: available.add(items[idx][1]); idx+=1
        runs=[]
        for _,g in itertools.groupby(enumerate(sorted(available)),key=lambda x:x[1]-x[0]):
            vals=[x[1] for x in g]
            if len(vals)>=need: runs.append(vals)
        if runs:
            chosen=min(runs,key=lambda x:(len(x),x[0])); result.append([qi,chosen[0],chosen[0]+need-1]); available.difference_update(chosen[:need])
    return result
items=list(zip([495,500,510,535,540,545,550,565],[202,206,203,201,208,207,204,205]))
ok('202601-Q15：转运起号206',transport([[555,3]],items)==[[0,206,208]])

# 2026 June
s='172D6AF'; i=len(s)-1; c='*'; rows=[]
while i>=0 and c=='*':
    char=s[i]
    if '0'<=char<='9': c=char
    else: i-=1
    rows.append([char,i,c])
ok('202606-Q10：6',c=='6'); trace('202606-Q10',['本轮字符','动作后i','c'],rows)
def arena(a):
    m=r=0
    for i in range(len(a)):
        if a[i]<a[m]: r=i
        else: m=i
    return r
first=[10,9,8,7,6,5,4,11,12,13]; second=[10,3,9,8,7,4,6,11,12,13]
assert arena(first)==arena(second)==6
for _ in range(5000):
    a=R.sample(range(100),10)
    if arena(a)==6: assert a[6]<a[7]
ok('202606-Q11：必要关系随机核对及两个反例',not first[0]<first[6] and not second[6]<second[5])
values=[-12,6,-7,9,8,-6]; d=[[v,i+1] for i,v in enumerate(values)]; d[-1][1]=-1
head=0; p=head; q=-1; rows=[]
while p!=-1:
    if d[p][0]<0:
        if q==-1: head=d[p][1]; act='删除头节点'
        else: d[q][1]=d[p][1]; act='前驱跳过当前节点'
    else: q=p; act='保留，更新前驱'
    rows.append([p,d[p][0],act,head,q]); p=d[p][1]
got=[]; p=head
while p!=-1: got.append(d[p][0]); p=d[p][1]
ok('202606-Q12：删除负值',got==[6,9,8])
trace('202606-Q12',['p','数据','动作','head','q'],rows)
def move(lst,idx):
    if 0<=idx<len(lst)-1:
        q=lst[idx]; k=idx
        while k<len(lst)-1 and lst[k+1][1]>=q[1]: lst[k]=lst[k+1]; k+=1
        lst[k]=q
lst=[[0,5],[1,6],[4,8],[2,7],[3,4]]; move(lst,1)
ok('202606-Q15：move指定位置',lst[2][0]==2)
for _ in range(100):
    a=[[i,R.randrange(20)] for i in range(12)]; expected=sorted(x[1] for x in a)[::-1]
    for i in range(len(a)-1): move(a,len(a)-i-2)
    assert [x[1] for x in a]==expected
ok('202606-Q15：修正fsort下标100组',True)
def recruit(reqs,cands):
    rsum=sorted([[i,sum(v)] for i,v in enumerate(reqs)],key=lambda x:-x[1]); sel=[-1]*len(cands); rows=[]
    while rsum:
        num=rsum[0][0]; maxcnt=0; bestc=-1
        for i in range(len(cands)):
            if sel[i]==-1:
                cnt=0
                for j in cands[i]:
                    if reqs[num][j]!=0: cnt+=1
                if cnt>maxcnt: maxcnt=cnt; bestc=i
        if bestc==-1: rsum.pop(0)
        else:
            sel[bestc]=num
            for i in cands[bestc]:
                if reqs[num][i]!=0: reqs[num][i]-=1
            rsum[0][1]-=maxcnt; rows.append([num,bestc,maxcnt,reqs[num][:],rsum[0][1]])
            if rsum[0][1]==0: rsum.pop(0)
            else: move(rsum,0)
    return sel,rows
sel,rows=recruit([[2,1,3],[0,3,1]],[[0,1],[1],[0,1,2],[1,2],[0,2],[2]])
ok('202606-Q15：第二次录用3号候选人',rows[0][1]==2 and rows[1][0:2]==[1,3])
trace('202606-Q15',['工作组','录用候选人','满足技能项数','该组更新后需求','更新后总需求'],rows)

root=Path(__file__).resolve().parent
(root/'traces.json').write_text(json.dumps(traces,ensure_ascii=False),encoding='utf-8')
(root/'verification.json').write_text(json.dumps({'checks':checks,'count':len(checks),'traceCount':len(traces),'result':'PASS'},ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'result':'PASS','checks':len(checks),'traceCount':len(traces)},ensure_ascii=False))
