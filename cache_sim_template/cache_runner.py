import subprocess
import csv

# Define the range of values for each flag
sizes = [1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096, 8192]
block_sizes = [4, 8, 16, 32, 64]
associativities = [1, 2, 4, 8, 16]

# Open a CSV file for writing
with open('cache_data.csv', 'w', newline='') as csvfile:
    # Create a CSV writer object
    csvwriter = csv.writer(csvfile)

    # Write header row to the CSV file
    #csvwriter.writerow(['Size', 'Block_Size', 'Associativity', 'Output'])
    csvwriter.writerow(['cache_size_kb','block_size_b','associativity','overhead_size_b','total_cost','hit_rate','miss_rate','cpi','unused_space','waste_cost'])

    # Iterate through each combination of flag values
    for size in sizes:
        for block_size in block_sizes:
            for associativity in associativities:
                # Run your program using subprocess
                command = [
                    "python3",
                    "milestone3.py",
                    "-s", str(size),
                    "-b", str(block_size),
                    "-a", str(associativity),
                    "-r", "RR",
                    "-f", "A-9_new_1.5.pdf.trc",
                ]

                # Execute the command and capture the output
                result = subprocess.run(command, capture_output=True, text=True)

                # Write the results to the CSV file
                #csvwriter.writerow([size, block_size, associativity, overhead_size_b, total_cost, hit_rate, miss_rate, cpi, unused_space, waste_cost, result.stdout])
                output_lines = result.stdout.strip().split('\n')
                data_line = output_lines[-1].split(',')
                csvwriter.writerow([size] + [block_size] + [associativity] + data_line[3:])
