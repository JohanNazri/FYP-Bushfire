import csv
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib import colors
from datetime import datetime

class HillModel:
    """Takes point cloud data in ESRI ASCII format and converts it to XYZ format"""

    def __init__(self, input_file):
        """Initialize file to be converted"""
        self.input_file = input_file

        # For coordinate transformation later
        self.dx = None 
        self.dy = None
        self.alpha = None

    def EA2XYZ(self, x_smooth=0, y_smooth=0, z_offset=0):
        """Converts from ESRI ASCII to XYZ"""
        # x_smooth & y_smooth are percentage values
        # The values are used to help move the values of the elevation at the edges to be closer to 0
        # z_offset is used to translate the elevation by a constant amount

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

    def save_file(self, file_name="HillData.txt"):
        """Saves the point cloud data in the XYZ format"""

        txt_file = open(file_name,"w")

        for j in range(0,self.nrows):
            for i in range(0,self.ncols):
                txt_file.write(f"{i*self.cellsize}\t{j*self.cellsize}\t{self.point_data[j][i]}\n") 
        txt_file.close()

    def hill_map(self, domain_length, domain_width, delta_x=None, delta_y=None, angle=None):
        """Generate contour plot of the hill"""
        # domain_length & domain_width are the length and width of the domain in ANSYS Fluent
        # delta_x, delta_y & angle are the transformations applied to the hill in Designmodeler

        self.len = domain_length
        self.wid = domain_width

        # Checks for any previous entry for delta_x, delta_y and angle
        if delta_x==None:
            if self.dx==None:
                print("Err")
        else:
            self.dx = delta_x

        if delta_y==None:
            if self.dy==None:
                print("Err")
        else:
            self.dy = delta_y

        if angle==None:
            if self.alpha==None:
                print("Err")
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
        fig, ax = plt.subplots()
        cs = ax.contour(t_y_grid, t_x_grid, self.point_data, cmap = 'YlOrBr', alpha = 0.75)
        plt.ylim(0,self.len)
        plt.gca().invert_xaxis()
        plt.xlabel('Y-Position', fontsize=12)
        plt.ylabel('X-Position (Streamwise-Direction)', fontsize=12)
        plt.show()

    # def particle_data(particle_file, domain_length=3200, delta_x=None, delta_y=None, angle=None, grid_size = 5):
    # print(f"Reading {particle_file}")
    # data_points = []
    # count = 0

    # with open(particle_file) as points:
    #     data_reader = csv.reader(points, delimiter=' ')
    #     for data in data_reader:
    #         while '' in data:
    #             data.remove('')
    #         if count > 2:
    #             for number in data:
    #                 if len(data)<4:
    #                     bad_num = data[-1]
    #                     # print(badNum)
    #                     temp_num = []

    #                     for char in badNum:
    #                         temp_num.append(char)
    #                     exp_index = bad_num.index('e')
    #                     y_val = ''.join(bad_num[0:exp_index+4])
    #                     z_val = ''.join(bad_num[exp_index+4:])
    #                     data = data[0:2]
    #                     data.append(y_val)
    #                     data.append(z_val)
    #             for index,number in enumerate(data):
    #                 data[index] = float(number)
    #         count = count + 1
    #         particle_points.append(data)
            
    # print(f"{len(particle_points[3:])} particles released.") # line 3 onwards
    # particle_data = []
    # for particle_point in particle_points[3:]:
    #     if particle_point[1]>domain_length*0.75 and particle_point[3]<0.1:
    #         particle_data.append(particle_point)
    #     elif particle_point[1]<domain_length*0.75:
    #         particle_data.append(particle_point)

    # if delta_x==None:
    #     if self.dx==None:
    #         print("Err")
    # else:
    #     self.dx = delta_x

    # if delta_y==None:
    #     if self.dy==None:
    #         print("Err")
    # else:
    #     self.dy = delta_y

    # if angle==None:
    #     if self.dx==None:
    #         print("Err")
    # else:
    #     self.alpha = angle*np.pi/180

    # transformed_particles = []

    # for particle in particle_data:
    #     x_prime = particle[1]-self.dx
    #     y_prime = particle[2]-self.dy
    #     x_prime_prime = x_prime*np.cos(-self.alpha)-(y_prime)*np.sin(-self.alpha)
    #     y_prime_prime = x_prime*np.sin(-self.alpha)+y_prime*np.cos(-self.alpha)
    #     transformed_particles.append([particle[0],x_prime_prime,y_prime_prime,particle[3]])

    # trapped_particles = []
    # for i in range(0,len(transformed_particles)):
    #     if transformed_particles[i][3]<1000:
    #         trapped_particles.append(particle_data[i])
    # print(f"{len(trapped_particles)} particles trapped.")
    


    # x_co = np.linspace(0,3200,3200//grid_size)
    # y_co = np.linspace(0,4000,4000//grid_size)

    # x_grid, y_grid = np.meshgrid(x_co,y_co)

    # XGrid, YGrid = np.meshgrid(np.linspace(0, 133*20, 133),np.linspace(0, 126*20, 126) )

    # particle_count = []
    # particle_row = []
    # transAskervein = []
    # transXGrid = []
    # transYGrid = []
    # empty_row = []
    # for j in range(0,126):
    #     for i in range(0,133):
    #         empty_row.append(0)
    #     transXGrid.append(empty_row)
    #     empty_row = []

    # empty_row = []
    # for j in range(0,126):
    #     for i in range(0,133):
    #         empty_row.append(0)
    #     transYGrid.append(empty_row)
    #     empty_row = []

    # for j in range(0,126): # row
    #     for i in range(0,133): # col            
    #         x_prime = XGrid[j][i]*np.cos(angle)-YGrid[j][i]*np.sin(angle)
    #         y_prime = XGrid[j][i]*np.sin(angle)+YGrid[j][i]*np.cos(angle)
    #         transXGrid[j][i] = x_prime+delta_x
    #         transYGrid[j][i] = y_prime+delta_y