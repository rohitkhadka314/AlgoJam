import os, glob, pandas as pd, numpy as np
from pathlib import Path

files = sorted(glob.glob('trader_interface/data/*_price_history.csv'))
for f in files:
    df = pd.read_csv(f)
    p = df['Price'].to_numpy(dtype=float)
    ret = np.diff(p) / p[:-1]
    z = np.diff(np.log(p))
    # simple stats
    mean_ret = float(np.mean(z))
    std_ret = float(np.std(z))
    sharpe = mean_ret / std_ret if std_ret > 0 else 0.0
    autocorr1 = float(np.corrcoef(z[:-1], z[1:])[0,1]) if len(z) > 2 else 0.0
    # change-point-ish sign flips
    sign_changes = int(np.sum(np.sign(z[1:]) != np.sign(z[:-1])))
    print(os.path.basename(f))
    print('  n=', len(p), 'mean_log_ret=', round(mean_ret, 6), 'std=', round(std_ret, 6), 'sharpe=', round(sharpe, 4), 'autocorr1=', round(autocorr1, 4), 'sign_changes=', sign_changes)
    print('  first10=', [round(float(x), 2) for x in p[:10]])
    print('  last10=', [round(float(x), 2) for x in p[-10:]])
    print('  last5_logrets=', [round(float(x), 6) for x in z[-5:]])
    print()
