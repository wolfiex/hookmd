import jinja2
import pandas as pd




def group(self,filename = 'test.html'):
        
        tot = self.diff('self',False)
        cal = self.diff('callself',False)
        ncalls = self.base.all['#calls'][1].fillna(0)
        
        tot /= tot.sum()
        cal /= cal.sum()
    
        
        marr = pd.DataFrame(tot)
        marr['mod']= [i.split(':')[0] for i in marr.index] 
        g = marr.groupby('mod',group_keys=True).sum() 
        g = g.sort_values(by=0,ascending = False) 
        
        g = g[(g > 0).all(axis=1)]   
        #g /= g.sum()
        
        out = {}
        for z in g.iterrows():
            
            match = tot[[z[0] in i for i in tot.index]].sort_values(ascending=False)
            # tg = tot.loc[match] 
            # cg = cal.loc[match] 
            # 
            res = []
            for i in match.index:
                
                group = {'name':i.split(':')[-1].title(),'self':tot.loc[i],'callself':cal.loc[i],'selft':'%.2e s'%tot.loc[i], 'callselft':'%d calls @%.2e s'%(ncalls.loc[i],cal.loc[i])}
                
                if group['self'] > 0 or group['callself'] > 0 : 
                    res.append(group)
            
            
            if len(res)>0:
                out['%s - %.2e s'%(z[0],z[1][0])] = res
        
        
        

        subs = jinja2.Environment(
                loader=jinja2.FileSystemLoader('templates/')
            ).get_template('cgroup.html').render(title='Compare Example',runs = out)
        
        with open(filename,'w') as f: f.write(subs)

            
        return g





































