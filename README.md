# pascal_voc_labeler
Uses tensorflow detection graph (.pb file) to generate labels in pascal Voc format



This is adapted from Tensorflow (https://github.com/tensorflow/models/tree/master/research/object_detection);



To use, run:
python tf_od_predict.py --model_name=inference_graph \
                         --path_to_label=training/label_map.pbtxt \
                         --test_image_path=images
                         
                         
                         
