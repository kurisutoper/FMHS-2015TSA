def decision(planets, alignment):
  transfers = []
  for i in range(0, len(planets)):
    if planets[i].population < 10: continue
    if planets[i].alignment == alignment:
      for j in range(0, len(planets)):
        if planets[j].alignment != alignment:
          transfers.append([i, j])
  return transfers
