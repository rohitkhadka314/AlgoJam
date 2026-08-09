import pandas as pd, glob, os, numpy as np
files=sorted(glob.glob('trader_interface/data/*_price_history.csv'))
frames=[]
for f in files:
    df=pd.read_csv(f)
    name=os.path.basename(f).replace('_price_history.csv','')
    p=df['Price'].to_numpy(float)
    r=np.diff(np.log(p))
    frames.append(pd.Series(r, name=name))
ret_df=pd.concat(frames, axis=1)
print(ret_df.corr().round(3))
