import os, glob, pandas as pd, numpy as np

files = sorted(glob.glob('trader_interface/data/*_price_history.csv'))

for f in files:
    df = pd.read_csv(f)
    p = df['Price'].to_numpy(dtype=float)
    # simple mean-reversion z-score signal
    best = None
    for lookback in [5,10,20,30,60]:
        for thresh in [0.5,1.0,1.5,2.0]:
            pos = np.zeros(len(p), dtype=int)
            for i in range(lookback, len(p)):
                window = p[i-lookback:i]
                mu = window.mean()
                std = window.std()
                z = (p[i-1]-mu)/std if std>0 else 0
                if z > thresh:
                    pos[i] = -1
                elif z < -thresh:
                    pos[i] = 1
            pnl = np.sum(np.diff(p) * pos[1:])
            if best is None or pnl > best[0]:
                best = (pnl, lookback, thresh)
    print(os.path.basename(f), 'best_mean_revert', best)

    best2 = None
    for lookback in [3,5,10,20]:
        pos = np.zeros(len(p), dtype=int)
        for i in range(lookback, len(p)):
            # momentum: compare current price to lookback mean
            if p[i-1] > p[i-lookback:i].mean():
                pos[i] = 1
            else:
                pos[i] = -1
        pnl = np.sum(np.diff(p) * pos[1:])
        if best2 is None or pnl > best2[0]:
            best2 = (pnl, lookback)
    print('  best_momentum', best2)
    print()
