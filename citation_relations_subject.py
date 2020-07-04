#coding:utf-8
'''
根据不同给的subject标签对wos的论文进行分领域处理

'''

from basic_config import *
from gini import gini


'''

选择6个top领域，然后在6个top领域内分别选择一个子领域作为实验数据。

'''
def get_paperids_of_subjects(subjName):

    pass

##统计wos所有论文的citation count随着时间的变化情况
def stats_citation_count_of_papers():

    logging.info('loading paper year obj ...')
    paper_year = json.loads(open('../cascade_temporal_analysis/data/pubyear_ALL.json').read())

    logging.info('start to stat citation relations ...')

    pid_year_citnum = defaultdict(lambda:defaultdict(int))

    progress = 0

    lines = []
    for line in open('../cascade_temporal_analysis/data/pid_cits_ALL.txt'):

        progress+=1

        if progress%10000000==0:
            logging.info('reading %d citation relations....' % progress)

        line = line.strip()

        pid,citing_id = line.split("\t")

        if paper_year.get(pid,None) is None or paper_year.get(citing_id,None) is None:
            continue

        pid_year_citnum[pid][int(paper_year[citing_id])]+=1

    open('data/pid_year_citnum.json','w').write(json.dumps(pid_year_citnum))
    logging.info('pid year citnum saved to data/pid_year_citnum.json.')

##整体领域高被引论文的平均数随着数据规模的变化情况
def general_top_citation_trend_over_datasize():
        ## 加载top subject
        pid_topsubj = json.loads(open('../cascade_temporal_analysis/data/_ids_top_subjects.json').read())

        pid_subjs = json.loads(open('../cascade_temporal_analysis/data/_ids_subjects.json').read())

        ## paper year
        paper_year = json.loads(open('../cascade_temporal_analysis/data/pubyear_ALL.json').read())

        paper_ts = json.loads(open('data/pid_teamsize.json').read())

        sub_foses = set(['computer science','physics'])

        ## 按照学科进行分析
        pid_year_citnum = json.loads(open('data/pid_year_citnum.json').read())

        ## 各个学科各年份的分布
        ## subj year num count 各学科每年的引用次数分布
        subj_year_citnum_dis = defaultdict(lambda:defaultdict(lambda:defaultdict(int)))
        ## 根据发布年份的引用次数分布
        subj_puby_year_citnum_dis = defaultdict(lambda:defaultdict(lambda:defaultdict(lambda:defaultdict(int))))
        ##各学科每年的论文数量
        subj_year_num = defaultdict(lambda:defaultdict(int))

        ## 各学科中 不同 teamsize随着时间的变化
        subj_ts_year_citnum_dis = defaultdict(lambda:defaultdict(lambda:defaultdict(lambda:defaultdict(int))))


        for pid in pid_year_citnum.keys():

            pubyear = int(paper_year[pid])

            if pubyear>= 2011:
                 continue

            topsubjs = pid_topsubj.get(pid,None)

            if topsubjs is None:
                continue

            subjs = pid_subjs[pid]

            ts = paper_ts.get(pid,1)

            for subj in topsubjs:
                subj_year_num[subj][pubyear]+=1

            for subj in subjs:
                if subj.lower() in sub_foses:
                    subj_year_num[subj][pubyear]+=1

            year_total =  paper_year_total_citnum(pid_year_citnum[pid])

            for year in range(pubyear,2011):

                for subj in topsubjs:

                    citN = year_total.get(year,0)

                    if citN==0:
                        continue

                    subj_year_citnum_dis[subj][year][citN]+=1
                    subj_puby_year_citnum_dis[subj][pubyear][year][citN]+=1
                    subj_ts_year_citnum_dis[subj][ts][year][citN]+=1

                for subj in subjs:
                    if subj.lower() in sub_foses:

                        citN = year_total.get(year,0)

                        if citN==0:
                            continue

                        subj_year_citnum_dis[subj][year][citN]+=1
                        subj_puby_year_citnum_dis[subj][pubyear][year][citN]+=1
                        subj_ts_year_citnum_dis[subj][ts][year][citN]+=1

        open('data/subj_year_num.json','w').write(json.dumps(subj_year_num))
        logging.info('subject year paper num data saved to data/subj_year_num.json')

        open('data/subj_year_citnum_dis.json','w').write(json.dumps(subj_year_citnum_dis))
        logging.info('subject year paper citnum dis data saved to data/subj_year_citnum_dis.json')

        open('data/subj_puby_year_citnum_dis.json','w').write(json.dumps(subj_puby_year_citnum_dis))
        logging.info('subject pubyear year paper citnum dis data saved to data/subj_puby_year_citnum_dis.json')


        open('data/subj_ts_year_citnum_dis.json','w').write(json.dumps(subj_ts_year_citnum_dis))
        logging.info('subject teamsize year paper citnum dis data saved to data/subj_ts_year_citnum_dis.json')

        logging.info('done')

##不同的年代发表的高被引论文的引用次数平均数随着数据规模的变化情况
def temporal_top_citation_trend_over_datasize():
    paper_num_dis_over_pubyear()
    subj_upper_limit_over_year()

## 不同学科 不同年份的引用次数分布
def subj_upper_limit_over_year():

    logging.info('loading subj year citnum dis ...')
    subj_year_citnum_dis = json.loads(open('data/subj_year_citnum_dis.json').read())

    subj_year_num = json.loads(open('data/subj_year_num.json').read())

    fig,axes = plt.subplots(4,2,figsize=(10,16))

    for i,subj in enumerate(sorted(subj_year_citnum_dis.keys())):

        year_num = subj_year_num[subj]

        ax = axes[i/2,i%2]

        year_citnum_dis = subj_year_citnum_dis[subj]

        xs = []
        ys_10 = []
        ys_100 = []
        ys_1000 = []

        num_t = 0
        for year in sorted(year_citnum_dis.keys(),key=lambda x:int(x)):
            # xs.append(int(year))
            num_t+=year_num[year]
            xs.append(num_t)

            citnum_dis = year_citnum_dis[year]

            top10 = topN_mean(citnum_dis,10)

            top100 = topN_mean(citnum_dis,100)

            top1000 = topN_mean(citnum_dis,1000)

            ys_10.append(top10)
            ys_100.append(top100)
            ys_1000.append(top1000)

        curve_fit_plotting(ax,xs,ys_10,'top10')
        curve_fit_plotting(ax,xs,ys_100,'top100')
        curve_fit_plotting(ax,xs,ys_1000,'top100')

        ax.set_title(subj)

        ax.set_xlabel('dataset size')

        ax.set_ylabel('citation upper limit')

        ax.set_xscale('log')

        ax.legend()


    plt.tight_layout()

    plt.savefig('fig/subj_citation_upper_limit.png',dpi=400)

    logging.info('fig saved to fig/subj_citation_upper_limit.png.')



def curve_fit_plotting(ax,xs,ys,label):

    line = ax.plot(xs,ys,label=label)

    c= line[0].get_color()


    def logFunc(x,a,b):
        return a*np.log(x)+b

    popt, pcov = curve_fit(logFunc, xs, ys)

    a = popt[0]
    b = popt[1]

    ax.plot(xs,[logFunc(x,a,b) for x in xs],'-.',c=c)




## 引用次数最高的N篇论文的平均引用次数
def topN_mean(citnum_dis,N):

    values = citnum_dis.values()

    total = np.sum(values)

    topN = sorted(values,key=lambda x:int(x),reverse=True)[:N]

    mean_of_topNn = np.mean(topN)

    return mean_of_topNn


## 引用最高的Npercent的论文所占总引用次数的比例
def top_percent(citnum_dis,percent):

    values = citnum_dis.values()

    total = np.sum(values)

    N = int(len(values)*percent)

    topN = sorted(values,key=lambda x:int(x),reverse=True)[:N]

    sum_of_topN = np.sum(topN)

    return float(sum_of_topN)/total


## 占相同比例的引用次数的从高到低的论文文章分布
def diversity_of_equal_percentile(citnum_dis,N):

    values = citnum_dis.values()

    total = np.sum(values)

    num = len(values)

    acc_total = 0
    c_p = 0
    num_of_p = 0

    percents = []
    for v in sorted(values,key=lambda x:int(x),reverse=True):

        acc_total+=v

        ##
        if acc_total/float(total)-c_p>=1/float(N):

            c_p+=1/float(N)

            num_of_p+=1

            percents.append(num_of_p/float(num))

            num_of_p = 0

    ##得到不同社区的文章比例，后计算不同percentile的论文的diversity

    diversity = gini(percents)

    return percents,diversity


def paper_num_dis_over_pubyear():

    ## 不同领域随着年份领域论文总数量的变化
    logging.info('loading subj year paper num ...')
    subj_year_num = json.loads(open('data/subj_year_num.json').read())

    plt.figure(figsize = (5,4))

    for subj in sorted(subj_year_num.keys()):

        year_num = subj_year_num[subj]
        xs= []
        ys = []
        total = 0
        for year in sorted(year_num.keys(),key=lambda x:int(x)):

            xs.append(int(year))
            total+= int(year_num[year])
            ys.append(total)

        plt.plot(xs,ys,label="{}".format(subj))


    plt.xlabel('publication year')

    plt.ylabel('total number of papers')

    plt.yscale('log')

    plt.legend()

    plt.tight_layout()

    plt.savefig('fig/subj_year_num_dis.png',dpi=400)

    logging.info('paper year num dis saved to fig/subj_year_num_dis.png')



def paper_year_total_citnum(year_citnum):

    years = [int(year) for year in year_citnum.keys()]

    minY = np.min(years)
    maxY = np.max(years)

    year_total = {}
    total = 0
    for y in range(minY,maxY+1):
        total+= year_citnum.get(str(y),0)
        year_total[int(y)]=total
    return year_total



if __name__ == '__main__':
    ## 统计论文引用次数随着时间的变化
    # stats_citation_count_of_papers()

    ## subj pubyear teamsize over datasize
    # general_top_citation_trend_over_datasize()

    temporal_top_citation_trend_over_datasize()
