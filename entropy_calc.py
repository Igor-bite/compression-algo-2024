import sys
from collections import Counter
from math import log

def main(args):
    files = sorted(["trans", "progp", "progl", "progc", "pic", "paper1", "paper2", "paper3", "paper4", "paper5", "paper6", "obj1", "obj2", "news", "geo", "book1", "book2", "bib"])
	
    with open(f"stats.csv", "w") as stats_file:
        stats_file.writelines([f"File,h_x,h_x_x,h_x_xx\n"])
        for file in files:
            (h_x, h_x_x, h_x_xx) = calc_entropy(stats_file, f"dataset/{file}")
            stats_file.writelines([f"{file},{h_x},{h_x_x},{h_x_xx}\n"])
	

def calc_entropy(file):
    with open(file, "rb") as inp:
        data = inp.read()
        h_x = hx(data)
        h_x_x = hx_x(data)
        h_x_xx = hx_xx(data)
        return (h_x, h_x_x, h_x_xx)


def hx(data):
    counts = Counter(data)
    frequencies = ((i / len(data)) for i in counts.values())
    return -sum(p * log(p, 2) for p in frequencies)


def hx_x(data: bytes):
    result = {}
    prev_counts = {}
    for i in range(1, len(data)):
        cur = data[i]
        prev = data[i-1]
        if prev in prev_counts:
            prev_counts[prev] += 1
        else:   
            prev_counts[prev] = 1

        tuple = (cur, prev)
        if tuple in result:
            result[tuple] += 1
        else:
            result[tuple] = 1

    counts = Counter(data)
    data_len = len(data)

    whole_sum = 0
    for x1 in counts:
        x1_count = counts[x1]
        p_x1 = x1_count / data_len
        sum = 0
        for x2 in counts:
            pair = (x2, x1)
            if pair in result:
                p_x1_x2 = result[pair] / prev_counts[x1]
                sum += p_x1_x2 * log(p_x1_x2, 2)
        whole_sum += p_x1 * sum

    return -whole_sum


def hx_xx(data):
    result = {}
    prev_counts = {}
    prevs_len = 0
    for i in range(2, len(data)):
        cur = data[i]
        prev_1 = data[i-1]
        prev_2 = data[i-2]
        if (prev_2, prev_1) in prev_counts:
            prev_counts[(prev_2, prev_1)] += 1
        else:   
            prev_counts[(prev_2, prev_1)] = 1
        prevs_len += 1

        tuple = (cur, (prev_2, prev_1))
        if tuple in result:
            result[tuple] += 1
        else:
            result[tuple] = 1

    counts = Counter(data)

    whole_sum = 0
    for (prev_2, prev_1) in prev_counts:
        sum = 0
        p_x1 = prev_counts[(prev_2, prev_1)] / prevs_len
        for x2 in counts:
            val = (x2, (prev_2, prev_1))
            if val in result:
                p_x1_x2 = result[val] / prev_counts[(prev_2, prev_1)]
                sum += p_x1_x2 * log(p_x1_x2, 2)
        whole_sum += p_x1 * sum

    return -whole_sum
   

if __name__ == "__main__":
	main(sys.argv[1 : ])