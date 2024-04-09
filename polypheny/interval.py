def simple_plural(count, word):
    if count == 1:
        return word
    else:
        return word + "s"

def simple_str(count, word):
    return f"{count} {simple_plural(count, word)}"

class IntervalMonthMilliseconds():
    def __init__(self, months, milliseconds):
        #: The number of months
        self.months = months
        self.milliseconds = milliseconds

    def __eq__(self, other):
        return isinstance(other, IntervalMonthMilliseconds) and self.months == other.months and self.milliseconds == other.milliseconds

    def __str__(self):
        return simple_str(self.months, "month") + " and " + simple_str(self.milliseconds, "millisecond")
