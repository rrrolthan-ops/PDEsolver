"""Heat equation marker module.

The actual solver logic for `u_t = α² u_xx` lives in
`solver.methods.separation_of_variables`. This file exists so the
package layout matches the documented architecture; future generalisations
(non-homogeneous heat, multi-D heat, heat in cylindrical coordinates)
will land here as standalone helpers shared across methods.
"""
