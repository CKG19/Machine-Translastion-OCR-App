from PIL import Image
import pytesseract
import keras_ocr
import math
import os

class MyOCRModels:
    def __init__(self):
        # self.recognizer_alphabet = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~"
        # self.keras_recognizer = keras_ocr.recognition.Recognizer(alphabet=self.recognizer_alphabet)
        # self.keras_recognizer.model.load_weights(f"C:\\Users\\M-S-I\\Documents\\IBDA Semester 8\\Skripsi\\Machine Learning\\model\\keras_ocr_weights\\recognizer_cocotext_19.h5")
        # self.keras_pipeline = keras_ocr.pipeline.Pipeline(recognizer=self.keras_recognizer)
        pass

    def ocr_with_tesseract(self, image):
        os.environ['TESSDATA_PREFIX'] = f"C:\\Program Files\\Tesseract-OCR\\tessdata_best"
        custom_config = r'--oem 1 --psm 3'
        return pytesseract.image_to_string(image, config=custom_config)

    def ocr_with_keras(self, image_path):
        # initialize model
        recognizer_alphabet = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~"
        recognizer = keras_ocr.recognition.Recognizer(alphabet=recognizer_alphabet)
        recognizer.model.load_weights(f"C:\\Users\\M-S-I\\Documents\\IBDA Semester 8\\Skripsi\\Machine Learning\\model\\keras_ocr_weights\\recognizer_cocotext_mid_freeze.h5")
        pipeline = keras_ocr.pipeline.Pipeline(recognizer=recognizer)

        image = keras_ocr.tools.read(image_path)

        # get predictions but predictions is not in human readable format
        prediction_groups = pipeline.recognize([image])

        # get distance of predictions
        predictions = self.get_distance(prediction_groups[0])

        # Set thresh higher for text further apart
        predictions = list(self.distinguish_rows(predictions, thresh=15))
        
        # Remove all empty rows
        predictions = list(filter(lambda x:x!=[], predictions))

        # Order text detections in human readable format
        ordered_preds = []
        for row in predictions:
            row = sorted(row, key=lambda x:x['distance_from_origin'])
            for each in row: ordered_preds.append(each['text'])
        
        chunk_size = 16
        result = "\n".join([" ".join(ordered_preds[i:i+chunk_size]) for i in range(0, len(ordered_preds), chunk_size)])

        return result
    
    def get_distance(self, predictions):
        """
        Function returns dictionary with (key,value):
            * text : detected text in image
            * center_x : center of bounding box (x)
            * center_y : center of bounding box (y)
            * distance_from_origin : hypotenuse
            * distance_y : distance between y and origin (0,0)
        """

        # Point of origin
        x0, y0 = 0, 0

        # Generate dictionary
        detections = []
        for group in predictions:

            # Get center point of bounding box
            top_left_x, top_left_y = group[1][0]
            bottom_right_x, bottom_right_y = group[1][1]
            center_x, center_y = (top_left_x + bottom_right_x)/2, (top_left_y + bottom_right_y)/2

            # Use the Pythagorean Theorem to solve for distance from origin
            distance_from_origin = math.dist([x0,y0], [center_x, center_y])

            # Calculate difference between y and origin to get unique rows
            distance_y = center_y - y0

            # Append all results
            detections.append({
                                'text': group[0],
                                'center_x': center_x,
                                'center_y': center_y,
                                'distance_from_origin': distance_from_origin,
                                'distance_y': distance_y
                            })
        return detections
    
    def distinguish_rows(self, lst, thresh=15):
        """Function to help distinguish unique rows"""
        sublists = []
        for i in range(0, len(lst)-1):
            if (lst[i+1]['distance_y'] - lst[i]['distance_y'] <= thresh):
                if lst[i] not in sublists:
                    sublists.append(lst[i])
                sublists.append(lst[i+1])
            else:
                yield sublists
                sublists = [lst[i+1]]
        yield sublists