class DelayCalculator:
    def __init__(self, limit=30, increment=1):
        self._delay = 0
        self._limit = limit
        self._increment = increment
        self._job_performed = False

    def done(self):
        self._job_performed = True

    def get(self):
        if self._job_performed:
            self._delay = 0
            self._job_performed = False
        else:
            self._delay += self._increment

        if self._delay > self._limit:
            self._delay = self._limit

        return self._delay
