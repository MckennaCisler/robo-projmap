from maskrcnn_benchmark.config import cfg
from mask_rcnn_demo.predictor import COCODemo
import numpy as np
from kinect import Kinect

k = Kinect()
k.start()

config_file = "mask_rcnn_demo/maskrcnn-benchmark/configs/caffe2/e2e_mask_rcnn_R_50_FPN_1x_caffe2.yaml"

# update the config options with the config file
cfg.merge_from_file(config_file)
# manual override some options
cfg.merge_from_list(["MODEL.DEVICE", "cuda"])

coco_demo = COCODemo(
    cfg,
    min_image_size=800,
    confidence_threshold=0.7,
)
# load image and then run prediction

while True:
    print('a')
    image, d = k.get_current_rgbd_frame(copy=True)
    image = image[..., :3]
    print('d')
    predictions = coco_demo.run_on_opencv_image(image)
    print('c')
    print(predictions.shape, predictions.dtype)

k.stop()
