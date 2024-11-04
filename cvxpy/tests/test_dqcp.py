"""
Copyright, the CVXPY authors

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import numpy as np
import pytest

import cvxpy as cp
import cvxpy.settings as s
from cvxpy.reductions.dqcp2dcp.dqcp2dcp import Dqcp2Dcp
from cvxpy.reductions.solvers import bisection
from cvxpy.tests import base_test

SOLVER = cp.CLARABEL


class TestDqcp(base_test.BaseTest):
    def test_basic_with_interval(self) -> None:
        x = cp.Variable()
        expr = cp.ceil(x)

        self.assertTrue(expr.is_dqcp())
        self.assertTrue(expr.is_quasiconvex())
        self.assertTrue(expr.is_quasiconcave())
        self.assertFalse(expr.is_convex())
        self.assertFalse(expr.is_concave())
        self.assertFalse(expr.is_dcp())
        self.assertFalse(expr.is_dgp())

        problem = cp.Problem(cp.Minimize(expr), [x >= 12, x <= 17])
        self.assertTrue(problem.is_dqcp())
        self.assertFalse(problem.is_dcp())
        self.assertFalse(problem.is_dgp())

        red = Dqcp2Dcp(problem)
        reduced = red.reduce()
        self.assertTrue(reduced.is_dcp())
        self.assertEqual(len(reduced.parameters()), 1)
        soln = bisection.bisect(reduced, low=12, high=17, solver=cp.SCS)
        self.assertAlmostEqual(soln.opt_val, 12.0, places=3)

        problem.unpack(soln)
        self.assertEqual(soln.opt_val, problem.value)
        self.assertAlmostEqual(x.value, 12.0, places=3)

    def test_basic_without_interval(self) -> None:
        x = cp.Variable()
        expr = cp.ceil(x)

        self.assertTrue(expr.is_dqcp())
        self.assertTrue(expr.is_quasiconvex())
        self.assertTrue(expr.is_quasiconcave())
        self.assertFalse(expr.is_convex())
        self.assertFalse(expr.is_concave())
        self.assertFalse(expr.is_dcp())
        self.assertFalse(expr.is_dgp())

        problem = cp.Problem(cp.Minimize(expr), [x >= 12, x <= 17])
        self.assertTrue(problem.is_dqcp())
        self.assertFalse(problem.is_dcp())
        self.assertFalse(problem.is_dgp())

        red = Dqcp2Dcp(problem)
        reduced = red.reduce()
        self.assertTrue(reduced.is_dcp())
        self.assertEqual(len(reduced.parameters()), 1)
        soln = bisection.bisect(reduced, solver=cp.SCS)
        self.assertAlmostEqual(soln.opt_val, 12.0, places=3)

        problem.unpack(soln)
        self.assertEqual(soln.opt_val, problem.value)
        self.assertAlmostEqual(x.value, 12.0, places=3)

    def test_basic_solve(self) -> None:
        x = cp.Variable()
        expr = cp.ceil(x)

        self.assertTrue(expr.is_dqcp())
        self.assertTrue(expr.is_quasiconvex())
        self.assertTrue(expr.is_quasiconcave())
        self.assertFalse(expr.is_convex())
        self.assertFalse(expr.is_concave())
        self.assertFalse(expr.is_dcp())
        self.assertFalse(expr.is_dgp())

        problem = cp.Problem(cp.Minimize(expr), [x >= 12, x <= 17])
        self.assertTrue(problem.is_dqcp())
        self.assertFalse(problem.is_dcp())
        self.assertFalse(problem.is_dgp())
        problem.solve(SOLVER, qcp=True, low=12, high=17)
        self.assertAlmostEqual(problem.value, 12.0, places=3)
        self.assertAlmostEqual(x.value, 12.0, places=3)

        problem._clear_solution()
        problem.solve(SOLVER, qcp=True)
        self.assertAlmostEqual(problem.value, 12.0, places=3)
        self.assertAlmostEqual(x.value, 12.0, places=3)

        problem._clear_solution()
        problem.solve(SOLVER, qcp=True, high=17)
        self.assertAlmostEqual(problem.value, 12.0, places=3)
        self.assertAlmostEqual(x.value, 12.0, places=3)

        problem._clear_solution()
        problem.solve(SOLVER, qcp=True, low=12)
        self.assertAlmostEqual(problem.value, 12.0, places=3)
        self.assertAlmostEqual(x.value, 12.0, places=3)

        problem._clear_solution()
        problem.solve(SOLVER, qcp=True, low=0, high=100)
        self.assertAlmostEqual(problem.value, 12.0, places=3)
        self.assertAlmostEqual(x.value, 12.0, places=3)

    def test_basic_maximization_with_interval(self) -> None:
        x = cp.Variable()
        expr = cp.ceil(x)

        self.assertTrue(expr.is_dqcp())
        self.assertTrue(expr.is_quasiconvex())
        self.assertTrue(expr.is_quasiconcave())
        self.assertFalse(expr.is_convex())
        self.assertFalse(expr.is_concave())
        self.assertFalse(expr.is_dcp())
        self.assertFalse(expr.is_dgp())

        problem = cp.Problem(cp.Maximize(expr), [x >= 12, x <= 17])
        self.assertTrue(problem.is_dqcp())
        self.assertFalse(problem.is_dcp())
        self.assertFalse(problem.is_dgp())

        problem.solve(SOLVER, qcp=True)
        self.assertAlmostEqual(x.value, 17.0, places=3)

    def test_basic_maximum(self) -> None:
        x, y = cp.Variable(2)
        expr = cp.maximum(cp.ceil(x), cp.ceil(y))

        problem = cp.Problem(cp.Minimize(expr), [x >= 12, x <= 17, y >= 17.4])
        self.assertTrue(problem.is_dqcp())
        problem.solve(SOLVER, qcp=True)
        self.assertEqual(problem.objective.value, 18.0)
        self.assertLess(x.value, 17.1)
        self.assertGreater(x.value, 11.9)
        self.assertGreater(y.value, 17.3)

    def test_basic_minimum(self) -> None:
        x, y = cp.Variable(2)
        expr = cp.minimum(cp.ceil(x), cp.ceil(y))

        problem = cp.Problem(cp.Maximize(expr), [x >= 11.9, x <= 15.8, y >= 17.4])
        self.assertTrue(problem.is_dqcp())
        problem.solve(SOLVER, qcp=True)
        self.assertEqual(problem.objective.value, 16.0)
        self.assertLess(x.value, 16.0)
        self.assertGreater(x.value, 14.9)
        self.assertGreater(y.value, 17.3)

    def test_basic_composition(self) -> None:
        x, y = cp.Variable(2)
        expr = cp.maximum(cp.ceil(cp.ceil(x)), cp.ceil(cp.ceil(y)))

        problem = cp.Problem(cp.Minimize(expr), [x >= 12, x <= 17, y >= 17.4])
        self.assertTrue(problem.is_dqcp())
        problem.solve(SOLVER, qcp=True)
        self.assertEqual(problem.objective.value, 18.0)
        self.assertLess(x.value, 17.1)
        self.assertGreater(x.value, 11.9)
        self.assertGreater(y.value, 17.3)

        # This problem should have the same solution.
        expr = cp.maximum(cp.floor(cp.ceil(x)), cp.floor(cp.ceil(y)))
        problem = cp.Problem(cp.Minimize(expr), [x >= 12, x <= 17, y >= 17.4])
        self.assertTrue(problem.is_dqcp())
        problem.solve(SOLVER, qcp=True)
        self.assertEqual(problem.objective.value, 18.0)
        self.assertLess(x.value, 17.1)
        self.assertGreater(x.value, 11.9)
        self.assertGreater(y.value, 17.3)

    def test_basic_floor(self) -> None:
        x = cp.Variable()
        expr = cp.floor(x)

        self.assertTrue(expr.is_dqcp())
        self.assertTrue(expr.is_quasiconvex())
        self.assertTrue(expr.is_quasiconcave())
        self.assertFalse(expr.is_convex())
        self.assertFalse(expr.is_concave())
        self.assertFalse(expr.is_dcp())
        self.assertFalse(expr.is_dgp())

        problem = cp.Problem(cp.Minimize(expr), [x >= 11.8, x <= 17])
        self.assertTrue(problem.is_dqcp())
        self.assertFalse(problem.is_dcp())
        self.assertFalse(problem.is_dgp())

        problem.solve(SOLVER, qcp=True)
        self.assertEqual(problem.objective.value, 11.0)
        self.assertGreater(x.value, 11.7)

    def test_basic_multiply_nonneg(self) -> None:
        x, y = cp.Variable(2, nonneg=True)
        expr = x * y
        self.assertTrue(expr.is_dqcp())
        self.assertTrue(expr.is_quasiconcave())
        self.assertFalse(expr.is_quasiconvex())

        self.assertFalse(expr.is_dcp())

        problem = cp.Problem(cp.Maximize(expr), [x <= 12, y <= 6])
        self.assertTrue(problem.is_dqcp())
        self.assertFalse(problem.is_dcp())
        self.assertFalse(problem.is_dgp())

        problem.solve(cp.SCS, qcp=True)
        self.assertAlmostEqual(problem.objective.value, 72, places=1)
        self.assertAlmostEqual(x.value, 12, places=1)
        self.assertAlmostEqual(y.value, 6, places=1)

    def test_basic_multiply_nonpos(self) -> None:
        x, y = cp.Variable(2, nonpos=True)
        expr = x * y
        self.assertTrue(expr.is_dqcp())
        self.assertTrue(expr.is_quasiconcave())
        self.assertFalse(expr.is_quasiconvex())

        self.assertFalse(expr.is_dcp())

        problem = cp.Problem(cp.Maximize(expr), [x >= -12, y >= -6])
        self.assertTrue(problem.is_dqcp())
        self.assertFalse(problem.is_dcp())
        self.assertFalse(problem.is_dgp())

        problem.solve(cp.SCS, qcp=True)
        self.assertAlmostEqual(problem.objective.value, 72, places=1)
        self.assertAlmostEqual(x.value, -12, places=1)
        self.assertAlmostEqual(y.value, -6, places=1)

    def test_basic_multiply_qcvx(self) -> None:
        x = cp.Variable(nonneg=True)
        y = cp.Variable(nonpos=True)
        expr = x * y
        self.assertTrue(expr.is_dqcp())
        self.assertTrue(expr.is_quasiconvex())
        self.assertFalse(expr.is_quasiconcave())

        self.assertFalse(expr.is_dcp())

        problem = cp.Problem(cp.Minimize(expr), [x <= 7, y >= -6])
        self.assertTrue(problem.is_dqcp())
        self.assertFalse(problem.is_dcp())
        self.assertFalse(problem.is_dgp())

        problem.solve(cp.SCS, qcp=True)
        self.assertAlmostEqual(problem.objective.value, -42, places=1)
        self.assertAlmostEqual(x.value, 7, places=1)
        self.assertAlmostEqual(y.value, -6, places=1)

        x = cp.Variable(nonneg=True)
        y = cp.Variable(nonpos=True)
        expr = y * x
        self.assertTrue(expr.is_dqcp())
        self.assertTrue(expr.is_quasiconvex())
        self.assertFalse(expr.is_quasiconcave())

        self.assertFalse(expr.is_dcp())

        problem = cp.Problem(cp.Minimize(expr), [x <= 7, y >= -6])
        self.assertTrue(problem.is_dqcp())
        self.assertFalse(problem.is_dcp())
        self.assertFalse(problem.is_dgp())

        problem.solve(cp.SCS, qcp=True)
        self.assertAlmostEqual(problem.objective.value, -42, places=1)
        self.assertAlmostEqual(x.value, 7, places=1)
        self.assertAlmostEqual(y.value, -6, places=1)

    def test_concave_multiply(self) -> None:
        x, y = cp.Variable(2, nonneg=True)
        expr = cp.sqrt(x) * cp.sqrt(y)
        self.assertTrue(expr.is_dqcp())
        self.assertTrue(expr.is_quasiconcave())
        self.assertFalse(expr.is_quasiconvex())

        problem = cp.Problem(cp.Maximize(expr), [x <= 4, y <= 9])
        problem.solve(cp.SCS, qcp=True)
        self.assertAlmostEqual(problem.objective.value, 6, places=1)
        self.assertAlmostEqual(x.value, 4, places=1)
        self.assertAlmostEqual(y.value, 9, places=1)

        x, y = cp.Variable(2, nonneg=True)
        expr = (cp.sqrt(x) + 2.0) * (cp.sqrt(y) + 4.0)
        self.assertTrue(expr.is_dqcp())
        self.assertTrue(expr.is_quasiconcave())
        self.assertFalse(expr.is_quasiconvex())

        problem = cp.Problem(cp.Maximize(expr), [x <= 4, y <= 9])
        problem.solve(cp.SCS, qcp=True)
        # (2 + 2) * (3 + 4) = 28
        self.assertAlmostEqual(problem.objective.value, 28, places=1)
        self.assertAlmostEqual(x.value, 4, places=1)
        self.assertAlmostEqual(y.value, 9, places=1)

    def test_basic_ratio(self) -> None:
        x = cp.Variable()
        y = cp.Variable(nonneg=True)
        expr = x / y
        self.assertTrue(expr.is_dqcp())
        self.assertTrue(expr.is_quasiconcave())
        self.assertTrue(expr.is_quasiconvex())

        problem = cp.Problem(cp.Minimize(expr), [x == 12, y <= 6])
        self.assertTrue(problem.is_dqcp())

        problem.solve(cp.SCS, qcp=True)
        self.assertAlmostEqual(problem.objective.value, 2.0, places=1)
        self.assertAlmostEqual(x.value, 12, places=1)
        self.assertAlmostEqual(y.value, 6, places=1)

        x = cp.Variable()
        y = cp.Variable(nonpos=True)
        expr = x / y
        self.assertTrue(expr.is_dqcp())
        self.assertTrue(expr.is_quasiconcave())
        self.assertTrue(expr.is_quasiconvex())

        problem = cp.Problem(cp.Maximize(expr), [x == 12, y >= -6])
        self.assertTrue(problem.is_dqcp())

        problem.solve(cp.SCS, qcp=True)
        self.assertAlmostEqual(problem.objective.value, -2.0, places=1)
        self.assertAlmostEqual(x.value, 12, places=1)
        self.assertAlmostEqual(y.value, -6, places=1)

    def test_lin_frac(self) -> None:
        x = cp.Variable((2,), nonneg=True)
        A = np.array([[1.0, 2.0], [3.0, 4.0]])
        b = np.arange(2)
        C = 2 * A
        d = np.arange(2)
        lin_frac = (cp.matmul(A, x) + b) / (cp.matmul(C, x) + d)
        self.assertTrue(lin_frac.is_dqcp())
        self.assertTrue(lin_frac.is_quasiconvex())
        self.assertTrue(lin_frac.is_quasiconcave())

        problem = cp.Problem(cp.Minimize(cp.sum(x)), [x >= 0, lin_frac <= 1])
        self.assertTrue(problem.is_dqcp())
        problem.solve(SOLVER, qcp=True)
        self.assertAlmostEqual(problem.objective.value, 0, places=1)
        np.testing.assert_almost_equal(x.value, 0, decimal=5)

    def test_concave_frac(self) -> None:
        x = cp.Variable(nonneg=True)
        concave_frac = cp.sqrt(x) / cp.exp(x)
        self.assertTrue(concave_frac.is_dqcp())
        self.assertTrue(concave_frac.is_quasiconcave())
        self.assertFalse(concave_frac.is_quasiconvex())

        problem = cp.Problem(cp.Maximize(concave_frac))
        self.assertTrue(problem.is_dqcp())
        problem.solve(cp.SCS, qcp=True)
        self.assertAlmostEqual(problem.objective.value, 0.428, places=1)
        self.assertAlmostEqual(x.value, 0.5, places=1)

    def test_length(self) -> None:
        x = cp.Variable(5)
        expr = cp.length(x)
        self.assertTrue(expr.is_dqcp())
        self.assertTrue(expr.is_quasiconvex())
        self.assertFalse(expr.is_quasiconcave())

        problem = cp.Problem(cp.Minimize(expr), [x[0] == 2.0, x[1] == 1.0])
        problem.solve(SOLVER, qcp=True)
        self.assertEqual(problem.objective.value, 2)
        np.testing.assert_almost_equal(x.value, np.array([2, 1, 0, 0, 0]))

    def test_length_example(self) -> None:
        """Fix #1760."""
        n = 10
        np.random.seed(1)
        A = np.random.randn(n, n)
        x_star = np.random.randn(n)
        b = A @ x_star
        epsilon = 1e-2
        x = cp.Variable(n)
        mse = cp.sum_squares(A @ x - b) / n
        problem = cp.Problem(cp.Minimize(cp.length(x)), [mse <= epsilon])
        assert problem.is_dqcp()

        problem.solve(qcp=True)
        assert np.isclose(problem.value, 8)

    def test_length_monototicity(self) -> None:
        n = 5
        x = cp.Variable(n)
        self.assertTrue(cp.length(cp.abs(x)).is_incr(0))
        self.assertFalse(cp.length(cp.abs(x) - 1).is_incr(0))
        self.assertTrue(cp.length(cp.abs(x)).is_dqcp())
        self.assertFalse(cp.length(cp.abs(x) - 1).is_dqcp())
        self.assertTrue(cp.length(-cp.abs(x)).is_decr(0))
        self.assertFalse(cp.length(-cp.abs(x) + 1).is_decr(0))

    def test_infeasible(self) -> None:
        x = cp.Variable(2)
        problem = cp.Problem(cp.Minimize(cp.length(x)), [x == -1, cp.ceil(x) >= 1])
        problem.solve(SOLVER, qcp=True)
        self.assertIn(problem.status, (s.INFEASIBLE, s.INFEASIBLE_INACCURATE))

    def test_sign(self) -> None:
        x = cp.Variable()
        problem = cp.Problem(cp.Minimize(cp.sign(x)), [-2 <= x, x <= -0.5])
        problem.solve(SOLVER, qcp=True)
        self.assertEqual(problem.objective.value, -1)
        self.assertLessEqual(x.value, 0)

        problem = cp.Problem(cp.Maximize(cp.sign(x)), [1 <= x, x <= 2])
        problem.solve(SOLVER, qcp=True)
        self.assertEqual(problem.objective.value, 1.0)
        self.assertGreater(x.value, 0)

        # Check that sign doesn't change value.
        vector = np.array([0.1, -0.3, 0.5])
        variable = cp.Variable(len(vector))
        problem = cp.Problem(cp.Maximize(vector @ variable), [cp.norm2(variable) <= 1.0])
        problem.solve(solver=cp.SCS)

        value = variable.value.copy()
        cp.sign(variable).value
        self.assertItemsAlmostEqual(value, variable.value)

        # sign is only QCP for univariate input.
        # See issue #1828
        x = cp.Variable(2)
        obj = cp.sum_squares(np.ones(2) - x)
        constr = [cp.sum(cp.sign(x)) <= 1]
        prob = cp.Problem(cp.Minimize(obj), constr)
        assert not prob.is_dqcp()

    def test_dist_ratio(self) -> None:
        x = cp.Variable(2)
        a = np.ones(2)
        b = np.zeros(2)
        problem = cp.Problem(cp.Minimize(cp.dist_ratio(x, a, b)), [x <= 0.8])
        problem.solve(cp.SCS, qcp=True)
        np.testing.assert_almost_equal(problem.objective.value, 0.25, decimal=3)
        np.testing.assert_almost_equal(x.value, np.array([0.8, 0.8]), decimal=3)

    def test_infeasible_exp_constr(self) -> None:
        x = cp.Variable()
        constr = [cp.exp(cp.ceil(x)) <= -5]
        problem = cp.Problem(cp.Minimize(0), constr)
        problem.solve(SOLVER, qcp=True)
        self.assertEqual(problem.status, s.INFEASIBLE)

    def test_infeasible_inv_pos_constr(self) -> None:
        x = cp.Variable(nonneg=True)
        constr = [cp.inv_pos(cp.ceil(x)) <= -5]
        problem = cp.Problem(cp.Minimize(0), constr)
        problem.solve(SOLVER, qcp=True)
        self.assertEqual(problem.status, s.INFEASIBLE)

    def test_infeasible_logistic_constr(self) -> None:
        x = cp.Variable(nonneg=True)
        constr = [cp.logistic(cp.ceil(x)) <= -5]
        problem = cp.Problem(cp.Minimize(0), constr)
        problem.solve(SOLVER, qcp=True)
        self.assertEqual(problem.status, s.INFEASIBLE)

    def test_noop_exp_constr(self) -> None:
        x = cp.Variable()
        constr = [cp.exp(cp.ceil(x)) >= -5]
        problem = cp.Problem(cp.Minimize(0), constr)
        problem.solve(SOLVER, qcp=True)
        self.assertEqual(problem.status, s.OPTIMAL)

    def test_noop_inv_pos_constr(self) -> None:
        x = cp.Variable()
        constr = [cp.inv_pos(cp.ceil(x)) >= -5]
        problem = cp.Problem(cp.Minimize(0), constr)
        problem.solve(SOLVER, qcp=True)
        self.assertEqual(problem.status, s.OPTIMAL)

    def test_noop_logistic_constr(self) -> None:
        x = cp.Variable(nonneg=True)
        constr = [cp.logistic(cp.ceil(x)) >= -5]
        problem = cp.Problem(cp.Minimize(0), constr)
        problem.solve(SOLVER, qcp=True)
        self.assertEqual(problem.status, s.OPTIMAL)

    def test_gen_lambda_max_matrix_completion(self) -> None:
        A = cp.Variable((3, 3))
        B = cp.Variable((3, 3), PSD=True)
        gen_lambda_max = cp.gen_lambda_max(A, B)
        known_indices = tuple(zip(*[[0, 0], [0, 2], [1, 1]]))
        constr = [
            A[known_indices] == [1.0, 1.9, 0.8],
            B[known_indices] == [3.0, 1.4, 0.2],
        ]
        problem = cp.Problem(cp.Minimize(gen_lambda_max), constr)
        self.assertTrue(problem.is_dqcp())
        # smoke test
        problem.solve(cp.SCS, qcp=True)

    def test_condition_number(self) -> None:
        A = cp.Variable((2, 2), PSD=True)
        con_num = cp.condition_number(A)
        constr = [
            A[0][0] == 2.0,
            A[1][1] == 3.0,
            A[0][1] <= 2,
            A[0][1] >= 1,
            A[1][0] <= 2,
            A[1][0] >= 1,
        ]
        prob = cp.Problem(cp.Minimize(con_num), constr)
        self.assertTrue(prob.is_dqcp())
        # smoke test
        prob.solve(cp.SCS, qcp=True)
        ans = np.asarray([[2.0, 1.0], [1.0, 3.0]])
        self.assertItemsAlmostEqual(A.value, ans, places=1)

    def test_card_ls(self) -> None:
        n = 10
        np.random.seed(0)
        A = np.random.randn(n, n)
        x_star = np.random.randn(n)
        b = cp.matmul(A, x_star)
        epsilon = 1e-3

        x = cp.Variable(n)
        objective_fn = cp.length(x)
        mse = cp.sum_squares(cp.matmul(A, x) - b) / n
        problem = cp.Problem(cp.Minimize(objective_fn), [mse <= epsilon])
        # smoke test
        problem.solve(SOLVER, qcp=True)

    def test_multiply_const(self) -> None:
        x = cp.Variable()
        obj = cp.Minimize(0.5 * cp.ceil(x))
        problem = cp.Problem(obj, [x >= 10])
        problem.solve(SOLVER, qcp=True)
        self.assertAlmostEqual(x.value, 10, places=1)
        self.assertAlmostEqual(problem.value, 5, places=1)

        x = cp.Variable()
        obj = cp.Minimize(cp.ceil(x) * 0.5)
        problem = cp.Problem(obj, [x >= 10])
        problem.solve(SOLVER, qcp=True)
        self.assertAlmostEqual(x.value, 10, places=1)
        self.assertAlmostEqual(problem.value, 5, places=1)

        x = cp.Variable()
        obj = cp.Maximize(-0.5 * cp.ceil(x))
        problem = cp.Problem(obj, [x >= 10])
        problem.solve(SOLVER, qcp=True)
        self.assertAlmostEqual(x.value, 10, places=1)
        self.assertAlmostEqual(problem.value, -5, places=1)

        x = cp.Variable()
        obj = cp.Maximize(cp.ceil(x) * -0.5)
        problem = cp.Problem(obj, [x >= 10])
        problem.solve(SOLVER, qcp=True)
        self.assertAlmostEqual(x.value, 10, places=1)
        self.assertAlmostEqual(problem.value, -5, places=1)

    def test_div_const(self) -> None:
        x = cp.Variable()
        obj = cp.Minimize(cp.ceil(x) / 0.5)
        problem = cp.Problem(obj, [x >= 10])
        problem.solve(SOLVER, qcp=True)
        self.assertAlmostEqual(x.value, 10, places=1)
        self.assertAlmostEqual(problem.value, 20, places=1)

        x = cp.Variable()
        obj = cp.Maximize(cp.ceil(x) / -0.5)
        problem = cp.Problem(obj, [x >= 10])
        problem.solve(SOLVER, qcp=True)
        self.assertAlmostEqual(x.value, 10, places=1)
        self.assertAlmostEqual(problem.value, -20, places=1)

    def test_reciprocal(self) -> None:
        x = cp.Variable(pos=True)
        problem = cp.Problem(cp.Minimize(1 / x))
        problem.solve(SOLVER, qcp=True)
        self.assertAlmostEqual(problem.value, 0, places=3)

    def test_abs(self) -> None:
        x = cp.Variable(pos=True)
        problem = cp.Problem(cp.Minimize(cp.abs(1 / x)))
        problem.solve(SOLVER, qcp=True)
        self.assertAlmostEqual(problem.value, 0, places=3)

        x = cp.Variable(neg=True)
        problem = cp.Problem(cp.Minimize(cp.abs(1 / x)))
        problem.solve(SOLVER, qcp=True)
        self.assertAlmostEqual(problem.value, 0, places=3)

    def test_tutorial_example(self) -> None:
        x = cp.Variable()
        y = cp.Variable(pos=True)
        objective_fn = -cp.sqrt(x) / y
        problem = cp.Problem(cp.Minimize(objective_fn), [cp.exp(x) <= y])
        # smoke test
        problem.solve(cp.SCS, qcp=True)

    def test_curvature(self) -> None:
        x = cp.Variable(3)
        expr = cp.length(x)
        self.assertEqual(expr.curvature, s.QUASICONVEX)
        expr = -cp.length(x)
        self.assertEqual(expr.curvature, s.QUASICONCAVE)
        expr = cp.ceil(x)
        self.assertEqual(expr.curvature, s.QUASILINEAR)
        self.assertTrue(expr.is_quasilinear())

    def test_tutorial_dqcp(self) -> None:
        # The sign of variables affects curvature analysis.
        x = cp.Variable(nonneg=True)
        concave_frac = x * cp.sqrt(x)
        constraint = [cp.ceil(x) <= 10]
        problem = cp.Problem(cp.Maximize(concave_frac), constraint)
        self.assertTrue(concave_frac.is_quasiconcave())
        self.assertTrue(constraint[0].is_dqcp())
        self.assertTrue(problem.is_dqcp())

        w = cp.Variable()
        fn = w * cp.sqrt(w)
        problem = cp.Problem(cp.Maximize(fn))
        self.assertFalse(fn.is_dqcp())
        self.assertFalse(problem.is_dqcp())

    def test_add_constant(self) -> None:
        # The sign of variables affects curvature analysis.
        x = cp.Variable()
        problem = cp.Problem(cp.Minimize(cp.ceil(x) + 5), [x >= 2])
        problem.solve(SOLVER, qcp=True)
        np.testing.assert_almost_equal(x.value, 2)
        np.testing.assert_almost_equal(problem.objective.value, 7)

    def test_max(self) -> None:
        x = cp.Variable(2, pos=True)
        obj = cp.max((1 - 2 * cp.sqrt(x) + x) / x)
        problem = cp.Problem(cp.Minimize(obj), [x[0] <= 0.5, x[1] <= 0.9])
        self.assertTrue(problem.is_dqcp())
        problem.solve(cp.SCS, qcp=True)
        self.assertAlmostEqual(problem.objective.value, 0.1715, places=1)

    def test_min(self) -> None:
        x = cp.Variable(2)
        expr = cp.min(cp.ceil(x))
        problem = cp.Problem(cp.Maximize(expr), [x[0] >= 11.9, x[0] <= 15.8, x[1] >= 17.4])
        self.assertTrue(problem.is_dqcp())
        problem.solve(SOLVER, qcp=True)
        self.assertAlmostEqual(problem.objective.value, 16.0)
        self.assertLess(x[0].value, 16.0)
        self.assertGreater(x[0].value, 14.9)
        self.assertGreater(x[1].value, 17.3)

    def test_sum_of_qccv_not_dqcp(self) -> None:
        t = cp.Variable(5, pos=True)
        expr = cp.sum(cp.square(t) / t)
        self.assertFalse(expr.is_dqcp())

    def test_flip_bounds(self) -> None:
        x = cp.Variable(pos=True)
        problem = cp.Problem(cp.Maximize(cp.ceil(x)), [x <= 1])
        problem.solve(SOLVER, qcp=True, low=0, high=0.5)
        self.assertGreater(x.value, 0)
        self.assertLessEqual(x.value, 1)

        problem.solve(SOLVER, qcp=True, low=0, high=None)
        self.assertGreater(x.value, 0)
        self.assertLessEqual(x.value, 1)

        problem.solve(SOLVER, qcp=True, low=None, high=0.5)
        self.assertGreater(x.value, 0)
        self.assertLessEqual(x.value, 1)

    def test_scalar_sum(self) -> None:
        x = cp.Variable(pos=True)
        problem = cp.Problem(cp.Minimize(cp.sum(1 / x)))
        problem.solve(SOLVER, qcp=True)
        self.assertAlmostEqual(problem.value, 0, places=3)

        # TODO: Make this test pass. Need to add a special case for scalar sums.
        with self.assertRaises(Exception) as cm:
            problem = cp.Problem(cp.Minimize(cp.cumsum(1 / x)))
            problem.solve(SOLVER, qcp=True)
        self.assertEqual(str(cm.exception), "axis 0 is out of bounds for array of dimension 0")

    def test_parameter_bug(self) -> None:
        """Test bug with parameters arising from interaction of
        DQCP and DPP.

        https://github.com/cvxpy/cvxpy/issues/2386
        """
        x = cp.Variable()

        objective = cp.Minimize(cp.sqrt(x))

        constraints = [x <= 2, x >= 1]

        problem = cp.Problem(objective, constraints)

        problem.solve(qcp=True, solver=cp.SCS)

        self.assertAlmostEqual(x.value, objective.value, places=3)
        self.assertAlmostEqual(x.value, 1, places=3)

    def test_psd_constraint_bug(self) -> None:
        """Test bug with DQCP and PSD constraints.

        https://github.com/cvxpy/cvxpy/issues/2373
        """
        A = cp.Variable((2, 2), symmetric=True)

        x = A[0, 1]
        y = A[1, 1]

        # assertions and constraints
        x = cp.atoms.affine.wraps.nonneg_wrap(x)
        y = cp.atoms.affine.wraps.nonneg_wrap(y)
        constraints = [A >> 0]

        # function
        f = x * y

        # create the problem
        problem = cp.Problem(cp.Maximize(f), constraints)

        # solve
        assert problem.is_dqcp()
        with pytest.raises(cp.SolverError, match="Max iters hit during bisection."):
            problem.solve(qcp=True, solver=cp.SCS, max_iters=1)
