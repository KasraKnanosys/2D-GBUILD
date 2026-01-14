""" 
Cretaed by Nuruzzaman Sakib (nsakib@crimson.ua.edu)
tags_data=[0=id, 1=posx, 2=posy, 3=posz, 4=neighbour1,5=neighbour2,6=neighbour3,7=flag,8=color]
No atom of tags in visit_list
"""
import sys
if len(sys.argv) != 2:
    print("Syntax: python type_assign.py GBX_Y.lmp")
    sys.exit()
tags_data=[]   #store atom id
bond_data=[]
global count_visit
count_visit = 0
global visit_list
visit_list=[1]
convert_wse2 = []

pos_z_se1 = 13.3648
pos_z_se2 = 9.99923
pos_z_w   = 11.6821
dim_z_conv = 23.364029

conv_multi = 1.37  #for wse2 and graphene bond length ratio

#read the mindata.lmp file for coordinates of atoms
with open(sys.argv[1],'r') as fdata:
    lines = fdata.readlines()
    n_atom = int(lines[2].split()[0])
    dim_x = float(lines[5].split()[1])
    dim_y = float(lines[6].split()[1])
    dim_z = float(lines[7].split()[1])
    #print(dim_x,dim_y,dim_z)
    for i in range(15,n_atom+15):
        #print(i)
        data = lines[i].split()
        tags_data.append([int(data[0]),float(data[2]),float(data[3]),float(data[4])])
fdata.close()
    
tags_data.sort(key=lambda x:x[0])

#read the bond data and create neighbour list
with open('bond_data.txt','r') as fdata:
    for line in fdata:
        data=line.split()
        #print(data)
        tags_data[int(data[0])-1].append(int(data[1]))
        tags_data[int(data[1])-1].append(int(data[0]))
fdata.close()

with open('same_atom.dat','r') as fdata:
    for line in fdata:
        data=line.split()
        #print(data)
        #print(tags_data[int(data[0])-1])
        #print(tags_data[int(data[1])-1])
        tags_data[int(data[0])-1][4:7] = [int(data[0]) if item == int(data[1]) else item for item in tags_data[int(data[0])-1][4:7]]
        tags_data[int(data[1])-1][4:7] = [int(data[1]) if item == int(data[0]) else item for item in tags_data[int(data[1])-1][4:7]]
        #print(tags_data[int(data[0])-1])
        #print(tags_data[int(data[1])-1])
fdata.close()

for i in range(len(tags_data)):
    tags_data[i].append(0)  # for flags
    tags_data[i].append(0)  #for color

def vertex_col(u,col_of_u):
    global count_visit
    for v in tags_data[u-1][4:7]:   #v is neighbour
        if tags_data[v-1][7]==0:    #if flag on or off
            if (tags_data[u-1][8]==1):  #check the color of atom
                
                tags_data[v-1][8]=2     #assign the color of atom
                tags_data[v-1][7]=1
                    
            elif (tags_data[u-1][8]==2):
               
                tags_data[v-1][8]=1
                tags_data[v-1][7]=1
                
        if v not in visit_list:
            visit_list.append(v)
    count_visit=count_visit+1

tags_data[0][7]=1  #set flag active to atom id 1
tags_data[0][8]=1  #set initial color to atom id 1

while (count_visit!=len(visit_list)):
    vertex_col(visit_list[count_visit],tags_data[visit_list[count_visit]-1][8])

for i in range(len(tags_data)):
    if (tags_data[i][8] ==1):
        convert_wse2.append([tags_data[i][8],0.0,tags_data[i][1]*conv_multi,tags_data[i][2]*conv_multi,pos_z_se1])
        convert_wse2.append([tags_data[i][8],0.0,tags_data[i][1]*conv_multi,tags_data[i][2]*conv_multi,pos_z_se2])
    else:
        convert_wse2.append([tags_data[i][8],0.0,tags_data[i][1]*conv_multi,tags_data[i][2]*conv_multi,pos_z_w])

convert_wse2.sort(key=lambda x:x[1])
        
#data output section
with open('out_col.txt','w') as fdata:
    for i in range(len(tags_data)):
        fdata.write('{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n'.format(tags_data[i][0],tags_data[i][1],tags_data[i][2],tags_data[i][3],tags_data[i][4],tags_data[i][5],tags_data[i][6],tags_data[i][7],tags_data[i][8]))
fdata.close()

with open('type.txt','w') as fdata:
    for i in range(len(tags_data)):
        fdata.write('{}\n'.format(tags_data[i][8]))
fdata.close()

with open('data.lmp','w') as fdata:
    fdata.write('# LAMMPS data file written by python_NSAKIB\n')
    fdata.write('{} {}\n'.format(n_atom,'atoms'))
    fdata.write('2 atom types\n')
    fdata.write('{} {} {}\n'.format('0.0',dim_x,'xlo xhi'))
    fdata.write('{} {} {}\n'.format('0.0',dim_y,'ylo yhi'))
    fdata.write('{} {} {}\n'.format('0.0',dim_z,'zlo zhi'))
    fdata.write('\n')
    fdata.write('Mass\n')
    fdata.write('\n')
    fdata.write('1  12.0 # C\n')
    fdata.write('\n')
    fdata.write('Atoms  # atomic\n')
    fdata.write('\n')
        
    for i in range(len(tags_data)):
        fdata.write('{}\t{}\t{}\t{}\t{}\n'.format(tags_data[i][0],tags_data[i][8],tags_data[i][1],tags_data[i][2],tags_data[i][3]))

fdata.close()

with open('WSe2_'+sys.argv[1][2:],'w') as fdata:
    fdata.write('# LAMMPS data file written by python_NSAKIB\n')
    fdata.write('{} {}\n'.format(int(n_atom*1.5),'atoms'))
    fdata.write('2 atom types\n')
    fdata.write('{} {} {}\n'.format('0.0',dim_x*conv_multi,'xlo xhi'))
    fdata.write('{} {} {}\n'.format('0.0',dim_y*conv_multi,'ylo yhi'))
    fdata.write('{} {} {}\n'.format('0.0',dim_z_conv,'zlo zhi'))
    fdata.write(' \n')
    fdata.write('Masses\n')
    fdata.write(' \n')
    fdata.write('1  78.96000000     # Se\n')
    fdata.write('2  183.8400000     # W\n')
    fdata.write(' \n')
    fdata.write('Atoms  # charge\n')
    fdata.write('\n')
        
    for i in range(len(convert_wse2)):
        fdata.write('{}\t{}\t{}\t{}\t{}\t{}\n'.format(i+1,convert_wse2[i][0],convert_wse2[i][1],convert_wse2[i][2],convert_wse2[i][3],convert_wse2[i][4]))

fdata.close()        
