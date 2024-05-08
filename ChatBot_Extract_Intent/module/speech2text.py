
from transformers import pipeline
import librosa
import soundfile
import io, time
import os
os.environ['CURL_CA_BUNDLE'] = ''

transcriber = pipeline("automatic-speech-recognition", model = "vinai/PhoWhisper-small", device = "cpu")

def downsampleWav(sound, dst):
    y, s = librosa.load(sound, sr=16000)
    soundfile.write(dst, y, s)

def speech_2_text(path_audio):
    t0 = time.time()
    text = transcriber(path_audio)["text"]
    print('speech_2_text time: ',time.time() - t0)
    return text


