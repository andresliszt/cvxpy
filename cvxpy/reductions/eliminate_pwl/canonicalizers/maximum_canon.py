"""
Copyright 2013 Steven Diamond

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

from cvxpy.atoms.affine.wraps import nonneg_wrap, nonpos_wrap
from cvxpy.expressions.variable import Variable


def maximum_canon(expr, args):
    shape = expr.shape
    t = Variable(shape)

    if expr.is_nonneg():
        t = nonneg_wrap(t)
    if expr.is_nonpos():
        t = nonpos_wrap(t)

    constraints = [t >= elem for elem in args]
    return t, constraints
