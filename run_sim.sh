#!/bin/bash

# Check that one arg is provided
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <path_to_memory_trace_file>"
    exit 1
fi

# Get path to memory trace file 
TRACE_FILE="$1"

# Check if trace file exists
if [ ! -f "$TRACE_FILE" ]; then
    echo "ERROR: file '$TRACE_FILE' does not exist"
    exit 1
fi

# Run the simulator
python simple_simulator.py -f "$TRACE_FILE" -s 1024
