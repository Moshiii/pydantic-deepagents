import random

numbers = [random.randint(1, 10) for _ in range(10)]
with open('/workspace/numbers.txt', 'w') as f:
    f.write(','.join(str(num) for num in numbers))
