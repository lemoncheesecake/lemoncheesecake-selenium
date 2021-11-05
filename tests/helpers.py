from lemoncheesecake.matching.matcher import Matcher, MatchResult


class MyMatcher(Matcher):
    def __init__(self, result=MatchResult.success()):
        super().__init__()
        self.actual = None
        self.result = result

    def build_description(self, transformation):
        return transformation("to be here")

    def matches(self, actual):
        self.actual = actual
        return self.result


