def simple_plural(count, word):
    if count == 1:
        return word
    else:
        return word + "s"

def simple_str(count, word):
    return f"{count} {simple_plural(count, word)}"

class IntervalMonth():
    def __init__(self, months):
        #: The number of months
        self.months = months

    def __eq__(self, other):
        return isinstance(other, IntervalMonth) and self.months == other.months

    def __str__(self):
        if self.months == 12:
            return simple_str(int(self.months / 12), "year")
        elif self.months > 12:
            years, months = int(self.months / 12), self.months % 12
            return simple_str(years, "year") + " and " + simple_str(months, "month")
        else:
            return simple_str(self.months, "month")

