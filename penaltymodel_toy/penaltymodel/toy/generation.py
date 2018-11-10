from itertools import product
import numpy as np
import penaltymodel.core as pm
from scipy.optimize import linprog

#TODO: would be nice to have a file for default linear energy ranges (currently, [-2, 2]); quad energy [-1, 1]

def generate_bqm(graph, table, decision_variables,
                 linear_energy_ranges=None, quadratic_energy_ranges=None,
                 precision=7, max_decision=8, max_variables=10,
                 return_auxiliary=False):

    # TODO: better way of saying that toy does not deal with auxiliary
    # Check for auxiliary variables in the graph
    if len(graph) != len(decision_variables):
        return

    # TODO: Note: table is a dict when you're using QUBOs in the problem
    # Set variable names for lengths
    m_linear = len(decision_variables)      # Number of linear biases
    m_quadratic = len(graph.edges)          # Number of quadratic biases
    n_valid = len(table)                    # Number of valid spin combinations
    n_invalid = 2**(m_linear) - n_valid     # Number of invalid spin combinations

    # Determining valid and invalid states
    all_linear = set(product([-1, 1], repeat=m_linear))
    valid_linear = set(table.keys())
    invalid_linear = all_linear - valid_linear

    # Valid states
    valid_states = np.empty((n_valid, m_linear + m_quadratic))
    valid_states[:, m_linear] = np.asarray(list(valid_linear))      # Populate linear spins

    for j, (u, v) in enumerate(graph.edges):
        u_ind = decision_variables.index(u)     #TODO: smarter way of grabbing relevant column
        v_ind = decision_variables.index(v)

        #TODO: math is so simple, may not need to multiply; could do pattern matching
        valid_states[:, j + m_linear] = np.multiply(valid_states[:, u_ind], valid_states[:, v_ind])

    valid_states[:, -2] = 1     # Column associated with offset
    valid_states[:, -1] = 0     # Column associated with gap

    # Invalid states


    # Bounds
    #TODO: assumes order of edges does not change; NEED TO VERIFY
    #TODO: aux probably needs energy range too; NO it doesn't because this won't deal with auxiliary
    bounds = []
    for node in decision_variables:
        try:
            bounds.append(linear_energy_ranges[node])
        except KeyError:
            bounds.append((-2, 2))

    for edge in graph.edges():
        try:
            bounds.append(quadratic_energy_ranges[edge])
        except KeyError:
            bounds.append((-1, 1))

    bqm, gap, _, success, _, _, _ = linprog(1, bounds=bounds)

    print("Inside toy generate bqm!")