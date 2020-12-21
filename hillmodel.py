import csv
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib import colors
from datetime import datetime

class HillModel:
    """Hill Model Class used to create data visualization media of hills and particle landing zones for TERRAIN EFFECTS ON FIREBRAND TRANSPORT DYNAMICS by JOHAN BIN MOHAMMAD NAZRI"""

    def __init__(self, input_file):
        """Takes a DEM file in the ESRI ASCII format"""
        self.input_file = input_file
        self.len = self.wid = self.dx = self.dy = self.alpha = self.sou = None

    def save_file(self, file_name="HillData.txt"):
        """Saves the DEM file in the XYZ format"""

        txt_file = open(file_name,"w")

        for j in range(0,self.nrows):
            for i in range(0,self.ncols):
                txt_file.write(f"{i*self.cellsize}\t{j*self.cellsize}\t{self.point_data[j][i]}\n") 
        txt_file.close()

    def EA2XYZ(self, x_smooth=0, y_smooth=0, z_offset=0):
        """Converts from ESRI ASCII to XYZ"""
        """x_smooth & y_smooth are percentage values. The values are used to help move the values of the elevation at the edges to be closer to 0"""
        """z_offset is used to translate the elevation by a constant amount"""

        data_points = []
        count = 0

        with open(self.input_file) as points:
            data_reader = csv.reader(points, delimiter=' ')
            for data in data_reader:
                while '' in data:
                    data.remove('')
                if count > 5: # Converts elevation values to float
                    for index, number in enumerate(data):
                        data[index] = float(number)
                count += 1
                data_points.append(data)
                
        self.ncols = int(data_points[0][1]) # Reads number of columns
        self.nrows = int(data_points[1][1]) # Reads number of rows
        self.cellsize = int(data_points[2][1]) # Reads cell size
        nodata_value = int(data_points[3][1]) # Reads no data value

        # Obtains elevation values
        p_data = data_points[6:]

        # Edge Smoothing
        x_sedge = round(self.ncols*x_smooth/100) 
        y_sedge = round(self.nrows*y_smooth/100)

        for j in range(0,self.nrows):
            for i in range(0,self.ncols):
                if i>=x_sedge and j>=y_sedge and i<=(self.ncols-x_sedge) and j<=(self.nrows-y_sedge):
                    p_data[j][i] = p_data[j][i]-z_offset
                    if p_data[j][i] < 0:
                        p_data[j][i] = 0

                elif i<x_sedge or j<y_sedge:
                    factor_i = i/(x_sedge)
                    factor_j = j/(y_sedge)
                    f = min(factor_i,factor_j)**2
                    if f > 1:
                        f = 1
                    z = (p_data[j][i]-z_offset)*(f)
                    if z > 0:
                        p_data[j][i] = z
                    else:
                        p_data[j][i] = 0

                elif i>(self.ncols-x_sedge) or j>(self.nrows-y_sedge):
                    factor_i = (self.ncols-i)/(self.ncols-x_sedge)
                    factor_j = (self.nrows-j)/(self.nrows-y_sedge)
                    f = min(factor_i,factor_j)**2
                    if f > 1:
                        f = 1
                    z = (p_data[j][i]-z_offset)*(f)
                    if z > 0:
                        p_data[j][i] = z
                    else:
                        p_data[j][i] = 0

                else:
                    p_data[j][i] = 0

                self.point_data = p_data

        # Default naming convention for XYZ file
        time_obj = datetime.now()
        new_file = f"{time_obj.year}-{time_obj.month}-{time_obj.day}-{time_obj.hour}{time_obj.minute}-{self.input_file[:-4]}.txt"
        self.save_file(new_file)

    def hill_map(self, domain_length=None, domain_width=None, x_offset=None, y_offset=None, angle=None, combo=None):
        """Generate contour plot of the hill"""
        """domain_length & domain_width are the length and width of the domain in ANSYS Fluent"""
        """x_offset, y_offset & angle are the transformations applied to the hill in Designmodeler"""

        # Check for previous entry for values
        if domain_length is None:
            if self.len is None:
                print("Domain length is missing")
        else:
            self.len = domain_length

        if domain_width is None:
            if self.wid is None:
                print("Domain width is missing")
        else:
            self.wid = domain_width

        if x_offset is None:
            if self.dx is None:
                print("X offset is missing")
        else:
            self.dx = x_offset

        if y_offset is None:
            if self.dy is None:
                print("Y offset is missing")
        else:
            self.dy = y_offset

        if angle is None:
            if self.alpha is None:
                print("Angle of rotation is missing")
        else:
            self.alpha = angle*np.pi/180

        # Generates grid using original coordinates
        x_grid, y_grid = np.meshgrid(np.linspace(0, self.ncols*self.cellsize, self.ncols),np.linspace(0, self.nrows*self.cellsize, self.nrows) )

        t_x_grid = []
        t_y_grid = []
        empty_row = []

        # Generates grid of zeros in transformed coordinates
        for j in range(0,self.nrows):
            for i in range(0,self.ncols):
                empty_row.append(0)
            t_x_grid.append(empty_row)
            empty_row = []

        empty_row = []

        for j in range(0,self.nrows):
            for i in range(0,self.ncols):
                empty_row.append(0)
            t_y_grid.append(empty_row)
            empty_row = []

        # Transforms original coordinates and inserts into transformed grid
        for j in range(0,self.nrows):
            for i in range(0,self.ncols):           
                x_prime = x_grid[j][i]*np.cos(self.alpha)-y_grid[j][i]*np.sin(self.alpha)
                y_prime = x_grid[j][i]*np.sin(self.alpha)+y_grid[j][i]*np.cos(self.alpha)
                t_x_grid[j][i] = x_prime+self.dx
                t_y_grid[j][i] = y_prime+self.dy

        # Plots contour plot
        if combo == "Yes":
             self.t_x_grid, self.t_y_grid = t_x_grid, t_y_grid
        else:
            fig, ax = plt.subplots()
            cs = ax.contour(t_y_grid, t_x_grid, self.point_data, cmap = 'YlOrBr', alpha = 0.75)
            plt.xlabel('Y-Position', fontsize=12)
            plt.xlim(self.wid, 0)
            plt.ylabel('X-Position (Streamwise-Direction)', fontsize=12)
            plt.ylim(0,self.len)
            plt.show()

    def add_particles(self, particle_file, domain_length=None, domain_width=None):
        """Takes data from particle solution history in the ensight format"""
        """particle_file is the particle solution history file in the ensight format"""
        """domain_length & domain_width are the length and width of the domain in ANSYS Fluent"""

        # Check for previous entry for values
        if domain_length is None:
            if self.len is None:
                print("Domain length is missing")
        else:
            self.len = domain_length

        if domain_width is None:
            if self.wid is None:
                print("Domain width is missing")
        else:
            self.wid = domain_width

        print(f"Reading {particle_file}")
        particles = []
        count = 0

        # Takes values from file
        with open(particle_file) as points:
            data_reader = csv.reader(points, delimiter=' ')
            for data in data_reader:
                while '' in data:
                    data.remove('')
                if count > 2:
                    for number in data:
                        if len(data)<4: # Check for negative numbers
                            bad_num = data[-1]
                            # print(bad_num)
                            temp_num = []
                            for char in bad_num:
                                temp_num.append(char)
                            exp_index = bad_num.index('e')
                            y_val = ''.join(bad_num[0:exp_index+4])
                            z_val = ''.join(bad_num[exp_index+4:])
                            data = data[0:2]
                            data.append(y_val)
                            data.append(z_val)
                    for index,number in enumerate(data):
                        data[index] = float(number)
                count = count + 1
                particles.append(data)
                
        print(f"{len(particles[3:])} particles released.")
        part_data = []

        # Check if particle has landed
        for point in particles[3:]:
            if point[1]>self.len*0.9 or point[2]<self.wid*0.1 or point[2]>self.wid*0.9:
                if point[3]<0.01:
                    part_data.append(point)
            else:
                part_data.append(point)

        self.trap_particles = part_data
        print(f"{len(particles[3:])-len(self.trap_particles)} particle(s) escaped.")
    
    def particle_map(self, particle_file, grid_size=5, domain_length=None, domain_width=None, combo=None):
        """Plots contour map of the particle landing zones"""
        """particle_file is the particle solution history file in the ensight format"""
        """domain_length & domain_width are the length and width of the domain in ANSYS Fluent"""
        """grid_size is the desired size of the landing zones"""
        """combo is for use with alternate graphs"""

        # Calls the add_particles method to get data from file
        self.add_particles(particle_file)
        
        # Check for previous entry for values
        if domain_length is None:
            if self.len is None:
                print("Domain length is missing")
        else:
            self.len = domain_length

        if domain_width is None:
            if self.wid is None:
                print("Domain width is missing")
        else:
            self.wid = domain_width

        # Generate particle landing zone grid
        p_row = []
        p_count = []
        for j in range(0,self.wid//grid_size):
            for i in range(0,self.len//grid_size):
                p_row.append(0)
            p_count.append(p_row)
            p_row = []

        # Counts number of particles in each grid square
        for particle in self.trap_particles:
            p_count[int(round(particle[2]//grid_size))][int(round(particle[1]//grid_size))] += 1
        self.p_count = p_count

        # Grid for contour plot
        x_co = np.linspace(0,self.len,self.len//grid_size)
        y_co = np.linspace(0,self.wid,self.wid//grid_size)
        x_grid, y_grid = np.meshgrid(x_co,y_co)

        if combo == "Yes":
            self.x_grid, self.y_grid = x_grid, y_grid
        else:
            fig, ax = plt.subplots()
            cs = ax.contourf(y_grid, x_grid, p_count, norm=colors.LogNorm(), cmap='plasma')
            cbar = fig.colorbar(cs)
            plt.xlabel('Y-Position', fontsize=12)
            plt.ylabel('X-Position (Streamwise-Direction)', fontsize=12)
            plt.show()

    def combo_map(self, particle_file, grid_size=5, domain_length=None, domain_width=None, x_offset=None, y_offset=None, angle=None):
        """Plots a contour plot containing both the elevation of the hill and the particle landing zones"""
        """particle_file is the particle solution history file in the ensight format"""
        """grid_size is the desired size of the landing zones"""
        """domain_length & domain_width are the length and width of the domain in ANSYS Fluent"""
        """x_offset, y_offset & angle are the transformations applied to the hill in Designmodeler"""

                # Check for previous entry for values
        if domain_length is None:
            if self.len is None:
                print("Domain length is missing")
        else:
            self.len = domain_length

        if domain_width is None:
            if self.wid is None:
                print("Domain width is missing")
        else:
            self.wid = domain_width

        if x_offset is None:
            if self.dx is None:
                print("X offset is missing")
        else:
            self.dx = x_offset

        if y_offset is None:
            if self.dy is None:
                print("Y offset is missing")
        else:
            self.dy = y_offset

        if angle is None:
            if self.alpha is None:
                print("Angle of rotation is missing")
        else:
            self.alpha = angle*np.pi/180

        # Calls hill_map and particle_map methods to get contour plot arguments
        self.hill_map(domain_length=self.len, domain_width=self.wid, x_offset=self.dx, y_offset=self.dy, angle=angle, combo="Yes")
        self.particle_map(particle_file, grid_size, combo="Yes")

        # Plots combined contour plot
        fig, ax = plt.subplots()
        cs = ax.contour(self.t_y_grid, self.t_x_grid, self.point_data, cmap = 'YlOrBr', alpha = 0.75)
        cs = ax.contourf(self.y_grid, self.x_grid, self.p_count, norm=colors.LogNorm(), cmap='plasma')
        cbar = fig.colorbar(cs)

        plt.xlabel('Y-Position', fontsize=12)
        plt.xlim(self.wid, 0)
        plt.ylabel('X-Position (Streamwise-Direction)', fontsize=12)
        plt.ylim(0,self.len)
        plt.show()

    def landing_bar(self, particle_file, source=None, grid_size=5, domain_length=None, domain_width=None):
        """Plots the distribution of landed particles downwind from the heat source"""
        """particle_file is the particle solution history file in the ensight format"""
        """source is the x-position of the heat source"""
        """grid_size is the desired size of the landing zones"""
        """domain_length & domain_width are the length and width of the domain in ANSYS Fluent"""

        # Check for previous entry for values
        if domain_length is None:
            if self.len is None:
                print("Domain length is missing")
        else:
            self.len = domain_length

        if domain_width is None:
            if self.wid is None:
                print("Domain width is missing")
        else:
            self.wid = domain_width

        if source is None:
            if self.sou is None:
                print("Fire source location is missing")
        else:
            self.sou = source

        self.particle_map(particle_file, grid_size=grid_size, domain_length=self.len, domain_width=domain_width, combo="Yes")

        # Generate grid for landing zones
        x_co = np.linspace(0,self.len,self.len//grid_size)

        # Counts number of particles that land x distance away from source
        bar_count = [sum(row[i] for row in self.p_count) for i in range(len(self.p_count[0]))]

        # Plots bar chart
        fig, ax = plt.subplots()
        cs =ax.bar(x_co-self.sou, bar_count, width = 5, alpha = 0.5)
        plt.xlim(0,self.len-self.sou)
        plt.xlabel('Distance from the Heat Source', fontsize=12)
        plt.ylabel('Number of Landed Particles', fontsize=12)
        plt.show()

    def sum_line(self, particle_file, source=None, grid_size=5, domain_length=None, domain_width=None):
        """Plots the cumulative sum of landed particles x distance away from the heat source"""
        """particle_file is the particle solution history file in the ensight format"""
        """source is the x-position of the heat source"""
        """grid_size is the desired size of the landing zones"""
        """domain_length & domain_width are the length and width of the domain in ANSYS Fluent"""

        # Check for previous entry for values
        if domain_length is None:
            if self.len is None:
                print("Domain length is missing")
        else:
            self.len = domain_length

        if domain_width is None:
            if self.wid is None:
                print("Domain width is missing")
        else:
            self.wid = domain_width

        if source is None:
            if self.sou is None:
                print("Fire source location is missing")
        else:
            self.sou = source

        # Calls particle_map method to obtain particle landing locations
        self.particle_map(particle_file, grid_size=grid_size, domain_length=self.len, domain_width=domain_width, combo="Yes")

        # Generates grid for particle landing zones
        x_co = np.linspace(0,self.len,self.len//grid_size)
        bar_count = [sum(row[i] for row in self.p_count) for i in range(len(self.p_count[0]))]

        # Converts simple count to cumulative sum
        line_count = []
        l_count = 0

        for count in bar_count:
            l_count += count
            line_count.append(l_count)

        # Plots line graph
        fig, ax = plt.subplots()
        cs =ax.plot(x_co-self.sou, line_count)
        plt.xlim(0,self.len-self.sou)
        plt.fill_between(x_co-self.sou, line_count)
        plt.xlabel('Distance from the Heat Source', fontsize=12)
        plt.ylim(0, line_count[-1]*1.1)
        plt.ylabel('Cumulative Sum of Landed Particles', fontsize=12)
        plt.show()
