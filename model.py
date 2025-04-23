# -*- coding: utf-8 -*-
"""
Created on Tue Apr 22 14:16:55 2025

@author: alann
"""

from pulp import LpProblem, LpMinimize, LpVariable, LpInteger, lpSum, allcombinations

#%%

def build_model(trucks, depots, customers, products, prod_availability,
                prod_volume, truck_cap, demand, cost_per_mile, dist_matrix,
                truck_base, big_m):
    """
    trucks: A list of distinct truck labels (e.g., ['T1', 'T2', ...])
    depots: A list of distinct depot labels (e.g., ['D1', 'D2', ...])
    customers: A list of distinct customer labels (e.g., ['C1', 'C2', ...])
    products: A list of distinct product labels (e.g., ['P1', 'P2', ...])
    prod_availability: Dict {<depot>: {<product>: <units available>}}
    prod_volume: Dict {<product>: <volume>}
    truck_cap: Dict {<truck>: <volume capacity>}
    demand: Dict {<customer>: {<product>: <units ordered>}}
    cost_per_mile: Dict {<truck>: <cost per mile>}
    dist_matrix: Dict {(<loc1>, <loc2>): <distance>}
    truck_base: Dict {<truck>: <depot>}
    big_m: An arbitrarily large constant
    """
    # Sets
    H = trucks           # Trucks
    I = depots           # Depots
    J = customers        # Customers
    K = products         # Products
    L = I + J            # All locations
    
    # Parameters
    a = prod_availability
    e = prod_volume
    E = truck_cap
    r = demand
    c = cost_per_mile
    d = dist_matrix
    b = {h: {i: 1 if truck_base[h] == i else 0 for i in I} for h in H}

    # VARIABLES
    # u[h][j][k] = Units of product k delivered to customer j on truck h
    # lowerbound = 0, upper bound = None
    u = LpVariable.dicts("u", (H, J, K), 0, None, LpInteger)
    
    # x[h][i][j] == 1 if truck h travels directly from location i to j, 0 otherwise
    x = LpVariable.dicts("x", (H, L, L),  0, 1, LpInteger)
    

    
    
    model = LpProblem("MultiDepot_VRP", LpMinimize)
    
    
    # OBJECTIVE FUNCTION
    # Minimize the sum of all travel costs incurred.
    model += (lpSum([c[h] * d[i,j] * x[h][i][j] for h in H for i in L for j in L]), 
                   'Total_Cost')
    
    
    # CONSTRAINTS
    for h in H:
        # Ensure no truck capacity exceeded
        model += (lpSum([e[k] * u[h][j][k] for j in J for k in K]) <= E[h])
        
        for i in L:
            # For each loc, truck in -> truck out
            model += (lpSum([x[h][j][i] for j in L]) == lpSum([x[h][i][j] for j in L]))
            
        # Ensure no truck departs from a depot that is not its base
        for i in I:
            model += (lpSum([x[h][i][j] for j in L]) <= b[h][i])
        
        # Ensure no subset of customers contains a circuit or subtour elimination
        for W in allcombinations(J, len(J)):
            model += (lpSum([x[h][i][j] for i in W for j in W]) <= len(W) - 1)
       
        
    
    
    for k in K:
        for i in I:
            # No depot ships more of a product than it has
            model += (lpSum([b[h][i] * u[h][j][k] for h in H for j in J]) <= a[i][k])
        
        for j in J:
            # Each customer gets the products they ordered
            model += (lpSum(u[h][j][k] for h in H) == r[j][k])
            
            for h in H:
                # No truck carries products for a customer unless it visits the customer.
                model += (u[h][j][k] <= big_m * lpSum(x[h][i][j] for i in L))
    
    
    return model

#%%
















