#coding:utf-8
'''

从一整个数据集中抽样出多个大小的数据集，统计最大数据集中top100的论文的引用次数的变化


'''

from basic_config import *

## 根据领域名称过滤paper
def select_papers_by_subject(subjName,tag):


    logging.info('load id subject json ...')

    id_subjects = json.loads(open('../cascade_temporal_analysis/data/_ids_subjects.json').read())

    logging.info('id subjects loaded.')

    filtered_ids = []

    for _id in id_subjects.keys():

        for subj in id_subjects[_id]:

            if subj.lower()==subjName.lower():
                filtered_ids.append(_id)


    filtered_ids = list(set(filtered_ids))

    logging.info('{} ids in subject {}.'.format(len(filtered_ids),subjName))

    path = 'data/paper_ids_{}.txt'.format(tag)

    open(path,'w').write('\n'.join(filtered_ids))

    logging.info('data saved to {}.'.format(path))


def GetCitRelationsInsubj(subjName,tag):

    path = 'data/paper_ids_{}.txt'.format(tag)

    paper_ids = set([line.strip() for line in open(path)])

    outpath = 'data/pid_cits_{}.txt'.format(tag)

    of = open(outpath,'w')

    pid_citnum = defaultdict(int)

    progress = 0

    lines = []
    for line in open('../cascade_temporal_analysis/data/pid_cits_ALL.txt'):

        progress+=1

        if progress%10000000==0:
            logging.info('reading %d citation relations....' % progress)

        line = line.strip()

        pid,citing_id = line.split("\t")

        if pid in paper_ids and citing_id in paper_ids:

            lines.append(line)

            pid_citnum[pid]+=1

        if len(lines)>0 and len(lines)%100000==0:

            of.write('\n'.join(lines)+'\n')

            lines = []

    if len(lines)>0 and len(lines)%100000==0:

            of.write('\n'.join(lines)+'\n')

            lines = []


    of.close()

    open('data/pid_citnum_{}.json'.format(tag),'w').write(json.dumps(pid_citnum))
    logging.info('citation relations saved to {}, pid citnum saved to {}.'.format(outpath,'data/pid_citnum_{}.json'.format(tag)))


def plot_citation_distribution(tag):

	paper_citnum = json.loads(open('data/pid_citnum_{}.json'.format(tag)).read())

	top100papers  = sorted(paper_citnum.keys(),key=lambda x:int(paper_citnum[x]),reverse=True)[:100]

	open('data/top_100ids_{}.txt'.format(tag),'w').write('\n'.join(top100papers))

	logging.info('data saved to data/top_100ids_{}.txt'.format(tag))

	value_counter = Counter(paper_citnum.values())

	xs = []

	ys = []

	for citnum in sorted(value_counter.keys(),key=lambda x:int(x)):

		xs.append(int(citnum))

		ys.append(value_counter[citnum])

	ys = np.array(ys)/float(np.sum(ys))

	plt.figure(figsize=(5,4))

	plt.plot(xs,ys,'o',fillstyle='none')


	plt.xscale('log')
	plt.yscale('log')

	plt.xlabel('number of citations')

	plt.ylabel('probality')

	plt.tight_layout()

	plt.savefig("fig/citation_distribution_{}.png".format(tag),dpi=400)

	logging.info('fig saved to fig/citation_distribution_{}.png'.format(tag))



if __name__ == '__main__':
    # select_papers_by_subject('computer science','cs')
    # GetCitRelationsInsubj('computer science','cs')
    plot_citation_distribution('cs')