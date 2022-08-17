import ezdxf
from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
from ezdxf.addons.drawing import Frontend, RenderContext

import matplotlib.pyplot as plt
import matplotlib as mpl

doc = ezdxf.readfile('C:/Users/Matt Dewar/Dropbox/Git/Ka-Boost/lib/draw/src/dxf/test.dxf')
msp = doc.modelspace()
auditor = doc.audit()

if len(auditor.errors) == 0:
  fig = plt.figure()
  ax = fig.add_axes([0, 0, 1, 1])
  ctx = RenderContext(doc)
  ctx.set_current_layout(msp)

  out = MatplotlibBackend(ax)
  Frontend(ctx, out).draw_layout(msp, finalize=True)

  plt.show()
