import math
def decision(planets, alignment):
    transfers = []
    for i in range(0, len(planets)):
        if planets[i].population < 10: continue
        min_distance = 0
        candidate = -1
        for j in range(0, len(planets)):
            if i != j:
                distance = math.sqrt(pow(planets[i].x-planets[j].x, 2)+
                                     pow(planets[i].y-planets[j].y, 2))
                if distance < min_distance or candidate == -1:
                    min_distance = distance
                    candidate = j
        if candidate != -1:
            transfers.append([i, candidate])
    return transfers
