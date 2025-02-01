# whoistheking
ranking calculation methods for our efootball league

## Bradley-Terry Model
### Overview

The Bradley–Terry model is a probabilistic model used to estimate the "ability" or "strength" parameters of competitors (teams or individuals) based on paired comparisons or game outcomes. In this model, each competitor \(i\) is assigned a positive parameter \(\beta_i\), and the probability that competitor \(i\) beats competitor \(j\) is given by:

\[
P(i \text{ beats } j) = \frac{\beta_i}{\beta_i + \beta_j}
\]

This formula implies that if \(\beta_i > \beta_j\), then competitor \(i\) has a greater than 50% chance of winning against competitor \(j\).

