import argparse
import os
import random
import math

from collections import OrderedDict

# class LRUCache:
#     def __init__(self, capacity):
#         self.capacity = 16                              #size/64
#         self.cache = OrderedDict()


LRUCache = OrderedDict()

#Parse arugements from your input
def parse_arguments():
    parser = argparse.ArgumentParser(description="Cache Simulator")
    parser.add_argument("-f", dest="trace_file", nargs="+", help="The file being passed in", required=True)
    parser.add_argument("-s", type=int, default=1024, help="Cache size in KB")
    parser.add_argument("-b", type=int, default=64, help="Cacheline/Block size")
    parser.add_argument("-a", type=int, default=16, help="Associativity")

    return parser.parse_args()

def calculate_address(address, associativity, cache_size):
    binary_address = bin(int(str(address), 16))[2:].zfill(64)
    offset = binary_address[-6:] #Always 64 bit
    # SetNumofBits = int(math.sqrt(associativity) + -6)  #For the substring


    # Total cache size / cache line size = num of cache lines
    #  size / 64 = # of cache lines
    # num of cache lines / associativity = num of sets
    # num of cache lines / 16 = num of sets
    SetNumofBits = math.log2((cache_size / 64) / associativity)  #For the substring
    SetNumofBits = int(SetNumofBits)
    Sindex = binary_address[-6-SetNumofBits:-6]
    tag = binary_address[:-6-SetNumofBits] 
    return offset, Sindex, tag

def cache_get(tag, LRUCache):
    
    if tag not in LRUCache:
        return -1 
    else:    
        LRUCache.move_to_end(tag)  # Move to the end
        return LRUCache[tag]

def cache_put(LRUCache, tag, Sindex, offset, capacity):
    # if tag in LRUCache:

    LRUCache[tag] = [Sindex, offset]
    LRUCache.move_to_end(tag)
    if len(LRUCache) > capacity:
        LRUCache.popitem(last=False) 


def main():
    args = parse_arguments()

    # associativity = 16
    associativity = args.a
    size = args.s * 1024
    capacity = size / 64
    cache_hit = 0
    cache_miss = 0
    total_rows = 0
    miss_rate = 0
    with open(args.trace_file[0], "r") as file:
        for line in file:
            total_rows = total_rows + 1
            parts = line.split()
            offset, SetIndex, tag = calculate_address(parts[2],associativity, size)
            result = cache_get(tag, LRUCache)
            if result != -1:
                # print("DO I EVER GET HERE")
                cache_hit = cache_hit + 1
            else:
                cache_miss = cache_miss + 1
                cache_put(LRUCache, tag, SetIndex, offset, capacity)
    miss_rate = cache_miss / total_rows
    print(total_rows)
    print(cache_miss)
    print(f'Cache miss rate: {round(100 * cache_miss / total_rows, 2)}%')

if __name__ == "__main__":
    main()
