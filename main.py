import imageio
import numpy
import argparse
import os
import soundfile
from mutagen.mp3 import MP3
import math
import random
import PIL
import moviepy.editor as mpy

GIF_PATH = '/home/samday/Pictures/random_gifs'
FPS = 24
RATE = 4 #half-bar/2 beats
OUT_GIF = 'out.gif'
OUT_TMP = 'tmp.mp4'
OUT_MOVIE = 'out_unsynced.mp4'
SIZE=(750,750)

class ImageItem:
    def __init__(self, uri=''):
        self.uri = uri
        self.start = 0
        self.end = None

        self.synced = False
        self.num_loops = 1

        self.reader = imageio.get_reader(self.uri)
        self.length = self.reader.get_length()
        self.end = self.length

    def get_frame(self, index):
        im = PIL.Image.fromarray(self.reader.get_data(index))
        return numpy.asarray(im.resize(SIZE))

    def get_frames(self, num_frames):
        if num_frames < 1:
            return []
        elif num_frames == 1:
            return [self.get_frame(0)]

        if self.synced:
            frame_indices = [round(x*((((self.end-self.start)/self.num_loops)-1)/(num_frames-1))) for x in range(0,num_frames)]
            return [self.get_frame(x) for x in frame_indices]
        else:
            return [self.get_frame(x%(self.end-self.start)) for x in range(0, num_frames)]

parser = argparse.ArgumentParser()
parser.add_argument('audio')
# parser.add_argument('gifpath')
parser.add_argument('bpm', type=float)
args = parser.parse_args()

image_items = [ImageItem(os.path.join(GIF_PATH,x)) for x in os.listdir(GIF_PATH)]

if '.wav' in args.audio:
    sf = soundfile.SoundFile(args.audio)
    duration = len(sf)/sf.samplerate
elif '.mp3' in args.audio:
    duration = MP3(args.audio).info.length

total_frames = math.ceil(FPS*duration)
frame_rate=(1/FPS)
beat_rate=(1/(args.bpm/60))

frames = []
cut_points = []
current_frame = 0
current_time = 0
iter_rate = beat_rate*RATE
while current_time < duration:
    num_frames = round((current_time+iter_rate)/frame_rate)-current_frame
    if (num_frames + current_frame) > total_frames:
        num_frames = total_frames-current_frame

    cut_points.append(num_frames)
    frames.append(random.choice(image_items).get_frames(num_frames))

    current_time += iter_rate
    current_frame += num_frames

with imageio.get_writer(OUT_TMP, fps=FPS) as writer:
    for iframes in frames:
        for f in iframes:
            writer.append_data(f)

mpy.VideoFileClip(OUT_TMP).write_videofile(OUT_MOVIE, rewrite_audio=True, audio=args.audio)

print(cut_points)
# LIST_A = [1,2,3,4]