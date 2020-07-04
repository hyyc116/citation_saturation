#coding:utf-8
'''
根据不同给的subject标签对wos的论文进行分领域处理

'''

from basic_config import *



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

            xs.append(year)
            total+= year_num[year]
            ys.append(total)

        plt.plot(xs,ys,label="{}".format(subj))


    plt.xlabel('publication year')

    plt.ylabel('total number of papers')

    plt.yscale('log')

    plt.legend()

    plt.tight_layout()

    plt.savefig('fig/subj_year_num_dis.png',dpi=400)




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
