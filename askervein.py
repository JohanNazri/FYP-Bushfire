import csv
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib import colors
from datetime import datetime

dateTimeObj = datetime.now()
newFileName = f"{dateTimeObj.year}-{dateTimeObj.month}-{dateTimeObj.day}-{dateTimeObj.hour}{dateTimeObj.minute}-Askervein.txt"

hTHeightData = []
data_points = []
count = 0

with open("hTHillData.txt") as points:
    data_reader = csv.reader(points, delimiter='\t')
    for data in data_reader:
        while '' in data:
            data.remove('')
        if count > 3:
            for index, number in enumerate(data):
                data[index] = float(number)
                hTHeightData.append(data)
        count += 1
        
count = 0
with open("Askervein.asc") as points:
    data_reader = csv.reader(points, delimiter=' ')
    for data in data_reader:
        while '' in data:
            data.remove('')
        if count > 5:
            for index, number in enumerate(data):
                data[index] = float(number)
        count += 1
        data_points.append(data)
        
askervein_data = data_points[6:] # line 7 onwards

for j in range(0,126): # row
    for i in range(0,133): # col
        # {askervein_data[row][col]}
        if i> 15 and j>3 and i<100 and j<80:
            askervein_data[j][i] = askervein_data[j][i]-3.7
            if askervein_data[j][i] < 0:
                askervein_data[j][i] = 0
        elif i<=15 or j<=3:
            factor_i = 1+1/(15)*(i-15)
            factor_j = 1+1/(3)*(j-3)
            f = min(factor_i,factor_j)**2
            if f > 1:
                f = 1
            z = (askervein_data[j][i]-3.7)*(f)
            if z > 0:
                askervein_data[j][i] = z
            else:
                askervein_data[j][i] = 0
        elif i>99 or j>79:
            factor_i = 1+1/(100-133)*(i-100)
            factor_j = 1+1/(80-126)*(j-80)
            f = min(factor_i,factor_j)**2
            if f > 1:
                f = 1
            z = (askervein_data[j][i]-3.7)*(f)
            if z > 0:
                askervein_data[j][i] = z
            else:
                askervein_data[j][i] = 0
        else:
            askervein_data[j][i] = 0

delta_x = 1060
delta_y = 3800
angle = 227*np.pi/180

transAskervein = []
transX = []
transY = []

for j in range(0,126): # row
    for i in range(0,133): # col            
        x_prime = i*np.cos(angle)-(j)*np.sin(angle)
        y_prime = i*np.sin(angle)+j*np.cos(angle)        
        x_prime_prime = x_prime+delta_x
        y_prime_prime = y_prime+delta_y

        transAskervein.append([x_prime_prime,y_prime_prime,askervein_data[j][i]])


# txt_file = open(newFileName,"w")

# for j in range(0,126): # row
#     for i in range(0,133): # col
#         txt_file.write(f"{i*20}\t{j*20}\t{askervein_data[j][i]}\n") 
# txt_file.close()



# folderName = ["D-10","D-09","D-08","D-07","D-06","D-05"]
folderName = ["Downhill3","Uphill2","Flat2"]

for folder in folderName:
    fileName = f"{folder}/default.mpg0010"
    print(f"Reading {fileName}")
    data_points = []
    count = 0

    with open(fileName) as points:
        data_reader = csv.reader(points, delimiter=' ')
        for data in data_reader:
            while '' in data:
                data.remove('')
            if count > 2:
                for number in data:
                    if len(data)<4:
                        badNum = data[-1]
                        # print(badNum)
                        tempNum = []

                        for char in badNum:
                            tempNum.append(char)
                        expIndex = badNum.index('e')
                        yVal = ''.join(badNum[0:expIndex+4])
                        zVal = ''.join(badNum[expIndex+4:])
                        data = data[0:2]
                        data.append(yVal)
                        data.append(zVal)
                for index,number in enumerate(data):
                    data[index] = float(number)
            count = count + 1
            data_points.append(data)
            
    print(f"{len(data_points[3:])} particles released.") # line 3 onwards
    particle_data = []
    for data_point in data_points[3:]:
        if data_point[1]>3200*0.75 and data_point[3]<0.1:
            particle_data.append(data_point)
        elif data_point[1]<3200*0.75:
            particle_data.append(data_point)

    transformed_particles = []

    for particle in particle_data:
        x_prime = particle[1]-delta_x
        y_prime = particle[2]-delta_y
        x_prime_prime = x_prime*np.cos(-angle)-(y_prime)*np.sin(-angle)
        y_prime_prime = x_prime*np.sin(-angle)+y_prime*np.cos(-angle)
        transformed_particles.append([particle[0],x_prime_prime,y_prime_prime,particle[3]])

    trapped_particles = []
    for i in range(0,len(transformed_particles)):
        if transformed_particles[i][3]<1000:
            trapped_particles.append(particle_data[i])
    print(f"{len(trapped_particles)} particles trapped.")
    
    gridSize = 5

    x_co = np.linspace(0,3200,3200//gridSize)
    y_co = np.linspace(0,4000,4000//gridSize)

    x_grid, y_grid = np.meshgrid(x_co,y_co)

    XGrid, YGrid = np.meshgrid(np.linspace(0, 133*20, 133),np.linspace(0, 126*20, 126) )

    particle_count = []
    particle_row = []
    transAskervein = []
    transXGrid = []
    transYGrid = []
    empty_row = []
    for j in range(0,126):
        for i in range(0,133):
            empty_row.append(0)
        transXGrid.append(empty_row)
        empty_row = []

    empty_row = []
    for j in range(0,126):
        for i in range(0,133):
            empty_row.append(0)
        transYGrid.append(empty_row)
        empty_row = []

    for j in range(0,126): # row
        for i in range(0,133): # col            
            x_prime = XGrid[j][i]*np.cos(angle)-YGrid[j][i]*np.sin(angle)
            y_prime = XGrid[j][i]*np.sin(angle)+YGrid[j][i]*np.cos(angle)
            transXGrid[j][i] = x_prime+delta_x
            transYGrid[j][i] = y_prime+delta_y

    fig, ax = plt.subplots()
    cs = ax.contour(transYGrid, transXGrid, askervein_data, [10,20,30,40,50,60,70,80,90,100,110,120,130,140,150], cmap = 'YlOrBr', alpha = 0.75)

    plt.xlabel('Y-Position', fontsize=12)
    plt.ylabel('X-Position (Streamwise-Direction)', fontsize=12)

    for j in range(0,4000//gridSize):
        for i in range(0,3200//gridSize):
            particle_row.append(0)
        particle_count.append(particle_row)
        particle_row = []

    for particle in trapped_particles:
        particle_count[int(round(particle[2]//gridSize))][int(round(particle[1]//gridSize))] += 1

    mpl.rcParams['figure.figsize'] = 5,20
    cs = ax.contourf(y_grid, x_grid, particle_count,[1,10,100,1000,10000,100000],norm=colors.LogNorm(), cmap='plasma')
    cbar = fig.colorbar(cs)
    plt.xlabel('Y-Position', fontsize=12)
    # plt.xlim(1500,2500)
    plt.ylim(0,3200)
    plt.ylabel('X-Position (Streamwise-Direction)', fontsize=12)
    plt.show()
    # plt.savefig(f'{folder}-particle-contour.png',dpi=300)

    scatterCount = []
    scatterCount = [sum(row[i] for row in particle_count) for i in range(len(particle_count[0]))]

    hTXPositions = [i[0] for i in hTHeightData]
    hTHeights = [i[1] for i in hTHeightData]

    fig, ax = plt.subplots()
    cs = ax.plot(hTXPositions, hTHeights)
    cs =ax.bar(x_co,scatterCount, width = 5, alpha = 0.5)
    plt.xlim(200,3200)
    plt.show()