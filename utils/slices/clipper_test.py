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

subj = [
    [[180, 200], [260, 200], [260, 150], (180, 150)],
    [[215, 160], [230, 190], [200, 190]]
]

clip = [[190, 210],[240, 210], [240, 130], [190, 130]]

original = []
for s in subj:
  codes = [(Path.MOVETO if i == 0 else Path.LINETO) for i in range(len(s))]
  s.append(s[0])
  codes.append(Path.CLOSEPOLY)
  original.append(Path(s , codes))

codes = [(Path.MOVETO if i == 0 else Path.LINETO) for i in range(len(clip))]
clip.append(clip[0])
codes.append(Path.CLOSEPOLY)
original.append(Path(clip, codes))

pc = pyclipper.Pyclipper()
pc.AddPath(clip, pyclipper.PT_CLIP, True)
pc.AddPaths(subj, pyclipper.PT_SUBJECT, True)

solution = pc.Execute(pyclipper.CT_INTERSECTION, pyclipper.PFT_EVENODD, pyclipper.PFT_EVENODD)

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
  patch = patches.PathPatch(o, facecolor=color, alpha=0.5, lw=2)
  ax.add_patch(patch)

plt.show(block=False)

fig2, ax2 = plt.subplots()
ax2.grid()
ax2.set_xlim(0, 300)
ax2.set_ylim(0, 300)

for p in path:
  color = random_color_gen()
  color = list(map(lambda i: i*1.0/255, color))
  patch = patches.PathPatch(p, facecolor=color, alpha=1, lw=2)
  ax2.add_patch(patch)

plt.show(block=True)

