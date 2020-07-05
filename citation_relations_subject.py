#coding:utf-8
'''
根据不同给的subject标签对wos的论文进行分领域处理

'''

from basic_config import *
from gini import gini


'''

选择6个top领域，然后在6个top领域内分别选择一个子领域作为实验数据。

'''
def get_paperids_of_subjects():

    pid_subjs = json.loads(open('../cascade_temporal_analysis/data/_ids_subjects.json').read())

    paper_year = json.loads(open('../cascade_temporal_analysis/data/pubyear_ALL.json').read())


    subj_ids = defaultdict(list)
    subj_year_num = defaultdict(lambda:defaultdict(int))

    # pid_topsubj = json.loads(open('../cascade_temporal_analysis/data/_ids_top_subjects.json').read())

    sub_foses = set(['computer science','physics','chemistry','medicine','art','biology'])

    for pid in pid_subjs.keys():

        for subj in pid_subjs[pid]:

            for s in sub_foses:

                if s in subj.lower():

                    subj_ids[s].append(pid)

                    subj_year_num[s][paper_year[pid]]+=1

    open('data/subj_pids.json','w').write(json.dumps(subj_ids))

    logging.info('data saved to data/subj_pids.json')

    open('data/subj_paper_num.json','w').write(json.dumps(subj_year_num))

    logging.info('data saved to data/subj_paper_num.json')


    for subj in subj_ids.keys():
        logging.info('there are {} papers in subj {}'.format(len(subj_ids[subj]),subj))

##统计wos所有论文的citation count随着时间的变化情况
def stats_citation_count_of_papers(subj,tag):

    logging.info('loading paper year obj ...')
    paper_year = json.loads(open('../cascade_temporal_analysis/data/pubyear_ALL.json').read())

    logging.info('start to stat citation relations ...')

    subj_pids = json.loads(open('data/subj_pids.json').read())

    ## 需要保证是local citation才行
    # _ids_top_subjects = json.loads(open(''))
    id_set = set(subj_pids[subj])

    pid_year_citnum = defaultdict(lambda:defaultdict(int))

    progress = 0

    lines = []
    for line in open('../cascade_temporal_analysis/data/pid_cits_ALL.txt'):

        progress+=1

        if progress%10000000==0:
            logging.info('reading %d citation relations....' % progress)

        line = line.strip()

        pid,citing_id = line.split("\t")

        if pid not in id_set:
            continue

        if citing_id not in id_set:
            continue

        if paper_year.get(pid,None) is None or paper_year.get(citing_id,None) is None:
            continue

        pid_year_citnum[pid][int(paper_year[citing_id])]+=1

    open('data/pid_year_citnum_{}.json'.format(tag),'w').write(json.dumps(pid_year_citnum))
    logging.info('pid year citnum saved to data/pid_year_citnum_{}.json.'.format(tag))

##整体领域高被引论文的平均数随着数据规模的变化情况
def general_top_citation_trend_over_datasize(subj,tag):

    ## paper year
    paper_year = json.loads(open('../cascade_temporal_analysis/data/pubyear_ALL.json').read())

    paper_ts = json.loads(open('data/pid_teamsize.json').read())

    ## 按照学科进行分析
    pid_year_citnum = json.loads(open('data/pid_year_citnum_{}.json'.format(tag)).read())

    ## year num count 各学科每年的引用次数分布
    year_citnum_dis = defaultdict(lambda:defaultdict(int))
    ## 根据发布年份的引用次数分布
    puby_year_citnum_dis = defaultdict(lambda:defaultdict(lambda:defaultdict(int)))

    ## 各学科中 不同 teamsize随着时间的变化
    ts_year_citnum_dis = defaultdict(lambda:defaultdict(lambda:defaultdict(int)))

    for pid in pid_year_citnum.keys():

        pubyear = int(paper_year[pid])

        if pubyear>= 2016:
             continue

        ts = paper_ts.get(pid,1)

        year_total =  paper_year_total_citnum(pid_year_citnum[pid])

        for year in range(pubyear,2016):
            citN = year_total.get(year,0)
            
            if citN==0:
                continue

            year_citnum_dis[year][citN]+=1
            puby_year_citnum_dis[pubyear][year][citN]+=1
            ts_year_citnum_dis[ts][year][citN]+=1

    open('data/year_citnum_dis_{}.json'.format(tag),'w').write(json.dumps(year_citnum_dis))
    logging.info('subject year paper citnum dis data saved to data/year_citnum_dis_{}.json'.format(tag))

    open('data/puby_year_citnum_dis_{}.json'.format(tag),'w').write(json.dumps(puby_year_citnum_dis))
    logging.info('subject pubyear year paper citnum dis data saved to data/puby_year_citnum_dis_{}.json'.format(tag))


    open('data/ts_year_citnum_dis_{}.json'.format(tag),'w').write(json.dumps(ts_year_citnum_dis))
    logging.info('subject teamsize year paper citnum dis data saved to data/ts_year_citnum_dis_{}.json'.format(tag))

    logging.info('done')

##不同的年代发表的高被引论文的引用次数平均数随着数据规模的变化情况
def temporal_top_citation_trend_over_datasize(subj,tag):
    # paper_num_dis_over_pubyear()
    subj_upper_limit_over_year()

    # fig,axes = plt.subplots(4,2,figsize=(10,16))


    # for i,subj in enumerate(sorted(year_citnum_dis.keys())):

        


    # plt.tight_layout()

    # plt.savefig('fig/subj_citation_upper_limit.png',dpi=400)

    # logging.info('fig saved to fig/subj_citation_upper_limit.png.')

    # year_num = subj_year_num[subj]


## 不同学科 不同年份的引用次数分布
def upper_limit_over_year(subj,tag):

    logging.info('loading subj year citnum dis ...')
    year_citnum_dis = json.loads(open('data/year_citnum_dis_{}.json'.format(tag)).read())

    year_num = json.loads(open('data/subj_year_num.json').read())[subj]

    fig,ax = plt.subplots(figsize=(5,4))
    year_citnum_dis = year_citnum_dis[subj]

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

    ax.set_yscale('log')


    ax.legend()

    plt.tight_layout()

    plt.savefig('fig/subj_citation_upper_limit_{}.png'.format(tag),dpi=400)

    logging.info('fig saved to fig/subj_citation_upper_limit_{}.png.'.format(tag))



def curve_fit_plotting(ax,xs,ys,label):

    ##对数据的数量进行过滤
    start_pos = 0
    for i in range(len(xs)):
        if xs[i]>10000:
            start_pos = i
            break

    xs = xs[start_pos:]
    ys = ys[start_pos:]

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



def paper_num_dis_over_pubyear():

    ## 不同领域随着年份领域论文总数量的变化
    logging.info('loading subj year paper num ...')
    subj_year_num = json.loads(open('data/subj_year_num.json').read())

    plt.figure(figsize = (6,4))

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

    lgd = plt.legend(loc=6,bbox_to_anchor=(0.5, -0.2), ncol=2)
    # plt.legend()

    plt.tight_layout()

    plt.savefig('fig/subj_year_num_dis.png',dpi=400,additional_artists=[lgd],bbox_inches="tight")

    logging.info('paper year num dis saved to fig/subj_year_num_dis.png')



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



if __name__ == '__main__':

    ##需要研究的领域的论文id
    # get_paperids_of_subjects()

    subjs = ['computer science','physics','chemistry','medicine','art','biology']
    tags = ['cs','physics','chemistry','medicine','art','biology']

    for i in range(len(subjs)):

        subj = subjs[i]
        tag = tags[i]

        ## 统计论文引用次数随着时间的变化
        stats_citation_count_of_papers(subj,tag)
        
        general_top_citation_trend_over_datasize(subj,tag)

        upper_limit_over_year(subj,tag)

    ## subj pubyear teamsize over datasize
    # 

    # temporal_top_citation_trend_over_datasize()
