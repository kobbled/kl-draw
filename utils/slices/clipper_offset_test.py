import pyclipper
from random import randint

import matplotlib.pyplot as plt
from matplotlib.path import Path
import matplotlib.patches as patches

def random_color_gen():
  """Generates a random RGB color
  
  :return: 3 elements in the form [R, G, B]
  :rtype: list
  """
  r = randint(0, 255)
  g = randint(0, 255)
  b = randint(0, 255)
  return (r, g, b)

subj = [[180, 200], [260, 200], [260, 150], [180, 150]]

original = []
codes = [(Path.MOVETO if i == 0 else Path.LINETO) for i in range(len(subj))]
subj.append(subj[0])
codes.append(Path.CLOSEPOLY)
original.append(Path(subj, codes))

solution = []

pco = pyclipper.PyclipperOffset()
pco.AddPath(subj, pyclipper.JT_ROUND, pyclipper.ET_CLOSEDPOLYGON)
solution.extend(pco.Execute(-7.0))

pco = pyclipper.PyclipperOffset()
pco.AddPath(solution[0], pyclipper.JT_ROUND, pyclipper.ET_CLOSEDPOLYGON)
solution.extend(pco.Execute(-7.0))

path = []
for s in solution:
  codes = [(Path.MOVETO if i == 0 else Path.LINETO) for i in range(len(s))]
  s.append(s[0])
  codes.append(Path.CLOSEPOLY)
  path.append(Path(s , codes))

fig, ax = plt.subplots()
ax.grid()
ax.set_xlim(0, 300)
ax.set_ylim(0, 300)

for o in original:
  color = random_color_gen()
  color = list(map(lambda i: i*1.0/255, color))
  patch = patches.PathPatch(o, facecolor=color, alpha=1, lw=2)
  ax.add_patch(patch)

for p in path:
  color = random_color_gen()
  color = list(map(lambda i: i*1.0/255, color))
  patch = patches.PathPatch(p, facecolor=color, alpha=0.5, lw=2)
  ax.add_patch(patch)

plt.show(block=True)

