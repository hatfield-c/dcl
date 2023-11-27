
import time
import cv2
import os
import glob

class config_class:
	def __init__(self):

		self.vid_path = "data/render/out.mp4"
		self.fps = 60
		self.img_size = (256,256)

		self.frame_path = "data/render/frames/"

		self.print_every_frame = 100

class VideoBuilder:
	def __init__(self):
		self.config = config_class()

	def write_video(self):
		CONFIG = self.config

		writePath = CONFIG.vid_path

		print("Writing video at: " + writePath)

		start_time = time.time()

		paths = self.frame_paths()
		frame_count = len(paths)

		writer = cv2.VideoWriter(
			writePath,
			cv2.VideoWriter_fourcc('m', 'p', '4', 'v'),
			CONFIG.fps,
			(CONFIG.img_size[0], CONFIG.img_size[1])
		)

		print("Frame count:", frame_count)
		for i in range(frame_count):
			if i % CONFIG.print_every_frame == 0:
				print("Frame:", i, "  {:.2f}".format((i / frame_count) * 100) + "% finished.")

			f_path = paths[i]

			img = cv2.imread(f_path)

			if img is None:
				print("\n\nERROR: Image not found:")
				print("   ", f_path, "\n\n")

			img = cv2.resize(img, (CONFIG.img_size[0], CONFIG.img_size[1]), interpolation = cv2.INTER_NEAREST)

			writer.write(img)

		writer.release()

		print("Total write time: " + str(time.time() - start_time))

	def frame_paths(self):
		contents = list(filter(os.path.isfile, glob.glob(self.config.frame_path + "*")))
		contents.sort(key = os.path.getmtime)

		return contents
