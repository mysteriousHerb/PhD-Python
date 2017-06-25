# cd to the directory

import tm4.simClasses as sim
import matplotlib.pyplot as plt
import numpy as np
from tm4.colourTools import specToRGB




class chiral_nematic_simulation():
    def __init__(self):
        # simulation wavelength range
        self.wlRange = np.linspace(400,800,300)
        pass

    def materials(self):
        self.CNC = sim.UniaxialMaterial(1.586,1.524) # this might not be right
        self.air = sim.HomogeneousNondispersiveMaterial(1)
        self.cellulose = sim.HomogeneousNondispersiveMaterial(1.55)
        # Set the glass as a practical backend
        self.glass = sim.HomogeneousNondispersiveMaterial(1.55)
        self.front = sim.IsotropicHalfSpace(self.air)
        self.airhalf= sim.IsotropicHalfSpace(self.air)
        self.glasshalf = sim.IsotropicHalfSpace(self.glass)

        # set space before and after the sample
        self.s = sim.OptSystem()
        # set space before and after the sample
        self.s.setHalfSpaces(self.airhalf ,self.glasshalf)
        


    def simple_film(self):
        # helicoidal structure with CNC, pitch and thickness
        heli = sim.HeliCoidalStructure
        h1 = heli(self.CNC,180,1000)
        # set structure for simulation
        self.s.setStructure([h1])
        result = self.s.scanSpectrum(self.wlRange)
        plt.plot(result[0],result[1], color = specToRGB(result))
        

    def chiral_nematic_film(self, materials, half_pitch = 180, thickness = 1000):
        # helicoidal structure with CNC, pitch and thickness
        heli = sim.HeliCoidalStructure
        h1 = heli(materials, half_pitch, thickness)
        # set structure for simulation
        self.s.setStructure([h1])
        result = self.s.scanSpectrum(self.wlRange)
        plt.plot(result[0],result[1], color = specToRGB(result))
        
        

    def plot_spectrum(self):
        plt.rcParams['figure.figsize'] = (8,6)
        plt.rcParams['savefig.dpi'] = 100
        # change font size, axis  etc..
        plt.show()

    def CNC_water_mixture_refractive_index(self, water_volume_fraction):
        water = 1.33
        CNC = (1.586, 1.524)
        # dielectric constant epsilon is sqrt of refractive index
        # for composite materials, dielectric constant calculation: 
        # e = e1*v1 + e2*v2  v is the volume fraction   http://www.sciencedirect.com/science/article/pii/S0030401899006951
        CNC_water_mixture  = (np.square(np.sqrt(CNC[0])*(1-water_volume_fraction)+np.sqrt(water)*water_volume_fraction),
                            np.square(np.sqrt(CNC[1])*(1-water_volume_fraction)+np.sqrt(water)*water_volume_fraction))

        self.CNC_water_mixture  = sim.UniaxialMaterial(CNC_water_mixture[0], CNC_water_mixture[1])
        return self.CNC_water_mixture
        



chiral_simulation = chiral_nematic_simulation()
chiral_simulation.materials()

# for swelling with only pitch change (the number of repeats stayed the same)
'''for half_pitch in [100,150,200,250]:
    pseudo_layers = 20
    chiral_simulation.chiral_nematic_film(materials = chiral_simulation.CNC, half_pitch = half_pitch, thickness = pseudo_layers*half_pitch)
'''

# for swelling with only refractive index change
for water_volume_fraction in [0,0.05,0.1,0.15,0.2,0.3,0.4,0.5,0.6]:
    pseudo_layers = 25
    original_half_pitch = 140
    swollen_thickness = original_half_pitch*pseudo_layers/(1-water_volume_fraction)
    swollen_half_pitch = swollen_thickness/pseudo_layers
    CNC_water_mixture = chiral_simulation.CNC_water_mixture_refractive_index(water_volume_fraction)
    chiral_simulation.chiral_nematic_film(materials = CNC_water_mixture, half_pitch = original_half_pitch, thickness = original_half_pitch*pseudo_layers)


'''# for swelling with both refractive index change and pitch change
for water_volume_fraction in [0,0.05,0.1,0.15,0.2,0.3,0.4,0.5,0.6]:
    pseudo_layers = 25
    original_half_pitch = 140
    swollen_thickness = original_half_pitch*pseudo_layers/(1-water_volume_fraction)
    swollen_half_pitch = swollen_thickness/pseudo_layers
    CNC_water_mixture = chiral_simulation.CNC_water_mixture_refractive_index(water_volume_fraction)
    chiral_simulation.chiral_nematic_film(materials = CNC_water_mixture, half_pitch = swollen_half_pitch, thickness = swollen_thickness)

'''



chiral_simulation.plot_spectrum()
