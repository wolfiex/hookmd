import pandas as pd
import numpy as np
import glob,re,time
import matplotlib.pyplot as plt


__folder__ = '/Users/dna/Desktop/hookmd/data/hookfiles_u-bz168_2020-1103-0344_/atmos_strat_16x8/'

files = glob.glob(__folder__+'drhook.prof.*')

'''
    #  % Time         Cumul         Self        Total     # of calls        Self       Total    Routine@<thread-id>
                                                                             (Size; Size/sec; Size/call; MinSize; MaxSize)
        (self)        (sec)        (sec)        (sec)                    ms/call     ms/call
'''

'''
% = Self/proctotal_meta
self  = #calls * callself     /1000
total = #calls * calltotal    /1000
'''






columns = '# % Cumulative self total #calls callself calltotal name' .split()
getmod = lambda x: x.split(':')[0]

dfdict = {}

start = time.time()
for fname in files:

    pnum = int(fname.split('.')[-1])
    df = pd.read_csv(fname,sep='\s+',skiprows=12,names=columns,index_col='name')
    df['module'] = [getmod(i) for i in df.index]
    df._metadata = {}
    df._metadata['proc_num'] = pnum


    dfdict[pnum] = df.replace(0, np.nan, inplace=False)

panel = pd.Panel(dfdict)

print('Time taken to create panel %.2fs'%((time.time()-start)/60))


# del dfdict,pnum,df,start

subroutines = panel.major_axis


'''
Standardize

optimisation map:

total time,
number of calls





'''



#
# from sklearn.decomposition import PCA
# pca = PCA(n_components=2, svd_solver='full')
# subroutines = panel.major_axis
# data = []
# names = []
#
# for s in subroutines:
#     n = panel[:,s,['self','callself']].replace(np.nan,1e99).values.flatten()
#     # n = n[np.nonzero(n > 0)].reshape(-1)
#     data.append( n.tolist() )
#     names.append(s)
#
# fit = pca.fit_transform(np.array(data))
# pc = 1+ 10*panel[:,:,'%'].mean(axis=1)
# pc = 1+ 10*panel[:,:,'self'].mean(axis=1)
# cl = 1+ 10*panel[:,:,'callself'].mean(axis=1)
# plt.scatter(fit[:,0],fit[:,1],s = pc,alpha=.6,c=cl)
# plt.show()


# fig = plt.figure()
# ax1 = fig.add_subplot(111)
# for i in panel.items:
#     cl = (np.random.random()*255, np.random.random()*255, np.random.random()*255)
#     panel[i,:,['self','callself']].replace(np.nan,0).plot(kind='scatter',x='self',y='callself',ax = ax1)
# plt.show()



'''
selection = panel[:,:,'%']
box = selection[selection.sum(axis=1)>0]

ten = box.mean(axis=1).sort_values(ascending=False).iloc[0:10].index
ten = box.loc[ten]

ten.T.plot(kind='box')
plt.show()

'''

'''
panel[:,subroutines,'%'].median(axis=1).sort_values(ascending=False)

max % time for each run
panel[:,:,'%'].max()

max describe
panel[:,:,:].max()
'''
