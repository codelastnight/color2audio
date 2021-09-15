import numpy as np
import cv2
import mido 

# barcodes
qrDecoder = cv2.QRCodeDetector()
# Capturing video through webcam
webcam = cv2.VideoCapture(0)
#open midi ports

ports = mido.get_output_names()

outport = mido.open_output(ports[1])

colorBGR = {
        "red": (0,0,255),
        "green": (0,255,0),
        "blue": (255,0,0)
    }

colorRange = {
    "red": {
        "lower": [136, 87, 111],
        "upper": [180, 255, 255]
    },
    "green": {
        "lower": [25, 52, 72],
        "upper": [102, 255, 255]
    },
    "blue": {
        "lower": [94, 80, 2],
        "upper": [120, 255, 255]
    }
}

lastOn =[]

# convert array into uint8
def uintArr(input):
    return np.array(input, np.uint8)

# Start a while loop
while(1):
      
    # Reading the video from the webcam
    _, imageFrame = webcam.read()
  
    #block out certain parts
    dimensions = imageFrame.shape
    width = int((dimensions[1] / 2))
    height = dimensions[0]
    imageFrame = cv2.rectangle(imageFrame, (0, 0), (width,height), (0,0,0), -1)
    
    # Convert the imageFrame from BGR to HSV
    hsvFrame = cv2.cvtColor(imageFrame, cv2.COLOR_BGR2HSV)

    #masks dict
    masks = {}

    #define color ranges
    for color in colorRange.keys():
        masks[color] = cv2.inRange(hsvFrame, uintArr(colorRange[color]["lower"]), uintArr(colorRange[color]["upper"]))
    
    # Morphological Transform, Dilation
    # for each color and bitwise_and operator between imageFrame and mask determines to detect only that particular color
    kernal = np.ones((5, 5), "uint8")
    
    #result dict
    res = {}

    for color in colorRange.keys():
        masks[color] = cv2.dilate(masks[color], kernal)
        res[color] =   cv2.bitwise_and(imageFrame, imageFrame, 
                              mask = masks[color])
 
    # Creating contour to track red color
    audioMsg = []
    currentOn = []
    for color in colorRange.keys():
        
        contours, hierarchy = cv2.findContours(masks[color],
                                            cv2.RETR_TREE,
                                            cv2.CHAIN_APPROX_SIMPLE)

        for pic, contour in enumerate(contours):
            area = cv2.contourArea(contour)
            if(area > 600):
                x, y, w, h = cv2.boundingRect(contour)

                note =40 +  int((y + h/2) /height * 60)
                note = int(note /2) *2 +1
                #print (note)
                msg = mido.Message('note_on', note= note)
                audioMsg.append(msg)
                currentOn.append(note)
                imageFrame = cv2.rectangle(imageFrame, (x, y), 
                                        (x + w, y + h), 
                                        colorBGR[color], 2)
                
                cv2.putText(imageFrame, color, (x, y),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.0,
                            colorBGR[color])  
        
        for note in lastOn:
            msg = mido.Message('note_off', note= note)
            audioMsg.append(msg)

        lastOn = currentOn
        for msg in audioMsg:
            outport.send(msg)
        

  
    #----------------
  
              
    # Program Termination
    cv2.imshow("color2audio", imageFrame)
    if cv2.waitKey(10) & 0xFF == ord('q'):
        for note in lastOn:
            msg = mido.Message('note_off', note= note)
            audioMsg.append(msg)
        outport.close()
        cap.release()
        cv2.destroyAllWindows()
        break