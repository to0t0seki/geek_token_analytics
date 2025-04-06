# %% 最初のセル
import sys
print("Python Path:")
for path in sys.path:
    print(f"- {path}")

# %% 2番目のセル
x = 10
y = 20
print(f"x + y = {x + y}")

# %% 3番目のセル - データ可視化の例
import matplotlib.pyplot as plt
import numpy as np

x = np.linspace(0, 10, 100)
plt.plot(x, np.sin(x))
plt.title("Sin Wave")
plt.show() 