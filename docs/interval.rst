Intervals
---------

In Polypheny intervals consist of two values: Months and milliseconds.
Values of this type are returned as instances of the
:py:class:`polypheny.interval.IntervalMonthMilliseconds` class.

.. Note::

   Intervals cannot be used as dynamic parameter in queries.

.. autoclass:: polypheny.interval.IntervalMonthMilliseconds()

   .. autoattribute:: months
   .. autoattribute:: milliseconds

