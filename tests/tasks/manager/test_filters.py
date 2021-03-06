# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright 2015 by Ecpy Authors, see AUTHORS for more details.
#
# Distributed under the terms of the BSD license.
#
# The full license is in the file LICENCE, distributed with this software.
# -----------------------------------------------------------------------------
"""Test for base tasks filters.

"""
from __future__ import (division, unicode_literals, print_function,
                        absolute_import)

import pytest

from ecpy.tasks.api import ComplexTask, SimpleTask
from ecpy.tasks.manager.infos import TaskInfos
from ecpy.tasks.manager.filters import (TaskFilter, GroupTaskFilter,
                                        SubclassTaskFilter, MetadataTaskFilter)


@pytest.fixture
def tasks():
    return {'SimpleTask': TaskInfos(cls=SimpleTask, metadata={'meta': True}),
            'ComplexTask': TaskInfos(cls=ComplexTask,
                                     metadata={'group': 'Complex',
                                               'meta': False})}


@pytest.fixture
def templates():
    return {'Template1': ''}


def test_task_filter(tasks, templates):
    """Test the default task filter.

    """
    filtered = TaskFilter().filter_tasks(tasks, templates)
    assert sorted(filtered) == sorted(list(tasks) + list(templates))


def test_group_task_filter(tasks, templates):
    """Test filtering by group.

    """
    filtered = GroupTaskFilter(group='Complex').filter_tasks(tasks, templates)
    assert sorted(filtered) == ['ComplexTask']


def test_subclass_task_filter(tasks, templates):
    """Test filtering by subclass.

    """
    filtered = SubclassTaskFilter(subclass=SimpleTask).filter_tasks(tasks,
                                                                    templates)
    assert sorted(filtered) == ['SimpleTask']


def test_meta_task_filter(tasks, templates):
    """Test filtering by metadata.

    """
    filtered = MetadataTaskFilter(meta_key='meta',
                                  meta_value=True).filter_tasks(tasks,
                                                                templates)
    assert sorted(filtered) == ['SimpleTask']
