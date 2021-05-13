# Copyright (c) 2020-2021 Thomas Paviot (tpaviot@gmail.com)
#
# This file is part of ProcessScheduler.
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.

import unittest

import processscheduler as ps
import processscheduler.context as ps_context

def new_problem_or_clear() -> None:
    """ clear the current context. If no context is defined,
    create a SchedulingProject object """
    if ps_context.main_context is None:
        ps.SchedulingProblem('NewProblem')
    else:
        ps_context.main_context.clear()

class TestTask(unittest.TestCase):
    def test_clear_context(self) -> None:
        ps_context.main_context = None
        new_problem_or_clear()
        self.assertIsInstance(ps_context.main_context, ps.SchedulingContext)

    def test_create_task_zero_duration(self) -> None:
        ps.SchedulingProblem('ProblemWithoutHorizon')
        task = ps.ZeroDurationTask('zdt')
        self.assertIsInstance(task, ps.ZeroDurationTask)

    def test_create_task_fixed_duration(self) -> None:
        new_problem_or_clear()
        task = ps.FixedDurationTask('fdt', 1)
        self.assertIsInstance(task, ps.FixedDurationTask)
        with self.assertRaises(TypeError):
            ps.FixedDurationTask('FloatDuration', 1.0)
        with self.assertRaises(TypeError):
            ps.FixedDurationTask('NullInteger', 0)
        with self.assertRaises(TypeError):
            ps.FixedDurationTask('NegativeInteger', -1)
        with self.assertRaises(TypeError):
            ps.FixedDurationTask('FloatWorkAmount', 2, work_amount=1.0)
        with self.assertRaises(TypeError):
            ps.FixedDurationTask('NegativeWorkAmount', 2, work_amount=-3)

    def test_create_task_variable_duration(self) -> None:
        new_problem_or_clear()
        ps.VariableDurationTask('vdt1')
        vdt_2 = ps.VariableDurationTask('vdt2', length_at_most=4)
        vdt_3 = ps.VariableDurationTask('vdt3', length_at_least=5)
        ps.VariableDurationTask('vdt4', work_amount=10)
        self.assertEqual(vdt_2.length_at_most, 4)
        self.assertEqual(vdt_3.length_at_least, 5)

    def test_task_types(self) -> None:
        new_problem_or_clear()
        with self.assertRaises(TypeError):
            ps.VariableDurationTask('vdt5', length_at_most=4.5)
        with self.assertRaises(TypeError):
            ps.VariableDurationTask('vdt6', length_at_most=-1)
        with self.assertRaises(TypeError):
            ps.VariableDurationTask('vdt7', length_at_least=-1)
        with self.assertRaises(TypeError):
            ps.VariableDurationTask('vdt8', work_amount=-1)
        with self.assertRaises(TypeError):
            ps.VariableDurationTask('vdt9', work_amount=1.5)
        with self.assertRaises(TypeError):
            ps.VariableDurationTask('vdt10', work_amount=None)

    def test_task_same_names(self) -> None:
        new_problem_or_clear()
        ps.VariableDurationTask('t1')
        with self.assertRaises(ValueError):
            ps.VariableDurationTask('t1')

    def test_eq_overloading(self) -> None:
        new_problem_or_clear()
        task_1 = ps.ZeroDurationTask('task1')
        task_2 = ps.ZeroDurationTask('task2')
        self.assertEqual(task_1, task_1)
        self.assertNotEqual(task_1, task_2)

    def test_redondant_tasks_resources(self) -> None:
        pb = ps.SchedulingProblem('SameNameTasks')
        # we should not be able to add twice the same resource or task
        task_1 = ps.ZeroDurationTask('task1')
        self.assertEqual(list(pb.context.tasks), [task_1])
        self.assertEqual(list(pb.context.tasks), [task_1])
        # do the same for resources
        worker_1 = ps.Worker('Worker1')
        self.assertEqual(list(pb.context.resources), [worker_1])
        self.assertEqual(list(pb.context.resources), [worker_1])

    def test_resource_requirements(self) -> None:
        new_problem_or_clear()
        task_1 = ps.FixedDurationTask('task1', duration=3)
        worker_1 = ps.Worker('Worker1')
        worker_2 = ps.Worker('Worker2')
        worker_3 = ps.Worker('Worker3')
        worker_4 = ps.Worker('Worker4')
        task_1.add_required_resource(worker_1)
        task_1.add_required_resource(worker_2)
        task_1.add_required_resources([worker_3, worker_4])
        self.assertEqual(len(task_1.required_resources), 4)

    def test_wrong_assignement(self) -> None:
        new_problem_or_clear()
        task_1 = ps.FixedDurationTask('task1', duration=3)
        worker_1 = ps.Worker('Worker1')
        task_1.add_required_resource(worker_1)
        with self.assertRaises(TypeError):
            task_1.add_required_resource(3)
        with self.assertRaises(TypeError):
            task_1.add_required_resources("a_string")
        with self.assertRaises(ValueError):
            task_1.add_required_resource(worker_1)

    #
    # Single task constraints
    #
    def test_create_task_start_at(self) -> None:
        new_problem_or_clear()
        task = ps.FixedDurationTask('task', 2)
        c = ps.TaskStartAt(task, 1)
        self.assertIsInstance(c, ps.TaskStartAt)
        self.assertEqual(c.value, 1)

    def test_create_task_start_after_strict(self) -> None:
        new_problem_or_clear()
        task = ps.FixedDurationTask('task', 2)
        c = ps.TaskStartAfterStrict(task, 3)
        self.assertIsInstance(c, ps.TaskStartAfterStrict)
        self.assertEqual(c.value, 3)

    def test_create_task_start_after_lax(self) -> None:
        new_problem_or_clear()
        task = ps.FixedDurationTask('task', 2)
        c = ps.TaskStartAfterLax(task, 3)
        self.assertIsInstance(c, ps.TaskStartAfterLax)
        self.assertEqual(c.value, 3)

    def test_create_task_end_at(self) -> None:
        new_problem_or_clear()
        task = ps.FixedDurationTask('task', 2)
        c = ps.TaskEndAt(task, 3)
        self.assertIsInstance(c, ps.TaskEndAt)
        self.assertEqual(c.value, 3)

    def test_create_task_before_strict(self) -> None:
        new_problem_or_clear()
        task = ps.FixedDurationTask('task', 2)
        c = ps.TaskEndBeforeStrict(task, 3)
        self.assertIsInstance(c, ps.TaskEndBeforeStrict)
        self.assertEqual(c.value, 3)

    def test_create_task_before_lax(self) -> None:
        new_problem_or_clear()
        task = ps.FixedDurationTask('task', 2)
        constraint = ps.TaskEndBeforeLax(task, 3)
        self.assertIsInstance(constraint, ps.TaskEndBeforeLax)
        self.assertEqual(constraint.value, 3)

    #
    # Two tasks constraints
    #
    def test_create_task_precedence_lax(self) -> None:
        new_problem_or_clear()
        t_1 = ps.FixedDurationTask('t1', duration=2)
        t_2 = ps.FixedDurationTask('t2', duration=3)
        precedence_constraint = ps.TaskPrecedence(t_1, t_2, offset=1, kind='lax')
        self.assertIsInstance(precedence_constraint, ps.TaskPrecedence)

    def test_create_task_precedence_tight(self) -> None:
        new_problem_or_clear()
        t_1 = ps.FixedDurationTask('t1', duration=2)
        t_2 = ps.FixedDurationTask('t2', duration=3)
        precedence_constraint = ps.TaskPrecedence(t_1, t_2, offset=1, kind='tight')
        self.assertIsInstance(precedence_constraint, ps.TaskPrecedence)

    def test_create_task_precedence_strict(self) -> None:
        new_problem_or_clear()
        t_1 = ps.FixedDurationTask('t1', duration=2)
        t_2 = ps.FixedDurationTask('t2', duration=3)
        precedence_constraint = ps.TaskPrecedence(t_1, t_2, offset=1, kind='strict')
        self.assertIsInstance(precedence_constraint, ps.TaskPrecedence)

    def test_create_task_precedence_raise_exception_kind(self) -> None:
        new_problem_or_clear()
        t_1 = ps.FixedDurationTask('t1', duration=2)
        t_2 = ps.FixedDurationTask('t2', duration=3)
        with self.assertRaises(ValueError):
            ps.TaskPrecedence(t_1, t_2, offset=1, kind='foo')

    def test_create_task_precedence_raise_exception_offset_int(self) -> None:
        new_problem_or_clear()
        t_1 = ps.FixedDurationTask('t1', duration=2)
        t_2 = ps.FixedDurationTask('t2', duration=3)
        with self.assertRaises(ValueError):
            ps.TaskPrecedence(t_1, t_2, offset=1.5, kind='lax')  # should be int

    def test_tasks_dont_overlap(self) -> None:
        new_problem_or_clear()
        t_1 = ps.FixedDurationTask('t1', duration=2)
        t_2 = ps.FixedDurationTask('t2', duration=3)
        constraint = ps.TasksDontOverlap(t_1, t_2)
        self.assertIsInstance(constraint, ps.TasksDontOverlap)

    def test_tasks_start_sync(self) -> None:
        new_problem_or_clear()
        t_1 = ps.FixedDurationTask('t1', duration=2)
        t_2 = ps.FixedDurationTask('t2', duration=3)
        constraint = ps.TasksStartSynced(t_1, t_2)
        self.assertIsInstance(constraint, ps.TasksStartSynced)

    def test_tasks_end_sync(self) -> None:
        new_problem_or_clear()
        t_1 = ps.FixedDurationTask('t1', duration=2)
        t_2 = ps.FixedDurationTask('t2', duration=3)
        constraint = ps.TasksEndSynced(t_1, t_2)
        self.assertIsInstance(constraint, ps.TasksEndSynced)

    def test_schedule_n_task_raise_exception(self) -> None:
        new_problem_or_clear()
        with self.assertRaises(TypeError):
            ps.ScheduleNTasksInTimeIntervals('list_of_tasks', 1, 'list_of_time_intervals')
        with self.assertRaises(TypeError):
            ps.ScheduleNTasksInTimeIntervals([], 1, 'list_of_time_intervals')



if __name__ == "__main__":
    unittest.main()
