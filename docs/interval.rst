Intervals
---------

Polypheny allows two types of intervals.  The first are intervals with
a well-defined duration, such as days or minutes.  The second type are
consisting of months and years.  As only the first type can be converted
to :py:class:`datetime.timedelta` the driver will subsitute its own
:py:class:`polypheny.interval.IntervalMonth` class.

.. Note::

   Intervals cannot be used as dynamic parameter in queries.

.. autoclass:: polypheny.interval.IntervalMonth()

   .. autoattribute:: months

