import argparse
import socket
import struct
import time
import random
import numpy as np

# Matrix generation function
def generate_matrices(rows_A, cols_A, rows_B, cols_B):
    if cols_A != rows_B:
        raise ValueError("Number of columns in A must be equal to the number of rows in B.")
    # Generate random integer matrices A and B
    matrix_A = np.random.randint(1, 10, (rows_A, cols_A))
    matrix_B = np.random.randint(1, 10, (rows_B, cols_B))
    # Return matrix_A and matrix_B in a tuple of matrices
    return matrix_A, matrix_B

def divide_matrices(matrices_tuple, total_clients):

    # Needs to split the left matrix and update the 
    # tuple so no data is lost. Also needs to 
    # transpose the right matrix to rows for more
    # efficient stride(python uses row major order).
    # The entire right matrix should be sent to each client
    # to avoid high packet overhead. 

    # Put all of matrix A in one array, then
    # all of matrix B in another.
    A, B = matrices_tuple
    A_blocks = np.array_split(A, total_clients)
    return A_blocks, B

def create_packet(split_matrices,):
    pass

# Clients are going to need to talk to eachother to send 
# data from the split matrices back to the other clients that 
# haven't multiplied the other ones together yet. 

# Add time and memory data to see if splitting the right matrix 
# saves on packet overhead. Maybe add telemetry for bandwidth data.

def main():
    # Containers and their port numbers
    clients = [("client1", 8080), ("client2", 8081), ("client3", 8082), ("client4", 8083)]

    matrices = generate_matrices(5, 5, 5, 5) # Generates two random n * n matrices.
    A, B = matrices
    print("Matrix A:")
    print(A)
    print("Matrix B:")
    print(B)
    Ablocks, Bblock = divide_matrices(matrices, len(clients)) # Splits the left matrix into blocks for each client.

if __name__ == "__main__":
    main()