import sympy as sp
import numpy as np
import matplotlib.pyplot as plt

def solve_volume_problem(f_top, f_bottom, axis_of_rotation, limit_a, limit_b):
    """
    Logic Engine to solve Volume of Revolution problems (Disk vs Washer).
    """
    x = sp.Symbol('x')
    
    # 1. Classification Logic (Disk vs Washer)
    # If the distance between functions is just one radius and touches the axis = Disk
    # If there is an inner and outer radius = Washer
    
    R_outer = f_top - axis_of_rotation
    r_inner = f_bottom - axis_of_rotation
    
    if r_inner == 0:
        method = "Disk Method"
        integrand = sp.pi * (R_outer**2)
    else:
        method = "Washer Method"
        integrand = sp.pi * (R_outer**2 - r_inner**2)
    
    # 2. Integration Step (The Math)
    volume_integral = sp.integrate(integrand, (x, limit_a, limit_b))
    step_by_step_formula = sp.simplify(integrand)
    
    # 3. Outputting Results
    print(f"--- [SOLUTION STEPS] ---")
    print(f"Step 1: Identified Method -> {method}")
    print(f"Step 2: Outer Radius (R) = {R_outer}")
    if method == "Washer Method":
        print(f"Step 3: Inner Radius
