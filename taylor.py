"""
Taylor diagram (Taylor, 2001) test implementation.

This is a fork of Yannick Copin's <yannick.copin@laposte.net> script.

http://www-pcmdi.llnl.gov/about/staff/Taylor/CV/Taylor_diagram_primer.htm
"""

import numpy as NP
import matplotlib.pyplot as PLT
import random
import sys

class TaylorDiagram(object):
    """Taylor diagram: plot model standard deviation and correlation
    to reference (data) sample in a single-quadrant polar plot, with
    r=stddev and theta=arccos(correlation).
    """

    def __init__(self, refsample):
        """refsample is the reference (data) sample to be compared to."""

        self.ref = NP.asarray(refsample)

    def setup_axes(self, fig, rect=111):
        """Set up Taylor diagram axes, i.e. single quadrant polar
        plot, using mpl_toolkits.axisartist.floating_axes.

        Wouldn't the ideal be to define its own non-linear
        transformation, so that coordinates are directly r=stddev and
        theta=correlation? I guess it would allow 
        """

        from matplotlib.projections import PolarAxes
        import mpl_toolkits.axisartist.floating_axes as FA
        import mpl_toolkits.axisartist.grid_finder as GF

        tr = PolarAxes.PolarTransform()

        # Correlation labels
        rlocs = NP.concatenate((NP.arange(10)/10.,[0.95,0.99]))
        tlocs = NP.arccos(rlocs)        # Conversion to polar angles
        gl1 = GF.FixedLocator(tlocs)    # Positions
        tf1 = GF.DictFormatter(dict(zip(tlocs, map(str,rlocs))))

        ghelper = FA.GridHelperCurveLinear(tr,
                                           extremes=(0,NP.pi/2, # 1st quadrant
                                                     0,1.5*self.ref.std()),
                                           grid_locator1=gl1,
                                           tick_formatter1=tf1,
                                           )

        ax = FA.FloatingSubplot(fig, rect, grid_helper=ghelper)
        fig.add_subplot(ax)

        # Adjust axes
        ax.axis["top"].set_axis_direction("bottom")  # "Angle axis"
        ax.axis["top"].toggle(ticklabels=True, label=True)
        ax.axis["top"].major_ticklabels.set_axis_direction("top")
        ax.axis["top"].label.set_axis_direction("top")
        ax.axis["top"].label.set_text("Correlation")

        ax.axis["left"].set_axis_direction("bottom") # "X axis"
        ax.axis["left"].label.set_text("Standard deviation")

        ax.axis["right"].set_axis_direction("top")   # "Y axis"
        ax.axis["right"].toggle(ticklabels=True)
        ax.axis["right"].major_ticklabels.set_axis_direction("left")

        ax.axis["bottom"].set_visible(False)         # Useless
        
        # Grid
        ax.grid()

        self._ax = ax                   # Graphical axes
        self.ax = ax.get_aux_axes(tr)   # Polar coordinates

        # Add reference point and stddev contour
        print "Reference std:", self.ref.std()
        self.ax.plot([0],self.ref.std(),'ko', label='_')
        t = NP.linspace(0,NP.pi/2)
        r = NP.zeros_like(t) + self.ref.std()
        self.ax.plot(t,r,'k--', label='_')

        return self.ax

    def get_coords(self, sample):
        """Computes theta=arccos(correlation),rad=stddev of sample
        wrt. reference sample."""

        std = NP.std(sample)
        corr = NP.corrcoef(self.ref, sample) # [[1,rho],[rho,1]]
        theta = NP.arccos(corr[0,1])

        print "Sample std,rho:",std,corr[0,1]

        return theta,std

    def plot_sample(self, sample, *args, **kwargs):
        """Add sample to the Taylor diagram. args and kwargs are
        directly propagated to the plot command."""

        t,r = self.get_coords(sample)
        l, = self.ax.plot(t,r, *args, **kwargs) # (theta,radius)

        return l


if __name__=='__main__':
    colors = ['b', 'g', 'r', 'c', 'm', 'y']
    diagram = None

    data = [line.strip() for line in open("values.txt", 'r')]
    for line in data:
        if not line.startswith("#"):
            plot_values = []
            plot_name = line.split()[0]

            values = line.split("= ")[1]
            for value in values.split(", "):
                plot_values.append(float(value))

            if diagram is None:
                x = NP.linspace(0,4*NP.pi,len(plot_values))
                dia = TaylorDiagram(plot_values)
                fig = PLT.figure(figsize=(10,4))
                ax1 = fig.add_subplot(1,2,1, xlabel='X', ylabel='Y')
                ax2 = dia.setup_axes(fig, 122)
                diagram = True

            color = random.choice(colors)
            colors.remove(color)

            try:
                if "data" in plot_name:
                    ax1.plot(x,plot_values,'ko',label='Data')
                    dia.plot_sample(plot_values, ('ko'))
                else:
                    ax1.plot(x,plot_values, (color+'-'), label=plot_name.upper())
                    dia.plot_sample(plot_values, (color+'o'))
            except ValueError, e:
                print("Error: \nCheck if your data has the same length amongst all models")
                print(e)
                sys.exit()
    
    ax1.legend(numpoints=1, prop=dict(size='small'), loc='best')

    PLT.show()