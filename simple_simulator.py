import argparse
import os
import random
import math

from collections import OrderedDict

#Parse arugements from your input
def parse_arguments():
    parser = argparse.ArgumentParser(description="Cache Simulator")
    parser.add_argument("-f", dest="trace_file", nargs="+", help="The file being passed in", required=True)
    parser.add_argument("-s", type=int, default=1024, help="Cache size in KB")
    parser.add_argument("-b", type=int, default=64, help="Cacheline/Block size")
    parser.add_argument("-a", type=int, default=16, help="Associativity")

    return parser.parse_args()

def calculate_address(address, associativity, cache_size):
    block_size = 64

    # binary address is always 64 bits, since the cacheline is always 64 bytes
    binary_address = bin(int(str(address), 16))[2:].zfill(block_size)

    offset = binary_address[-6:] #Always 64 bits, so always the last 6 bits


    # Total cache size / cache line size = num of cache lines
    #  size / 64 = # of cache lines
    # num of cache lines / associativity = num of sets
    # num of cache lines / 16 = num of sets
    SetNumofBits = math.log2((cache_size / block_size) / associativity)  #For the substring
    SetNumofBits = int(SetNumofBits)
    Sindex = binary_address[-6-SetNumofBits:-6]
    
    # Whatever bits are not the offset and set_index
    tag = binary_address[:-6-SetNumofBits] 
    
    return offset, Sindex, tag

def cache_get(tag, Sindex, LRUCache):
    try:
        # convert binary string to int
        Sindex = int(Sindex, 2)
    except:
        # if it's blank, there's only one set, LRUCache[0]
        Sindex = 0
    # print(Sindex)

    if tag not in LRUCache[Sindex]:
        return -1 
    else:    
        # LRUCache[Sindex] is now the most recently used, 
        # so move to the end
        LRUCache[Sindex].move_to_end(tag)
        return LRUCache[Sindex][tag]

def cache_put(LRUCache, tag, Sindex, offset, capacity):
    try:
        # convert binary string to int
        Sindex = int(Sindex, 2)
    except:
        # if it's blank, there's only one set, LRUCache[0]
        Sindex = 0

    # add tag to queue for set at Sindex
    LRUCache[Sindex][tag] = [offset]
    LRUCache[Sindex].move_to_end(tag)

    if len(LRUCache[Sindex]) > capacity:
        # pop least recently used tag in this set 
        LRUCache[Sindex].popitem(last=False) 


def main():
    args = parse_arguments()

    associativity = args.a
    cache_size = args.s * 1024
    capacity = args.a
    block_size = 64

    cache_hit = 0
    cache_miss = 0
    total_rows = 0
    miss_rate = 0
    
    with open(args.trace_file[0], "r") as file:
        for line in file:
            # For the first iteration, find the number of sets
            # And intitialize a list of X OrderedDicts, 
            # where X is equal to the number of sets
            if total_rows == 0:
                num_of_set_bits = int(math.log2((cache_size / block_size) / associativity))
                num_of_sets = 2 ** num_of_set_bits
                LRUCache = [OrderedDict() for _ in range(num_of_sets)]
            #  try/except here to catch bad lines
            try:
                total_rows = total_rows + 1

                parts = line.split()
                offset, SetIndex, tag = calculate_address(parts[2],associativity, cache_size)
                
                result = cache_get(tag, SetIndex, LRUCache)
                # print(tag+"!!!", SetIndex+"!!!", offset)
                if result != -1:
                    cache_hit = cache_hit + 1
                else:
                    cache_miss = cache_miss + 1
                    cache_put(LRUCache, tag, SetIndex, offset, capacity)
            except:
                continue
    
    miss_rate = cache_miss / total_rows
    print(total_rows)
    print(cache_miss)
    print(f'Cache miss rate: {round(100 * cache_miss / total_rows, 2)}%')

if __name__ == "__main__":
    main()
