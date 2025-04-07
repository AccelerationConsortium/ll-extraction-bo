Adjust the following bare bones template script to take the following input parameters:

aqueous solvent identity (composition)
organic solvent identity (composition)
stirring speed [100 - 500] # rpm
stirring time [10 - 120] # seconds
temperature during extraction [4 - 40] # deg C
aq and organic should sum to 1.0. I.e., treat as a composition constraint.

We have five objectives, with the objective thresholds given.

R = recovery of the target analyte (measured as a percentage of the total amount recovered). less than 0.5 is a no-go
P = purity of the recovered analyte in the desired phase (measured as HPLC area percent (LCAP))., less than 90% is a no-go
S = efficiency of phase separation (measured by clarity or turbidity of phases).
E = emulsions or rag layers (penalty based on percentage of 2D image area dominated by emulsion assessed by computer vision).
T = total time required to achieve separation (penalized for longer processing times) should be less than 1200 seconds
