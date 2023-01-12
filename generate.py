import requests
import random
import base64
import json

from pydub import AudioSegment
from pydub.playback import play

def gen_seed():
	return random.randint(10000000, 99999999)

class Generator:
	def __init__(self, prompt, seed=None):
		self.url = '/run_inference'
		self.prompt = prompt
		self.alpha = 0.75
		self.num_inference_steps = 50
		self.seed_image_id = "og_beat"
		self.denoising = 0.75
		self.guidance = 7.0
		self.set_seed(gen_seed() if seed is None else seed)
		self.play_seed = gen_seed()

	def set_seed(self, seed):
		self.seed = seed
		random.seed(self.seed)
		print("Seed:", seed)

	def make_input(self):
		next_seed = gen_seed()
		ipt = {
			"alpha": self.alpha,
			"num_inference_steps": self.num_inference_steps,
			"seed_image_id": self.seed_image_id,
			"start": {
				"prompt": self.prompt,
				"seed": self.play_seed,
				"denoising": self.denoising,
				"guidance": self.guidance
			},
			"end": {
				"prompt": self.prompt,
				"seed": next_seed,
				"denoising": self.denoising,
				"guidance": self.guidance
			}
		}
		self.play_seed = next_seed
		return ipt

	def get_response(self):
		rtext = requests.post(self.url, json=self.make_input()).text
		resp = json.loads(rtext)
		return [base64.b64decode(resp["image"][23:]), base64.b64decode(resp["audio"][23:])]

	def save_response(self, resp, img_path="./mel.jpg", audio_path="./result.mp3"):
		with open(img_path, "wb") as f:
			f.write(resp[0])

		with open(audio_path, "wb") as f:
			f.write(resp[1])

	def play_result_audio(self, audio_path="./result.mp3"):
		play(AudioSegment.from_mp3(audio_path) - 24)

	def oneshot(self):
		self.save_response(self.get_response())
		print(self.prompt)
		self.play_result_audio()

if __name__ == '__main__':
	prompt = "down tempo, lofi beats"  # input("> Prompt: ")

	generator = Generator(prompt)
	generator.oneshot()
