import sys
import os
sys.path.append(os.getcwd()+'\..')
import pandas as pd
from lib import etabs_utils as etb
import sys
from ipywidgets import widgets
from mem import latex_utils as ltx
from IPython.display import clear_output, display

#Programado para etabs 2019

#widgets
def dropdown(op, desc, val=''):
    return widgets.Dropdown(options=op, description=desc,
                            style={'description_width': 'initial'}, value=val)


def input_box(desc, val=''):
    return widgets.Text(description=desc, value=val, style={'description_width': 'initial'})


def check_box(desc, val=False):
    return widgets.Checkbox(value=val, description=desc, style={'description_width': 'initial'})


def change_filter(change, table, column, widget):
    if change['type'] == 'change' and change['name'] == 'value':
        clear_output(wait=False)
        display(widget)
        if change['new'] == 'sin filtro':
            display(table)
        else:
            display(table[table[column] == change['new']])


def show_table(table, column='OutputCase'):
    list_columns = tuple(table[column].unique())
    widget = dropdown(list_columns + ('sin filtro',), 'Filtro', val='sin filtro')
    widget.observe(lambda change: change_filter(change, table, column, widget))
    display(widget)
    display(table)



#Funciones básicas

#Cálculo del exponente de altura
def get_k(T):
    if T < 0.5:
        return 1
    elif 0.75+0.5*T < 2:
        return 0.75+0.5*T
    else:
        return 2

#Cálculo del Factor C
def get_C(T,Tp,Tl):
    if T < Tp:
        return 2.5
    elif T < Tl:
        return 2.5*Tp/T
    else:
        return 2.5*Tp*Tl/T**2

#Cálculo del coeficiente de sismo estático
def get_ZUCS_R(C,Z,U,S,R):
    if C/R>0.11:
        return Z*U*C*S/R
    else:
        return Z*U*S*0.11

#Sismo Estático
def ana_modal(SapModel):
    _,modal = etb.get_table(SapModel,'Modal Participating Mass Ratios')
    
    modal = modal[['Mode','Period','UX','UY','RZ','SumUX','SumUY','SumRZ']]
    
    #Masas Participativas 
    MP_x = float(max(modal.SumUX))

    MP_y = float(max(modal.SumUY))

    #Periodos Fundamentales
    mode_x = modal[modal.UX == max(modal.UX)].index
    T_x = float(modal.Period[mode_x[0]])
    Ux = float(modal.UX[mode_x[0]])

    mode_y = modal[modal.UY == max(modal.UY)].index
    T_y = float(modal.Period[mode_y[0]])
    Uy = float(modal.UX[mode_y[0]])

    
    #Reporte
    print("\nAnálisis Modal:")
    print('Masa Participativa X: {0:.2f}'.format(MP_x))
    if MP_x<0.9:
        print('---Aumentar Grados de Libertad: {0:.2f} < 0.9'.format(MP_x))
    print('Masa Participativa Y: {0:.2f}'.format(MP_y))
    if MP_y<0.9:
        print('---Aumentar Grados de Libertad {0:.2f} < 0.9'.format(MP_y))
    print('Periodo y deformaxión X: Tx={0:.3f}'.format(T_x)+', Ux={0:.3f}'.format(Ux))
    print('Periodo y deformaxión Y: Ty={0:.3f}'.format(T_y)+', Uy={0:.3f}'.format(Uy))
    
    data = {'modal':modal,'T_x':T_x,'T_y':T_y}
    
    return data

def sismo_estatico(SapModel,N,Z,U,S,Tp,Tl,Ip,Ia,R_o):
    data = {}
    data['R'] = R_o*Ip*Ia
    data['modal'], data['T_x'], data['T_y'] = ana_modal(SapModel).values()
    data['k_x'] = get_k(data['T_x'])
    data['k_y'] = get_k(data['T_y'])
    data['C_x'] = get_C(data['T_x'],Tp,Tl)
    data['C_y']  = get_C(data['T_y'],Tp,Tl)
    data['ZUCS_Rx'] = get_ZUCS_R(data['C_x'],Z,U,S,data['R'])
    data['ZUCS_Ry'] = get_ZUCS_R(data['C_y'],Z,U,S,data['R'])

    #Resumen
    print('Factor de Reduccion con Irregularidades: R={}'.format(data['R']))
    print('C en X: {0:.2f}'.format(data['C_x']))
    print('C en Y: {0:.2f}'.format(data['C_y']))

    print('\nCoeficiente de sismo estático X: {0:.3f}'.format(data['ZUCS_Rx']))
    print('Coeficiente de sismo estático Y: {0:.3f}'.format(data['ZUCS_Ry']))
    print('Exponente de altura X: {0:.2f}'.format(data['k_x']))
    print('Exponente de altura Y: {0:.2f}'.format(data['k_y']))

    return data


#Revisión por Torsión

def get_max_over_avg_drifts(SapModel,loads):
    SapModel.DatabaseTables.SetLoadCasesSelectedForDisplay(loads)
    _ , table = etb.get_table(SapModel,'Story Max Over Avg Drifts')
    table['OutputCase'] = table.OutputCase+' '+table.StepType
    table = table[['Story','OutputCase','Direction','Max Drift','Avg Drift','Ratio']]
    return table

def create_rev_torsion_table(SapModel,loads,max_drift,R,is_regular=True):
    table = get_max_over_avg_drifts(SapModel,loads)
    stories  = etb.get_story_data(SapModel)
    table = table.merge(stories[['Story','Height']], on = 'Story')
    if is_regular:
        table['Drifts']=table['Max Drift'].apply(lambda x:float(x))/table['Height'].apply(lambda x:float(x))*0.75*R
    else:
        table['Drifts']=table['Max Drift'].apply(lambda x:float(x))/table['Height'].apply(lambda x:float(x))*0.85*R
    table['Drift < Dmax/2'] = table['Drifts'] < max_drift/2
    tor_reg = (table['Drift < Dmax/2']) | (table['Ratio'].apply(lambda x: float(x)) < 1.3)
    table['tor_reg'] = tor_reg.apply(lambda x: 'Regular' if x else 'Irregular')

    return table

#Piso Blando
     
def rev_piso_blando(SapModel,loads):
    SapModel.DatabaseTables.SetLoadCasesSelectedForDisplay(loads)
    _,data = etb.get_table(SapModel,'Diaphragm Center Of Mass Displacements')
    data['OutputCase'] = data.OutputCase+ ' ' +data.StepType.fillna('')
    data['OutputCase'] = data['OutputCase'].apply(lambda x:x.rstrip())
    data = data[['Story','OutputCase','UX','UY']]
    table = pd.DataFrame()

    _,data_forces = etb.get_table(SapModel,'Story Forces')
    data_forces['OutputCase'] = data_forces.OutputCase+ ' ' +data_forces.StepType.fillna('')
    data_forces['OutputCase'] = data_forces['OutputCase'].apply(lambda x:x.rstrip())
    data_forces = data_forces[ data_forces.Location=='Top']
    data_forces = data_forces[['Story','OutputCase','VX','VY']]

    for load in set(data_forces.OutputCase):
        load_data = data[data.OutputCase == load]
        load_data = load_data.reset_index(drop=True)
        UX_0 = load_data.UX.astype(float) #desplazamiento del piso
        UX_1 = UX_0.shift(-1).fillna(0) #desplazamiento del piso inferior
        UY_0 = load_data.UY.astype(float) #desplazamiento del piso
        UY_1 = UY_0.shift(-1).fillna(0) #desplazamiento del piso inferior
        load_data['ΔUX'] = UX_0 - UX_1 #desplazamiento relativo X
        load_data['ΔUY'] = UY_0 - UY_1 #desplazamieto relativo Y
        load_data = load_data.merge(data_forces)
        lat_rig_1 = abs(load_data.VX.apply(lambda x:float(x))/load_data.ΔUX.apply(lambda x:float(x))) #rigidez calculada en X
        lat_rig_2 = abs(load_data.VY.apply(lambda x:float(x))/load_data.ΔUY.apply(lambda x:float(x))) #rigidez calculada en Y
        load_data['lat_rig(k)'] = lat_rig_1 if lat_rig_1.mean() > lat_rig_2.mean() else lat_rig_2 #La rigidez en el sentido correcto será la mayor

        load_data['0.7_prev_k'] = load_data['lat_rig(k)'].shift(1).fillna(0)*0.7 #70% de la rigidez del piso superior
        
        k_3 = load_data['lat_rig(k)'].shift(3).fillna(0) #rigidez del tercer piso superior
        k_2 = load_data['lat_rig(k)'].shift(-1).shift(3).fillna(0) #rigidez del segundo piso superior
        k_1 = load_data['lat_rig(k)'].shift(-2).shift(3).fillna(0) #rigidez del piso superior
        
        load_data['0.8k_prom'] = 0.8*(k_1+k_2+k_3)/3 #80% del promedio de tres pisos superiores

        table = pd.concat([table,load_data],ignore_index=True)


    is_reg = (table['lat_rig(k)'] > table['0.7_prev_k']) & (table['lat_rig(k)'] > table['0.8k_prom'])
    table['is_reg'] = is_reg.apply(lambda x: 'Regular' if x else 'Irregular')   

    return table

# Masa

def rev_masa(SapModel,n_sotanos,n_azoteas):
    _,masa = etb.get_table(SapModel,'Mass Summary by Story')
    masa['Mass'] = masa.UX
    masa = masa[['Story','Mass']]
    
    stories = masa.Story
    sotanos = list(stories[-1-n_sotanos:])
    azoteas = list(stories[0:n_azoteas+1])
         
    def set_story(story):
        if story in sotanos:
            return 'Sotano'
        elif story in azoteas:
            return 'Azotea'
        else:
            return 'Piso'
    
    masa['story_type'] = masa.Story.apply(set_story)
    masa.Mass = masa.Mass.astype(float)
    masa['1.5 Mass'] = masa.apply(lambda x: 1.5 * x['Mass'] if x['story_type'] == 'Piso' else None,axis=1)
    masa['inf_mass'] = masa['1.5 Mass'].shift(-1).fillna(float('inf'))
    masa['sup_mass'] = masa['1.5 Mass'].shift(1).fillna(float('inf'))
    
    def is_reg(row):
        if row['story_type'] in ['Sotano','Azotea']:
            return 'Regular'
        elif (row['Mass'] < row['inf_mass']) and (row['Mass'] < row['sup_mass']):
            return 'Regular'
        else:
            return 'Irregular'
    
    masa['is_regular'] = masa.apply(is_reg, axis = 1)
    
    masa = masa[['Story','Mass','1.5 Mass','story_type','is_regular']].fillna('')
    return masa

# Derivas
def get_rev_drift(rev_torsion, max_drift):
    rev_drift = rev_torsion[['Story','OutputCase','Direction','Drifts']]
    rev_drift = rev_drift.assign(Drift_Check = (rev_drift['Drifts'] < max_drift).apply(lambda x: 'Cumple' if x else 'No Cumple'))
    return rev_drift

# Centros de Masas y Rigideces

def get_CM_CR(SapModel):
    _,rev_CM_CR = etb.get_table(SapModel,'Centers Of Mass And Rigidity')
    rev_CM_CR = rev_CM_CR[['Story','XCCM','XCR','YCCM','YCR']]
    rev_CM_CR['DifX'] = rev_CM_CR.XCCM.apply(lambda x: float(x)) - rev_CM_CR.XCR.apply(lambda x: float(x))
    rev_CM_CR['DifY'] = rev_CM_CR.YCCM.apply(lambda x: float(x)) - rev_CM_CR.YCR.apply(lambda x: float(x))
    return rev_CM_CR


def min_shear(SapModel,is_regular=True,loads={'X':('Sx','SDx'),'Y':('Sy','SDy')},story='Story1'):
    etb.set_units(SapModel,'Ton_m_C')
    set_loads = [load for tupla in loads.values() for load in tupla]
    SapModel.DatabaseTables.SetLoadCasesSelectedForDisplay(set_loads)
    _,base_shear=etb.get_table(SapModel,'Story Forces')
    base_shear = base_shear[base_shear['Story']==story]
    base_shear = base_shear[base_shear['Location']=='Bottom']
    base_shear['StepType'] = base_shear['StepType'].fillna('Max')
    base_shear = base_shear[base_shear['StepType']=='Max']
    base_shear = base_shear[['OutputCase','VX','VY']]
    Sx = float(base_shear[base_shear['OutputCase'].apply(lambda x:x.upper()) =='SX']['VX'])
    SDx = float(base_shear[base_shear['OutputCase'].apply(lambda x:x.upper()) =='SDX']['VX'])
    Sy = float(base_shear[base_shear['OutputCase'].apply(lambda x:x.upper()) =='SY']['VY'])
    SDy = float(base_shear[base_shear['OutputCase'].apply(lambda x:x.upper()) =='SDY']['VY'])
    per_min = 80 if is_regular else 90
    per_x = abs(round(SDx/Sx*100,2))
    per_y = abs(round(SDy/Sy*100,2))
    fex = 1 if per_x > per_min else round(per_min/per_x,2)
    fey = 1 if per_y > per_min else round(per_min/per_y,2)
    table = pd.DataFrame(
        [['','X','Y'],
        ['V din (Ton)',SDx,SDy],
        ['V est (Ton)',Sx,Sy],
        ['% min',per_min,per_min],
        ['%',per_x,per_y],
        ['F.E.',fex,fey]])
    return table

# Main
def rev_sismo(SapModel,Dt,T_analisis):
    
    loads = Dt['loads']
    model_loads = etb.get_table(SapModel, 'Load Case Definitions - Summary')[1].Name
    for load in loads:
        if load not in list(model_loads):
            sys.exit(f'El caso de carga "{load}" no está definido en el modelo \n')
            
    if T_analisis == 1:
        return ana_modal(SapModel)
    elif T_analisis == 2:
        return sismo_estatico(SapModel,N=Dt['N'],Z=Dt['Z'],U=Dt['U'],S=Dt['S'],Tp=Dt['Tp'],
                       Tl=Dt['Tl'],Ip=Dt['Ip'],Ia=Dt['Ia'],R_o=Dt['R_o'])
    elif T_analisis == 3:
        R = Dt['R_o']*Dt['Ia']*Dt['Ip']
        return create_rev_torsion_table(SapModel,Dt['loads'],Dt['max_drift'],R)
    elif T_analisis == 4:
        return rev_piso_blando(SapModel,Dt['loads'])
    elif T_analisis == 5:
        return rev_masa(SapModel,Dt['n_sotanos'],Dt['n_techos']) 
    elif T_analisis == 6:
        return get_CM_CR(SapModel)
    elif T_analisis == 7:
        R = Dt['R_o']*Dt['Ia']*Dt['Ip']
        rev_torsion = create_rev_torsion_table(SapModel,Dt['loads'],Dt['max_drift'],R)
        return get_rev_drift(rev_torsion, Dt['max_drift'])
    else:
        data = {}
        data['sismo_estatico'] = sismo_estatico(SapModel,N=Dt['N'],Z=Dt['Z'],U=Dt['U'],S=Dt['S'],Tp=Dt['Tp'],
                   Tl=Dt['Tl'],Ip=Dt['Ip'],Ia=Dt['Ia'],R_o=Dt['R_o'])
        R = Dt['R_o']*Dt['Ia']*Dt['Ip']
        data['torsion_table'] = create_rev_torsion_table(SapModel,Dt['loads'],Dt['max_drift'],R)
        data['piso_blando'] = rev_piso_blando(SapModel,Dt['loads'])
        data['rev_masa'] = rev_masa(SapModel,Dt['n_sotanos'],Dt['n_techos']) 
        data['CM_CR'] = get_CM_CR(SapModel)
        rev_torsion = data['torsion_table']
        data['drifts'] = get_rev_drift(rev_torsion, Dt['max_drift'])
        return data



class sismo_e30():
    def __init__(self,data=False):
        self.data = {'Factor de Importancia': 'C',
                     'Sistema Estructural': 'Dual de Concreto Armado',
                     'Número de Pisos': '4',
                     'Número de Sotanos': '0',
                     'Número de Azoteas': '1',
                     'Factor Zona': '2',
                     'Factor Suelo': 'S2',
                     'Piso Blando': 'False',
                     'Piso Blando Extremo': 'False',
                     'Irregularidad de Masa': 'False',
                     'Irregularidad Vertical': 'False',
                     'Dicontinuidad Vertical': 'False',
                     'Dicontinuidad Vertical Extrema': 'False',
                     'Irregularidad Torsional': 'False',
                     'Irregulariad Torsional Extrema': 'False',
                     'Esquinas Entrantes': 'False',
                     'Discontinuidad del diafragma': 'False',
                     'Sistemas no Paralelos': 'False'}
        
        if data:
            self.data.update(data)
        else:
            self.data.update(ltx.read_dict('..\datos\data.txt'))              

        self.factor_zona = pd.DataFrame([[4, 0.45], [3, 0.35], [2, 0.25], [1, 0.1]], columns=['Zona', 'Z'])
        self.factor_suelo = pd.DataFrame(
            [[4, 0.8, 1, 1.05, 1.1],
             [3, 0.8, 1, 1.15, 1.20],
             [2, 0.80, 1, 1.2, 1.4],
             [1, 0.8, 1, 1.6, 2]],
            columns=['Z', 'S0', 'S1', 'S2', 'S3'])
        self.periodos_suelo = pd.DataFrame(
            [[0.3, 0.4, 0.6, 1],
             [3, 2.5, 2, 1.6]],
            columns=['S0', 'S1', 'S2', 'S3'],
            index=['Tp', 'Tl'])
        self.sist_estructural = pd.DataFrame(
            [['Pórticos Especiales de Acero Resistentes a Momentos', 8, 0.01],
             ['Pórticos Intermedios de Acero Resistentes a Momentos', 5, 0.01],
             ['Pórticos Ordinarios de Acero Resistentes a Momentos', 4, 0.01],
             ['Pórticos Especiales de Acero Concénticamente Arriostrados', 7, 0.01],
             ['Pórticos Ordinarios de Acero Concénticamente Arriostrados', 4, 0.1],
             ['Pórticos Acero Excéntricamente Arriostrados', 8, 0.01],
             ['Pórticos de Concreto Armado', 8, 0.007],
             ['Dual de Concreto Armado', 7, 0.007],
             ['De Muros Estructurales de Concreto Armado', 6, 0.007],
             ['Muros de Ductilidad Limita de Concreto Armado', 4, 0.005],
             ['Albañilería Armada o Confinada', 3, 0.005],
             ['Madera', 7, 0.01]],
            columns=['sistema', 'R_0', 'max_drift'])

        self.cat_edificacion = pd.DataFrame(
            [['A1 aislado', 1],
             ['A1 no aislado', 1.5],
             ['A2', 1.5],
             ['B', 1.3],
             ['C', 1]],
            columns=['categoria', 'U']
        )

        self.irreg_altura = {
            'Piso Blando': 0.75,
            'Piso Blando Extremo': 0.50,
            'Irregularidad de Masa': 0.90,
            'Irregularidad Vertical': 0.90,
            'Dicontinuidad Vertical': 0.80,
            'Dicontinuidad Vertical Extrema': 0.60,
        }

        self.irreg_planta = {
            'Irregularidad Torsional': 0.75,
            'Irregulariad Torsional Extrema': 0.60,
            'Esquinas Entrantes': 0.90, 
            'Discontinuidad del diafragma': 0.85,
            'Sistemas no Paralelos': 0.90
        }

        self.set_data()
        

    def w_change(self, change, url='..\datos\data.txt'):
        if change['type'] == 'change' and change['name'] == 'value':
            ltx.save_var(change['owner'].description, change['new'], url)
            self.data.update(ltx.read_dict(url))
            self.set_data()

    def parametros_e30(self):
        zona = dropdown(['1', '2', '3', '4'], 'Factor Zona', val=self.data['Factor Zona'])
        uso = dropdown(self.cat_edificacion.categoria, 'Factor de Importancia', val=self.data['Factor de Importancia'])
        suelo = dropdown(['S0', 'S1', 'S2', 'S3'], 'Factor Suelo', val=self.data['Factor Suelo'])
        sistema = dropdown(self.sist_estructural.sistema, 'Sistema Estructural', val=self.data['Sistema Estructural'])
        pisos = input_box('Número de Pisos', val=self.data['Número de Pisos'])
        sotanos = input_box('Número de Sotanos', val=self.data['Número de Sotanos'])
        azoteas = input_box('Número de Azoteas', val=self.data['Número de Azoteas'])
        zona.observe(self.w_change)
        uso.observe(self.w_change)
        suelo.observe(self.w_change)
        sistema.observe(self.w_change)
        pisos.observe(self.w_change)
        sotanos.observe(self.w_change)
        azoteas.observe(self.w_change)
        return display(widgets.VBox([zona, uso, suelo, sistema, pisos, sotanos, azoteas]))

    def irregularidades_e30(self):
        i_piso_b = check_box('Piso Blando', eval(self.data['Piso Blando']))
        i_piso_be = check_box('Piso Blando Extremo', eval(self.data['Piso Blando Extremo']))
        i_masa = check_box('Irregularidad de Masa', eval(self.data['Irregularidad de Masa']))
        i_vert = check_box('Irregularidad Vertical', eval(self.data['Irregularidad Vertical']))
        i_disc = check_box('Dicontinuidad Vertical', eval(self.data['Dicontinuidad Vertical']))
        i_disc_e = check_box('Dicontinuidad Vertical Extrema', eval(self.data['Dicontinuidad Vertical Extrema']))
        description_a = widgets.HTML(value='<b>Irregularidad en Altura</b>')
        i_altura = widgets.VBox([description_a, i_piso_b, i_piso_be, i_masa, i_vert, i_disc, i_disc_e])
        for i in [description_a, i_piso_b, i_piso_be, i_masa, i_vert, i_disc, i_disc_e]:
            i.observe(self.w_change)

        i_torsion = check_box('Irregularidad Torsional', eval(self.data['Irregularidad Torsional']))
        i_tosion_e = check_box('Irregulariad Torsional Extrema', eval(self.data['Irregulariad Torsional Extrema']))
        i_esquinas = check_box('Esquinas Entrantes', eval(self.data['Esquinas Entrantes']))
        i_disc_diaf = check_box('Discontinuidad del diafragma', eval(self.data['Discontinuidad del diafragma']))
        i_no_paral = check_box('Sistemas no Paralelos', eval(self.data['Sistemas no Paralelos']))
        description_p = widgets.HTML(value='<b>Irregularidad en Planta</b>')
        i_planta = widgets.VBox([description_p, i_torsion, i_tosion_e, i_esquinas, i_disc_diaf, i_no_paral])
        for i in [description_p, i_torsion, i_tosion_e, i_esquinas, i_disc_diaf, i_no_paral]:
            i.observe(self.w_change)
        return widgets.HBox([i_altura, i_planta])

    def show_params(self):
        self.R = self.R_0 * self.Ia * self.Ip
        print('''
\033[1mParámetros de sitio:\033[0m
Factor de zona: 
    Z={:.2f}
Factor de Importancia: 
    U={:.2f}
Factor de Suelo: 
    S={:.2f}
Periodos del Suelo: 
    Tp={:.2f}
    Tl={:.2f}
Factor Básico de Reducción:
    Rox={:.2f}
    Roy={:.2f}
Irregularidad en planta:
    Ipx={:.2f}
    Ipy={:.2f}
Irregularidad en altura:
    Iax={:.2f}
    Iay={:.2f}
Factor de Reducción:
    Rx={:.2f}
    Ry={:.2f}
'''.format(self.Z, self.U, self.S, self.Tp, self.Tl, self.R_0, self.R_0, self.Ip, self.Ip,
           self.Ia, self.Ip, self.R, self.R))

    def set_data(self):
        zona = int(self.data['Factor Zona'])
        self.Z = float(self.factor_zona[self.factor_zona.Zona == zona].Z)
        categoria = self.data['Factor de Importancia']
        self.U = float(self.cat_edificacion[self.cat_edificacion.categoria == categoria].U)
        suelo = self.data['Factor Suelo']
        self.S = float(self.factor_suelo[self.factor_suelo.Z == zona][suelo])
        self.Tp = self.periodos_suelo[suelo].loc['Tp']
        self.Tl = self.periodos_suelo[suelo].loc['Tl']
        sistema = self.data['Sistema Estructural']
        self.R_0 = float(self.sist_estructural[self.sist_estructural.sistema == sistema]['R_0'])
        self.max_drift = float(self.sist_estructural[self.sist_estructural.sistema == sistema]['max_drift'])
        self.N = int(self.data['Número de Pisos'])
        self.n_sotanos = int(self.data['Número de Sotanos'])
        self.n_azoteas = int(self.data['Número de Azoteas'])
        self.Ip = min([j for i, j in self.irreg_planta.items() if eval(self.data[i])] + [1, ])
        self.Ia = min([j for i, j in self.irreg_altura.items() if eval(self.data[i])] + [1, ])

    def sismo_estatico(self, SapModel):
        N = self.N
        Z = self.Z
        U = self.U
        S = self.S
        Tp = self.Tp
        Tl = self.Tl
        Ip = self.Ip
        Ia = self.Ia
        R_o = self.R_0
        
        self.param_sis_est = sismo_estatico(SapModel, N, Z, U, S, Tp, Tl, Ip, Ia, R_o)
        self.modal = self.param_sis_est.pop('modal')

    def piso_blando(self, SapModel, loads=['Sx', 'Sy', 'SDx', 'SDy']):
        self.piso_blando_table = rev_piso_blando(SapModel, loads)

    def irregularidad_masa(self, SapModel):
        self.rev_masa_table = rev_masa(SapModel, self.n_sotanos, self.n_azoteas)

    def centro_masa_inercia(self, SapModel):
        self.CM_CR_table = get_CM_CR(SapModel)

    def irregularidad_torsion(self, SapModel, loads=['Sx', 'Sy', 'SDx', 'SDy']):
        self.R = self.R_0 * self.Ia * self.Ip
        self.is_regular = self.Ip == 1 and self.Ia == 1
        self.torsion_table = create_rev_torsion_table(SapModel, loads, self.max_drift, self.R,
                                                          is_regular=self.is_regular)

    def derivas(self):
        self.drift_table = get_rev_drift(self.torsion_table, self.max_drift)

    def min_shear(self, SapModel):
        self.shear_table = min_shear(SapModel, is_regular=self.is_regular)

    def analisis_sismo(self, SapModel):
        self.sismo_estatico(SapModel)
        self.piso_blando(SapModel)
        self.irregularidad_masa(SapModel)
        self.centro_masa_inercia(SapModel)
        self.irregularidad_torsion(SapModel)
        self.derivas()
        self.min_shear(SapModel)


if __name__ == '__main__':



    _,_SapModel= etb.connect_to_etabs()

    #Definir variables de salida 'Ton_m_C' o 'kgf_cm_C'
    etb.set_units(_SapModel,'Ton_m_C')

    sistemas = ['Pórticos de Concreto Armado',
                'Dual de Concreto Armado',
                'De Muros Estructurales de Concreto Armado',
                'Pórticos Especiales de Acero Resistentes a Momentos',
                'Pórticos Intermedios de Acero Resistentes a Momentos',
                'Pórticos Ordinarios de Acero Resistentes a Momentos',
                'Pórticos Especiales de Acero Concénticamente Arriostrados',
                'Pórticos Ordinarios de Acero Concénticamente Arriostrados',
                'Pórticos Acero Excéntricamente Arriostrados',
                'Muros de Ductilidad Limita de Concreto Armado',
                'Albañilería Armada o Confinada',
                'Madera']

    datos = {'Factor de Importancia': 'C',
            'Sistema Estructural': sistemas[0],
            'Número de Pisos': '4',
            'Número de Sotanos': '0',
            'Número de Azoteas': '0',
            'Factor Zona': '2',
            'Factor Suelo': 'S2',
            'Piso Blando': 'False',
            'Piso Blando Extremo': 'False',
            'Irregularidad de Masa': 'False',
            'Irregularidad Vertical': 'False',
            'Dicontinuidad Vertical': 'False',
            'Dicontinuidad Vertical Extrema': 'False',
            'Irregularidad Torsional': 'False',
            'Irregulariad Torsional Extrema': 'False',
            'Esquinas Entrantes': 'False',
            'Discontinuidad del diafragma': 'False',
            'Sistemas no Paralelos': 'False'}

    sismo = sismo_e30(data=datos)
    sismo.show_params()
    sismo.analisis_sismo(_SapModel)
    
    


    
    
    

    