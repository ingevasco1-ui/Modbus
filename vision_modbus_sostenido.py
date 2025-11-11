import cv2
import mediapipe as mp
from math import dist
from pymodbus.client import ModbusTcpClient

client = ModbusTcpClient('192.168.0.1', port=502)
client.connect()

mpHands = mp.solutions.hands
hands = mpHands.Hands(max_num_hands=1, min_detection_confidence=0.7, min_tracking_confidence=0.7)
mpDraw = mp.solutions.drawing_utils

dedos = {"indice":[6,8], "anular":[10,12], "mayor":[14,16], "menyque":[18,20]}
estado_dedos = [0, 0, 0, 0]
detection_activa = True

def pulgar_cerrado(hand_landmarks):
    return hand_landmarks.landmark[4].x >= hand_landmarks.landmark[5].x

def detectarDedo(hand_landmarks):
    global estado_dedos, detection_activa
    detection_activa = not pulgar_cerrado(hand_landmarks)
    
    if detection_activa:
        try:
            x_palma, y_palma = hand_landmarks.landmark[0].x, hand_landmarks.landmark[0].y
            for i, (medio, punta) in enumerate(dedos.values()):
                x_medio, y_medio = hand_landmarks.landmark[medio].x, hand_landmarks.landmark[medio].y
                x_punta, y_punta = hand_landmarks.landmark[punta].x, hand_landmarks.landmark[punta].y
                d_medio = dist([x_palma, y_palma], [x_medio, y_medio])
                d_punta = dist([x_palma, y_palma], [x_punta, y_punta])
                estado_dedos[i] = 1 if d_punta > d_medio else 0
        except: pass
    return estado_dedos

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret: break
    
    results = hands.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    
    if results.multi_hand_landmarks:
        for handLms in results.multi_hand_landmarks:
            detectarDedo(handLms)
            mpDraw.draw_landmarks(frame, handLms, mpHands.HAND_CONNECTIONS)
            
            for id, lm in enumerate(handLms.landmark):
                if id in [4,8,12,16,20]:
                    cx, cy = int(lm.x * frame.shape[1]), int(lm.y * frame.shape[0])
                    if id == 4:
                        color = (0,0,255) if not detection_activa else (0,255,0)
                        cv2.circle(frame, (cx,cy), 12, color, 2)
                    else:
                        idx = [8,12,16,20].index(id)
                        color = (0,255,0) if estado_dedos[idx] == 1 else (0,0,255)
                        cv2.circle(frame, (cx,cy), 10, color, -1)

    client.write_coils(0, [bool(x) for x in estado_dedos], slave=1)
    
    estado_texto = "ACTIVA" if detection_activa else "MANTENIENDO"
    color_estado = (0,255,0) if detection_activa else (0,255,255)
    cv2.putText(frame, f"Dedos: {sum(estado_dedos)} - {estado_texto}", (20,30), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, color_estado, 2)
    
    cv2.imshow('Mano - Modbus', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'): break

client.close()
cap.release()
cv2.destroyAllWindows()