import argparse
import os
import random
import math


class CacheBlock:
    def __init__(self, block_size):
        self.valid = False
        self.tag = None
        self.data = [0] * block_size
        self.rr_count = 0 # only used if round robin is the replacement policy

class Cache:
    def __init__(self, cache_size, block_size, associativity, replacement_policy, total_rows):
        self.cache_size = cache_size
        self.block_size = block_size
        self.associativity = associativity
        self.replacement_policy = replacement_policy
        self.num_sets = total_rows
        self.cache = [[CacheBlock(block_size) for _ in range(associativity)] for _ in range(self.num_sets)]
        self.cycle_count = 0
        self.compulsory_miss_count = 0
        self.conflict_miss_count = 0
        self.miss_count = self.compulsory_miss_count + self.conflict_miss_count
        self.hit_count = 0
        self.access_count = self.hit_count + self.miss_count
        if (replacement_policy == "RR"):
            for row in range(self.num_sets):
                for col in range(self.associativity):
                    self.cache[row][col].rr_count = (col + 1) % self.associativity

    def get_address_info(self, address): # Address is already int(address,16)
        address_size = 32
        #print("Before conversion",hex(address))
        # Calculate block offset, index, and tag size in bits
        block_offset_bits = int(math.log2(self.block_size))
        index_bits = int(math.log2(self.num_sets)) # Converts from float to int
        #print(index_bits,math.log2(self.num_sets),self.num_sets)
        tag_bits = address_size - (index_bits + block_offset_bits)
      
        # print("tag_bits",tag_bits)
        # print("index_bits:",index_bits)
        # print("block_offset_bits:",block_offset_bits)
        
        # Address in Hex -> hex(address)
        # Address in Decimal -> address
        # Address in Binary -> (bin(address)[2:]).zfill(address_size)
        """
        print("Address",hex(address))
        print("In decimal:",address)
        print("In binary:",(bin(address)[2:]).zfill(address_size))
        """

        address_bin = (bin(address)[2:]).zfill(address_size)
        #print(address)
        # print("Address in binary:",address_bin)

        tag = int(address_bin[0:tag_bits], 16) # To print these, print(hex(tag)) otherwise will print decimal equivalent
        tag_neutral = int(str(hex(tag))[2:],2)
        """
        print("Tag:",hex(tag_neutral))
        print("In decimal:",tag_neutral)
        print("In binary:",bin(tag_neutral)[2:].zfill(tag_bits))
        """

        try:
        	index = int(address_bin[tag_bits:tag_bits + index_bits], 16)
        	index_neutral = int(str(hex(index))[2:],2)
        except:
            index = 0
            index_neutral = 0
        """
        print("Index:",hex(index_neutral))
        print("In decimal:",index_neutral)
        print("In binary:",bin(index_neutral)[2:].zfill(index_bits))
        """

        block_offset = int(address_bin[tag_bits + index_bits:], 16)
        #print(address_bin)
        #print(address_bin[tag_bits + index_bits:])
        #print(block_offset)
        block_offset_neutral = int(str(hex(block_offset))[2:],2)
        """
        print("Block Offset:",hex(block_offset_neutral))
        print("In decimal:",block_offset_neutral)
        print("In binary:",bin(block_offset_neutral)[2:].zfill(block_offset_bits))
        """
        #print("After",hex(tag_neutral),hex(index_neutral),hex(block_offset_neutral))
        #return tag, index, block_offset
        return hex(tag_neutral), index_neutral, block_offset_neutral

    def choose_block_to_replace(self, row):
        if (self.replacement_policy == 'RR'):
            # Round Robin
            # print("Round Robin")
            for block in self.cache[row]:
                block.rr_count = (block.rr_count + 1) % self.associativity
                # print(block.rr_count)
            
            for block in self.cache[row]:
                if (block.rr_count == 0):
                    return block
        else:
            # Randomly selects a block
            # print("Random")
            return self.cache[row][random.randint(0,self.associativity-1)] # [0,associativity)

    # Function to access cache
    def access_data(self, address, byte_length, data):
       # Get tag, row_index, and block_offset from address
        tag, row_index, block_offset = self.get_address_info(address)
        
        """
        print("tag:",tag)
        print("row_index:",row_index)
        print("block_offset:",block_offset)
        print("Max Rows:",self.num_sets)
        """
        
        #print(row_index,tag,block_offset)
        # Determine the number of rows to be accessed
        if (block_offset + byte_length) > self.block_size:
            num_rows = math.ceil((block_offset + byte_length) / self.block_size)
            #print(num_rows)
        else:
            num_rows = 1

        hit = False # Initialize hit to False

        conflictMiss = False
        # Outer loop for rows
        for row in range(row_index, row_index + num_rows):
            if row >= self.num_sets:
                row = row - self.num_sets
            
            # Searching all the blocks for a matching tag. If none are found, that is a conflict miss
            # If compulsory miss, fill that block directly. DO NOT USE REPLACEMENT POLICY
            # If conflict miss, use replacement policy
            compulsory_miss_block = None
            hit = False
            #print(row)

            for block in self.cache[row]:
                if block.valid:
                    if str(block.tag) == str(tag):
                        hit = True
                        self.hit_count += 1
                        self.cycle_count += 3 if data is None else 2
                        conflictMiss = False
                        break
                    else:
                        #self.cycle_count += 2 + 4 * math.ceil(self.block_size/4) if data is None else 1 + 4 * math.ceil(self.block_size/4)
                        #self.conflict_miss_count += 1
                        conflictMiss = True
                else:
                    compulsory_miss_block = block # Directly fill data to this block
                    self.cycle_count += 2 + 4 * math.ceil(self.block_size/4) if data is None else 1 + 4 * math.ceil(self.block_size/4)
                    self.compulsory_miss_count += 1
                    compulsory_miss_block.valid = True
                    compulsory_miss_block.tag = tag
                    compulsory_miss_block.data = data
                    conflictMiss = False
                    break
            if conflictMiss:
            	conflictMiss = False
            	block_to_replace = self.choose_block_to_replace(row)
            	block_to_replace.valid = True
            	block_to_replace.tag = tag
            	block_to_replace.data = data
            	self.cycle_count += 2 + 4 * math.ceil(self.block_size/4) if data is None else 1 + 4 * math.ceil(self.block_size/4)
            	self.conflict_miss_count += 1
            	conflictMiss = True
        # Update other counters
        self.miss_count = self.compulsory_miss_count + self.conflict_miss_count
        self.access_count = self.hit_count + self.miss_count

        return

# Function to parse command-line arguments
def parse_arguments():
    parser = argparse.ArgumentParser(description="Cache Simulator")
    parser.add_argument("-f", dest="trace_files", nargs="+", help="List of trace files")
    parser.add_argument("-s", type=int, default=512, help="Cache size in KB")
    parser.add_argument("-b", type=int, default=16, help="Block size")
    parser.add_argument("-a", type=int, default=2, help="Associativity")
    parser.add_argument("-r", choices=["RR", "RND"], default="RR", help="Replacement policy")
    parser.add_argument("--print-addresses", action="store_true", help="Print the first 20 addresses and lengths")

    return parser.parse_args()

# Function to check if a file path is valid
def is_valid_file(file_path):
    return os.path.exists(file_path) and os.path.isfile(file_path)

# Function to extract addresses and lengths from a trace file
def extract_addresses_and_lengths(trace_file):
    addresses_and_lengths = []

    with open(trace_file, "r") as file:
        for line in file:
            if len(addresses_and_lengths) >= 20:
                break  # Stop after the first 20 addresses

            # Extract the address and length
            parts = line.split()
            if len(parts) and parts[0] == "EIP":
                address = int(parts[2], 16)
                length = int(parts[1][1:3])
                addresses_and_lengths.append((address, length))

    return addresses_and_lengths

# Main function
def main():
    args = parse_arguments()

    # Check if trace files are valid
    for trace_file in args.trace_files:
        if not is_valid_file(trace_file):
            print(f"Bad file path: {trace_file}")
            return

    print(f"Trace File: {args.trace_files[0]}")
    print("\n***** Cache Input Parameters *****")
    print(f"Cache Size: \t\t\t{args.s} KB")
    print(f"Block Size: \t\t\t{args.b} bytes")
    print(f"Associativity: \t\t\t{args.a}")
    print(f"Replacement Policy: \t\t{'Random' if args.r == 'RND' else 'Round Robin'}")
    print("\n***** Cache Calculated Values *****\n")

    # Calculate and print other cache-related values
    total_blocks = args.s * 1024 // args.b
    tag_size = 32 - int(math.log2(args.s * 1024)) + int(math.log2(args.a))
    index_size = total_blocks.bit_length() - args.a.bit_length()
    total_rows = total_blocks // args.a
    overhead_size = (tag_size + 1) * total_blocks // 8
    implementation_memory_size = overhead_size + total_blocks * args.b
    cost = implementation_memory_size / 1024 * 0.09  # Assuming $0.09 per KB
    
    print(f"Total # Blocks: \t\t{total_blocks}")
    print(f"Tag Size: \t\t\t{tag_size} bits")
    print(f"Index Size: \t\t\t{index_size} bits")
    print(f"Total # Rows: \t\t\t{total_rows}")
    print(f"Overhead Size: \t\t\t{overhead_size} bytes")
    print(f"Implementation Memory Size: \t{implementation_memory_size / 1024:.2f} KB ({implementation_memory_size} bytes)")
    print(f"Cost: \t\t\t\t${cost:.2f}\n\n")

    if args.print_addresses:
        addresses_and_lengths = extract_addresses_and_lengths(args.trace_files[0])
        print("***** First 20 Addresses and Lengths *****")
        for i, (address, length) in enumerate(addresses_and_lengths):
            print(f"0x{address:08X}: ({length})")

    cache_sim = Cache(args.s * 1024, args.b, args.a, args.r, total_rows)
    instruction_count = 0
    address_count = 0
    with open(args.trace_files[0], "r") as file:
        for line in file:
            parts = line.split()
            if parts:
                if parts[0] == "EIP":
                    instruction_count += 1
                    instruction_address = int(parts[2], 16)
                    byte_length = int(parts[1][1:3])
                    cache_sim.access_data(instruction_address, byte_length, None)
                    address_count += 1
                if "dstM" in parts[0] and parts[4] != "00000000" and parts[5] != "--------":
                    source_address = int(parts[4], 16)
                    source_data = int(parts[5], 16)
                    cache_sim.access_data(source_address, 4, source_data)
                    address_count += 1
                if "dstM" in parts[0] and parts[1] != "00000000" and parts[2] != "--------":
                    destination_address = int(parts[1], 16)
                    destination_data = int(parts[2], 16)
                    cache_sim.access_data(destination_address, 4, destination_data)
                    address_count += 1

    # Calculate metrics
    hit_rate = (cache_sim.hit_count * 100) / cache_sim.access_count
    miss_rate = 100 - hit_rate

    print("***** CACHE SIMULATION RESULT *****\n")
    print(f"Total Accesses: \t{cache_sim.access_count}  ({address_count} addresses)")
    print(f"Cache Hits: \t\t{cache_sim.hit_count}")
    print(f"Cache Misses: \t\t{cache_sim.miss_count}")
    print(f"--- Compulsory Misses: \t{cache_sim.compulsory_miss_count}")
    print(f"--- Conflict Misses: \t{cache_sim.conflict_miss_count}\n\n")
    print(f"***** ***** CACHE HIT & MISS RATE: ***** *****\n")
    print(f"Hit Rate: \t\t{hit_rate:.4f}%")
    print(f"Miss Rate: \t\t{miss_rate:.4f}%")
    print(f"CPI: \t\t\t{(cache_sim.cycle_count/instruction_count):.2f} Cycles/Instruction ({instruction_count})")
    unused_bytes = (total_blocks-cache_sim.compulsory_miss_count) * (args.b + (tag_size + 1)/8)
    print(f"Unused Cache Space: \t{(unused_bytes / 1024):.2f} KB / {implementation_memory_size / 1024:.2f} KB = {(100 * (unused_bytes/implementation_memory_size)):.2f}% Waste: ${(0.09 * (unused_bytes/1024)):.2f}")
    print(f"Unused Cache Blocks: \t{total_blocks-cache_sim.compulsory_miss_count} / {total_blocks}")
    print(f"cache_size_kb,block_size_b,associativity,overhead_size_b,total_cost,hit_rate,miss_rate,cpi,unused_space,waste_cost")
    print(f"{args.s},{args.b},{args.a},{overhead_size},{cost:.2f},{hit_rate:.4f},{miss_rate:.4f},{(cache_sim.cycle_count/instruction_count):.5f},{(100 * (unused_bytes/implementation_memory_size)):.2f},{(0.09 * (unused_bytes/1024)):.2f}")

if __name__ == "__main__":
    main()
