"""SPDX-License-Identifier: MIT. Isolated pure states: what microscopic loops under past-preserving
selection would do to interference, and how existing Born-rule tests constrain it.

Model (a hypothesis, not established physics):
  With probability eps, a particle's path couples to a microscopic loop. The loop qubit picks up a
  phase phi_j when the particle takes path j:  U = sum_j |j><j| x diag(1, e^{i phi_j}).
  Then C = Tr_loop U = sum_j (1 + e^{i phi_j}) |j><j|, i.e. each path amplitude is multiplied by
  c_j = (1 + e^{i phi_j}) / 2.
  For an isolated pure state, past-preserving selection equals P-CTC: psi -> C psi / ||C psi||.
  Which slits are open, and whether the particle got through them, is a recorded fact (blocked
  particles are absorbed), so that probability is kept; the renormalisation acts inside it.

Standard quantum mechanics is eps = 0, or phi_j all equal (then C is proportional to the identity).

Sorkin parameter, as in Kauten et al., New J. Phys. 19, 033017 (2017):
  eps_3   = p_ABC - p_AB - p_AC - p_BC + p_A + p_B + p_C          (p_0 = 0 here)
  delta_3 = |I_AB| + |I_AC| + |I_BC|,  I_kl = p_kl - p_k - p_l
  kappa_3 = eps_3 / delta_3, evaluated at the fully constructive point.
"""
from itertools import combinations

import numpy as np


def c_factors(phis):
    return (1 + np.exp(1j * np.asarray(phis, float))) / 2


def intensity(open_paths, amps, phases, c, eps):
    """Detection probability density with the given paths open, at one screen point."""
    if not open_paths:
        return 0.0
    a = np.array([amps[j] * np.exp(1j * phases[j]) for j in open_paths])
    cc = np.array([c[j] for j in open_paths])
    qm = abs(a.sum()) ** 2
    through = float(np.sum(abs(a) ** 2))
    loop = through * abs((cc * a).sum()) ** 2 / float(np.sum(abs(cc * a) ** 2))
    return (1 - eps) * qm + eps * loop


def sorkin_kappa(eps, phis, amps=(1, 1, 1), phases=(0, 0, 0)):
    c = c_factors(phis)
    p = {s: intensity(s, amps, phases, c, eps) for r in range(4) for s in combinations(range(3), r)}
    e3 = (p[(0, 1, 2)] - p[(0, 1)] - p[(0, 2)] - p[(1, 2)] + p[(0,)] + p[(1,)] + p[(2,)])
    d3 = sum(abs(p[(k, l)] - p[(k,)] - p[(l,)]) for k, l in combinations(range(3), 2))
    return e3 / d3


def max_eps(bound, phis, **kw):
    """Largest eps in [0, 1] with |kappa_3| <= bound (kappa grows monotonically with eps here)."""
    if abs(sorkin_kappa(1.0, phis, **kw)) <= bound:
        return 1.0
    lo, hi = 0.0, 1.0
    for _ in range(80):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if abs(sorkin_kappa(mid, phis, **kw)) <= bound else (lo, mid)
    return lo


def two_path_shift(p, phi, eps):
    """Change in P(path 1) for a pure superposition with |beta|^2 = p, path 1 coupled with phase phi."""
    w = abs(c_factors([phi])[0]) ** 2
    return eps * (p * w / (1 - p + p * w) - p)


# Published bounds on |kappa_3| used for comparison (2 standard deviations where an uncertainty is given).
BOUNDS = [
    dict(name='Kauten et al. 2017, laser light', value=2 * 3.1e-5,
         ref='New J. Phys. 19, 033017; arXiv:1508.03253 (kappa_3 = 0.0 +/- 3.1e-5)'),
    dict(name='Kauten et al. 2017, heralded single photons', value=2 * 1.6e-3,
         ref='New J. Phys. 19, 033017; arXiv:1508.03253 (kappa_3 = 0.0 +/- 1.6e-3)'),
    dict(name='Jin et al. 2017, single NV spin; Park et al. 2012, NMR', value=1e-3,
         ref='PRA 95, 012107 (arXiv:1612.08563); NJP 14, 113025 (arXiv:1207.2321): order 1e-3'),
    dict(name='Sinha et al. 2010, photons', value=1e-2,
         ref='Science 329, 418; arXiv:1007.4193 (below 1e-2)'),
]
