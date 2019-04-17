"""
This is adapted from Tensorflow (https://github.com/tensorflow/models/tree/master/research/object_detection);
Save this code under the directory `models/research/object_detection/`
To use, run:
python tf_od_predict.py --model_name=building_od_ssd \
                         --path_to_label=data/building_od.pbtxt \
                         --test_image_path=test_images
"""
#python tf_od_predict.py --model_name=inference_graph --path_to_label=training\labelmap.pbtxt --test_image_path=images
import os
from os import makedirs, path as op
import sys
import glob
import six.moves.urllib as urllib
import tensorflow as tf
import tarfile

from io import StringIO
import zipfile
import numpy as np
from collections import defaultdict
from matplotlib import pyplot as plt
from PIL import ImageDraw, Image

sys.path.append("..")

from object_detection.utils import label_map_util
from object_detection.utils import visualization_utils as vis_util

from pascal_voc_writer import Writer

flags = tf.app.flags
flags.DEFINE_string('model_name', '', 'Path to frozen detection graph')
flags.DEFINE_string('path_to_label', '', 'Path to label file')
flags.DEFINE_string('test_image_path', '', 'Path to test imgs and output diractory')
FLAGS = flags.FLAGS



def load_image_into_numpy_array(image):
    (im_width, im_height) = image.size
    return np.array(image.getdata()).reshape((im_height, im_width, 3)).astype(np.uint8)

def tf_od_pred():
    with detection_graph.as_default():
        with tf.Session(graph=detection_graph) as sess:
            # Definite input and output Tensors for detection_graph
            image_tensor = detection_graph.get_tensor_by_name('image_tensor:0')
            # Each box represents a part of the image where a particular object was detected.
            detection_boxes = detection_graph.get_tensor_by_name('detection_boxes:0')
            # Each score represent how level of confidence for each of the objects.
            # Score is shown on the result image, together with the class label.
            detection_scores = detection_graph.get_tensor_by_name('detection_scores:0')
            detection_classes = detection_graph.get_tensor_by_name('detection_classes:0')
            num_detections = detection_graph.get_tensor_by_name('num_detections:0')
            for image_path in test_imgs:
                image = Image.open(image_path)
                image_np = load_image_into_numpy_array(image)
                # the array based representation of the image will be used later in order to prepare the
                # result image with boxes and labels on it.
                # Expand dimensions since the model expects images to have shape: [1, None, None, 3]
                image_np_expanded = np.expand_dims(image_np, axis=0)
                # Actual detection.
                (boxes, scores, classes, num) = sess.run(
                  [detection_boxes, detection_scores, detection_classes, num_detections],
                  feed_dict={image_tensor: image_np_expanded})
                 # draw_bounding_box_on_image(image, boxes, )
                 # Visualization of the results of a detection.
				 
				 #Uncomment this code to output labeled images
                '''
                vis_image = vis_util.visualize_boxes_and_labels_on_image_array(
                         image_np,
                         np.squeeze(boxes),
                         np.squeeze(classes).astype(np.int32),
                         np.squeeze(scores),
                         category_index,
                         use_normalized_coordinates=True,
                         line_thickness=1)
                print("{} boxes in {} image tile!".format(len(boxes), image_path))
                image_pil = Image.fromarray(np.uint8(vis_image)).convert('RGB')
                with tf.gfile.Open(image_path, 'w') as fid:
                    image_pil.save(fid, 'PNG')
                '''

				
				#This is the only code i added
				#get image height and width for each image
                (im_height, im_width) = image.size
				#Sort List by x values
				#1.zip scores and boxes together
                zip_boxes = np.array(list(zip(boxes[0], scores[0], classes[0])))
				#sort the ziped (boxes and scores)by x values
                soreted_zip_boxes = sorted(zip_boxes, key=lambda x: x[0][1])
				#unzip the sorted boxes into scores 
                unzip_boxes = list(zip(*soreted_zip_boxes))
                boxes = [(unzip_boxes[0])]
                scores = [(unzip_boxes[1])]
                classes = [(unzip_boxes[2])]
				#creat list of scores above 0.5 for each box 
                lst = np.where(np.squeeze(scores) > 0.5)
				# Writer(path, width, height)
                writer = Writer(image_path + "/*.jpg", im_width, im_width)
                for i in lst[0]:
						# ::addObject(name, xmin, ymin, xmax, ymax)
                        writer.addObject(category_index [(np.squeeze(classes)[i])]['name'],
                        int(np.squeeze(boxes)[i][3]*im_height), int(np.squeeze(boxes)[i][2]*im_width),
                        int(np.squeeze(boxes)[i][1]*im_height), int(np.squeeze(boxes)[i][0]*im_width))
			    # ::save(path)
                writer.save(image_path.replace(".jpg", ".xml"))
                print(image_path.replace(".jpg", ".xml"))
				
				
				
if __name__ =='__main__':
    # load your own trained model inference graph. This inference graph was generated from
    # export_inference_graph.py under model directory, see `models/research/object_detection/`
    model_name = op.join(os.getcwd(), FLAGS.model_name)
    # Path to frozen detection graph.
    path_to_ckpt = op.join(model_name,  'frozen_inference_graph.pb')
    # Path to the label file
    path_to_label = op.join(os.getcwd(), FLAGS.path_to_label)
    #only train on buildings
    num_classes = 10
    #Directory to test images path
    test_image_path = op.join(os.getcwd(), FLAGS.test_image_path)
	#test_imgs1 = glob.glob(test_image_path + "/*")
    test_imgs = glob.glob(test_image_path + "/*.jpg")

    ############
    #Load the frozen tensorflow model
    #############

    detection_graph = tf.Graph()
    with detection_graph.as_default():
        od_graph_def = tf.GraphDef()
        with tf.gfile.GFile(path_to_ckpt, 'rb') as fid:
            serialized_graph = fid.read()
            od_graph_def.ParseFromString(serialized_graph)
            tf.import_graph_def(od_graph_def, name='')

    ############
    #Load the label file
    #############
    label_map = label_map_util.load_labelmap(path_to_label)
    categories = label_map_util.convert_label_map_to_categories(label_map, max_num_classes=num_classes, use_display_name=True)
    category_index = label_map_util.create_category_index(categories)
    tf_od_pred()