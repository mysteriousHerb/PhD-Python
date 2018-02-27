#!/usr/bin/python
# encoding: utf-8

# Berreman4x4 example
# Author: O. Castany, C. Molinaro

# Example of a cholesteric liquid crystal

import numpy, Berreman4x4
from numpy import sin, sqrt, abs
from Berreman4x4 import c, pi, e_y, e_z, e_x
import matplotlib.pyplot as pyplot

# use pandas for data output 
import pandas as pd


class chiral_nematic_simulation():
    def __init__(self):
        # simulation wavelength range
        self.wavelength_range = (300e-9, 800e-9)   # range of simulation
        self.wavelength_list = numpy.linspace(self.wavelength_range[0], self.wavelength_range[1], 400) # number of calculated wavelength
        # Normal incidence, Reduced incidence wavenumber
        self.Kx = 0.0
        self.k0_list = 2*pi/self.wavelength_list    #'k0' : wave vector in vacuum, k0 = ω/c = 2pi/lambda
        # run some methods in the beginning 
        self.materials()



    def materials(self):
        # Materials
        self.glass = Berreman4x4.IsotropicNonDispersiveMaterial(1.55)
        self.water = 1.33
        self.CNC = (1.51, 1.59)
        self.front = Berreman4x4.IsotropicHalfSpace(self.glass)
        self.back = Berreman4x4.IsotropicHalfSpace(self.glass)

    def isotropic_layer(self, refractive_index = 1.55, thickness = 10e-9):
        isotropic_material = Berreman4x4.IsotropicNonDispersiveMaterial(refractive_index)
        thickness = 10e-9
        return  Berreman4x4.HomogeneousIsotropicLayer(isotropic_material, thickness)

    def create_chiral_nematic_layer(self, pitch = 300e-9, thickness = 2000e-9, z_rotate_angle = 0):
        ''' 
        The periodicity determines the length of helical axis - anything other than pi gives a incomplete structure and N should be 1

        z_rotate_angle rotate the whole structure around helical axis
        '''
        # Creates a uniaxial (bi-refringent) non-dispersive material: https://www.tulane.edu/~sanelson/eens211/uniaxial_minerals.htm
        # An optical axis is a line along with rotational symmetry 
        nematic = Berreman4x4.UniaxialNonDispersiveMaterial(self.CNC[0], self.CNC[1])  # ne along z
        
        # Returns rotation matrix defined by a unit rotation vector and an angle
        # rotation of pi/2 along y
        R = Berreman4x4.rotation_v_theta(e_y, pi/2)             
        # Change non-dispersive material into a rotated material with the rotation matrix (apply rotation from z to x)
        chiral_nematic = nematic.rotated(R)          

        # apply another rotation around z axis
        R_z = Berreman4x4.rotation_v_theta(e_z, z_rotate_angle)         
        chiral_nematic = chiral_nematic.rotated(R_z)     

        # Create structure based on thickness. The quotient is repeated layer and modulo as excessive bit to add on top
        N = int(thickness // pitch)
        excessive_fraction = (thickness % pitch)/pitch
        # excessive structure that does not finish a whole pitch
        chiral_nematic_excessive = Berreman4x4.TwistedMaterial(material=chiral_nematic, d=pitch*excessive_fraction, angle=-2*pi*excessive_fraction, div=80)
        chiral_nematic_excessive_layer = Berreman4x4.InhomogeneousLayer(chiral_nematic_excessive)

        # full pitch of left handed (angle = -2*pi)
        chiral_nematic = Berreman4x4.TwistedMaterial(material=chiral_nematic, d=pitch, angle=-2*pi, div=100)
        # create repeated layer for multiple pitches
        chiral_nematic_layer = Berreman4x4.InhomogeneousLayer(chiral_nematic)
        chiral_nematic_layer = Berreman4x4.RepeatedLayers(layers=[chiral_nematic_layer], n=N)

        return [chiral_nematic_layer, chiral_nematic_excessive_layer]


    def calculate_structure(self, material_layers):
        # the final structure to be simulated
        # also draw the structure 
        self.structure = Berreman4x4.Structure(self.front, material_layers, self.back)
        # Calculation with Berreman4x4
        data = Berreman4x4.DataList([self.structure.evaluate(self.Kx,k0) for k0 in self.k0_list])

        self.simulation_results = {}
        ####################### all the results ###################################
        # Naming convention (Fujiwara, p. 220):
        # 't_ps' : transmitted 'p' component for an 's' incident wave
        # 't_ss' : transmitted 's' component for an 's' incident wave
        # 'r_LR' : Reflection of LCP channel from a RCP light
        self.simulation_results['T_pp'] = data.get('T_pp')
        self.simulation_results['T_ps'] = data.get('T_ps')
        self.simulation_results['T_ss'] = data.get('T_ss')
        self.simulation_results['T_sp'] = data.get('T_sp')
        self.simulation_results['T_RR'] = data.get('T_RR')
        self.simulation_results['T_LL'] = data.get('T_LL')

        # Transmission coefficients for incident unpolarized light:
        self.simulation_results['T_pn'] = 0.5 * (self.simulation_results['T_pp'] + self.simulation_results['T_ps'])
        self.simulation_results['T_sn'] = 0.5 * (self.simulation_results['T_sp'] + self.simulation_results['T_ss'])
        self.simulation_results['T_nn'] = self.simulation_results['T_sn'] + self.simulation_results['T_pn']

        # Transmission coefficients for 's' and 'p' polarized light, with 
        # unpolarized measurement.
        self.simulation_results['T_ns'] = self.simulation_results['T_ps'] + self.simulation_results['T_ss']
        self.simulation_results['T_np'] = self.simulation_results['T_pp'] + self.simulation_results['T_sp']

        ############################## Reflectance #########################
        # Jones matrices for the circular wave basis
        # Second R and L is the incident light (Right handed)
        # Third is the filter channel before sensor
        self.simulation_results['R_RR'] = data.get('R_RR')
        self.simulation_results['R_LL'] = data.get('R_LL')

        # Cross polarisation and Parallel polarisation
        self.simulation_results['R_ss'] = data.get('R_ss')
        self.simulation_results['R_pp'] = data.get('R_pp')
        self.simulation_results['R_sp'] = data.get('R_sp')
        self.simulation_results['R_ps'] = data.get('R_ps')


    def analytical_verification(self):
        birefirengence = abs(self.CNC[0] - self.CNC[1])  # birefriengence
        n_ave = (self.CNC[0] + self.CNC[1])/2 # average n

        ###########################################################################
        # Text output: eigenvalues and eigenvectors of the transmission matrix for 
        # a wavelength in the middle of the stop-band.
        i = numpy.argmin(abs(lbda_list-lbda_B))     # index for stop-band center
        T = data[i].T_ti                            # transmission matrix
        eigenvalues, eigenvectors = numpy.linalg.eig(T)
        numpy.set_printoptions(precision=3)
        print("\nTransmission in the middle of the stop-band...\n")
        print("Eigenvalues of the Jones transmission matrix:")
        print(eigenvalues)
        print("Corresponding power transmission:")
        print(abs(eigenvalues)**2)
        print("Corresponding eigenvectors:")
        print(eigenvectors)
        # Note: the transformation matrix to the eigenvector basis is
        # B = numpy.matrix(eigenvectors), and the matrix B⁻¹ T B is diagonal.
        print("Normalization to the 'p' componant:")
        print(eigenvectors/eigenvectors[0,:])
        print("Ratio 's'/'p':")
        print(abs(eigenvectors[1,:]/eigenvectors[0,:]))
        print("Complex angle (°) (+90°: L, -90°: R)")
        print(180/pi*numpy.angle(eigenvectors[1,:]/eigenvectors[0,:]))
        # We observe that the eigenvectors are nearly perfectly polarized circular waves

        ############################################################################
        # Analytical calculation for the maximal reflection
        R_th = numpy.tanh(Dn/n_med*pi*h/p)**2
        lbda_B = p * n_med      # peak wavelenght
        lbda_B1, lbda_B2 = p*no, p*ne   #peak width


    def plotting(self, conditions = ['R_RR', 'R_LL', 'R_ps', 'R_sp']):
        fig = pyplot.figure()
        ax = fig.add_subplot("111")
        for condition in conditions:
            ax.plot(self.wavelength_list, self.simulation_results[condition], label=condition)

        ax.legend(loc='center right', bbox_to_anchor=(1.00, 0.50))

        ax.set_title("chiral nematic structure")
        ax.set_xlabel(r"Wavelength $\lambda_0$ (m)")
        ax.set_ylabel(r"Normalised transmitance $T$ and reflectance $R$")
        #fmt = ax.xaxis.get_major_formatter()
        #fmt.set_powerlimits((-3,3))
        # draw the refractive index variation
        self.structure.drawStructure()
        pyplot.show()

    def output_data_to_csv(self, conditions):
        # use panda to save the table into csv
        self.final_data = {}
        self.final_data['wavelength'] = self.wavelength_list
        for condition in conditions:
            self.final_data[condition] = self.simulation_results[condition]
        self.df = pd.DataFrame(self.final_data)
        # reverse the columns
        columns = self.df.columns.tolist()
        columns = columns[-1:] + columns[:-1] 
        self.df = self.df[columns]
        self.df.to_csv(self.folder +'\\'+ self.output_filename + '.csv',  sep=',')
        print('saved to ' + self.folder +'\\'+ self.output_filename + '.csv')



class water_infiltration():
    def __init__(self):
        pass

    def CNC_water_mixture_refractive_index(self, water_volume_fraction):
        water = 1.33
        CNC = (1.586, 1.524)
        # dielectric constant epsilon is sqrt of refractive index
        # for composite materials, dielectric constant calculation: 
        # e = e1*v1 + e2*v2  v is the volume fraction   http://www.sciencedirect.com/science/article/pii/S0030401899006951
        CNC_water_mixture  = (numpy.square(numpy.sqrt(CNC[0])*(1-water_volume_fraction)+numpy.sqrt(water)*water_volume_fraction),
                            numpy.square(numpy.sqrt(CNC[1])*(1-water_volume_fraction)+numpy.sqrt(water)*water_volume_fraction))

        self.CNC_water_mixture  = sim.UniaxialMaterial(CNC_water_mixture[0], CNC_water_mixture[1])
        return self.CNC_water_mixture


if __name__ == "__main__":
    cholesteric_simulation = chiral_nematic_simulation()
    cholesteric_simulation.CNC = (1.51, 1.59)
    CNC_layer = cholesteric_simulation.create_chiral_nematic_layer(pitch = 300e-9, thickness = 3500e-9, z_rotate_angle = 0)
    #CNC_interface = cholesteric_simulation.isotropic_layer(refractive_index = 1.6, thickness = 10e-9)
    #CNC_layer_2 = cholesteric_simulation.create_chiral_nematic_layer(material = CNC, half_pitch = 185e-9, thickness = 2000e-9, z_rotate_angle = 0)
    cholesteric_simulation.calculate_structure(material_layers = [CNC_layer[0], CNC_layer[1]])

    # simulation conditions: refer to chiral_nematic_simulation.calculate_structure()
    conditions = ['R_RR','R_LL','R_pp','R_sp']
    # save result to csv
    cholesteric_simulation.folder = r'C:\Users\herbz\Documents\GitHub\PhD-python\model the light\Berreman4x4-master\examples'
    cholesteric_simulation.output_filename = r'simple_chiral_nematic_film'
    cholesteric_simulation.output_data_to_csv(conditions = conditions)
    # plot
    cholesteric_simulation.plotting(conditions = conditions)


# to implement - water infiltration

