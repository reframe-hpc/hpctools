#!/usr/local/bin/python3

# https://data36.com/linear-regression-in-python-numpy-polyfit/
import pandas as pd
import matplotlib.pyplot as plt
# %matplotlib inline
import numpy as np

# {{{
n_sedov = [
278,
288,
297,
306,
314,
318,
322,
330,
337,
344,
350,
363,
369,
375,
380,
386,
391,
396,
401,
406,
411,
416,
420,
]

MiB_gpu = [
4759,
5291,
5731,
6271,
6759,
6979,
7247,
7785,
8275,
8767,
9247,
10277,
10767,
11305,
11741,
12285,
12769,
13257,
13747,
14239,
14777,
15317,
15751,
]
# }}} 
p100 = {'n_sedov': n_sedov, 'MiB_gpu': MiB_gpu}
mydata = pd.DataFrame(data=p100)
x = mydata.n_sedov
xx = [i**3 for i in x]
y = mydata.MiB_gpu
# plt.scatter(x,y)
model = np.polyfit(xx, y, 1) # array([2.50256443e-03, 2.54777987e+02])
model
# y = model[0] * x + model[1]

predict = np.poly1d(model)
# hours_studied = 20
# predict(hours_studied)
from sklearn.metrics import r2_score
r2_score(y, predict(xx))  # 0.9999902500986138

x_lin_reg = range(1800000, 6200000)
y_lin_reg = predict(x_lin_reg)
plt.scatter(x, y)
plt.plot(x_lin_reg, y_lin_reg, c = 'r')
