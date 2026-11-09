import argparse
import socket
import struct
import time
import random

# Matrix generation function
def generate_matrices(rows_A, cols_A, rows_B, cols_B):

    # Return matrix_A and matrix_B in a tuple of matrices
    pass

def divide_matrices(matrices_tuple, total_clients):

    # Needs to split the left matrix and update the 
    # tuple so no data is lost. Also needs to 
    # transpose the right matrix to rows for more
    # efficient stride(python uses row major order).
    # The entire right matrix should be sent to each client
    # to avoid high packet overhead. 

    # Put all of matrix A in one array, then
    # all of matrix B in another.
    pass

def create_packet(split_matrices,):
    pass


# Clients are going to need to talk to eachother to send 
# data from the split matrices back to the other clients that 
# haven't multiplied the other ones together yet. 

# Add time and memory data to see if splitting the right matrix 
# saves on packet overhead. Maybe add telemetry for bandwidth data.