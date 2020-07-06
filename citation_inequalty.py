#coding:utf-8
'''
分析马太效应、不平等随时间的变化
'''

from basic_config import *

from gini import gini


def stat_subj_paper_year_citnum():

    pid_topsubj = json.loads(open('../cascade_temporal_analysis/data/_ids_top_subjects.json').read())
    paper_year = json.loads(open('../cascade_temporal_analysis/data/pubyear_ALL.json').read())

    subj_paper_year_citnum = defaultdict(lambda:defaultdict(lambda:defaultdict(int)))
    progress=0
    for line in open('../cascade_temporal_analysis/data/pid_cits_ALL.txt'):
        progress+=1

        if progress%10000000==0:
            logging.info('reading %d citation relations....' % progress)

        line = line.strip()

        pid,citing_id = line.split("\t")

        if paper_year.get(pid,None) is None or paper_year.get(pid,None) is None or pid_topsubj.get(pid,[])==[] or pid_topsubj.get(citing_id,[])==[]:
            continue

        pubyear = paper_year[pid]
        citing_year = paper_year[citing_id]

        subjs = pid_topsubj[pid]

        citing_subjs = pid_topsubj[citing_id]

        ##计算的是领域内的引用
        sameset =  list(set(subjs) & set(citing_subjs))

        if len(sameset)==0:
            continue

        for subj in sameset:
            subj_paper_year_citnum[subj][pid][citing_year]+=1

    open('data/topsubj_paper_year_citnum.json','w').write(json.dumps(subj_paper_year_citnum))
    logging.info('data saved to data/topsubj_paper_year_citnum.json.')


def top20_percent_trend_over_time():

    subj_paper_year_citnum = json.loads(open('data/topsubj_paper_year_citnum.json').read())

    subj_type_xys = defaultdict(dict)

    for subj in subj_paper_year_citnum.keys():

        year_citnum_dis = defaultdict(lambda:defaultdict(int))
        for pid in subj_paper_year_citnum[subj].keys():

            year_citnum = subj_paper_year_citnum[subj][pid]

            year_total = paper_year_total_citnum(year_citnum)

            for year in year_total.keys():

                year_citnum_dis[year][year_total[year]]+=1

        ## 每年的引用次数分布
        xs = []
        top20_percents = []

        divs = []
        for year in sorted(year_citnum_dis.keys(),key=lambda x:int(x)):

            citnum_dis = year_citnum_dis[year]

            tp = top_percent(citnum_dis,0.2)

            xs.append(year)
            top20_percents.append(tp)

            percentiel_precents,diversity = diversity_of_equal_percentile(citnum_dis,10)

            divs.append(diversity)


        subj_type_xys[subj]['top20'] = [xs,top20_percents]
        subj_type_xys[subj]['div'] = [xs,divs]


    open('data/subj_type_xys.json','w').write(json.dumps(subj_type_xys))

    logging.info('data saved to data/subj_type_xys.json.')


def plot_diversity_figs():


    subj_type_xys = json.loads(open('subj_type_xys.json').read())

    fig,axes = plt.subplots(1,2,figsize=(10,5))

    ax = axes[0]
    for i,subj in enumerate(subj_type_xys.keys()):

        xs,top20_percents = subj_type_xys[subj]['top20']

        ax.plot(xs,top20_percents,label='{}'.format(subj))


    ax.set_title('top 20% citation percentage')

    ax.set_xlabel('year')

    ax.set_ylabel('percentage')

    lgd1 = ax.legend(loc=6,bbox_to_anchor=(0.5, -0.2), ncol=2)


    ax = axes[1]
    for i,subj in enumerate(subj_type_xys.keys()):

        xs,top20_percents = subj_type_xys[subj]['div']

        ax.plot(xs,top20_percents,label='{}'.format(subj))


    ax.set_title('diversity')

    ax.set_xlabel('year')

    ax.set_ylabel('diversity')

    lgd2 = ax.legend(loc=6,bbox_to_anchor=(0.5, -0.2), ncol=2)


    plt.tight_layout(,additional_artists=[lgd],bbox_inches="tight")

    plt.savefig('me.png',dpi=200)


            
def paper_year_total_citnum(year_citnum):

    years = [int(year) for year in year_citnum.keys()]

    minY = np.min(years)
    maxY = np.max(years)

    mY = maxY
    if maxY+1<2018:
        mY=2018


    year_total = {}
    total = 0
    for y in range(minY,mY):
        total+= year_citnum.get(str(y),0)
        year_total[int(y)]=total
    return year_total




## 引用最高的Npercent的论文所占总引用次数的比例
def top_percent(citnum_dis,percent):

    cits = []

    for key in citnum_dis.keys():

        num = citnum_dis[key]

        cits.extend([int(key)]*num)

    total = np.sum(cits)

    N = int(len(cits)*percent)

    topN = sorted(cits,key=lambda x:int(x),reverse=True)[:N]

    sum_of_topN = np.sum(topN)

    return float(sum_of_topN)/total


## 占相同比例的引用次数的从高到低的论文文章分布
def diversity_of_equal_percentile(citnum_dis,N):

    cits = []

    for key in citnum_dis.keys():

        num = citnum_dis[key]

        cits.extend([int(key)]*num)

    total = np.sum(cits)

    num = len(cits)

    acc_total = 0
    c_p = 0
    num_of_p = 0

    percents = []
    for v in sorted(cits,key=lambda x:int(x),reverse=True):

        acc_total+=v
        num_of_p+=1
        ##
        if acc_total/float(total)-c_p>=1/float(N):

            c_p+=1/float(N)

            percents.append(num_of_p/float(num))

            num_of_p = 0

    ##得到不同社区的文章比例，后计算不同percentile的论文的diversity

    diversity = gini(percents)
    print(percents)
    print(diversity)

    return percents,diversity


if __name__ == '__main__':
    # stat_subj_paper_year_citnum()

    # top20_percent_trend_over_time()


    plot_diversity_figs()











