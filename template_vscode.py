import os
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator

# 1) Define the QASM file path
qasm_path = "25.qasm"

# Check if file exists in the current working directory
if not os.path.exists(qasm_path):
    print(f"Error: The file '{qasm_path}' was not found.")
    print("Ensure the file is in the same folder you are running this script from.")
else:
    print(f"Found {qasm_path}! Loading circuit...")

    # 2) Load QASM circuit
    qc = QuantumCircuit.from_qasm_file(qasm_path)

    # 3) Ensure we have measurements for shot-based sampling
    try:
        qc.measure_all()
    except Exception as e:
        print(
            f"Note: Could not apply measure_all() (likely already measured). Details: {e}")

    # 4) Configure MPS simulator
    shots = 5000
    bond_dim = 64  # try 32, 64, 128, ... (higher is usually more accurate)

    sim = AerSimulator(
        method="matrix_product_state",
        matrix_product_state_max_bond_dimension=bond_dim,
    )

    # 5) Transpile + run
    # We provide a strict set of standard universal gates to bypass limits/errors.
    standard_gates = ['id', 'rz', 'sx', 'x', 'cx']
    print("Transpiling circuit...")
    qc_t = transpile(qc, basis_gates=standard_gates)

    print("Transpilation complete. Running simulator...")
    result = sim.run(qc_t, shots=shots).result()
    counts = result.get_counts()

    # 6) Most frequent bitstring as peak estimate
    if counts:
        peak_bitstring = max(counts, key=counts.get)
        peak_count = counts[peak_bitstring]
        peak_prob_est = peak_count / shots

        print("\n--- Results ---")
        print("Estimated peak bitstring:", peak_bitstring)
        print("Estimated peak probability:", peak_prob_est)
    else:
        print("No counts returned. Ensure your circuit has measurements.")
