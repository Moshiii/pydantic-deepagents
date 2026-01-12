import random
from collections import Counter

# 生成1000个0-9的随机整数
data = [random.randint(0, 9) for _ in range(1000)]

# 统计每个数字出现的频率
counter = Counter(data)

total = len(data)
distribution = {str(k): v / total for k, v in sorted(counter.items())}

# 保存结果
with open('/workspace/random_numbers.txt', 'w') as f:
    f.write('数字列表：\n')
    f.write(' '.join(map(str, data)) + '\n')
    f.write('\n概率分布：\n')
    for k, v in distribution.items():
        f.write(f'{k}: {v:.3f}\n')
