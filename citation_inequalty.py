#coding:utf-8
'''
分析马太效应、不平等随时间的变化
'''

from basic_config import *


def stat_subj_paper_year_citnum():

    pid_topsubj = json.loads(open('../cascade_temporal_analysis/data/_ids_top_subjects.json').read())
    paper_year = json.loads(open('../cascade_temporal_analysis/data/pubyear_ALL.json').read())

    subj_paper_year_citnum = defaultdict(lambda:defaultdict(lambda:defaultdict(int)))

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

if __name__ == '__main__':
    stat_subj_paper_year_citnum()











