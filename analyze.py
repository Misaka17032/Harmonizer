import os
import pypianoroll as pr
import json
from tqdm import tqdm

def symbol_index(symbol):
	# order: major, minor. aug, dim, sus, major7, minor7, dominant7
	order = 0
	char_list = list(symbol)

	if 'o' in char_list or 'ø' in char_list:
		# dim
		order = 4
	else:
		if '#' in char_list and '5' in char_list:
			# aug
			order = 3
		else:
			if 's' in char_list and 'u' in char_list:
				# sus
				order = 5
			else:
				if '7' in char_list or '9' in char_list or '11' in char_list:
					#7th chord
					if 'm' in char_list:
						#major7, minor7
						if 'j' in char_list:
							#maj7
							order = 6
						else:
							#minor7
							order = 7
					else:
						#dominant7
						order = 8
				else:
					#major. minor
					if 'm' in char_list and 'j' not in char_list:
						#minor
						order = 2
					else:
						#major
						order = 1
	index = 0
	dict_to_index = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}
	index = dict_to_index[char_list[0].upper()]
	if len(char_list) > 1:
		if char_list[1] == 'b':
			#flat
			index -= 1
		elif char_list[1] == '#':
			#sharp
			index += 1
		if index < 0:
			index += 12

	return index * 8 + (order - 1)

class Dataset():
	def __init__(self, data_path = "datasets",
						beat_resolution=24, 
						beats_per_chord=2,
						num_note_per_octave=12):

		self.beats_per_chord = beats_per_chord
		self.beat_resolution = beat_resolution
		self.num_note_per_octave = num_note_per_octave

		# Raw data
		self.melody_pianoroll = []
		self.chord_pianoroll = []
		self.symbols = []

		self.result = [[0] * 96 for i in range(96)]

		# Recursive search files
		for root, dirs, files in tqdm(list(os.walk(os.path.join(data_path, "pianoroll"))), dynamic_ncols=True):
			for file in files:
				if file.endswith(".npz"):
					# Arrange symbol and roman data paths from pianoroll data
					path_to_symbol = os.path.join(root, file).replace("\\pianoroll\\","\\event\\")[:-4] + "_symbol_nokey.json"
					# Read .npz(midi) file
					try:
						midi = pr.load(os.path.join(root, file))
					except:
						continue
					if len(midi.tracks) == 2:
						# Extract melody
						melody = midi.tracks[0]
						# Extract chord
						chord = midi.tracks[1]
						chord_list = []
						for i in range(chord.pianoroll.shape[0]):
							# Get chord per 2 beats 
							if i % (self.beat_resolution * self.beats_per_chord) == 0:
								chord_list.append(chord.pianoroll[i])

						# Gather all data to a big list
						self.melody_pianoroll.append(melody.pianoroll)
						self.chord_pianoroll.append(chord_list)

						# Create symbol data if pianoroll data exists
						# Read nokey_symbol json files 
						f = open(path_to_symbol)
						event = json.load(f)
						event_on = []
						event_off = []
						symbol = []

						# Warping factor to normalize sequences to tempo 4/4 for different time signatures, e.g tempo 6/8, 3/4, ...
						if int(midi.tempo[0]) != 0 and int(event['metadata']['BPM']) != 0:
							warping_factor = int(event['metadata']['BPM']) // int(midi.tempo[0])
						else:
							warping_factor = 1

						# Extract chord per 2 beat
						for chord in event['tracks']['chord']:
							if chord != None:
								event_on.append(chord['event_on'] / warping_factor)
								event_off.append(chord['event_off'] / warping_factor)
								symbol.append(chord['symbol'])

						symbol_len = event_on[-1]
						symbol_list = []
						q_index = [2 * i for i in range(len(chord_list))]  

						for i in range(len(q_index)):
							if q_index[i] in event_on:
								symbol_list.append(symbol[event_on.index(q_index[i])])
							else:
								if i == q_index[-1]:
									symbol_list.append(symbol[-1])

								else:
									count = 0
									for k in range(len(symbol)):
										if q_index[i] > event_on[k] and q_index[i] < event_off[k]:
											symbol_list.append(symbol[k])
											count += 1
											break
									if count == 0:
										symbol_list.append('')

						self.symbols.append(symbol_list)
						f.close()

		print("len of chord_pianoroll:", len(self.chord_pianoroll))

	def analyze(self):
		# Analyze dataset
		cnt = 0
		for piece in self.symbols:
			for i in range(len(piece) - 1):
				if piece[i] != '' and piece[i + 1] != '':
					self.result[symbol_index(piece[i])][symbol_index(piece[i + 1])] += 1
					cnt += 1

		print("Total number of analyzed chords:", cnt)

	def save(self, path="results.json"):
		# Save results
		with open(path, 'w') as fp:
			fp.write(json.dumps(self.result))


if __name__ == "__main__":
	ds = Dataset()
	ds.analyze()
	ds.save()
