#coding:utf-8
'''
分析马太效应、不平等随时间的变化
'''

from basic_config import *


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
        sameset =  list(set(subj) & set(citing_subjs))

        if len(sameset)==0:
            continue

        for subj in sameset:
            subj_paper_year_citnum[subj][pid][citing_year]+=1

    open('data/topsubj_paper_year_citnum.json','w').write(jsom.dumps(subj_paper_year_citnum))
    logging.info('data saved to data/topsubj_paper_year_citnum.json.')


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




if __name__ == '__main__':
    stat_subj_paper_year_citnum()











