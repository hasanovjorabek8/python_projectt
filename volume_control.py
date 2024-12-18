import cv2
import time
import numpy as np
import hand_tracking_module as htm
import math
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL  # Corrected import
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

####################################
wCam, hCam = 1920, 1080  # Full HD resolution
####################################

cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)
pTime = 0

detector = htm.HandDetector(detectionCon=0.7)

# Setting up the audio interface for controlling volume
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)  # Corrected constant
volume = cast(interface, POINTER(IAudioEndpointVolume))

# Get the volume range for future control
volRange = volume.GetVolumeRange()
volume.SetMasterVolumeLevel(0,None)
minVol = volRange[0]
maxVol = volRange[1]
vol = 0
volBar = 400
print(volRange)

while True:
    success, img = cap.read()
    if not success:
        break

    # Detect hands in the frame
    img = detector.findHands(img)
    lmList = detector.findPosition(img, draw=False)

    if len(lmList) != 0:
        # Thumb and index finger landmarks
        x1, y1 = lmList[4][1], lmList[4][2]  # Thumb tip
        x2, y2 = lmList[8][1], lmList[8][2]  # Index finger tip
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2  # Midpoint between thumb and index

        # Draw circles and lines between thumb and index
        cv2.circle(img, (x1, y1), 10, (255, 0, 255), cv2.FILLED)
        cv2.circle(img, (x2, y2), 10, (255, 0, 255), cv2.FILLED)
        cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), 3)
        cv2.circle(img, (cx, cy), 10, (255, 0, 255), cv2.FILLED)

        # Calculate the length between thumb and index finger
        length = math.hypot(x2 - x1, y2 - y1)
        #print(length)

        #Hand range 50 - 265
        #Volume Range -65 - 0

        vol = np.interp(length,[50,215], [minVol, maxVol])
        volBar = np.interp(length,[50,215], [400, 150])

        print(int(length), vol)
        volume.SetMasterVolumeLevel(vol, None)

        if length < 50:
            cv2.circle(img, (cx, cy), 10, (0, 255, 0), cv2.FILLED)

        cv2.rectangle(img, (50, 150), (85, 400), (0, 255, 0), 3   )
        cv2.rectangle(img, (50, int(volBar)), (85, 400), (0, 255, 0), cv2.FILLED)

        # Map the length to the volume range
        vol = np.interp(length, [30, 300], [minVol, maxVol])  # Adjust range as needed
        volume.SetMasterVolumeLevel(vol, None)

    # Calculate FPS
    cTime = time.time()
    fps = 1 / (cTime - pTime) if cTime - pTime > 0 else 0  # Avoid division by zero
    pTime = cTime

    # Display FPS on the image
    cv2.putText(img, f'FPS: {int(fps)}', (40, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 3)

    # Show the image
    cv2.imshow('img', img)

    # Break the loop when 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()
