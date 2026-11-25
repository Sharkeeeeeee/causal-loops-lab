"""SPDX-License-Identifier: MIT. What each loop rule predicts for the invitation, in a toy model.

Assume a time machine whose past mouth reaches the present. Model:

- the arriving message m is one of N values, or empty (index N: nothing arrives);
- r: the randomness of mining after the arrival (R values, uniform);
- g(m, r): the hash of block h, a random function of m and r (the message is published, so
  it may change later blocks: the hash depends on what arrived, including "nothing");
- the future sender sends back g(m, r) with probability s (willingness), else nothing;
- consistency: what is sent back equals what arrived.

Two questions for each rule: does a message arrive, and if one does, is it correct (equal to
the hash later mined)?

- no loop: nothing arrives from the future; any "reply" is a hoax, correct by chance 1/N;
- P-CTC: postselect on consistency, loop input uniform over the N + 1 values;
- D-CTC: the loop state is the Cesàro fixed point of the stochastic map, uncorrelated with r;
- PPS, r unrecorded at the arrival (the real situation: mining happens later): one world,
  P-CTC inside it;
- PPS, r recorded before the arrival (counterfactual): one world per r, P-CTC inside each,
  the D-CTC fallback in a world without any consistent history.
"""
import numpy as np


def model(n=64, r=200, seed=0):
    """g[m, r] for m = 0..n (row n: nothing arrived), values in 0..n-1."""
    return np.random.default_rng(seed).integers(n, size=(n + 1, r))


def _correct(g):
    n = g.shape[0] - 1
    return g[:n] == np.arange(n)[:, None]          # [m, r]: the message equals the later hash


def no_loop(g):
    return {'arrives': 0.0, 'correct_if_arrives': float(np.mean(_correct(g)))}


def _p_ctc_world(fixed_points, s):
    """P(arrives) inside one world from the number of consistent messages (weights s, 1 - s)."""
    w_send, w_none = s * fixed_points, (1 - s)
    total = w_send + w_none
    return None if total == 0 else w_send / total


def p_ctc(g, s=1.0):
    f = float(np.mean(np.sum(_correct(g), axis=0)))        # mean number of fixed points over r
    a = _p_ctc_world(f, s)
    return None if a is None else {'arrives': a, 'correct_if_arrives': 1.0}


def transition(g, s):
    n = g.shape[0] - 1
    t = np.zeros((n + 1, n + 1))
    for m in range(n + 1):
        t[:n, m] = s * np.bincount(g[m], minlength=n) / g.shape[1]
        t[n, m] = 1 - s
    return t


def cesaro(t, steps=4000):
    v = np.full(t.shape[0], 1.0 / t.shape[0])
    avg = np.zeros_like(v)
    for _ in range(steps):
        avg += v
        v = t @ v
    return avg / steps


def d_ctc(g, s=1.0):
    n = g.shape[0] - 1
    tau = cesaro(transition(g, s))
    arrives = 1 - tau[n]
    hit = float(tau[:n] @ np.mean(_correct(g), axis=1))
    return {'arrives': float(arrives), 'correct_if_arrives': hit / arrives if arrives > 0 else None}


def pps(g, s=1.0, mining_recorded=False):
    if not mining_recorded:
        return p_ctc(g, s)
    n = g.shape[0] - 1
    c = _correct(g)
    arrives = correct = 0.0
    for r in range(g.shape[1]):
        a = _p_ctc_world(float(np.sum(c[:, r])), s)
        if a is not None:                     # consistent histories exist: every arrival is correct
            arrives += a
            correct += a
        else:                                 # s = 1 and no fixed point: D-CTC fallback, deterministic map
            t = np.zeros((n + 1, n + 1))
            t[g[:, r], np.arange(n + 1)] = 1.0
            tau = cesaro(t, 2000)
            arrives += 1 - tau[n]
            correct += float(tau[:n] @ c[:, r])
    k = g.shape[1]
    return {'arrives': arrives / k, 'correct_if_arrives': correct / arrives if arrives > 0 else None}
