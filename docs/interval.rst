Intervals
=========

The connector returns a Polypheny interval as an
:py:class:`polypheny.interval.IntervalMonthMilliseconds`. Its ``months`` and
``milliseconds`` components are separate. Equality compares both components.
Use an SQL interval literal when supplying an interval to a query.

.. autoclass:: polypheny.interval.IntervalMonthMilliseconds

   .. attribute:: months

      The number of months.

   .. attribute:: milliseconds

      The number of milliseconds.

.. testcode::

   from polypheny.interval import IntervalMonthMilliseconds

   duration = IntervalMonthMilliseconds(1, 3000)
   assert duration.months == 1
   assert duration.milliseconds == 3000
   assert duration == IntervalMonthMilliseconds(1, 3000)
   print(str(duration))

.. testoutput::

   1 month and 3000 milliseconds
