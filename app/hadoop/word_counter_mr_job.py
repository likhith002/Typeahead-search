from mrjob.job import MRJob
from mrjob.step import MRStep


class WordCounter(MRJob):
    def steps(self):
        return [MRStep(mapper=self.mapper_words, reducer=self.reducer_word_counts)]

    def mapper_words(self, _, line):
        words = line.split()
        for word in words:
            yield word.lower(), 1

    def reducer_word_counts(self, word, counts):
        yield word, sum(counts)


# if __name__ == "__main__":
#     WordCounter().run()
