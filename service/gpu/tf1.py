# ---------------------- 
#
# run inference script
#    by follow the config.txt
# ----------------------

import os
import json
import numpy
import base64
import datetime
import tensorflow as tf
from tensorflow.python.platform import gfile

try:
    import gpu_utils
    gpu_exist = 1
except:
    print("no gpu_utils")
    gpu_exist = 0


try:
    from pynvml import *
except:
    print("no pynvml")


Workable = 1
PATH = os.path.dirname(os.path.abspath(__file__)) + '/models/'


class tf_inference():
	def readConfig(self):
		global PATH
		with open('config.json', 'rt') as f:
			js = json.load(f)
			version = 0
			for models in js:
				try: 
					version = models['version']
				except:
					dirs = os.listdir(models['base_path'])
					dirs.sort()
					version = int(float(dirs[-1]))
				path = models['base_path'] + '/' + str(version)
				pb_file = path + "/saved_model.pb"
				#with gfile.FastGFile(pb_file, 'rb') as pb:
				print(pb_file)
				with open(pb_file, 'rb') as pb:
					graph_def = tf.GraphDef()
					graph_def.ParseFromString(pb.read())
					print("-" * 30)
					print(graph_def)
					print("-" * 30)
				
                keys = dict()
				input_key = []
				output_key = []
				input_key.append('image_bytes')
				output_key.append('probabilities') 
				output_key.append('classes')
				keys['input'] = input_key
				keys['output'] = output_key
				keys['path'] = path
				keys['version'] = int(float(version))
				#print('keys = ', keys)
				#print('models = ', models['name'])
				self.modelConfigs[models['name']] = keys
				#with tf.device(	
				meta_graph_def = tf.saved_model.load(self.sess,['serve'],path)
				self.meta_graph_defss[models['name']] = meta_graph_def
	

    def detect_gpu(self):
		nvmlInit()
		self.freeGPU = []
		try:
			nvmlDeviceGetCount()
		except NVMLError as error:
			print(error)
		deviceCount = nvmlDeviceGetCount()

		print("deviceCount = ", deviceCount)
		for i in range(deviceCount):
			handle = nvmlDeviceGetHandleByIndex(i)
			mem = nvmlDeviceGetMemoryInfo(handle)
			print(mem.free/mem.total)
			if (mem.free/mem.total) >= 0.5:
				self.freeGPU.append(i)
        
		os.environ["CUDA_DEVICE_ORDER"]="PCI_BUS_ID"
		if self.freeGPU != '':
			os.environ["CUDA_VISIBLE_DEVICES"]=str(self.freeGPU[0])
			print(self.freeGPU[0])
       
		self.gpu_options = tf.GPUOptions(per_process_gpu_memory_fraction=memory*0.9)



	def __init__(self, memory):
        
        self.detect_gpu() # self Func

		self.config=tf.ConfigProto(log_device_placement=False)
		self.sess = tf.Session(graph=tf.Graph(), config=self.config)
		
		self.meta_graph_defss = dict()
		self.modelConfigs = dict()
		self.readConfig()  # self Func
    
		self.signature_key = 'predict'
		self.input_key = 'image_bytes'
		self.output_key = []
		self.output_key.append('probabilities')
		self.output_key.append('classes')

	def config_model(self,modelName):
		with open('config.json', 'rt') as f:
			path = ""
			j = json.load(f)
			serialNumber = 1
			
			#print(j[0])
			for name in j:
				#print(name['name'])
				if name['name'] == modelName:
					try:
						serialNumber = name['version']
					except:
						l = os.listdir(name['base_path'])
						l.sort()
						#print(l[-1])
						serialNumber = int(float(l[-1]))
					path = name['base_path']
		return serialNumber
	
    def deeper(self, path, listofInference, modelName):
		global Workable
        Workable = 0
        signature = self.meta_graph_defss[modelName].signature_def
		x_tensor_name = signature[self.signature_key].inputs[self.input_key].name
		y = []
		y_tensor_name = []
		y_tensor_name.append(signature[self.signature_key].outputs[self.output_key[0]].name)
		y_tensor_name.append(signature[self.signature_key].outputs[self.output_key[1]].name)
		x = self.sess.graph.get_tensor_by_name(x_tensor_name)

		y.append(self.sess.graph.get_tensor_by_name(y_tensor_name[0]))
		y.append(self.sess.graph.get_tensor_by_name(y_tensor_name[1]))
		
		output = []
    
		for l in listofInference.getlist('file'):
			data = l.stream.read()

			c = self.sess.run( y , feed_dict={x:(data,)})
			
            for i in range(len(c)):
				if isinstance(c[i][0], numpy.ndarray):
					output.append( { self.output_key[i]: c[i][0].tolist()} )	
				elif isinstance(c[i][0], numpy.int64):
					#print(type(c[i][0].item()))
					output.append( { self.output_key[i]: c[i][0].item()} )	
				else:
					output.append( { self.output_key[i]: c[i][0]} )	
			
			tf.reset_default_graph()
        Workable = 1
		return output


	def infer(self, modelName, listofInference):
		global PATH
		self.modelName = modelName
		print(self.modelName)
		serial = self.config_model(modelName)
		path = PATH + modelName + '/' + str(serial)
		re = self.deeper(path, listofInference, modelName)
		return re

