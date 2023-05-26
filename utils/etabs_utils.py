#from operator import index
#from re import S
import comtypes.client
import pandas as pd
import numpy as np
from scipy import interpolate



def connect_to_csi(prog):
    try:
        #create API helper object
        
        helper = comtypes.client.CreateObject(f'{prog}v1.Helper')
        exec(f'helper = helper.QueryInterface(comtypes.gen.{prog}v1.cHelper)')
        #attach to a running instance of ETABS
        EtabsObject = helper.GetObject(f"CSI.{prog}.API.ETABSObject")
        #create SapModel object
        SapModel = EtabsObject.SapModel
        
        try:
            set_envelopes_for_dysplay(SapModel)
        except:
            EtabsObject=comtypes.client.GetActiveObject(f"CSI.{prog}.API.ETABSObject")
            SapModel=EtabsObject.SapModel
            try:
                set_envelopes_for_dysplay(SapModel)
            except:
                print('Lo sentimos no es posible concetarnos al API de ETABS')  
                return None,None
        
        return EtabsObject, SapModel
        
    except:
        print(f'No es posible conectarse a {prog}')
        return None,None


def connect_to_etabs():
    return connect_to_csi('ETABS')

def connect_to_safe():
    return connect_to_csi('SAFE')
    

def set_units(SapModel,unit):
    units = {'Ton_m_C' : 12, 'kgf_cm_C':14}
    SapModel.SetPresentUnits(units[unit])


def get_modal_data(SapModel,clean_data='true'):
    SapModel.Results.Setup.DeselectAllCasesAndCombosForOutput()
    SapModel.Results.Setup.SetCaseSelectedForOutput("Modal")
    modal = SapModel.Results.ModalParticipatingMassRatios()
    modal = pd.DataFrame(modal[1:17],index= ['LoadCase', 'StepType', 'StepNum', 'Period', 'Ux', 'Uy', 'Uz', 'SumUx', 'SumUy', 'SumUz', 'Rx', 'Ry', 'Rz', 'SumRx', 'SumRy', 'SumRz']).transpose()
    if clean_data:
        modal = modal.drop(['LoadCase','StepType','StepNum','Rx', 'Ry', 'Rz', 'SumRx', 'SumRy', 'SumRz'],axis=1)

    #Masas Participativas 
    MP_x = max(modal.SumUx)

    MP_y = max(modal.SumUy)

    #Periodos Fundamentales
    mode_x = modal[modal.Ux == max(modal.Ux)].index
    period_x = modal.Period[mode_x[0]]
    Ux = modal.Ux[mode_x[0]]

    mode_y = modal[modal.Uy == max(modal.Uy)].index
    period_y = modal.Period[mode_y[0]]
    Uy = modal.Uy[mode_y[0]]

    return (modal,MP_x,MP_y,period_x,period_y,Ux,Uy)


def set_envelopes_for_dysplay(SapModel,set_envelopes=True):
    IsUserBaseReactionLocation=False
    UserBaseReactionX=0
    UserBaseReactionY=0
    UserBaseReactionZ=0
    IsAllModes=True
    StartMode=0
    EndMode=0
    IsAllBucklingModes=True
    StartBucklingMode=0
    EndBucklingMode=0
    MultistepStatic=1 if set_envelopes else 2
    NonlinearStatic=1 if set_envelopes else 2
    ModalHistory=1
    DirectHistory=1
    Combo=2
    SapModel.DataBaseTables.SetOutputOptionsForDisplay(IsUserBaseReactionLocation,UserBaseReactionX,
                                                        UserBaseReactionY,UserBaseReactionZ,IsAllModes,
                                                        StartMode,EndMode,IsAllBucklingModes,StartBucklingMode,
                                                        EndBucklingMode,MultistepStatic,NonlinearStatic,
                                                        ModalHistory,DirectHistory,Combo)

def get_table(SapModel,table_name,set_envelopes=True):
    set_envelopes_for_dysplay(SapModel,set_envelopes)
    data = SapModel.DatabaseTables.GetTableForDisplayArray(table_name,FieldKeyList='',GroupName='')
    
    if not data[2][0]:
        SapModel.Analyze.RunAnalysis()
        data = SapModel.DatabaseTables.GetTableForDisplayArray(table_name,FieldKeyList='',GroupName='')
        
    columns = data[2]
    data = [i if i else '' for i in data[4]] #reemplazando valores None por ''
    #reshape data
    data = pd.DataFrame(data)
    data = data.values.reshape(int(len(data)/len(columns)),len(columns))
    table = pd.DataFrame(data, columns=columns)
    return columns, table


def get_story_data(SapModel):
    _,story_data = get_table(SapModel,'Story Definitions')
    return story_data


def set_concrete(SapModel,fc=210):
    set_units(SapModel, 'kgf_cm_C')
    MATERIAL_CONCRETE = 2
    N_CONCRETO = "Concreto f'c =" + str(fc) + " kg/cm2"
    SapModel.PropMaterial.SetMaterial(N_CONCRETO, MATERIAL_CONCRETE)
    SapModel.PropMaterial.SetMPIsotropic(N_CONCRETO, 15000*fc**0.5 , 0.2, 0.0000055)
    IsLightweight = False
    FcsFactor = 1
    SSType = 2 #Mander
    SSHysType = 4 #Concrete
    StrainAtFc = 0.002219
    StrainUltimate = 0.005
    SapModel.PropMaterial.SetOConcrete(N_CONCRETO,fc,IsLightweight,FcsFactor,SSType,SSHysType,StrainAtFc,StrainUltimate)
    
def set_rebar(SapModel,fy=4200,fu=6300):
    set_units(SapModel, 'kgf_cm_C')
    MATERIAL_REBAR = 6
    N_REBAR = "Acero de Refuerzo f'c =" + str(fy) + " kg/cm2"
    SapModel.PropMaterial.SetMaterial(N_REBAR, MATERIAL_REBAR)
    SapModel.PropMaterial.SetMPIsotropic(N_REBAR, 2e6 , 0.2, 0.0000117)
    SSType = 1 #Simple
    SSHysType  = 1 #kinematic
    StrainAtHardening = 0.01
    StrainUltimate = 0.09
    UseCaltransSSDefaults = False
    SapModel.PropMaterial.SetORebar(N_REBAR,fy,fu,fy,fu,SSType,SSHysType,StrainAtHardening,StrainUltimate,UseCaltransSSDefaults)


def set_beam_sections(SapModel,b,h,r=5,fc=210,fy=4200):
    set_units(SapModel, 'kgf_cm_C')
    N_CONCRETO = "Concreto f'c =" + str(fc) + " kg/cm2"
    N_REBAR = "Acero de Refuerzo f'c =" + str(fy) + " kg/cm2"
    N_SECCION = f'Viga {b} x {h} cm'
    SapModel.PropFrame.SetRectangle(N_SECCION, N_CONCRETO, h, b)
    SapModel.PropFrame.SetRebarBeam(N_SECCION,N_REBAR,N_REBAR,r,r,0.0,0.0,0.0,0.0)
    
def set_column_sections(SapModel,b,h,r=5,fc=210,fy=4200):
    set_units(SapModel, 'kgf_cm_C')
    N_CONCRETO = "Concreto f'c =" + str(fc) + " kg/cm2"
    N_REBAR = "Acero de Refuerzo f'c =" + str(fy) + " kg/cm2"
    N_SECCION = f'Col {b} x {h} cm'
    SapModel.PropFrame.SetRectangle(N_SECCION, N_CONCRETO, b, h)
    Pattern = 1 #Rectangular
    ConfineType = 1 #Ties
    NumberCBars = 0 #Circular Bars
    NumberR3Bars = 3
    NumberR2Bars = 3
    RebarSize = SapModel.PropRebar.GetNameList()[1][3]
    TieSize = SapModel.PropRebar.GetNameList()[1][1]
    TieSpacingLongit = min(b,h)/2
    Number2DirTieBars = 2
    Number3DirTieBars = 2
    ToBeDesigned = False
    SapModel.PropFrame.SetRebarColumn(N_SECCION,N_REBAR,N_REBAR,Pattern,ConfineType,r,NumberCBars,NumberR3Bars,
                                      NumberR2Bars,RebarSize,TieSize,TieSpacingLongit,Number2DirTieBars,
                                      Number3DirTieBars,ToBeDesigned)

def set_shell_sections(SapModel,h,aligerado=True,fc=210):
    set_units(SapModel, 'kgf_cm_C')
    if aligerado:
        name = f'losa aligerada e= {h} cm'
        SlabType = 3
        ShellType = 3 #membrana
        MatProp = "Concreto f'c =" + str(fc) + " kg/cm2"
        Thickness = h
        SapModel.PropArea.SetSlab(name,SlabType,ShellType,MatProp,Thickness)
        SapModel.PropArea.SetSlabRibbed(name,OverallDepth=h,SlabThickness=5,StemWidthTop=10,StemWidthBot=10,
                                        RibSpacing=40,RibsParallelTo=1)

    else:
        name = f'losa llena e= {h} cm'
        SlabType = 0
        ShellType = 1 #shell thin
        MatProp = "Concreto f'c =" + str(fc) + " kg/cm2"
        Thickness = h
        SapModel.PropArea.SetSlab(name,SlabType,ShellType,MatProp,Thickness)
        

def set_wall_sections(SapModel,e,fc=210):
    set_units(SapModel, 'kgf_cm_C')
    name = f'Muro e= {e} cm'
    eWallPropType = 1
    ShellType = 1 #shell thin
    MatProp = "Concreto f'c =" + str(fc) + " kg/cm2"
    Thickness = e
    SapModel.PropArea.SetWall(name,eWallPropType,ShellType,MatProp,Thickness)


def draw_shell(SapModel,points,h,aligerado=True):
    if aligerado:
        prop_name = f'losa aligerada e= {h} cm'
    else:
        prop_name = f'losa llena e= {h} cm'
    X = points['X']
    Y = points['Y']
    Z = points['Z']
    area_obj = SapModel.AreaObj.AddByCoord(len(X),X,Y,Z)
    area_name = area_obj[3]
    SapModel.AreaObj.SetProperty(area_name,prop_name)


def draw_wall(SapModel,pi,pf,e,stories='all'):
    set_units(SapModel, 'kgf_cm_C')
    story_data = get_story_data(SapModel)
    story_data.Height = story_data.Height.astype('float64')
    story_data = story_data.sort_values(by=['Story'])
    story_data['t_height'] = story_data['Height'].cumsum()
    story_data.index = story_data.Story
    if stories == 'all':
        z1 = 0
        z2 = story_data['t_height'][-1]
    elif stories[0] not in story_data['Height']:
        z1 = 0
        z2 = story_data['t_height'][stories[1]]
    else:
        z1 = story_data['t_height'][stories[0]]
        z2 = story_data['t_height'][stories[1]]
        
    X = [pi[0],pf[0],pf[0],pi[0]]
    Y = [pi[1],pf[1],pf[1],pi[1]]    
    Z = [z1,z1,z2,z2]
    prop_name = f'Muro e= {e} cm'
    area_obj = SapModel.AreaObj.AddByCoord(len(X),X,Y,Z)
    area_name = area_obj[3]
    SapModel.AreaObj.SetProperty(area_name,prop_name)


def draw_beam(SapModel,pi,pf,b,h):
    set_units(SapModel, 'kgf_cm_C')
    Xi,Yi,Zi = pi
    Xj,Yj,Zj = pf
    propName = f'Viga {b} x {h} cm'
    SapModel.FrameObj.AddByCoord(Xi,Yi,Zi,Xj,Yj,Zj,PropName=propName)

def comb_CQC (r_mod, T, β = 0.05):
    '''
    Esta Función Nos permite obtener la respuesta máxima a partir de los valores de las respuestas 
    obtenidas para cada modo mediante la Combinación Cuadrática Completa:
          ______________________
    rn = √ Σ Σ ( rni x ρij x rnj)
           i j 

    Donde:
    rn = representa la respuesta elástica máxima esperada para el caso "n"
    rni = respuesta en el modo de vibración "i" para el caso "n"
    rnj = respuesta en el modo de vibración "j" para el caso "n"
    i,j = 1, 2, 3 ... #total de modos
    ρij = coeficiente de correlación del modo "i" con el modo "j"

    Donde:
    ρij = 8 β^2 (1 + λ) λ^3/2
          -----------------------------------
          (1-λ^2)^2 + 4 β^2 λ (1 + λ)^2

    λ = wj / wi  --> son las frecuencias angulares de los modos  i, j
    β = 0.05 ---> franccion de amortiguamiento crítico se puede suponer constante para todos los modos
        
    '''
    # Convertir r_mod y T a array
    r_mod = np.array(r_mod)
    T = np.array(T)

    # Hallar las frecuencias a partir de los periodos
    ω = 2*3.14159265/T

    #Verificamos que coincidan el numero de modos con el numero de peridos ω
    if np.shape(r_mod)[0] != np.shape(T)[0]:
        print ("El numero de modos no coincide con el numero de Periodos")
        return None        
    
    #Hallamos coeficiente de rho_matrix
    rho = np.vectorize(lambda β , λ : 
                       (8*(β**2)*(1+λ)*(λ**(3/2)))/(((1-(λ**2))**2) + (4*(β**2)*λ*(1+λ)**2))) 
    λ_matrix = ω/ω[:, np.newaxis]
    rho_matrix = rho(β,λ_matrix)

    #Sumatoria total
    return np.sum(r_mod[:, np.newaxis]*r_mod*rho_matrix)**0.5



# Generacion de cargas a exportar
def create_found_seism(SapModel,
                       seism_cases =   {'SDx':'x',
                                        'SDx +eY':'x',
                                        'SDx -eY':'x',
                                        'SDy':'y',
                                        'SDy +eX':'y',
                                        'SDy -eX':'y'}):
    '''
    crea cargas sísmicas equivalentes para análisis de la cimentación
    son asignadas al centro de masas (método 1)
    input:
    seism_cases: dict{case:direction}
    '''
    set_load = list(seism_cases.keys())
    SapModel.DatabaseTables.SetLoadCasesSelectedForDisplay(set_load)
    SapModel.DatabaseTables.SetLoadCombinationsSelectedForDisplay([]) 
    _,shear_table = get_table(SapModel,'Story Forces')
    shear_table = shear_table.query('Location == "Top"')[['Story','OutputCase','VX','VY']]

    _,mass_center = get_table(SapModel,'Centers Of Mass And Rigidity')
    mass_center = mass_center[['Story','Diaphragm','XCM','YCM']]

    shear_table = shear_table.merge(mass_center,on='Story')

    _,joint_table = get_table(SapModel,'Joint Assignments - Diaphragms')
    joint_table = mass_center.merge(joint_table,on=['Diaphragm','Story'])

    SapModel.SetModelIsLocked(False)

    #Creacion de CM
    CM_dict = {}
    for story in shear_table['Story'].unique():
        X = float(shear_table.query('Story==@story').iloc[0,5])
        Y = float(shear_table.query('Story==@story').iloc[0,6])
        Z = SapModel.PointObj.GetCoordCartesian(
            joint_table.query('Story == @story').iloc[0,5])[2]
        diaph = joint_table.query('Story == @story').iloc[0,1]
        CM_dict[story] = SapModel.PointObj.AddCartesian(X,Y,Z)[0]
        SapModel.PointObj.SetDiaphragm(CM_dict[story],3,diaph)

    #Creación de cargas
    for load in seism_cases.keys():
        data = shear_table.query('OutputCase==@load')
        data = data.assign(FX=data.loc[:,'VX'].astype(float) - data.loc[:,'VX'].astype(float).shift(1).fillna(0),
                           FY=data.loc[:,'VY'].astype(float) - data.loc[:,'VY'].astype(float).shift(1).fillna(0))
        
        SapModel.LoadPatterns.Add('f ' +load,5)
        
        for story, p_name in CM_dict.items():
            VX = data.query('Story==@story')['FX'].iloc[0]
            VY = data.query('Story==@story')['FY'].iloc[0]
            if seism_cases[load] == 'x':
                SapModel.PointObj.SetLoadForce(p_name,'f ' +load,[VX,0,0,0,0,0],Replace=True)
            elif seism_cases[load] == 'y':
                SapModel.PointObj.SetLoadForce(p_name,'f ' +load,[0,VY,0,0,0,0],Replace=True)



def create_found_seism_2(SapModel,
                         seism_modal_cases =   {'SDx':('Modal','x'),
                                                'SDx +eY':('Modal +eY','x'),
                                                'SDx -eY':('Modal -eY','x'),
                                                'SDy':('Modal','y'),
                                                'SDy +eX':('Modal +eX','y'),
                                                'SDy -eX':('Modal -eX','y')}):
    
    '''
    crea cargas sísmicas equivalentes para análisis de la cimentación
    combos equivalentes a partir del modo 1 (mérodo 2)
    input:
    seism_modal_cases: dict{case:(modal_name,direction)}
    '''

    #Identificamos los modos principales
    _,modal = get_table(SapModel,'Modal Participating Mass Ratios')
    modal = modal[['Case','Mode','UX','UY','RZ']]
    modal['Mode'] = modal.Mode.astype(int)
    modal['UX']=modal.UX.astype(float)
    mode_x = str(modal[modal.UX == max(modal.UX)].Mode.iloc[0])
    modal['UY']=modal.UY.astype(float)
    mode_y = str(modal[modal.UY == max(modal.UY)].Mode.iloc[0])

    #Cálculo de los momentos de volteo
    set_load = list(seism_modal_cases.keys()) + [i[0] for i in seism_modal_cases.values()]
    SapModel.DatabaseTables.SetLoadCasesSelectedForDisplay(set_load)
    SapModel.DatabaseTables.SetLoadCombinationsSelectedForDisplay([])                          
    _, table = get_table(SapModel,'Base Reactions',set_envelopes=False)
    table = table[['OutputCase','StepNumber','MX','MY']].query('StepNumber==@mode_x or StepNumber==@mode_y or StepNumber==""')
    table['over_moment'] = np.maximum(abs(table['MX'].astype(float)), abs(table['MY'].astype(float)))
    table = table[['OutputCase','StepNumber','over_moment']]
    
    #Calculo del factor de amplificacion en tuplas
    eq_factor = pd.DataFrame([(load,
                            case:=seism_modal_cases[load][0],
                            mode:=mode_x if seism_modal_cases[load][1] == 'x' else mode_y,
                            (table.query('OutputCase==@load')['over_moment'].iloc[0] /
                            table.query('OutputCase==@case and StepNumber==@mode')['over_moment'].iloc[0]))  
                            for load in seism_modal_cases.keys()],
                            columns=['load','case','mode','factor'])
    
    #Extraccion de puntos en base
    modal_cases = [i[0] for i in seism_modal_cases.values()]
    SapModel.DatabaseTables.SetLoadCasesSelectedForDisplay(modal_cases)
    SapModel.DatabaseTables.SetLoadCombinationsSelectedForDisplay([]) 
    _,point_table = get_table(SapModel,'Joint Reactions',set_envelopes=False)
    point_table = (point_table.query('StepNumber == @mode_x or StepNumber == @mode_y')
                   [['OutputCase','StepNumber','UniqueName','FX','FY','FZ','MX','MY','MZ']])
    point_table[['FX','FY','FZ','MX','MY','MZ']].astype(float)
    

    
    SapModel.SetModelIsLocked(False)
    #Creación de cases
    for load in seism_modal_cases.keys():
        SapModel.LoadPatterns.Add('found '+load,5)
        case = seism_modal_cases[load][0]
        point_loads = (point_table.query('OutputCase==@case')
                       .query('StepNumber == @mode_x' if seism_modal_cases[load][1] == 'x'
                              else'StepNumber == @mode_y' ))
        factor = eq_factor.query('load==@load').iloc[0,3]
        for p_name in point_loads.UniqueName:
            p_loads = (point_loads.query('UniqueName==@p_name')
                            [['FX','FY','FZ','MX','MY','MZ']].iloc[0])
            p_loads = [float(load)*float(factor)*-1 for load in p_loads]
            SapModel.PointObj.SetLoadForce(p_name,'found ' +load,p_loads,Replace=True)




def create_found_seism_3(SapModel,g=9.806,
                         n_Modes=12,
                        seism_modal_cases =   {'SDx':('Modal','x'),
                                                'SDx +eY':('Modal +eY','x'),
                                                'SDx -eY':('Modal -eY','x'),
                                                'SDy':('Modal','y'),
                                                'SDy +eX':('Modal +eX','y'),
                                                'SDy -eX':('Modal -eX','y')},
                        spectres = {'x' : 'ESPECTRO E.030-2018',
                                    'y' : 'ESPECTRO E.030-2018'}):
    
    '''
    Escala el analisis modal para análisis de la cimentación
    combos equivalentes a partir de las fuerzas cortantes (Método3)
    input:
    seism_modal_cases: dict{case:(modal_name,direction)}
    ''' 
    #Unidades de Trabajo
    set_units(SapModel, 'Ton_m_C') 
    #Extracción de modos
    _,modal = get_table(SapModel,'Modal Participating Mass Ratios')
    modal = modal[['Case','Mode','UX','UY','Period']]
    modal['UX']=modal.UX.astype(float)
    modal['UY']=modal.UY.astype(float)
    modal['Period']=modal.Period.astype(float)

    #Asignamos el espectro de aceleraciones para cada direccion
    a_x = SapModel.Func.GetValues(spectres['x']) 
    a_y = SapModel.Func.GetValues(spectres['y']) 
    espectro_x = interpolate.interp1d(a_x[1], a_x[2], kind='linear')
    espectro_y = interpolate.interp1d(a_y[1], a_y[2], kind='linear')

    #Tabla de Fuerzas para los modos
    set_load = [i[0] for i in seism_modal_cases.values()]
    unique_load =list(set(set_load))
    SapModel.DatabaseTables.SetLoadCasesSelectedForDisplay(unique_load)
    SapModel.DatabaseTables.SetLoadCombinationsSelectedForDisplay(unique_load)                          
    _,table = get_table(SapModel,'Base Reactions',set_envelopes=False)
    table = table[['OutputCase','StepNumber','FX','FY']]
    table['FX'] = table.FX.astype(float)
    table['FY'] = table.FY.astype(float)
    #Calculo de masa
    _,table_Mass = get_table(SapModel,'Mass Summary by Story')
    mass = table_Mass['UX'].astype(float).sum() - float(table_Mass[table_Mass['Story']=='Base']['UX'].iloc[0]) #RESTAMOS LA MASA DE LA BASE

    #Agregando las fuerzas a la tabla principal
    modal = modal.merge(table, right_on=['OutputCase','StepNumber'],left_on=['Case','Mode']).drop(['OutputCase','StepNumber'], axis=1)
    #Calculando Factores
    modal['VX'] = modal['Period'].apply(espectro_x)*mass*modal['UX']*g
    modal['VY'] = modal['Period'].apply(espectro_y)*mass*modal['UY']*g
    modal['FactorX'] = abs(modal['VX']/modal['FX']) 
    modal['FactorY'] = abs(modal['VY']/modal['FY'])
    
    #Verificación Cortante en la base
    seims_loads = [i for i in seism_modal_cases.keys()]
    SapModel.DatabaseTables.SetLoadCasesSelectedForDisplay(seims_loads)
    SapModel.DatabaseTables.SetLoadCombinationsSelectedForDisplay(seims_loads)
    _,shear_table = get_table(SapModel,'Base Reactions')
    shear_table = shear_table[['OutputCase','FX','FY']]
    shear_table['FX'] = shear_table.FX.astype(float)
    shear_table['FY'] = shear_table.FY.astype(float)
    #Añadir cases y sentidos a la tabla
    shear_table['Case'] = shear_table.OutputCase.apply(lambda x: seism_modal_cases[x][0])
    shear_table['Direction'] = shear_table.OutputCase.apply(lambda x: seism_modal_cases[x][1])
    #Calculamos los cortes mediante CQC
    shear_table = (shear_table.merge(modal.groupby('Case')
                                    .apply(lambda row: comb_CQC(row['VX'], row['Period']))
                                    .reset_index(),on='Case').rename(columns={0:'VX'}))
    shear_table = (shear_table.merge(modal.groupby('Case')
                        .apply(lambda row: comb_CQC(row['VY'], row['Period']))
                        .reset_index(),on='Case').rename(columns={0:'VY'}))
    
    #Calculamos el factor de escalamiento por cortante basal
    shear_table['Factor'] = shear_table.apply(lambda row: row.FX/row.VX if row.Direction == 'x' else row.FY/row.VY, axis=1)

    #Agregamos el factor calculado a la tabla principal
    modal = modal.merge(shear_table[['OutputCase','Case','Factor','Direction']],on='Case')
    #Calculamos el factor final
    modal['FoundFactor'] = modal.apply(lambda row: row['Factor']*row['FactorX'] if row.Direction == 'x' else row['Factor']*row['FactorY'],axis=1)
    #Tabla final
    modal['Mode']=modal.Mode.astype(int)
    found_factors = modal[['OutputCase','Case','Direction','Mode','FoundFactor','Period']].sort_values(by=['OutputCase','Mode']).reset_index(drop=True)

    return (found_factors)

def export_factors(SapModelSafe,found_factors):
    '''
    input
    foun_factors → df que contenga las columnas: 'OutputCase','Case','Direction','Mode','FoundFactor','Period'
    '''
    for load in found_factors.OutputCase.unique():
        data = found_factors.query('OutputCase==@load')
        SapModelSafe.LoadCases.StaticLinear.SetCase('periods '+load)
        modes = [data.Case.iloc[0]+'_MODE'+str(i) for i in data.Mode]
        SapModelSafe.LoadCases.StaticLinear.SetLoads('periods '+load,data.shape[0],['Load']*data.shape[0],modes,list(data.Period))
        for _, row in data.iterrows():
            SapModelSafe.LoadCases.StaticLinear.SetCase('found '+load+' Mode'+str(row.Mode))
            SapModelSafe.LoadCases.StaticLinear.SetLoads('found '+load+' Mode'+str(row.Mode),1,['Load'],[row.Case+'_MODE'+str(row.Mode)],[row.FoundFactor])

def extract_strip_data(SapModelSafe,seism_loads):
    _,table = get_table(SapModelSafe,'Strip Forces')
    table = table[['StripObject','Station','Location','OutputCase','V2','M3']]
    table = table[table['OutputCase'].str.startswith('found ')]
    table['Load'] = table['OutputCase'].apply(lambda load: load[:load.find(' Mode')])
    df_periods = pd.DataFrame()
    for load in seism_loads:
        periods = SapModelSafe.LoadCases.StaticLinear.GetLoads('Periods '+load)[-2]
        loads = ['found '+load+' Mode' + str(i+1) for i,_ in enumerate(periods)]
        df_periods = pd.concat([df_periods,pd.DataFrame(loads,periods).reset_index().rename(columns={'index':'Periods',0:'OutputCase'})],axis=0)
    table = table.merge(df_periods, on='OutputCase')
    V2_cqc = (table.groupby(['Station','Location','StripObject','Load'])
              .apply(lambda row: comb_CQC(row['V2'].astype(float), row['Periods']))
              .reset_index().rename(columns={0:'V2'}))
    M3_cqc = (table.groupby(['Station','Location','StripObject','Load'])
              .apply(lambda row: comb_CQC(row['M3'].astype(float), row['Periods']))
              .reset_index().rename(columns={0:'M3'}))
    data = V2_cqc.merge(M3_cqc, on = ['Station','Location','StripObject','Load'])
    data['Station'] = data['Station'].astype(float)
    data = data.sort_values(by=['Location'],ascending=False).reset_index(drop=True)
    data = data.sort_values(by=['StripObject','Load','Station']).reset_index(drop=True)
    return data[['StripObject','Load','Station','Location','V2','M3']]
    
    
if __name__ == '__main__':
    #_,SapModel = connect_to_etabs()
    _,SapModelSafe = connect_to_safe()
    #SapModel.SetModelIsLocked(False)
    #print(set_envelopes_for_dysplay(SapModel))
    #_,table = get_table(SapModel,'Story Forces')

    # create_found_seism_2(SapModel,seism_modal_cases =   {'SDx':('Modal','x'),
    #                                                    'SDy':('Modal','y')})
    
    import time

    seism_loads= ['SismoX','Sismo+X','Sismo-X','SismoY','Sismo+Y','Sismo-Y']


    tiempo_inicial = time.time()
    # found_factors,shear_table,modal = create_found_seism_3(SapModel,
    #                                     g=1,
    #                                      seism_modal_cases =   
    #                                      {  'SismoX':('Modal','x'),
    #                                         'Sismo+X':('Modal+X','x'),
    #                                         'Sismo-X':('Modal-X','x'),
    #                                         'SismoY':('Modal','y'),
    #                                         'Sismo+Y':('Modal+Y','y'),
    #                                         'Sismo-Y':('Modal-Y','y')},
    #                                     spectres = {'x' : 'C para espectro',
    #                                                 'y' : 'C para espectro'})
    # export_factors(SapModelSafe,found_factors)
    print(extract_strip_data(SapModelSafe,seism_loads))
    print(time.time()-tiempo_inicial)
