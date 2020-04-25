import bpy
from mathutils import Vector

import numpy as np
import pandas as pd

import json




#decalre global variables
stepsize = 10
scale = 0.001
seperation = 30
curveThickness = 10
    
#duration of animtation
anim_duration = 3.5 * 60        #in secounds
anim_frame = anim_duration * 24 #in frames
    
start_frame = 1
end_frame = anim_frame
bpy.data.scenes["Scene"].frame_end = (end_frame)


location_of_directoty = 'E:\covid_3d\\'



#read pickel
read_data = pd.read_pickle( location_of_directoty + 'CovisCases_dataframe.pkl')


#GET COUNTRY NAME AND ISO CODE
        
with open( location_of_directoty + 'Flags\countries.json') as f:
    country_codes = json.load(f)
#flip keys and values 
country_codes = dict([(value, key) for key, value in country_codes.items()])
    






def convert_Data3Cordinates_1_country(data_, stepSize, scale):
  verts = []
  
  #create horizontal margins
  h_margin = 15
  q = [-h_margin, 0,0]
  verts.append(q)
  
  for i in range(data_.shape[0]):
    vert = [i*stepSize, data_[i]*scale , 0]
    verts.append(vert)

  #close the loop
  #here 5 is the vertical margin
  v_margin = 5
  a = [verts[-1][0], -v_margin, 0]
  c = [0, -v_margin, 0]
  d = [-h_margin, -v_margin, 0]
  b = verts[0]
  verts.append(a)
  verts.append(c)
  verts.append(d)
  verts.append(b)

  return np.asarray(verts, dtype=np.float32)


def convert_Data2Cordinates(dataF, stepSize, scale):

  #for all country
  n = dataF.shape[1]  #number of country

  countryVertex = []

  for i in range(n):
    a = dataF.iloc[:, i]
    b = a.values

    v = convert_Data3Cordinates_1_country(b, stepSize, scale)
    countryVertex.append(v)
  return np.asarray(countryVertex, dtype=np.float32)

def createCollection(name):
    collection = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(collection)
    
    return collection


def write_country_name(name, collection1, size):
    
    name = name.replace(' ', '\n')

    font_curve = bpy.data.curves.new(type="FONT",name="Font Curve")
    font_curve.body = name

    country_name_obj = bpy.data.objects.new(name + 'Text', font_curve)
    collection1.objects.link(country_name_obj)


    new_font = location_of_directoty + 'Righteous\Righteous-Regular.ttf'
    country_name_obj.data.font = bpy.data.fonts.load(new_font)

    country_name_obj.data.align_x = 'CENTER'
    country_name_obj.data.align_y = 'BOTTOM'

    country_name_obj.rotation_euler = [np.pi/2, 0, np.pi/2]

    country_name_obj.data.size = size
    country_name_obj.data.extrude = country_name_obj.data.size/35
    
    country_name_obj.location = (0,0,0)
    
    #parent the text to COVER
    country_name_obj.parent = bpy.data.objects['COVER']
    
    return (country_name_obj)


def construct_ground(verts):
    bpy.ops.mesh.primitive_plane_add()
    plane = bpy.context.selected_objects[0]
    
    for i, vert in enumerate(verts):
        plane.data.vertices[i].co = vert



def construct_Cover__cube(read_data, stepsize, scale, seperation, start_frame, end_frame):
    n = read_data.shape[1]  #number of countries
    no_Days = read_data.shape[0] #number of days for which data is available
    all_max_value = read_data.select_dtypes(include=[np.number]).values.max()
    
    extraMargin = 0.05
    
    width = (stepsize*no_Days)                          #x direction
    length = ((n-1)*seperation + (2.0/3)*seperation)    #y direction
    height = (scale*all_max_value)                      #z direction
    

    #create a cube
    bpy.ops.mesh.primitive_cube_add()

    # newly created cube will be automatically selected
    cube = bpy.context.selected_objects[0]

    # change name
    cube.name = "COVER"

    cube.data.vertices[0].co = [0, -extraMargin*length, -extraMargin*height]
    cube.data.vertices[1].co = [0, -extraMargin*length, height + extraMargin*height]
    cube.data.vertices[2].co = [0, length + extraMargin*length, -extraMargin*height]
    cube.data.vertices[3].co = [0, length + extraMargin*length, height + extraMargin*height]

    cube.data.vertices[4].co = [width + extraMargin*width, -extraMargin*length, -extraMargin*height]
    cube.data.vertices[5].co = [width + extraMargin*width, -extraMargin*length, height + extraMargin*height]
    cube.data.vertices[6].co = [width + extraMargin*width, length + extraMargin*length, -extraMargin*height]
    cube.data.vertices[7].co = [width + extraMargin*width, length + extraMargin*length, height + extraMargin*height]
    
    
    cube.hide_render = True
    cube.display_type = 'WIRE'
    
    start_postion = [0,0,0]
    end_position = [width,0,0]
    
    positions = [start_postion, end_position]
    frame_positions = [start_frame, end_frame]
    
    for frame_position, position in zip(frame_positions, positions):
        
        bpy.context.scene.frame_set(frame_position)
        cube.location = position
        cube.keyframe_insert(data_path="location", index=-1)
        
        for fcurve in cube.animation_data.action.fcurves:
            kf = fcurve.keyframe_points[-1]
            kf.interpolation = 'LINEAR'
    
    
    verts = []
    a = [-20, -extraMargin*length, 0]
    b = [-20, length + extraMargin*length, 0]
    c = [width + extraMargin*width, -extraMargin*length, 0]
    d = [width + extraMargin*width, length + extraMargin*length, 0]
    verts.append(a)
    verts.append(b)
    verts.append(c)
    verts.append(d)
    construct_ground(verts)
    

def write_number_of_cases(initial_cases, name, collection1, size):
    
    initial_cases_string = '{:,}'.format(initial_cases)
    
    font_curve = bpy.data.curves.new(type="FONT",name="Font Curve")
    font_curve.body = initial_cases_string

    cases_obj = bpy.data.objects.new(name + 'Cases', font_curve)
    collection1.objects.link(cases_obj)


    new_font = location_of_directoty + 'Righteous\Righteous-Regular.ttf'
    cases_obj.data.font = bpy.data.fonts.load(new_font)

    cases_obj.data.align_x = 'CENTER'
    cases_obj.data.align_y = 'BOTTOM'

    cases_obj.rotation_euler = [np.pi/2, 0, np.pi/2]

    cases_obj.data.size = size
    cases_obj.data.extrude = cases_obj.data.size/50
    
    cases_obj.location = (0,0,0)
    
    #parent the text to COVER
    cases_obj.parent = bpy.data.objects['COVER']
    
    return (cases_obj)


def update_textNflag_locations_z(country_name,objects, cases, scale):
    #first identify the objects
    #first is the flag
    flag_name = country_name + 'Flag'
    cases_name = country_name + 'Cases'
    country_text_name = country_name + 'Text'
    
    heights = []
    z1 = 0
    z2 = 0
    z3 = 0
    
    flag_obj = None
    cases_obj = None
    text_obj = None
    
    padding = 1
    
    for obj in objects:
        if obj.name == flag_name:
           flag_obj = obj
        elif obj.name == cases_name:
            cases_obj = obj
        else:
            text_obj = obj
            
    if flag_obj != None:
        #if flag exists
        sFactor = flag_obj.scale[1]
        z1 = (flag_obj.dimensions)[1] + scale*cases
        
        z2 = z1 + (flag_obj.dimensions)[1]/2 + padding
        
        z3 = z2 + cases_obj.dimensions[1] + padding
    else:
        #no flag
        z1 = scale*cases
        
        z2 = z1 + padding
        
        z3 = z2 + cases_obj.dimensions[1] + padding
        
    #now finally apply the locations to the objects
    
    if flag_obj != None:
        flag_obj.location[2] = z1
        cases_obj.location[2] = z2
        text_obj.location[2] = z3
    else:
        cases_obj.location[2] = z2
        text_obj.location[2] = z3
    
    heights.append(z1)
    heights.append(z2)
    heights.append(z3)
    
    return heights
    



def constructCurves(read_data, stepsize = 0.3, scale = 0.01, seperation = 10, curveThickness = 10):
    
    ## use convert_Data2Cordinates(dataF, stepSize, scale)
    x =  convert_Data2Cordinates(read_data, stepsize, scale)
    
    n = read_data.shape[1]  #number of country
    #for each curves/country
    for id in range(n):

        coords_list = x[id].tolist()
            
        #get country name
        name = read_data.columns[id]

        #create collection
        collection1 = createCollection(name)
        
        
        #create a plane based on infection curve
        
        mesh = bpy.data.meshes.new(name + 'Curve')  # add the new mesh
        obj = bpy.data.objects.new(mesh.name, mesh)
        collection1.objects.link(obj)
        bpy.context.view_layer.objects.active = obj
        
        obj.rotation_euler = [np.pi/2, 0, 0]

        faces = [list(range(len(coords_list)))]
        mesh.from_pydata(coords_list, [], faces)
        
        bpy.ops.object.modifier_add(type='SOLIDIFY')
        bpy.context.object.modifiers["Solidify"].offset = 0
        bpy.context.object.modifiers["Solidify"].thickness = curveThickness



#        #add the cover cubeax
        bpy.ops.object.modifier_add(type='BOOLEAN')
        bpy.context.object.modifiers["Boolean"].operation = 'DIFFERENCE'
        bpy.context.object.modifiers["Boolean"].object = bpy.data.objects["COVER"]
        
        #collect flag, cases, text to update their location
        objs_without_curve = []
        
        #ADD FLAG
        #get country code for id
        country_name = read_data.columns[id]
        try:
            country_code = country_codes[country_name]
            flag_file = country_code.lower() + '.png'
            bpy.ops.import_image.to_plane(files=[{"name":flag_file}], directory= location_of_directoty + "Flags\png250px\\", align_axis='X+')
            flag = bpy.data.objects[country_code.lower()]
            collection1.objects.link(flag)
            flag.name = country_name + 'Flag'

            old_dim = flag.dimensions
            sFactor = (2*curveThickness/(old_dim[0]))
            flag.scale = [sFactor,sFactor,sFactor]
#            
            flag.location = [0,0, 0]
#            
            
            #parent the flag obj to COVER
            flag.parent = bpy.data.objects['COVER']
            
            #append flag obj
            objs_without_curve.append(flag)
            
        except:
            pass
        
        
        
        
        #construct number of cases text
#        loc = [0,0, flag.location[2] + (flag.dimensions*sFactor)[1]/2 + 1]
        initial_cases = read_data.iloc[0][id]
        cases_text_obj = write_number_of_cases(initial_cases ,name, collection1, 6.5)
        
        #append cases_obj 
        objs_without_curve.append(cases_text_obj)
        
        
        #write name of the country
        
#        loc = [0,0, loc[2] + dim_of_casetext[1] + 1]
        country_text_obj = write_country_name(country_name, collection1, 7)
        
        #append cases_obj 
        objs_without_curve.append(country_text_obj)
        
        
        #finally update the location of all 3 non curve objects at once with the function
        update_textNflag_locations_z(country_name,objs_without_curve, initial_cases, scale)
        
              
        #shift the curve by a seperation
        
#        all_obj_in_collection = list(collection1.objects)
#        
#        for ob in all_obj_in_collection:
#            ob.location[1] += id*seperation
        
        
        


def update_cases_number(scene):
    global scale
    #first find list of all the collections
    collections = list(bpy.data.collections)
    
    
    for collection in collections:
        country_name = collection.name
        #list all objects in this collection
        all_obj_in_collection = list(collection.objects)
        
        #find the obj responsible for case number
        name_of_cases_obj = country_name + 'Cases'
        
        curve_name = country_name + 'Curve'
        obj_not_curve = []
        cases = 0
        for obj_in_collection in all_obj_in_collection:
            
            if obj_in_collection.name == name_of_cases_obj:
                #if you are the right object then update it
                #first get the postion (x) of COVER
                cover_obj = bpy.data.objects["COVER"]
                cover_location_x = cover_obj.location[0]
                
                no_Days = read_data.shape[0]
                cover_max_location_x = stepsize*no_Days
                
                current_day_fraction = ((cover_location_x)/(cover_max_location_x))*no_Days
                    
                current_day_floor = int(current_day_fraction)
                
                
                if abs(current_day_fraction - current_day_floor) < 0.001:
                    #if current_day_fraction == current_day_floor
                    cases = int(read_data.iloc[current_day_floor][country_name])
                    
                else:
                    if current_day_floor == no_Days:
                        cases1 = read_data.iloc[current_day_floor - 1][country_name]
                    else:
                        #floor case nuber
                        cases1 = read_data.iloc[current_day_floor][country_name]
                    try:
                        #ceil case nuber
                        cases2 = read_data.iloc[current_day_floor + 1][country_name]
                    except:
                        cases2 = cases1
                            
                    #interpoating number of cases between days
                    cases = int(cases2 - (current_day_floor + 1 - current_day_fraction)*(cases2 - cases1)/(1))
                
                #convert the int case to string
                cases_str = '{:,}'.format(cases)
                
                #finally update the cases number on the screen
                obj_in_collection.data.body = cases_str
        
            
            #now lift up the name, case number and flag as the curve lifts up
            ##first collect the objects to lift
            if obj_in_collection.name != curve_name:
                #collect the objects
                obj_not_curve.append(obj_in_collection)
                
        #finally lift the objects        
        update_textNflag_locations_z(country_name,obj_not_curve, cases, scale)
                
                
        



def update_placements(scene):
    #first find list of all the collections
    collections = list(bpy.data.collections)
    
    no_Days = read_data.shape[0]
    
    current_frame_no = int(bpy.context.scene.frame_current)
    
    transition_length_frame = int((anim_frame/no_Days)/3)
    
    cover_obj = bpy.data.objects["COVER"]
    cover_location_x = cover_obj.location[0]
    cover_max_location_x = stepsize*no_Days
                
    current_day_fraction = ((cover_location_x)/(cover_max_location_x))*no_Days 
    
    current_day_floor_int = int(current_day_fraction)
    
    if current_day_floor_int == no_Days :
        current_day_floor_int = current_day_floor_int - 1
    
    transition_rate = int(anim_frame/no_Days)
    
    print('Came here: ', current_frame_no%transition_rate)
    if (current_frame_no%transition_rate == 0 or current_frame_no == 1):
        print('AM IN')
        #i.e. when day changes
        today_data = (read_data.iloc[current_day_floor_int]).values
        sorted_placement = np.argsort(today_data)
        sorted_country = read_data.columns[sorted_placement]
        
        #place all the country in their place
        for i, id in enumerate(sorted_country):
            
            collection = bpy.data.collections[id]
            all_obj_in_collection = list(collection.objects)
        
            for ob in all_obj_in_collection:

                ob.keyframe_insert(data_path="location", frame=current_frame_no)
                
                temp = ob.location[1]
                ob.location[1] = i*seperation 
                
                ob.keyframe_insert(data_path="location", frame=current_frame_no + transition_length_frame)
                ob.location[1] = temp
            


def update_date(scene):
    
    cover_obj = bpy.data.objects['COVER']
    cover_location_x = cover_obj.location[0]
    no_Days = read_data.shape[0]
    cover_max_location_x = stepsize*no_Days
                
    current_day_fraction = ((cover_location_x)/(cover_max_location_x))*no_Days
                    
    current_day_floor = int(current_day_fraction)
    
    
    data_text_obj = bpy.data.objects['DATE']
    
    df = read_data.index.strftime('%Y %b %d')
    
    date_string = str(df[current_day_floor])
    
    #find total cases
    
    if current_day_floor == no_Days:
        cases1 = np.sum((read_data.iloc[current_day_floor - 1]).values)
    else:
        #floor case nuber
        cases1 = np.sum((read_data.iloc[current_day_floor]).values)
    try:
        #ceil case nuber
        cases2 = np.sum((read_data.iloc[current_day_floor + 1]).values)
    except:
        cases2 = cases1
        
    #interpoating number of cases between days
    cases = int(cases2 - (current_day_floor + 1 - current_day_fraction)*(cases2 - cases1)/(1))
    
    date_string += '\n' + 'Total: ' '{:,}'.format(cases)
    
    data_text_obj.data.body = date_string
    
    
    

def frame_loop_handler(scene):
    #lets update the number of cases text
    update_cases_number(scene)
    
    #sort placements
    update_placements(scene)
    
    #update date
    update_date(scene)


def register():
    bpy.app.handlers.frame_change_post.append(frame_loop_handler)

def unregister():
    bpy.app.handlers.frame_change_post.remove(frame_loop_handler)
    
    
    
def add_material(obj, material_name, r, g, b):
    material = bpy.data.materials.get(material_name)

    if material is None:
        material = bpy.data.materials.new(material_name)

    material.use_nodes = True
    principled_bsdf = material.node_tree.nodes.get('Principled BSDF')

    if principled_bsdf is not None:
        principled_bsdf.inputs[0].default_value = (r, g, b, 1)  

    obj.active_material = material

def assignMaterials():
    #first find list of all the collections
    collections = list(bpy.data.collections)
    
    
    for collection in collections:
        all_obj_in_collection = list(collection.objects)
        flag_name = str(collection.name) + 'Flag'
        text_name = str(collection.name) + 'Text'
        cases_name = str(collection.name) + 'Cases'
        curve_name = str(collection.name) + 'Curve'
        
        for obj in all_obj_in_collection:
        
#            if obj.name != flag_name:
#                material_name = obj.name + 'Mat'
#                r ,b, g = np.random.rand(3)
#                add_material(obj, material_name, r, g, b)
                
            if obj.name == text_name or obj.name == cases_name:
                material_name = 'TextMat'
                add_material(obj, material_name, 0.55, 0, 0)
            elif obj.name == curve_name:
                material_name = 'CurveMat'
                add_material(obj, material_name, 0, 0.5, 0.8)
            elif obj.name != flag_name:
                material_name = 'TextMat'
                add_material(obj, material_name, 0.55, 0, 0)
                
def addlights():  
    bpy.ops.object.light_add(type='SUN', radius=1, location=(0, 0, 0))
    light_obj = bpy.context.selected_objects[0]
    light_obj.data.energy = 1
    cover_obj = bpy.data.objects['COVER']
    light_obj.location = [cover_obj.dimensions[0], (3/4.0)*cover_obj.dimensions[1], cover_obj.dimensions[2]]
    light_obj.rotation_euler = [0, np.pi/4, -np.pi/6]
    
    bpy.ops.object.light_add(type='AREA', radius=1, location=(0, 0, 0))
    light_obj2 = bpy.context.selected_objects[0]
    light_obj2.data.shape = 'SQUARE'
    light_obj2.data.size = 100

    light_obj2.data.energy = 1e+07
    cover_obj = bpy.data.objects['COVER']
    light_obj2.location = [0, (3/4.0)*cover_obj.dimensions[1], cover_obj.dimensions[2]]
    
    light_obj2.rotation_euler = [0, np.pi/4, -(2/3.0)*np.pi]
    
    
def addCamera():
    # create the first camera
    cam = bpy.data.cameras.new("Camera")
    cam.lens = 24

    # create the first camera object
    cam_obj = bpy.data.objects.new("Camera", cam)
    cam_obj.location = (0, 0, 0)
    cam_obj.rotation_euler = (0, 0, 0)
    cam_obj.data.clip_end = 50000
    bpy.context.scene.collection.objects.link(cam_obj)



def constructDate_text(read_data):
    
    df = read_data.index.strftime('%Y %b %d')
    
    initial_cases_string = str(df[0])
    
    today_data = (read_data.iloc[0]).values
    total_cases = np.sum(today_data)
    
    initial_cases_string += '\n' + 'Total: ' '{:,}'.format(total_cases)
    
    font_curve = bpy.data.curves.new(type="FONT",name="Font Curve")
    font_curve.body = initial_cases_string

    cases_obj = bpy.data.objects.new('DATE', font_curve)


    new_font = location_of_directoty + 'Righteous\Righteous-Regular.ttf'
    cases_obj.data.font = bpy.data.fonts.load(new_font)

    cases_obj.data.align_x = 'RIGHT'
    cases_obj.data.align_y = 'CENTER'

#    cases_obj.rotation_euler = [np.pi/2, 0, np.pi/2]

    cases_obj.data.size = 0.05
    
    
    
    #parent the text to COVER
    cam = bpy.data.objects['Camera']
    cases_obj.parent = cam
    
    cases_obj.location = (0.65,-0.3,cam.location[2]- 1)
    
    
    add_material(cases_obj, 'DateMat', 0, 0, 0)
    
    bpy.context.scene.collection.objects.link(cases_obj)


            

def main():
    global read_data, stepsize, scale, seperation, start_frame, end_frame
      
#    register the function  
    try:
        unregister()
    except:
        pass
    register()
    
    #make the COVER Cube
    construct_Cover__cube(read_data, stepsize, scale, seperation, start_frame, end_frame)
    #construct all the basics
    constructCurves(read_data, stepsize, scale, seperation)
    
    #assign material
    assignMaterials()
    
    
    #add light
    addlights()
    
    #addCamera
    addCamera()
    
    #print date
    constructDate_text(read_data)
    
      
main()