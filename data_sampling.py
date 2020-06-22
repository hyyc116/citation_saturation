#coding:utf-8
'''

从一整个数据集中抽样出多个大小的数据集，统计最大数据集中top100的论文的引用次数的变化


'''

from basic_config import *

## 根据领域名称过滤paper
def select_papers_by_subject(subjName,tag):


	logging.info('load id subject json ...')

	id_subjects = json.loads(open('../cascade_temporal_analysis/data/_id_subjects.json').read())

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


if __name__ == '__main__':
	select_papers_by_subject('computer science','cs')