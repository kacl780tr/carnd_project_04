import numpy as np
import calibration as cam
import components as cmp
import tools_image as tim
import tools_search as tsr


class Configuration(object):
	def __init__(self):
		self.trace = False
		self.trace_handler = None
		self.camera_file = "./calibration.p"


class Pipeline(object):
	"""
	Class to manage the processing pipeline
	"""
	def __init__(self, configuration):
		assert configuration is not None, "Pipeline configuration not available" 
		self.__config = configuration
		self.__camera = cam.calibration_retrieve(self.__config.camera_file)
		assert self.__camera is not None, "Camera calibration unavailable in file {}".format(self.__config.camera_file)
		self.__region = cmp.RegionBuilder()
		self.__path = tsr.PathFunctionBuilder()
		self.__binary = cmp.BinaryImageSobelSMHChannel()	# setup the binary image maker
		self.__trace = None
		if self.__config.trace:
			self.__trace = []								# set an empty list to retain processing steps
			self.__region.trace = self.__trace				# also set for region builder

	def __trace_reset(self):
		if self.__trace is not None:
			self.__trace = []
			self.__region.trace = self.__trace

	def __add_info(self, frame, path_function):
		dev = path_function.deviation()
		crv = path_function.realspace_path().curvature()
		text = "lane curvature {:>8.0f}m - deviation {:>2.2f}m to the {}"
		if dev[1] >= 0:
			side = "right"
		else:
		   side = "left"
		tim.draw_textpath(frame, text.format(crv, np.abs(dev[1]), side))

	def __process_main(self, frame):
		frame_corr = self.__camera.apply_correction(frame)									# apply camera correction
		region = self.__region.build_region(frame_corr)
		self.__region.previous = region														# set region for use with next frame
		binary = self.__binary.make_binary(frame_corr)
		binary_tfm = region.get_transform().apply(binary)
		path_function = self.__path.build_path(binary_tfm, anchor_points=region.anchor())	# extract path function from binary image
		self.__path.previous_path = path_function											# set region for use with next frame
		path_tfm = path_function.draw()														# draw path function template
		path_norm = region.get_transform().unapply(path_tfm)
		final = tim.make_overlay(frame_corr, path_norm)
		self.__add_info(final, path_function)
		return final

	def __process_trace(self, frame):
		self.__trace.append((frame, "raw"))
		frame_corr = self.__camera.apply_correction(frame)									# apply camera correction
		self.__trace.append((frame_corr, "corrected"))
		region = self.__region.build_region(frame_corr)
		self.__region.previous = region														# set region for use with next frame
		frame_region = np.copy(frame_corr)
		tim.draw_linepath(frame_region, region.get_source())
		self.__trace.append((frame_region, "region"))
		binary = self.__binary.make_binary(frame_corr)
		self.__trace.append((binary, "binary"))
		binary_tfm = region.get_transform().apply(binary)
		self.__trace.append((binary_tfm, "binary_transform"))
		path_function = self.__path.build_path(binary_tfm, anchor_points=region.anchor())	# extract path function from binary image
		self.__path.previous_path = path_function											# set region for use with next frame
		path_tfm = path_function.draw()
		self.__trace.append((path_tfm, "path_transform"))
		path_overlay = region.get_transform().unapply(path_tfm)
		self.__trace.append((path_overlay, "path_normal"))
		final = tim.make_overlay(frame_corr, path_overlay)
		self.__add_info(final, path_function)
		self.__trace.append((final, "final"))
		if self.__config.trace_handler is not None:
			self.__config.trace_handler.run(self.__trace)
		return final

	def has_trace(self):
		return bool(self.__trace is not None)

	def get_trace(self):
		return self.__trace

	def process(self, frame):
		if self.has_trace():
			self.__trace_reset()																# reset the trace
			return self.__process_trace(frame)
		else:
			return self.__process_main(frame)

	def reset_pipeline(self):
		self.__region.previous = None
		self.__path.previous_path = None



class TraceHandler(object):
	def run(self, trace):
		raise NotImplementedError
		