class AutoTagger:
    def __init__(self):
        self.default_tags = ["memory", "conversation"]

    def generate_tags(self, content):
        """
        Generate tags for the given content.
        For now, returns default tags. Can be enhanced with NLP later.
        """
        # TODO: Implement more sophisticated tagging using NLP
        return self.default_tags 