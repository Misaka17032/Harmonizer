import json
import numpy as np

from analyze import symbol_index


class Harmonizer:
	def __init__(self, result_file="results.json"):
		self.result = json.load(open(result_file, "r"))

	def index_to_chord(self, index):
		# index: 0 - 95
		keys = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
		# major, minor, aug, dim, sus, major7, minor7, dominant7
		orders = ["", "m", "5#", "o", "sus", "maj7", "m7", "7"]
		return keys[index // 8] + orders[index % 8]

	def get_chord_predict(self, chord):
		index = symbol_index(chord)
		chord = self.result[index]
		chord[index] = 0
		return chord

	def get_chord_probability(self, chord, next_chord):
		index = symbol_index(chord)
		next_index = symbol_index(next_chord)
		distribution = self.get_chord_predict(chord)
		probability = distribution[next_index] / sum(distribution)
		return probability

	def get_top_k(self, chord, k=5):
		index = symbol_index(chord)
		distribution = self.get_chord_predict(chord)
		top_k = sorted(range(len(distribution)), key=lambda i: distribution[i])[-k:]
		return [self.index_to_chord(i) for i in top_k]

	def random(self, chord):
		index = symbol_index(chord)
		distribution = self.get_chord_predict(chord)
		probability = [i / sum(distribution) for i in distribution]
		return self.index_to_chord(np.random.choice(range(96), p=probability))

if __name__ == "__main__":
	harmonizer = Harmonizer()
	chord = "C"
	print(harmonizer.get_chord_predict(chord))
	# print(harmonizer.get_top_k(chord))
	# chord_progression = chord + " "
	# for i in range(7):
	# 	chord = harmonizer.random(chord)
	# 	chord_progression += chord + " "
	# print(chord_progression)