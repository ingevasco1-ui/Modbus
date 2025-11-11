import cv2
import mediapipe as mp
from math import dist
from pymodbus.client import ModbusTcpClient

client = ModbusTcpClient('192.168.0.1', port=502)
client.connect()

mpHands = mp.solutions.hands
hands = mpHands.Hands(max_num_hands=2, min_detection_confidence=0.7, min_tracking_confidence=0.7)
mpDraw = mp.solutions.drawing_utils

ultimo_valor = 0
sosteniendo = False

def puños_cerrados(hand_landmarks_list):
    if not hand_landmarks_list: return False
    for hand in hand_landmarks_list:
        dedos_cerrados = sum(1 for punta, base in [(8,6),(12,10),(16,14),(20,18)] 
                           if hand.landmark[punta].y > hand.landmark[base].y)
        if dedos_cerrados < 3: return False
    return True

def calcular_distancia(hand_landmarks_list):
    global ultimo_valor, sosteniendo
    puños_actual = puños_cerrados(hand_landmarks_list)
    
    if puños_actual and not sosteniendo:
        sosteniendo = True
    elif not puños_actual and sosteniendo:
        sosteniendo = False
    
    if sosteniendo:
        return ultimo_valor
    
    if len(hand_landmarks_list) == 2:
        p0, p1 = hand_landmarks_list[0].landmark[0], hand_landmarks_list[1].landmark[0]
        ultimo_valor = int(dist([p0.x, p0.y], [p1.x, p1.y]) * 200)
    elif len(hand_landmarks_list) == 1:
        ultimo_valor = 0
    
    return ultimo_valor

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret: break
    
    results = hands.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    
    if results.multi_hand_landmarks:
        d_mm = calcular_distancia(results.multi_hand_landmarks)
        for handLms in results.multi_hand_landmarks:
            mpDraw.draw_landmarks(frame, handLms, mpHands.HAND_CONNECTIONS)
    else:
        d_mm = ultimo_valor

    estado = "SOSTENIDO" if sosteniendo else "ACTIVO"
    cv2.putText(frame, f"Dist: {d_mm}mm - {estado}", (20, 30), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,255) if sosteniendo else (0,255,0), 2)
    
    client.write_register(2, d_mm, 1)
    cv2.imshow('Distancia Manos', frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'): break

client.close()
cap.release()
cv2.destroyAllWindows()