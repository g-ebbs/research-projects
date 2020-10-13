### IMPORTS ###

# Importing standard Qiskit libraries and configuring account
from qiskit import QuantumCircuit, execute, Aer, IBMQ
from qiskit.compiler import transpile, assemble
from qiskit.tools.jupyter import *
from qiskit.visualization import *
from qiskit.providers.ibmq import least_busy
from qiskit.quantum_info import Statevector
import numpy as np
pi = np.pi
get_ipython().run_line_magic('matplotlib', 'inline')

# Loading your IBM Q account(s)
provider = IBMQ.load_account()

### BASIC INPUT INFORMATION ###

## Tagged State ##
# Enter a bit string for the tagged state
# Currentl support for strings of len 3-5 bits 
wstate = "010"

## Number of Qubits ##
# Current support for n = 3,4,5
n = 3

## Number of Iterations ##
R = 2

## Set up Quantum Circuit ##
gc = QuantumCircuit(n)

### INITIAL STATE OF THE CIRCUIT ###

def initial_s(qc, n):
    for q in range(n):
        qc.h(q)
    return qc

### GROVER ORACLE ###
def Uf(n, wstate):
    
    ## Quantum Circuit for Application of Uf ##
    qc = QuantumCircuit(n)
    
    ## 1st Set of X Gates for Tagged State ##
    for i in range(len(wstate)):  ## add error for incorect bit strings?
        if wstate[i] == '0':
            qc.x(i) 
            
    ## Oracle for 3-Qubit Case ##
    if n == 3: 
        # Control z-gate
        qc.cu1(pi/2, 0, 2)
        qc.cx(0, 1)
        qc.cu1(-pi/2, 1, 2)
        qc.cx(0, 1)
        qc.cu1(pi/2, 1, 2)
        
    ## Oracle for 4-Qubit Case ##
    elif n == 4: 
        # Control z-gate
        qc.cu1(pi/4, 0, 3)
        qc.cx(0, 1)
        qc.cu1(-pi/4, 1, 3)
        qc.cx(0, 1)
        qc.cu1(pi/4, 1, 3)
        qc.cx(1,2)
        qc.cu1(-pi/4, 2, 3)
        qc.cx(0, 2)
        qc.cu1(pi/4, 2, 3)
        qc.cx(1, 2)
        qc.cu1(-pi/4, 2, 3)
        qc.cx(0, 2)
        qc.cu1(pi/4, 2, 3)

    ## Oracle for 5-Qubit Case ##
    elif n == 5:
        # Control z-gate
        qc.cu1(pi/8, 0, 4)
        qc.cx(0, 1)
        qc.cu1(-pi/8, 1, 4)
        qc.cx(0, 1)
        qc.cu1(pi/8, 1, 4)
        qc.cx(1, 2)
        qc.cu1(-pi/8, 2, 4)
        qc.cx(0, 2)
        qc.cu1(pi/8, 2, 4)
        qc.cx(1, 2)
        qc.cu1(-pi/8, 2, 4)
        qc.cx(0, 2)
        qc.cu1(pi/8, 2, 4)
        qc.cx(0, 3)
        qc.cu1(-pi/8, 3, 4)
        qc.cx(2, 3)
        qc.cu1(pi/8, 3, 4)
        qc.cx(1, 3)
        qc.cu1(-pi/8, 3, 4)
        qc.cx(2, 3)
        qc.cu1(pi/8, 3, 4)
        qc.cx(0, 3)
        qc.cu1(-pi/8, 3, 4)
        qc.cx(2, 3)
        qc.cu1(pi/8, 3, 4)
        qc.cx(1, 3)
        qc.cu1(-pi/8, 3, 4)
        qc.cx(2, 3)
        qc.cu1(pi/8, 3, 4)
    # Else (add error message)
        
    ## 2nd Set of X Gates for Tagged State ##
    for i in range(len(wstate)):  ## add error for incorect bit strings?
        if wstate[i] == '0':
            qc.x(i) 

    ## Return gate and proper label ##
    Uf = qc.to_gate()
    Uf.name = "$U_f$"
    return Uf

### GROVER DIFFUSION ###
def Us(n):
    ## Quantum Circuit For Application of Us ##
    qc = QuantumCircuit(n)
    
    # First set of Hadamard Gates 
    for i in range(n):
        qc.h(i)
    # First set of X Gates 
    for i in range(n):
        qc.x(i)
    # Multi-controlled-Z gate
    qc.h(n-1)
    qc.mct(list(range(n-1)), n-1)  # multi-controlled-toffoli
    qc.h(n-1)
    # Second set of X Gates 
    for i in range(n):
        qc.x(i)
    # Second set of Hadamard Gates 
    for i in range(n):
        qc.h(i)
        
    # Return gate and proper label
    Us = qc.to_gate()
    Us.name = "$U_s$"
    return Us   

### CREATE THE GROVER'S ALGORITHM CIRCUIT ###

## Initialize the state s ##
gc = initial_s(gc, n)

## 3-Quit Case ##
if n == 3:
    # Repeat for Specified Number of Iterations
    for i in range(R):
        for i in range(n):
            gc.barrier(i)
        gc.append(Uf(n, wstate), [0,1,2])
        gc.append(Us(n), [0,1,2])
        i = i + 1

## 4-Qubit Case ##
elif n == 4:
    # Repeat for Specified Number of Iterations
    for i in range(R):
        for i in range(n):
            gc.barrier(i)
        gc.append(Uf(n, wstate), [0,1,2,3])
        gc.append(Us(n), [0,1,2,3])
        i = i + 1
    
## 5-Qubit Case ##
elif n == 5:
    # Repeat for Specified Number of Iterations
     for i in range(R):
        for i in range(n):
            gc.barrier(i)
        gc.append(Uf(n, wstate), [0,1,2,3,4])
        gc.append(Us(n), [0,1,2,3,4])
        i = i + 1
# Else (add error message)

## Plot the Circuit on the Q-Sphere ##
statevector = Statevector.from_instruction(gc)
plot_state_qsphere(statevector)

## Measure Each Qubit ##
gc.measure_all()
## Draw the Circuit Representation ##
gc.draw()

#### Add feature for drawing details of custom gates? ###
## Draw Examples of Each Defined Gate For Reference ##
#oracle_qc = QuantumCircuit(n)
#diffuser_qc = QuantumCircuit(n)
#oracle_qc.Uf ...

### SIMULATE THE GROVER"S ALGORITHM CIRCUIT ###

## Set up Simulator and Record Results ##
simulator = Aer.get_backend('qasm_simulator')
shots = 1024
results = execute(gc, backend = simulator, shots=shots).result()
counts = results.get_counts()

## Plot the Counts from the Simulated Results ##
plot_histogram(counts)
