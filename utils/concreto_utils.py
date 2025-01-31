import numpy as np
import math
import pandas as pd
import matplotlib.pyplot as plt
#import matplotlib.pyplot as plt


# Definicion de las unidades
N = 1
m = 1
cm = m/100
Pa = 1
MPa = 10**6*Pa
pulg = 2.54 *m / 100
kN = 1000*N
kgf = 9.80665*N
tonf = 1000*kgf
ft = 12*pulg
ksi = 6894757.2932*Pa
kip = ksi*pulg**2
psi = 6894.76*Pa


# Definicion de varillas de acero:
d_3 = 3/8 * pulg
d_4 = 1/4 * pulg
d_5 = 5/8 * pulg
d_6 = 3/4 * pulg
d_8 = 1 * pulg

A_3 = d_3 ** 2 /4 * math.pi
A_4 = d_4 ** 2 /4 * math.pi
A_5 = d_5 ** 2 /4 * math.pi
A_6 = d_6 ** 2 /4 * math.pi
A_8 = d_8 ** 2 /4 * math.pi

bar_dic={'3/8"':[d_3,A_3],'1/2"':[d_4,A_4],'5/8"':[d_5,A_5],
         '3/4"':[d_6,A_6],'1"':[d_8,A_8]}
#Lista de espaciamientos entre barras en losas
esp_list=[0.4,0.35,0.30,0.25,0.20,0.15,0.125,0.10,0.075,0.05]

class Concrete():
    def __init__(self,b,h,r=4*cm,gamma_c=2400*9.81):
        self.b = b
        self.h = h
        self.d = h-r
        self.Ag = b*h
        self.r = r
        self.fy = 420*MPa
        self.Es = 200000*MPa
        self.eps_y = self.fy/self.Es
        self.fc = 21*MPa
        self.eps_u = 0.003
        self.betha = 0.85
        self.gamma_c = gamma_c
    
    def set_concrete(self,fc,eps_u):
        self.fc = fc
        self.eps_u = eps_u
        if fc <= 28*MPa:
            self.betha = 0.85
        elif 28*MPa < fc & fc < 55 * MPa:
            self.betha = 0.85 - 0.05*(fc-28*MPa)/(7*MPa)
        else:
            self.betha = 0.65
    
    def set_steel_reb(self,fy,Es):
        self.fy = fy
        self.Es = Es
        self.eps_y = fy/Es

    def nominal_moment(self,phi_f=0.9):
        As = self.Ast
        fy = self.fy
        fc = self.fc
        b = self.b
        d = self.d
        self.a = As*fy/(0.5*fc*b)
        self.Mn = As*fy*(d-self.a/2)
        self.phi_Mn = phi_f*self.Mn

    def nominal_shear(self,phi_s=0.85):
        fc = self.fc
        self.Vn=0.17*(fc/MPa)**0.5*self.b*self.d*MPa
        self.phi_Vn = self.Vn*phi_s

    def nominal_punch_shear(self,punch_perim,phi_s=0.85):
        fc = self.fc
        self.Vn_p=0.33*(fc/MPa)**0.5*punch_perim*self.d*MPa
        self.phi_Vn_p = self.Vn_p*phi_s 
    
    
    def stress_f(self,c,x,mayored='False'):
        'Esfuerzo en barras de acero segun su posición'
        eps_u = self.eps_u
        Es = self.Es
        fy = self.fy
        if mayored:
            fy = 1.25*fy
        if c==0:
            return -fy
        fs = eps_u*(c-x)/c*Es
        if abs(fs) > fy:
            return math.copysign(fy, fs)
        else:
            return fs    
        
    def des_long(self,db,lamb=1,psi_g=1,psi_e=1,psi_s=0.8,psi_t=1):
        psi_t_e = psi_t*psi_e
        if psi_t_e > 1.7:
            psi_t_e = 1.7
            
        sqrt_fc = (self.fc/10**6)**0.5*MPa
        if sqrt_fc > 8.3*MPa:
           sqrt_fc = 8.3*MPa
            
        ld = self.fy/(1.1*lamb*sqrt_fc)*psi_g*psi_e*psi_s*psi_g*db
        
        #efecto de los estribos
        r = self.r
        d_st = self.d_st
        nb = self.n_c
        b = self.b

        cb1 = r+d_st+db*0.5
        cb2 = (b-2*r-2*d_st-db)/(nb-1)/2
        cb = min(cb1,cb2)

        k_tr = 0

        #restricciones de la norma
        alpha = (cb+k_tr)/db
        if alpha > 2.5:
            alpha = 2.5

        return ld/alpha 


    
class Beam(Concrete):
    def __init__(self,b,h,r):
        Concrete.__init__(self,b,h,r)
        self.d = h-r
        
    def set_rebar(self,d_s,n_s,u='top'):
        try:
            if u == 'top':
                self.Ast = sum([d_i**2/4*math.pi*n_s[i] for i,d_i in enumerate(d_s)])
            else:
                self.Asb = sum([d_i**2/4*math.pi*n_s[i] for i,d_i in enumerate(d_s)])
        except:
            if u == 'top':
                self.Ast = d_s**2/4*math.pi*n_s
            else:
                self.Asb = d_s**2/4*math.pi*n_s
        
    def nominal_moment(self,phi_f=0.9):
        As = self.Ast
        fy = self.fy
        fc = self.fc
        b = self.b
        d = self.d
        self.a = As*fy/(0.5*fc*b)
        self.Mn = As*fy*(d-self.a/2)
        self.phi_Mn = phi_f*self.Mn
 
    
class Column(Concrete):
    def __init__(self,b,h,r,l):
        Concrete.__init__(self,b,h,r)
        self.l = l
 
    def set_rebar(self, d_p, d_s, d_st, n_f, n_c):
        self.d_p = d_p
        self.d_S = d_s
        self.d_st = d_st
        self.n_f = n_f
        self.n_c = n_c
        #Matrices de refuerzos, areas y area de refuerzo
        self.reb_matx = self.create_rebar_matrix(d_p, d_s, n_f, n_c)
        self.area_matx = self.reb_matx**2*math.pi/4
        self.area_vect = self.area_matx.flatten()
        self.Aref = self.area_matx.sum()
        #Vectores de distancias a la varillas
        b = self.b
        h = self.h
        self.dist_vect_x = self.dist_vector(b, n_c)
        self.dist_vect_y = self.dist_vector(h, n_f)
        
    def create_rebar_matrix(self,d_p,d_s,n_f,n_c):
        reb_mat = [d_p] + [d_s]*(n_c-2) + [d_p]
        for i in range(n_f -2 ):
            fila = [d_s] + [0]*(n_c-2) + [d_s]
            reb_mat = np.vstack([reb_mat,fila])
        fila = [d_p] + [d_s]*(n_c-2) + [d_p]
        reb_mat = np.vstack([reb_mat,fila])
        return reb_mat
    
    def dist_vector(self,l,n):
        'Vector de distancias a las varillas de refuerzos'
        r = self.r
        d_p = self.d_p
        d_st = self.d_st
        sep = (l-2*(r+d_st)-d_p)/(n-1)
        reb_vect = [r+d_p/2+d_st+i*sep for i in range(n)]
        return np.array(reb_vect)

    def compress_resist(self,phi=0.65):
        'Reistencia a la compresión pura'
        fc = self.fc
        fy = self.fy
        Ag = self.Ag
        A_ref = self.Aref
        self.P_n = 0.85*fc*(Ag-A_ref)+A_ref*fy #Resistemcia Nominal
        self.phiP_n = phi*0.8*self.P_n #Resistencia reducida

    def give_phi(self,d_t,c):
        eps_u = self.eps_u
        eps_y = self.eps_y
        if c==0:
            return 0.9
        eps_t = (c-d_t)/c*eps_u
        phi = 0.65+0.25*(abs(eps_t)-eps_y)/0.003
        if phi < 0.65:
            return 0.65
        elif phi > 0.9:
            return 0.9
        else:
            return phi
        
    def comp_area(self,theta,a):
        'Area de compresion del elemento'
        b = self.b
        h = self.h
        if theta == 0:
            return a*h,a/2,h/2
        elif theta == math.pi/2:
            return a*b,b/2,a/2
        cost = math.cos(theta)
        sint = math.sin(theta)
        tant = math.tan(theta)
        if (a<=b*cost) & (a<=h*sint):
            A_c = a**2/(2*sint*cost)
            x_c = a/(3*cost)
            y_c = a/(3*sint)
        elif (a<=h*sint) & ~(a<=b*cost):
            A_c = a*b/sint - b**2/(2*tant)
            x_c = (a*b**2/(2*sint)-b**3/(3*tant))/A_c
            y_c = (a**2*b/(2*sint**2)-b**2/(2*tant)*(a/sint-b/(3*tant)))/A_c
        elif ~(a<=h*sint) & (a<=b*cost):
            A_c = a*h/cost - h**2*tant/2
            y_c = (a*h**2/(2*cost)-h**3*tant/3)/A_c
            x_c = (a**2*h/(2*cost**2)-h**2*tant/2*(a/cost-h*tant/3))/A_c
        else:
            aux = h*sint+b*cost-a
            A_c = b*h - aux**2/(2*sint*cost)
            x_c = (b**2*h/2-aux**2/(2*sint*cost)*(b-aux/(3*cost)))/A_c
            y_c = (b*h**2/2-aux**2/(2*sint*cost)*(h-aux/(3*sint)))/A_c
        
        return A_c, x_c, y_c

    def dist_rot_vect(self, theta):
        dist_vect_x_rot = self.dist_vect_x*math.cos(theta)
        dist_vect_y_rot = self.dist_vect_y*math.sin(theta)
        dist_matx = np.array([i+dist_vect_x_rot for i in dist_vect_y_rot])
        return dist_matx.flatten()
    
    def nominal_PM(self,theta,mayored=False):
        'return: vect_Pn,vect_phi_Pn,vect_Mn_x,vect_phi_Mn_x,vect_Mn_y,vect_phi_Mn_y,a,vect_phi,A_c,x_c,y_c'
        theta = math.radians(theta)
        b = self.b
        h = self.h
        betha = self.betha
        l = b*math.cos(theta)+h*math.sin(theta)
        a = np.array([i/100*l for i in range(101)])
        c = a/betha
        #Determinación del Area a compresion y su centroide:
        A_X_Y = np.array([self.comp_area(theta,a_i) for a_i in a])
        A_c = A_X_Y[:,0]
        x_c = A_X_Y[:,1]
        y_c = A_X_Y[:,2]
        #Vector de distancias de cada barra (paralelo a las distancias a)
        dist_vect = self.dist_rot_vect(theta)
        #Esfuerzos en cada barra de refuerzo:
        matx_fs = np.array([[self.stress_f(c_i,x,mayored) for x in dist_vect] for c_i in c])
        #distancia a las varillas extremas a tensión:
        d_t = dist_vect.max()
        #Valores de phi para cada valor de c
        vect_phi = np.array([self.give_phi(d_t, c_i) for c_i in c])
        #Aporte a la resistencia axial del acero:
        rsp = np.dot(matx_fs,self.area_vect)
        #Aporte a la resistencia de momento del acero:
        dist_list_x = np.array([self.dist_vect_x for _ in self.dist_vect_y]).flatten()
        dist_list_y = np.array([i for i in self.dist_vect_y for _ in self.dist_vect_x])
        dist_CM_x = b/2-dist_list_x
        dist_CM_y = h/2-dist_list_y
        rsm_x = np.dot(matx_fs*self.area_vect,dist_CM_x)
        rsm_y = np.dot(matx_fs*self.area_vect,dist_CM_y)
        #Carga Axial Nominal
        fc = self.fc
        vect_Pn = np.array([0.85*fc*A_c[i]+rsp_i for i,rsp_i in enumerate(rsp) ])
        #Carga Axial Reducida
        vect_phi_Pn = vect_phi*vect_Pn
        vect_phi_Pn = np.array([i if i < self.phiP_n else self.phiP_n for i in vect_phi_Pn])
        #Momento nominal:
        vect_Mn_x = np.array([0.85*fc*A_c[i]*(b/2-x_c[i])+rsm_i for i,rsm_i in enumerate(rsm_x)])
        vect_Mn_y = np.array([0.85*fc*A_c[i]*(h/2-y_c[i])+rsm_i for i,rsm_i in enumerate(rsm_y)])
        #Momento reducido:
        vect_phi_Mn_x = vect_phi*vect_Mn_x
        vect_phi_Mn_y = vect_phi*vect_Mn_y
            
        return vect_Pn,vect_phi_Pn,vect_Mn_x,vect_phi_Mn_x,vect_Mn_y,vect_phi_Mn_y,a,vect_phi,A_c,x_c,y_c
        
    def biaxial_flex_comp(self,n_theta=30):
        theta = [i/n_theta*90 for i in range(n_theta+1)]
        self.biaxial_f_c = pd.DataFrame() 
        for theta_i in theta:
            data = pd.DataFrame(self.nominal_PM(theta_i)).T
            data['theta'] = [theta_i for _ in data[0]]
            self.biaxial_f_c = pd.concat([self.biaxial_f_c,data])
        self.biaxial_f_c = self.biaxial_f_c.reset_index(drop=True)
        self.biaxial_f_c = self.biaxial_f_c.set_axis(['Pn','phi_Pn','Mn_x','phi_Mn_x','Mn_y','phi_Mn_y','a','phi','A_c','x_c','y_c','theta'], axis=1)
        self.biaxial_f_c = self.biaxial_f_c[['theta','a','Pn','phi_Pn','Mn_x','phi_Mn_x','Mn_y','phi_Mn_y','phi','A_c','x_c','y_c']]
        
    def plot_bi_f_c(self,ax,loads=None,factored=True,scale=10**3):
        if factored:
            M_x = self.biaxial_f_c.phi_Mn_x
            M_y = self.biaxial_f_c.phi_Mn_y
            Pn = self.biaxial_f_c.phi_Pn
        else:
            M_x = self.biaxial_f_c.Mn_x
            M_y = self.biaxial_f_c.Mn_y
            Pn = self.biaxial_f_c.Pn
            
        if type(loads) != type(None):
            for load in loads.Combinacion:
                data = loads[loads.Combinacion==load]
                ax.scatter(data['M2']/scale,data['M3']/scale,data['P']/scale*-1,alpha=0.5)
            
        n_theta = len(self.biaxial_f_c.theta.unique())
        
        for i in range(n_theta):
            M_x_i = M_x[101*i:101*(i+1)]
            M_y_i = M_y[101*i:101*(i+1)]
            Pn_i = Pn[101*i:101*(i+1)]
            ax.plot(M_x_i/scale,M_y_i/scale, Pn_i/scale
                    ,linestyle = ':',alpha=0.7,color='#23987C')
            ax.plot(-M_x_i/scale,-M_y_i/scale, Pn_i/scale
                    ,linestyle = ':',alpha=0.7,color='#23987C')
            ax.plot(-M_x_i/scale,M_y_i/scale, Pn_i/scale
                    ,linestyle = ':',alpha=0.7,color='#23987C')
            ax.plot(M_x_i/scale,-M_y_i/scale, Pn_i/scale
                    ,linestyle = ':',alpha=0.7,color='#23987C')
        
    def plot_f_c(self,ax,loads=None,axis='x',factored=True,scale=10**3):
        if axis == 'x':
            theta = 0
            data = self.biaxial_f_c[self.biaxial_f_c.theta==theta]
            if factored:
                M = data.phi_Mn_x
                Pn = data.phi_Pn
            else:
                M = data.Mn_x
                Pn = data.Pn
                
            if type(loads)!= type(None):
               for load in loads.Combinacion:
                   data = loads[loads.Combinacion==load]
                   ax.scatter(data['M2']/scale,data['P']/scale*-1,alpha=0.5) 
            
        if axis == 'y':
            theta = 90
            data = self.biaxial_f_c[self.biaxial_f_c.theta==theta]
            if factored:
                M = data.phi_Mn_y
                Pn = data.phi_Pn
            else:
                M = data.Mn_y
                Pn = data.Pn
            
            if type(loads)!= type(None):
               for load in loads.Combinacion:
                   data = loads[loads.Combinacion==load]
                   ax.scatter(data['M3']/scale,data['P']/scale*-1,alpha=0.5) 
                   
        ax.plot(M/scale, Pn/scale)
        ax.plot(-M/scale, Pn/scale)

    def find_i(self,data,value):
        for i,val in enumerate(abs(data-value)):
            if val == min(abs(data-value)):
                return i
        
    def colstrong_beamw(self,beam,loads):
        #Momento Resistente de la viga máximo con acero en tracción solamente
        beam.calc_Mnv(phi_f=0.9)
        #Menor carga que no se encuentra en el ultimo nivel
        P_min = loads[loads.Piso!=6]['P'].max()*-1
        self.P_min = P_min

        #Filtro de datos para la menor carga
        data = self.biaxial_f_c
        data = data[data.theta==0]
        data = data[abs(data.Pn-P_min)== min(abs(data.Pn-P_min))]

        #Momento de diseño
        Mnx_des = float(data.Mn_x)
        self.Mnx_des = Mnx_des

        #Verificación:
        if 2*Mnx_des < 1.2*(2*beam.Mn):
            return 'Viga más fuerte que la columna'
        else:
            return 'ok'
    
    def long_dev(self,beam,db):
        #Verificación por longitud de desarrollo en la columna
        lu = self.l - beam.h
        ld = self.des_long(d_6)
        self.ld = ld
        #Verificación
        if 1.25*ld <= lu/2:
            return 'Ok'
        else:
            return 'El acero no puede desarrolarse en la columna'
      
    def strib_area(self,s,loads):
        P_max = abs(loads.P.min())
        bc = self.b-2*self.r
        hc = self.h-2*self.r
        Ach = bc*hc
        self.Ach = Ach
        fc = self.fc
        fy = self.fy
        #Revisión X
        Ag = self.Ag
        Ash1 = 0.09*s*bc*fc/fy
        Ash2 = 0.3*s*bc*(Ag/Ach-1)*fc/fy
        Ash3 = 0
        nl = 10
        
        if 0.3*fc*Ag < P_max:
            print('Es necesario confinar todas las barras longitudinales')
            kf = fc/175+0.6
            if kf < 1.0:
                kf = 1.0 
            kn = nl/(nl-2)
            Ash3 = 0.2*kf*kn*P_max/(fy*Ach)
        self.Ashx = max(Ash1,Ash2,Ash3)

        #Revisión Y
        Ash1 = 0.09*s*hc*fc/fy
        Ash2 = 0.3*s*hc*(Ag/Ach-1)*fc/fy
        Ash3 = 0
        nl = 10
        if 0.3*fc*Ag < P_max:
            print('Es necesario confinar todas las barras longitudinales')
            kf = fc/175+0.6
            if kf < 1.0:
                kf = 1.0 
            kn = nl/(nl-2)
            Ash3 = 0.2*kf*kn*P_max/(fy*Ach)
        self.Ashy = max(Ash1,Ash2,Ash3)
      
    def add_stirrup(self,db,n,theta=0,axis='x',check=False):
        try:
            self.Astx
        except:
            self.Astx = 0
            
        try:
            self.Asty
        except:
            self.Asty = 0
        
        theta = math.radians(theta)
        if axis=='x':
            self.Astx += db**2/4*math.pi*n*math.cos(theta)
            if check:
                if self.Ashx > self.Astx:
                    print('Area de refuerzo insuficiente')
        else:
            self.Asty += db**2/4*math.pi*n*math.cos(theta)
            if check:
                if self.Ashy > self.Asty:
                    print('Area de refuerzo insuficiente')
           
    def mayored_moment(self,P_max,axis='x',graph=False,loads=None):
        if axis == 'x':
            flex_comp_data = self.nominal_PM(theta=0,mayored=True)
            Pn_x_may = flex_comp_data[0]
            Mn_x_may = flex_comp_data[2]
            self.VPn_x_may = Pn_x_may
            self.VMn_x_may = Mn_x_may
            
            if graph:
                #Diagrama en el eje x    
                fig, ax = plt.subplots()
                self.plot_f_c(ax,loads,axis='x',factored=False)
                ax.set_xlabel("$M_x$ (kN-m)")
                ax.set_ylabel("$Pn$ (kN)")
                plt.show()
            
            i = self.find_i(Pn_x_may,P_max)
            Mnx_des = Mn_x_may[i]
            self.Mnx_may = Mnx_des
            
        else:
            flex_comp_data = self.nominal_PM(theta=90,mayored=True)
            Pn_y_may = flex_comp_data[0]
            Mn_y_may = flex_comp_data[4]
            self.VPn_y_may = Pn_y_may
            self.VMn_y_may = Mn_y_may
            
            if graph:
                #Diagrama en el eje y  
                fig, ax = plt.subplots()
                self.plot_f_c(ax,loads,axis='y',factored=False)
                ax.set_xlabel("$Mn_y$ (kN-m)")
                ax.set_ylabel("$Pn$ (kN)")
                plt.show()
                
            i = self.find_i(Pn_y_may,P_max)
            Mny_des = Mn_y_may[i]
            self.Mny_may = Mny_des    
    
    def ultimate_shear(self,beamx,beamy):
        hnx = self.h - beamx.h
        hny = self.h - beamy.h
        Vux = 2*self.Mnx_may/hnx
        Vuy = 2*self.Mny_may/hny
        self.Vux = Vux
        self.Vuy = Vuy
    
    def concrete_shear(self,phi_c=0.85,lamb=1):
        fc =self.fc
        h = self.h
        b = self.b
        r = self.r
        d_st = self.d_st
        Y = abs(self.P_max)/(6*self.Ag)
        Y = min(Y,0.05*fc)

        Vcx1 = (0.17*lamb*(fc/MPa)**0.5*MPa+Y)*h*(b-r-d_st)
        Vcx2 = (0.42*lamb*(fc/MPa)**0.5*MPa)*h*(b-r-d_st)
        Vcx = min(Vcx1,Vcx2)
        Vsx = (self.Vux-phi_c*Vcx)/phi_c

        Vcy1 = (0.17*lamb*(fc/MPa)**0.5*MPa+Y)*b*(h-r-d_st)
        Vcy2 = (0.42*lamb*(fc/MPa)**0.5*MPa)*b*(h-r-d_st)
        Vcy = min(Vcy1,Vcy2)
        Vsy = (self.Vuy-phi_c*Vcy)/phi_c

        self.Vcx1 = Vcx1
        self.Vcx2 = Vcx2
        self.Vcx = Vcx
        self.Vcy1 = Vcy1
        self.Vcy2 = Vcy2
        self.Vcy = Vcy
        self.Vsx = Vsx
        self.Vsy = Vsy
    
    def check_secction(self,phi_c=0.85):
        fc = self.fc
        h = self.h
        b = self.b
        r = self.r
        d_st = self.d_st
        Vumx = phi_c*(self.Vcx+0.66*(fc/MPa)**0.5*MPa*h*(b-r-d_st))
        Vumy = phi_c*(self.Vcy+0.66*(fc/MPa)**0.5*MPa*b*(h-r-d_st))
        self.Vumx = Vumx
        self.Vumy = Vumy

        if Vumx < self.Vux:
            return 'Aumentar seccion (x)'
          
        if Vumy < self.Vuy:
            return 'Aumentar seccion (y)'
        else:
            return 'OK'
    
    def strib_sep(self):
        fy = self.fy
        h = self.h
        b = self.b
        r = self.r
        d_st = self.d_st
        Astx = self.Astx
        sx = Astx*fy*(h-r-d_st)/self.Vsy
        self.sx = sx 
        
        Asty = self.Asty
        sy = Asty*fy*(b-r-d_st)/self.Vsx
        self.sy = sy

        d_p = self.d_p
        self.s =  min(sx,sy,6*d_p,15*cm)
        
        return self.s
    
    def strib_des(self,loads,beamx,beamy,phi_c=0.85,lamb=1, graph = False):
        #Carga máxima]
        P_max = abs(loads['P'].min())
        self.P_max = P_max

        #Momentos Probables
        self.mayored_moment(P_max,axis='x',graph=graph,loads=loads)
        self.mayored_moment(P_max,axis='y',graph=graph,loads=loads)

        #Cortantes ultimas por capacidad
        self.ultimate_shear(beamx,beamy)

        #Cortante que toma el concreto:
        self.concrete_shear(phi_c=phi_c,lamb=lamb)
        
        #Comprobacion de la sección transversal
        print(self.check_secction(phi_c=phi_c))
        
        #Espaciamiento de estribos
        self.strib_sep()
    
    
    def pbeam_shear(self,beam,n_beam=1,axis='x'):
        'hn = self.h - max(beam1.h,beam1.h)'
        fy = self.fy
        fc = self.fc
        if beam == 2:
            beam1, beam2 = beam
            hn = self.l - max(beam1.h,beam1.h)
            a = beam1.Ast*1.25*fy/(0.85*fc*beam1.b)
            Mp1 = beam1.Ast*1.25*fy*(beam1.d-a/2)
            a = beam2.Ast*1.25*fy/(0.85*fc*beam2.b)
            Mp2 = beam2.Ast*1.25*fy*(beam2.d-a/2)
            Mp = max(Mp1,Mp2)
            Vu = 2*Mp/(2*hn)
            lc = 0.5*hn+max(beam1.h,beam2.h)
            V2 = 2*Mp/beam1.l
            V1 = 2*Mp/beam2.l
            Vcol = 2*Mp/lc + (V1+V2)*self.b/2/lc
            exec('self.hn'+axis+'=hn')
            exec('self.Mp1'+axis+'=Mp1')
            exec('self.Mp2'+axis+'=Mp2')
            exec('self.Mp'+axis+'=Mp')
            exec('self.Vu'+axis+'=Vu')
            exec('self.V1'+axis+'=V1')
            exec('self.V2'+axis+'=V2')
            exec('self.Vcol'+axis+'=Vcol')   
        else:
            hn = self.l - beam.h
            a = beam.Ast*1.25*fy/(0.85*fc*beam.b)
            Mp = beam.Ast*1.25*fy*(beam.d-a/2)
            lc = 0.5*hn+max(beam1.h,beam2.h)
            Vu = 4*Mp/(2*hn)
            V1 = 2*Mp/beam1.l
            V2 = 2*Mp/beam2.l
            Vcol = 2*Mp/lc + (V1+V2)*self.b/2/lc
            exec('self.hn'+axis+'=hn')
            exec('self.Mp'+axis+'=Mp')
            exec('self.Vu'+axis+'=Vu')
            exec('self.V1'+axis+'=V1')
            exec('self.V2'+axis+'=V2')
            exec('self.Vcol'+axis+'=Vcol')
  


class Soil():
    def __init__(self,q_adm,gamma_s):
        self.q_adm = q_adm
        self.gamma_s = gamma_s
 
class Foundation(Concrete):
    '''
    Clase general de diseño de cimentaciones
    '''
    def set_soil(self,q_adm,gamma_s):
        '''
        Parameters
        ----------
        q_adm : Capacidad portante del suelo.
        Df : Profundidad de desplante
        '''
        self.soil = Soil(q_adm,gamma_s)
        

class Isolate_footing(Foundation):
    '''
    Parameters
    ----------
    dimX_col : dimension x de la columna.
    dimY_col : dimension y de la columna.
    h : Altura de zapata.
    Fuerzas : Lista de cargas que llegan de la columna
    [Fz,Mx,My] para cada tipo de carga: D,L,Sx,Sy,Vx,Vy 
    (en ese orden).
    Returns
    -------
    None.
    '''
    def __init__(self,dimX_col,dimY_col,df,h,b=1,r=0.075,gamma_c=2.4*9.81):
        
        self.b_col = dimX_col  #Dimensión en X de la Columna que llega a la zapata
        self.h_col= dimY_col   #Dimensión en Y de la Columna que llega a la zapata
        self.df = df            #Altura de desplante
        
        super().__init__(b,h=h,r=r,gamma_c=gamma_c)
        
        #PREDIMENSIONAMIENTO:
        B=round(4*self.b_col,2)
        L=round(B+(self.h_col-self.b_col),2)
        self.set_foot_dimensions(B,L)

        


    def assign_forces(self,forces):
        '''
        Fuerzas : Lista de cargas que llegan de la columna
        [Fz,Mx,My] para cada tipo de carga: D,L,Sx,Sy,Vx,Vy 
        '''
        forces.append([0,0,0])
        self.forces=np.array(forces)

        #Definiendo la matriz de combinación
        #[D,L,SX,SY,VX,VY,PP]#POSIBILIDAD DE AUMENTAR LOS CASOS NEGATIVOS DE SISMO Y VIENTO
        Comb=[[1,1,0,0,0,0,1],
              [1,1,0.8,0,0,0,1],
              [1,1,-0.8,0,0,0,1],
              [1,1,0,0.8,0,0,1],
              [1,1,0,-0.8,0,0,1],
              [1,1,0,0,1,1,1],
              [1.4,1.7,0,0,0,0,1.4],
              [1.25,1.25,1,0,0,0,1.25],
              [1.25,1.25,-1,0,0,0,1.25],
              [1.25,1.25,0,1,0,0,1.25],
              [1.25,1.25,0,-1,0,0,1.25],
              [0.9,0,1,0,0,0,0.9],
              [0.9,0,0,1,0,0,0.9],
              [0.9,0,0,0,1,0,0.9],
              [0.9,0,1,0,0,1,0.9]]
            
        self.C=np.array(Comb)


    def soil_forces(self):
        #Peso del terreno y zapata:
        w_soil=self.soil.gamma_s*(self.B*self.L-self.b_col*self.h_col)*(self.df-self.h)
        w_col=self.gamma_c*(self.b_col*self.h_col)*(self.df-self.h)
        w_p=self.gamma_c*(self.B*self.L)*self.h
        self.forces[-1][0]  = w_soil+w_col+w_p


    def set_foot_dimensions(self,B,L):
        '''
        Se calculan las propiedades de area y momento
        de inercia de la zapata para el calculo de presiones
        Parameters
        ----------
        B : Ancho de zapata (eje x).
        L : Largo de zapata (eje y).
        Returns
        -------
        None.
        '''
        self.B = B
        self.L = L
        self.Lv1=(self.B-self.b_col)/2
        self.Lv2=(self.L-self.h_col)/2
        self.A=B*L
        self.Izx=B*L**3/12
        self.Izy=B**3*L/12

    def ultimate_shear(self):
        self.σ_U=np.amax(self.data_presiones[6:11])
        self.V_u=self.σ_U*self.b*(max(self.Lv1,self.Lv2)-self.d) #d_eff < Lv1]

    def ultimate_moments(self):
        self.Mu_x=self.σ_U*self.Lv2*self.b
        self.Mu_y=self.σ_U*self.Lv1*self.b
        self.Mu=max(self.Mu_x,self.Mu_y)

    def punch_dimensions(self):
        #Lados del perimetro punzonado
        self.h_pun=self.h_col+self.d/2 #Para la dimension en Y 
        self.b_pun=self.b_col+self.d/2 #Para la dimension en X
        #perimetro y area de punzonamiento:
        self.punch_perim=2*(self.h_pun+self.b_pun)
        self.punch_area=self.h_pun*self.b_pun

    def ultimate_punch_shear(self):
        self.punch_pressures() #Hallamos las presiones en las esquinas del área de punzonamiento PARA CADA COMBINACION
        V_punch = []
        for caso in range (np.shape(self.punch_presiones)[0]):
            p_p = self.punch_presiones[caso][:][:]
            #Hallamos el promedio de las 4 esquinas
            prom_caso = np.average(p_p)
            #Reaccion que genera el area de punzonamiento
            Reaccion = prom_caso*self.punch_area 
            #Hallamos el Corte por Punzonamiento
            V_punch.append(self.Pu_push[caso]-Reaccion)

        self.V_punch = np.array(V_punch) #Vector de los cortantes de punzonamiento
        self.Vu_puz = np.amax(self.V_punch) # Cortante última por punzonamiento


    def nominal_punch_shear(self, phi_s=0.85):
        super().nominal_punch_shear(self.punch_perim, phi_s)


    def soil_pressures(self,X,Y):
        '''
        Se calculan la presiones del suelo para una coordenada
        dentro de la zapata, tomandose el centro de coordenadas el 
        centro de gravedad de la zapata.
        Parameters
        ----------
        X : coordenada X.
        Y : coordenada Y.
        Returns
        -------
        None.
        '''
        Coord=[[1/self.A],[Y/self.Izx],[X/self.Izy]]
        Co=np.array(Coord)
        self.Pres=np.dot(self.forces,Co)
        self.Re=np.dot(self.C,self.Pres)


    def areas_pressures(self, Case = 1, n=0.2):
        '''
        Se calculan todas la presiones para todas la combinaciones 
        de carga definidas para la sección de la zapata las cuales se
        guardan en matrices por cada tipo de combinación.
        Parameters
        ----------
        n : opcional, dimensión máx de un elemento discretizado (en metros).
        Case:
            1: Para obtener las presiones en las esquinas del área total de la zapata
            2: Para obtener las presiones en las esquinas del área punzonada de la zapata
        Returns
        -------
        None.
        '''
        
        if Case == 1:
            DimX, DimY = self.B, self.L
            numx = int(DimX/n)   
            numy = int(DimY/n)
        elif Case == 2:
            DimX, DimY = self.b_pun, self.h_pun
            numx = 2   #Solo evaluamos la presion en las esquinas
            numy = 2   #Solo evaluamos la presion en las esquinas

        X_list=np.linspace(-DimX/2,DimX/2,num=numx)
        Y_list=np.linspace(-DimY/2,DimY/2,num=numy)

        Mapa=np.zeros((len(self.C),len(Y_list),len(X_list)))
        for i in range(len(Y_list)):
            for j in range(len(X_list)):
                self.soil_pressures(Y_list[i],X_list[j])
                for k in range(len(self.Re)):
                    Mapa[k][i][j]=self.Re[k]
        return Mapa

    def total_pressures(self,n=0.20, nc=None, und=Pa):
        '''
        nc : opcional, indice de la combinación para ser ploteada.
        und: opcional, unidades del sistema, por defecto Pa.
        '''
        #Obtenemos las presiones Totales
        self.data_presiones = self.areas_pressures(Case=1, n=n)
        if nc==None:
            pass
        else:
            fig, ax = plt.subplots()
            im=ax.imshow((self.data_presiones[nc]/und),cmap = "gist_rainbow")
            cbar = ax.figure.colorbar(im, ax = ax)
            cbar.ax.set_ylabel("Color bar", rotation = -90, va = "bottom")

    def punch_pressures(self):
        #Obtenemos las presiones en las esquinas del área de punzonamiento
        presiones_pun = self.areas_pressures(Case=2)
        #Elegimos solo las combinaciones de diseño
        self.punch_presiones = presiones_pun[6:11]
        #Hallamos solo las cargas axiales de diseño que llegan al base de las columnas
        Vector_F=[[1],[0],[0]]
        Fo=np.array(Vector_F)
        Pu_colum=np.dot(self.forces,Fo)
        Pu_push=np.dot(self.C,Pu_colum)
        #Elegimos solo las combinaciones de diseño
        self.Pu_push = Pu_push[6:11]
        

            
    def press_check(self,n=0.1):
        '''
        Se verifica si la presión máxima a servicio cumple con la presión admisible
        del suelo.
        Parameters
        ----------
        B : Ancho de zapata (eje x).
        L : Largo de zapata (eje y).
        n : opcional, dimensión máx de un elemento discretizado (en metros).
        Returns
        -------
        bool
            DESCRIPTION.
        '''
        self.total_pressures(n)
        self.σ_max_g=np.amax(self.data_presiones[0]) #presión máxima por gravedad
        self.σ_max_sismo=np.amax(self.data_presiones[1:5]) #presión máxima por sismo
        self.σ_min=np.amin(self.data_presiones[0:5]) #presión mínima por gravedad y sismo
        if (self.σ_max_g<=self.soil.q_adm*0.96) and (self.σ_max_sismo<=self.soil.q_adm*1.3*0.96) and (self.σ_min>=0):
            return True
        else:
            return False
        

    def foot_sizing(self):
        '''
        Realiza las verificaciones de presiones en el suelo
        y dimensiona las secciones finales de la zapata B y L.
        Parameters
        ----------
        B : Ancho de la zapata (Dirección X).
        L : Largo de la zapata (Dirección Y).
        Returns
        -------
        None.
        '''
        #actualizando el valor del peso de la zapata y terreno
        B = self.B
        L = self.L
        self.soil_forces()
        
        i=0 
        while self.press_check()==False:
            B=round(B+0.1*m,2)
            L=round(B+(self.h_col-self.b_col),2)
            #actualizando el valor del peso de la zapata y terreno
            self.set_foot_dimensions(B,L)
            self.soil_forces()
            i=i+1
            if i==40: #contador para iteraciones máximas
                break
        self.total_pressures()


    def shear_design(self):
        '''
        Diseño a cortante de la zapata, itera hast obtener la altura de la zapata
        que cumple el diseño por cortante.
        Returns
        -------
        None.
        '''
       
        #Cortante ultimo y nominal
        self.ultimate_shear()
        self.nominal_shear()
        i=0
        while self.V_u>=self.phi_Vn:
            self.h=self.h+0.05
            self.d=self.h-self.r
            self.nominal_shear()
            i=i+1
            if i==40:
                break


    def punch_design(self):
        '''
        Verificación del punzonamiento de la columna sobre la zapata.
        Parameters
        ----------
        Returns
        -------
        None.
        '''
        self.punch_dimensions()
        self.ultimate_punch_shear()
        self.nominal_punch_shear()

        i=0
        while self.Vu_puz>=self.phi_Vn_p:
            self.h=self.h+0.05*m
            self.d=self.h-self.r
            self.nominal_punch_shear()
            i=i+1
            if i==40:
                break


    def flex_design(self):
        '''
        Diseño a flexión de la zapata con un ancho unitario por defecto.
        Returns
        -------
        None.
        '''
        fy = self.fy
        fc = self.fc
        b = self.b
        #Momentos ultimos
        self.ultimate_moments()

        self.As_min=0.0018*self.b*self.h
        #espaciamiento máximo 0.40cm

        #se inicia con malla de 3/8" y 0.40cm de espaciamiento
        #en set_barras se guardaran todas varillas con su espacimineto que cumplen
        self.set_barras=[]
        for i in bar_dic:
            for j in esp_list:
                #math.ceil(b/j) es el numero de barras
                #bar_dic[i][1] es el area de una varilla de acero
                #i: es el string con el nombre de la varilla
                #j: es el espaciamiento de la lista de espaciamientos
                if (2*math.ceil(b/j)*bar_dic[i][1])>=self.As_min:
                    self.set_barras.append([i,j])
        self.set_diseño=[]
        for i in self.set_barras:
            a=bar_dic[i[0]][1]*fy/(0.85*fc*b)
            phiMn=0.90*bar_dic[i[0]][1]*(math.ceil(b/i[1]))*fy*(self.d-a/2)
            if phiMn>self.Mu and phiMn<1.30*self.Mu:
                self.set_diseño.append([i[0],i[1],phiMn])



if __name__ == '__main__':
    pass



