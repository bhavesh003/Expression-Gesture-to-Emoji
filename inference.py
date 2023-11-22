import cv2
import numpy as np
import mediapipe as mp
from keras.models import load_model

model = load_model("model.h5")
label = np.load("labels.npy")

def get_emoji(label):
    emojis = {
        
        "angry": "emojis/angry.png",
        "eye roll": "emojis/eye roll.png",
        "goodluck": "emojis/goodluck.png",
        "happy": "emojis/happy.png",
        "hi": "emojis/hi.png",
        "nope": "emojis/nope.png",
        "normal": "emojis/normal.png",
        "one": "emojis/one.png",
        "peace": "emojis/peace.png",
        "praying": "emojis/praying.png",
        "sleep": "emojis/sleep.png",
        "surprise": "emojis/surprise.png",
        "tongue out with wink": "emojis/tongue out with wink.png",
        "tongue": "emojis/tongue.png",
        "wink": "emojis/wink.png"
    }
    return emojis.get(label, "")


holistic = mp.solutions.holistic
hands = mp.solutions.hands
holis = holistic.Holistic()
drawing = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)

while True:
    lst = []

    _, frm = cap.read()

    frm = cv2.flip(frm, 1)

    res = holis.process(cv2.cvtColor(frm, cv2.COLOR_BGR2RGB))

    if res.face_landmarks:
        for i in res.face_landmarks.landmark:
            lst.append(i.x - res.face_landmarks.landmark[1].x)
            lst.append(i.y - res.face_landmarks.landmark[1].y)

        if res.left_hand_landmarks:
            for i in res.left_hand_landmarks.landmark:
                lst.append(i.x - res.left_hand_landmarks.landmark[8].x)
                lst.append(i.y - res.left_hand_landmarks.landmark[8].y)
        else:
            for i in range(42):
                lst.append(0.0)

        if res.right_hand_landmarks:
            for i in res.right_hand_landmarks.landmark:
                lst.append(i.x - res.right_hand_landmarks.landmark[8].x)
                lst.append(i.y - res.right_hand_landmarks.landmark[8].y)
        else:
            for i in range(42):
                lst.append(0.0)

        lst = np.array(lst).reshape(1, -1)

        pred = label[np.argmax(model.predict(lst))]

        emoji_path = get_emoji(pred)

        if emoji_path:
            emoji_img = cv2.imread(emoji_path)
            
            emoji_img = cv2.resize(emoji_img, (300, 300))

            frm[10:10 + emoji_img.shape[0], 10:10 + emoji_img.shape[1]] = emoji_img

        cv2.putText(frm, pred, (10, 10), cv2.FONT_HERSHEY_SIMPLEX, 0, (255, 0, 0), 0)

    drawing.draw_landmarks(frm, res.left_hand_landmarks, hands.HAND_CONNECTIONS)
    drawing.draw_landmarks(frm, res.right_hand_landmarks, hands.HAND_CONNECTIONS)

    cv2.imshow("window", frm)

    if cv2.waitKey(1) == 27:
        cv2.destroyAllWindows()
        cap.release()
        break
