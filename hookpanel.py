import pandas as pd
import numpy as np
import glob,re,time
import matplotlib.pyplot as plt
import xarray as xa




class HookPanel:
    def __init__(self, __dir__):
        '''
         A class containing the catenated result of all drhookfiles from a directory.
        '''
        self.path = __dir__+'drhook.prof.*'
        print(self.path)
        self.files = glob.glob(self.path)

        assert len(self.files)>0, 'No files found, check '+path

        '''
        % = Self/proctotal_meta
        self  = #calls * callself     /1000
        total = #calls * calltotal    /1000
        '''

        self.columns = '# % Cumulative self total #calls callself calltotal name' .split()

        self.all={}
        self.pids = []
        content = []


        start = time.time()
        for fname in self.files:

            df = pd.read_csv(fname,sep='\s+',skiprows=12,names=self.columns,index_col='name')

            content.append(df.replace(0, np.nan, inplace=False))
            self.pids.append(int(fname.split('.')[-1]))


        for metric in self.columns:
            if metric == 'name': continue
            df = pd.concat([i[metric] for i in content],axis=1)
            df.columns = self.pids
            self.all[metric] = df.copy()

        self.index = list(df.index)

        print('Time taken to create panel %.2fs'%((time.time()-start)/60))


    def get_mod(self,disp=True):
        '''
        Extract the module names from the data
        '''
        self.modules = [i.split(':')[0] for i in self.index if 'MOD' in str(i)]

        if disp: print(self.modules)


    def filterUKCA(self):
        '''
        Drop all non UKCA routines
        '''
        match = tuple(filter(lambda x: mod+'_' in x, self.all[self.columns[0]].index  ))
        print('Filtering only UKCA subroutines - %d found'%len(match))

        for metric in self.columns:
            self.all[metric] = self.all[metric].filter(match,axis=0)


    def filterMOD(self,mod,what='self'):
        ''' Get all modules from an item in all dict '''
        return self.all[what].loc[[mod in str(i) for i in self.index]  ]

    def filterALLindex(self,index,ret = False):
        for i in self.all:
            self.all[i] = self.all[i].loc[index]
        if ret: return self



    def median(self,what='self'):
        ''' Get the Median Value '''
        return self.all[what].median(axis=1)

    def median_all(self,dropna=True):
        ''' Get median value for all stats '''
        df = pd.DataFrame()
        for i in self.columns:
            if i == 'name': continue
            df[i] = self.median(what=i)

        if dropna:
            df = df.loc[df.max(axis=1).dropna().index]
        return df

    def group_plot(self,what = 'self'):
        m = pd.DataFrame(self.median(what))
        m['mod']= [i.split(':')[0] for i in m.index]
        g = m.groupby('mod',group_keys=True).sum()

        g = g.sort_values(by=0,ascending = False)
        g = g[(g > 0).all(axis=1)]
        g /= g.sum()


        return g


#############################################################################

class DrDr:
    def __init__(self, base, update):
        ''' A hook compare class '''

        ## check that both are the correct class
        assert isinstance(base,HookPanel), 'base path is not a HookPanel object: \n'+base.path
        assert isinstance(update,HookPanel), 'base path is not a HookPanel object: \n'+update.path



        self.overlap = list(set(base.index) & set(update.index))
        self.base   =   base.filterALLindex(self.overlap,True)
        self.update = update.filterALLindex(self.overlap,True)


    def diff(self,what='self',dropna = True):
        '''
        Get the mean difference between routines
        base - update
        '''
        d = self.base.median(what) - self.update.median(what)
        if dropna: return d.sort_values().dropna()
        else: return d.sort_values(ascending=False)

    def pdiff(self,what='self',dropna = True):
        '''
        Get the percentage difference between routines
        (base - update) / base
        '''
        d = self.diff(what = what, dropna = False)
        d = (d/self.base.median(what)).sort_values(ascending=False)


        if dropna: return d.dropna()
        else: return d

    def fndiff(self):
        ''' Return entries which do not exist in both groups '''
        return list(set(self.base.index).symmetric_difference(self.update.index))

    def group_mod(self,df):
        '''
        Group a DrDr produced class (mean median etc) into modules
        '''
        assert len(self.overlap) == len(df), 'length mismatch, may be because the diff function used to create the df has used dropna=True (default)'
        df = pd.DataFrame(df)
        df['mod'] = [i.split(':')[0] for i in self.overlap]
        return df.groupby('mod').sum().sort_values(ascending=False)

    def circ(self):
        t=3

if __name__ == '__main__':
    __folder__ = './data/hookfiles_u-bz168_2020-1112-2219_/atmos_strat_16x8/'
    panel = HookPanel(__folder__)
    #panel.filterUKCA()

    __folder1__ = './data/hookfiles_u-bz168_2020-1112-1710_/atmos_strat_16x8/'
    panel1 = HookPanel(__folder1__)
    #panel1.filterUKCA()

    compare = DrDr(base = panel1, update = panel)

    m = compare.diff(dropna=0)
    p = compare.pdiff(dropna=1)

    #
    # lc = 'ASAD_SPARSE_VARS:SPLINSLV2@1'
    # f = pd.DataFrame(panel.all['%'].loc[lc].sort_values())* .9
    # f['c'] = 0
    # v = pd.DataFrame(panel1.all['%'].loc[lc].sort_values())
    # v['c']=1
    # w = pd.concat([f,v])
    # w.sort_values(lc).to_csv('test.csv')
    #
    #w = f.append(v)
