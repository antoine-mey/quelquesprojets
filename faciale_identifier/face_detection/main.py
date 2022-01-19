# Use opencv to process images and detect faces thanks to haarcascade
import cv2

# load the image with faces
image = cv2.imread('dataset/test1.jpg')

# load the pre-trained model - Haar cascade
classifier = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

# Process the image to perform face detection
bboxes = classifier.detectMultiScale(image)

# Display bounding box for each detected face
for box in bboxes:
	# extract
	x, y, width, height = box
	x2, y2 = x + width, y + height
	# Draw a rectangle over the image to display the face area
	cv2.rectangle(image, (x, y), (x2, y2), (0,0,255), 1)

# Display the resulting image
cv2.imshow('face detection', image)

# Until we press a key keep the window opened
cv2.waitKey(0)

# Close the window and return to terminal
cv2.destroyAllWindows()


# What are the parameters to improve
# What are the specifications that you can give
# Advantages and problems