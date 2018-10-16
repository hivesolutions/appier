#!/usr/bin/python
# -*- coding: utf-8 -*-

# Hive Appier Framework
# Copyright (c) 2008-2018 Hive Solutions Lda.
#
# This file is part of Hive Appier Framework.
#
# Hive Appier Framework is free software: you can redistribute it and/or modify
# it under the terms of the Apache License as published by the Apache
# Foundation, either version 2.0 of the License, or (at your option) any
# later version.
#
# Hive Appier Framework is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# Apache License for more details.
#
# You should have received a copy of the Apache License along with
# Hive Appier Framework. If not, see <http://www.apache.org/licenses/>.

__author__ = "João Magalhães <joamag@hive.pt>"
""" The author(s) of the module """

__version__ = "1.0.0"
""" The version of the module """

__revision__ = "$LastChangedRevision$"
""" The revision number of the module """

__date__ = "$LastChangedDate$"
""" The last change date of the module """

__copyright__ = "Copyright (c) 2008-2018 Hive Solutions Lda."
""" The copyright for the module """

__license__ = "Apache License, Version 2.0"
""" The license for the module """

import time
import heapq
import calendar
import datetime
import traceback
import threading

from . import common

BACKGROUND = []
""" The list containing the various global registered
function to be executed as background operations, note
that only the name is used in the list so a possible
collision of tasks is possible """

SLEEP_TIME = 0.5
""" The amount of time to sleep between iteration
this amount should be small enough to provide some
resolution level to the schedule execution """

background_t = None
""" The background execution task to be started by
the appier execution system (global value) """

class ExecutionThread(threading.Thread):
    """
    The thread to be used in the execution of "random"
    "callables" for a provided time, this thread contains
    a series of thread safe method for operating over
    the work tuples.
    """

    run_flag = True
    """ The flag that controls the running operations
    of the execution thread, once this value is unset
    the thread is exited """

    work_list = []
    """ The list containing the various work descriptors
    for the work to be done, this work is going to be
    run in a single thread (in sequence) """

    work_lock = None
    """ The lock that control the access to the list of
    work to be executed """

    def __init__(self):
        """
        Constructor of the class.
        """

        threading.Thread.__init__(self, name = "Execution")

        self.daemon = True
        self.work_list = []
        self.work_lock = threading.RLock()

    def run(self):
        # iterates continuously (executing work)
        # while the run flag is set
        while self.run_flag:
            # creates a list list that will would the
            # work tuples to be executed (this way the
            # lock problem is avoided)
            execution_list = []

            # acquires the lock to access the list
            # of work and execute it
            self.work_lock.acquire()

            # retrieves the current time, this variable
            # is going to be used to check if the work in
            # iteration should be run or not
            current_time = time.time()

            try:
                # iterates continuously to execute all the
                # work that can be executed in the work list
                while True:
                    # in case there is no work pending to be
                    # executed must exist immediately
                    if not self.work_list: break

                    # retrieves the current work tuple to
                    # be used and executes it in case the
                    # time has passed (should be executed)
                    _time, callable, callback, args, kwargs = self.work_list[0]
                    if _time < current_time:
                        execution_list.append((callable, callback, args, kwargs))
                        heapq.heappop(self.work_list)
                    else:
                        break
            finally:
                # releases the work lock providing access
                # to the work list
                self.work_lock.release()

            # iterates over all the "callables" in the execution
            # list to execute their operations
            for callable, callback, args, kwargs in execution_list:
                # sets the initial (default) value for the error
                # variable that controls the result of the execution
                error = None

                # executes the "callable" and logs the error in case the
                # execution fails (must be done to log the error) then
                # sets the error flag with the exception variable
                try: callable(*args, **kwargs)
                except BaseException as exception:
                    error = exception
                    lines = traceback.format_exc().splitlines()
                    logger = common.base().get_logger()
                    logger.warning(str(exception))
                    for line in lines: logger.info(line)

                # calls the callback method with the currently set error
                # in order to notify the runtime about the problem, only
                # calls the callback in case such method is defined
                callback and callback(error = error)

            # sleeps for a while so that the process may
            # released for different tasks
            time.sleep(SLEEP_TIME)

    def stop(self):
        self.run_flag = False

    def insert_work(self, callable, args = [], kwargs = {}, target_time = None, callback = None):
        target_time = target_time or time.time()
        work = (target_time, callable, callback, args, kwargs)
        self.work_lock.acquire()
        try: heapq.heappush(self.work_list, work)
        finally: self.work_lock.release()

def background(timeout = None):

    def decorator(function):
        _timeout = timeout or 0.0

        def schedule(error = None, force = False):
            if timeout == None and not force: return
            target = time.time() + _timeout
            insert_work(function, target, schedule)

        # retrieves the name of the function and in
        # case the name already exists in the global
        # list of background execution tasks returns
        # immediately (nothing to be done, duplicate)
        fname = function.__name__
        exists = fname in BACKGROUND
        if exists: return function

        # runs the scheduling operation on the task and
        # then adds the function name to the list of already
        # registered names
        schedule(force = True)
        BACKGROUND.append(fname)
        return function

    return decorator

def insert_work(callable, args = [], kwargs = {}, target_time = None, callback = None):
    """
    Runs the provided callable (function, method, etc) in a separated
    thread context under submission of a queue system.
    It's possible to control the runtime for the execution with the
    ``target_time`` argument and it's also possible to be notified
    of the end of the execution providing a callable to the ``callback``
    parameter.

    .. warning::

        The execution is not guaranteed as the system process may be
        interrupted and resuming of the execution would not be possible.

    :type callable: Function
    :param callable: The callable object to be called in a separated\
    execution environment.
    :type args: List
    :param args: The list of unnamed argument values to be send to the\
    callable upon execution.
    :type args: Dictionary
    :param args: The dictionary of named argument values to be send to the\
    callable upon execution.
    :type target_time: float
    :param target_time: The target timestamp value for execution, in case\
    it's not provided the current time is used as the target one.
    :type callback: Function
    :param callback: The callback function to be called upon finishing the\
    execution of the callable, in case an error (exception) on executing\
    the callback the error is passed as error argument.
    """

    background_t.insert_work(
        callable,
        args = args,
        kwargs = kwargs,
        target_time = target_time,
        callback = callback
    )

def interval_work(
    callable,
    args = [],
    kwargs = {},
    callback = None,
    initial = None,
    interval = 60,
    eval = None
):
    initial = initial or (eval and eval()) or time.time()
    composed = build_composed(callable, initial, interval, eval, callback)
    insert_work(
        composed,
        args = args,
        kwargs = kwargs,
        target_time = initial,
        callback = callback
    )
    return initial

def seconds_work(callable, offset = 0, *args, **kwargs):
    eval = lambda: seconds_eval(offset)
    return interval_work(callable, eval = eval, *args, **kwargs)

def minutes_work(callable, offset = 0, *args, **kwargs):
    eval = lambda: minutes_eval(offset)
    return interval_work(callable, eval = eval, *args, **kwargs)

def hourly_work(callable, offset = 0, *args, **kwargs):
    eval = lambda: hourly_eval(offset)
    return interval_work(callable, eval = eval, *args, **kwargs)

def daily_work(callable, offset = 0, *args, **kwargs):
    eval = lambda: daily_eval(offset)
    return interval_work(callable, eval = eval, *args, **kwargs)

def weekly_work(callable, weekday = 4, offset = 0, *args, **kwargs):
    eval = lambda: weekly_eval(weekday, offset)
    return interval_work(callable, eval = eval, *args, **kwargs)

def monthly_work(callable, monthday = 1, offset = 0, *args, **kwargs):
    eval = lambda: monthly_eval(monthday, offset)
    return interval_work(callable, eval = eval, *args, **kwargs)

def seconds_eval(offset, now = None):
    now = now or datetime.datetime.utcnow()
    next = now + datetime.timedelta(seconds = offset)
    next_tuple = next.utctimetuple()
    return calendar.timegm(next_tuple)

def minutes_eval(offset, now = None):
    now = now or datetime.datetime.utcnow()
    current = datetime.datetime(
        year = now.year,
        month = now.month,
        day = now.day,
        hour = now.hour,
        minute = now.minute
    )
    next = current + datetime.timedelta(minutes = 1, seconds = offset)
    next_tuple = next.utctimetuple()
    return calendar.timegm(next_tuple)

def hourly_eval(offset, now = None):
    now = now or datetime.datetime.utcnow()
    current = datetime.datetime(year = now.year, month = now.month, day = now.day, hour = now.hour)
    next = current + datetime.timedelta(hours = 1, seconds = offset)
    next_tuple = next.utctimetuple()
    return calendar.timegm(next_tuple)

def daily_eval(offset, now = None):
    now = now or datetime.datetime.utcnow()
    today = datetime.datetime(year = now.year, month = now.month, day = now.day)
    tomorrow = today + datetime.timedelta(days = 1, seconds = offset)
    tomorrow_tuple = tomorrow.utctimetuple()
    return calendar.timegm(tomorrow_tuple)

def weekly_eval(weekday, offset, now = None):
    now = now or datetime.datetime.utcnow()
    today = datetime.datetime(year = now.year, month = now.month, day = now.day)
    distance = (weekday - today.weekday()) % 7
    weekday = today + datetime.timedelta(days = distance, seconds = offset)
    if weekday < now: weekday += datetime.timedelta(days = 7)
    weekday_tuple = weekday.utctimetuple()
    return calendar.timegm(weekday_tuple)

def monthly_eval(monthday, offset, now = None):
    now = now or datetime.datetime.utcnow()
    next_year, next_month = (now.year + 1, 1) if now.month == 12 else (now.year, now.month + 1)
    if now.day > monthday: month, year = (next_month, next_year)
    else: month, year = (now.month, now.year)
    monthday = datetime.datetime(year = year, month = month, day = monthday)
    monthday = monthday + datetime.timedelta(seconds = offset)
    if monthday < now:
        monthday = datetime.datetime(year = next_year, month = next_month, day = monthday.day)
        monthday += datetime.timedelta(seconds = offset)
    monthday_tuple = monthday.utctimetuple()
    return calendar.timegm(monthday_tuple)

def build_composed(callable, target_time, interval, eval, callback):

    def composed(*args, **kwargs):
        try:
            # runs the initial callable, propagating the provided normal arguments
            # and keyword based ones to the callable as it's expected by the current
            # underlying running logic (and by the specification)
            result = callable(*args, **kwargs)
        finally:
            if eval:
                # in case the evaluation function for the next timing exists it must be
                # called to be able to retrieve the target timing for the next execution
                # this is required from a specification point of view (dual mode)
                next_time = eval()
            else:
                # retrieves the current time value as the final value of execution, then
                # calculates the delta value and uses it to verify if the current work is
                # allowed for initial based time delta calculus (avoiding queue starvation)
                final = time.time()
                delta = final - target_time
                is_valid = delta < interval
                if is_valid: next_time = target_time + interval
                else: next_time = final + interval

            # builds a new callable (composed) method taking into account the state and
            # inserts the work unit again into the queue of processing
            composed = build_composed(callable, next_time, interval, eval, callback)
            insert_work(
                composed,
                args = args,
                kwargs = kwargs,
                target_time = next_time,
                callback = callback
            )

        # returns the current result from the original callable to the calling method,
        # this is the expected behavior from the scheduler point of view
        return result

    return composed
