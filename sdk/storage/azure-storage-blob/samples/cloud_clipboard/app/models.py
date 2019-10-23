class User:
    first = "Larry"
    last = "Olson"

    def __repr__(self):
            return 'User {}'.format(self.first + " " + self.last)