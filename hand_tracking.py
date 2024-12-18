from time import time  # Correct import for time() function

import cv2
import mediapipe as mp

cap = cv2.VideoCapture(0)

pTime = 0
cTime = 0

mpHands = mp.solutions.hands
hands = mpHands.Hands()
mpDraw = mp.solutions.drawing_utils

while True:
    success, img = cap.read()
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(imgRGB)

    if results.multi_hand_landmarks:
        for handLms in results.multi_hand_landmarks:
            for id , lm in enumerate(handLms.landmark):
                print(id, lm)
                h, w , c = img.shape
                cx, cy  = int(lm.x*w), int(lm.y*h)
                print(id, cx, cy)
                if id == 7:
                    cv2.circle(img, (cx, cy), 10, (0, 255, 0), cv2.FILLED )


            mpDraw.draw_landmarks(img, handLms, mpHands.HAND_CONNECTIONS)

        # Calculate and display FPS
        cTime = time()  # Use time from the 'time' module
        fps = 1 / (cTime - pTime)
        pTime = cTime

        cv2.putText(img, str(int(fps)), (10, 90), cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 255), 3)

    cv2.imshow("image", img)
    cv2.waitKey(1)
