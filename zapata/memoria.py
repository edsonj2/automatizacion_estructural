
ecuaciones = (
r'''% Longitud de desarrollo %Varibles db, fy, f'c
\newcommandx{\Ldi}[3][1=d_b, 2=f_y, 3=f'_c]{0.08 \cdot #1 \cdot \dfrac{#2}{\sqrt{#3}}}
\newcommandx{\Ldii}[2][1=d_b, 2=f_y]{0.004 \cdot #1 \cdot #2}

% d = max(ld1, ld2) 
\newcommandx{\ddd}[2][1=L_{d1}, 2=L_{d2}]{\max(#1, #2)}

% hz = d + 0.1m
\newcommandx{\hz}[1][1=d]{d + 0.1m}

% Capacidad portante neta del terreno
% Variables: σn = σt - γc·hz - γm·hs - γc·hp - S/C_piso
\newcommandx{\qn}[7][1=\sigma_t, 2=\gamma_c, 3=h_z, 4=\gamma_m, 5=h_s, 6=h_p, 7=S/C_{piso}]{#1 - #2 \cdot #3 - #4\cdot#5 - #2\cdot#6 - #7}

% Área tentativa % Variables: Pservicio, σn
\newcommandx{\AreaTentativa}[2][1=P_{servicio}, 2=\sigma_n]{\dfrac{#1}{#2}}
 
% Dimensiones de la zapata L y B
% Variables: At, c1, c2
\newcommandx{\LongitudZapL}[3][1=A_t, 2=c_1, 3=c_2]{\sqrt{#1} + \dfrac{#2 - #3}{2}} %Para L
\newcommandx{\LongitudZapB}[3][1=A_t, 2=c_1, 3=c_2]{\sqrt{#1} - \dfrac{#2 - #3}{2}} %Para B
\newcommandx{\Area}[2][1=L, 2=B]{#1 \cdot #2}

% Verificación de zapatas con cargas y momentos biaxiales
% variables: Pultima, Area(A), Mx, Vx, Iyy + My, Vy, Ixx
\newcommandx{\EcPresiones}[8][1=P_{ultima}, 2=A, 3=M_x, 4=V_x, 5=I_{yy}, 6=M_y, 7=V_y, 8=I_{xx}]{\sigma_{1,2,3,4} = \dfrac{#1}{#2} \pm \dfrac{#3\cdot#4}{#5} \pm \dfrac{#6\cdot#7}{#8}}

% Verificación de corte por punzonamiento
% Sección crítica bo, variables: c1, c2, d
\newcommandx{\SeccCriticaP}[3][1=c_1, 2=c_2, 3=d]{2(#1 + #3) + 2(#2 + #3)}
% Area tributaria, variables: c1, c2, d
\newcommandx{\AreaTributariaP}[3][1=c_1, 2=c_2, 3=d]{(#1 + #3)\cdot(#2 + #3)}

% Cortante de diseño por corte-punzonamiento
% Variables: σu, A, Ao
\newcommandx{\VuPunzonamiento}[3][1=\sigma_u, 2=A, 3=A_o]{#1 \cdot (#2 - #3)}

% Verificación cortante por punzonamiento (las 3 verificaciones)
% Variables: σ=0.85, f'c, bo, d, αs, β
\newcommandx{\VcPunzonamientoi}[4][1=f'_c, 2=b_o, 3=d, 4=\beta]{0.85 \cdot (0.17 \left( 1 + \dfrac{2}{#4} \right) \sqrt{#1}\cdot #2 \cdot #3)}

\newcommandx{\VcPunzonamientoii}[5][1=f'_c, 2=b_o, 3=d, 4=\beta, 5=\alpha_s]{0.85 \cdot ( 0.083 \left( \dfrac{#5 \cdot #3}{#2} + 2\right) \sqrt{#1}\cdot #2 \cdot #3)}

\newcommandx{\VcPunzonamientoiii}[3][1=f'_c, 2=b_o, 3=d]{0.85 \cdot (0.33 \cdot \sqrt{#1} \cdot #2 \cdot #3)}


% Cortante de diseño por flexion
% Variables: σu, B, c, d
\newcommandx{\VuFlexion}[4][1=\sigma_u, 2=B, 3=c, 4=d]{#1 \cdot #2 \cdot (#3 - #4)}

% Verificación cortante por corte-flexion
% Variables: σ=0.85, f'c, B, d
\newcommandx{\VcFlexion}[3][1=f'_c, 2=B, 3=d]{0.85 \cdot 0.17 \cdot \sqrt{#1} \cdot #2 \cdot #3}

% Cálculo de acero por flexión
% Variables: σu, Lv=, B=prof de la zapata
\newcommandx{\MomUltimoi}[3][1=\sigma_u, 2=L_v, 3=B]{\dfrac{#1 \cdot (#2)^2 \cdot #3}{2}}

% Variables: Mu, φ, B, d, f'c, %%w
\newcommandx{\MomUltimoii}[5][1=M_u, 2=\phi, 3=B, 4=d, 5=f'c]{#1 = #2 (#3)(#4^2)(#5)(w)(1 - 0.59 \cdot w)}

% Cálculo del área de acero
% Variables: w, b, d, f'c, fy
\newcommandx{\AreaAcero}[5][1=w, 2=b, 3=d, 4=f'_c, 5=f_y]{\dfrac{#1 \cdot #2 \cdot #3 \cdot #4}{#5}}

% Área de acero mínimo
% Variables: b, h
\newcommandx{\AreaAceroMin}[2][1=b, 2=h]{0.0018 \cdot #1 \cdot #2}  
'''
)

introduccion = (
r'''\subsection{Diseño de la cimentación}
Se presentaran las consideraciones para el dimensionamiento de la cimentación, control de presiones y el cálculo del refuerzo con las verificaciones necesarias en concreto armado.\\
Se asumen dos hipótesis básicas:
\begin{enumerate}
    \item El suelo es homogéneo, elástico y aislado del suelo circundante.
    \item Considerar la flexibilidad de la Cimentación y del suelo.
\end{enumerate}

\subsubsection{Modelamiento}
El modelo matemático simple que se usa en la practica consiste en incluir la flexibilidad del suelo a través de módulos de subrasante, el modelo más conocido es la solución de Winkler.\\
Es un modelo aproximado que se propuso en 1867, el cual sirve para resolver fundaciones sobre medios elásticos. Este método considera el suelo como un lecho de resortes. La presión de contacto queda definida por el producto de la rigidez elástica del resorte y el asentamiento que se ha producido en él debido a las cargas que actúan.\\

\begin{figure}[h!]
    \centering
    \caption{Modelamiento de la cimentación}
    \includegraphics[trim={0 0.5cm 0 0},clip,scale=0.6]{../idealizacion_cim.png}
    %\caption*{\small Fuente: \it \cite{empuje}}
    \label{atrans}
\end{figure} 
\newpage
En su tesis de maestría el ingeniero Nelson Morrison recopila varios estudios anteriormente realizados que relacionan directamente el módulo de subrasante con la capacidad admisible del suelo, el cual es válido para un área y NO necesita ser modificado a las dimensiones de la cimentación.

\begin{figure}[h!]
    \centering
    \caption{Coeficientes de Winkler}
    \includegraphics[scale=1]{../tabla_winkler.PNG}
    %\caption*{\small Fuente: \it \cite{empuje}}
    \label{atrans}
\end{figure} 

Cabe resaltar que para el diseño de fundaciones SAFE usa el Modelo de Winkler , el cual se resuelve a través del método de los elementos finitos FEM, usando elementos línea, áreas y resorte.\\
Structural Analysis by Finite Elements (SAFE), es un software creado por la empresa Computers and Structures, Inc. (CSI) , el cual sirve para diseñar sistemas de pisos ( Losas y Vigas) y Sistemas de Fundaciones.

\subsubsection{Tipología de la cimentación}
Se proyectan zapatas aisladas, zapatas combinadas y plateas parciales, debido a la presencia de las edificaciones vecinas las cimentaciones resultan excéntricas en 3 lados del edificio por lo que se hace uso de vigas rígidas de cimentación para controlar los momentos producto de la excentricidad de la carga axial. Tales vigas son diseñadas solo para tomar los momentos y uniformizar las presiones en la cimentación y no es diseñada para soportar fuerzas inducidas por la presión del suelo, por lo que debe ser aislada del suelo adecuadamente.\\
El peralte de la cimentación adoptado es el requerido para las solicitaciones de corte y/o punzonamiento en la cimentación, así como para asegurar el desarrollo del refuerzo que llega de las columnas y muros.\\
En las zapatas aisladas no existe momentos que traccionen la cara superior de la zapata por lo que no es necesario colocar refuerzo superior, sin embargo en las zapatas combinadas o cuando se colocan vigas de conexión si existen momento positivo y negativo, por lo que es necesario colocar doble malla.

\subsubsection{Exportación de cargas de ETABS a SAFE}
Debido a que los resultados del análisis modal espectral son productos de una combinación se pierde el signo en las fuerzas, para un análisis racional se exporto las cargas de los modos principales en ambas direcciones escalando sus valores proporcionalmente al valor los momentos totales en la base que se generan a partir de las fueras sísmicas de diseño.

\subsubsection{Predimensionamiento}

Se dimensiono preliminarmente considerando cargas en servicio (D+L) con un 90\% de la capacidad portante para tener holgura cuando se verifica con cargas sísmicas, posteriormente estas dimensiones se corrigieron después del análisis.\\
Para las zapatas combinadas se trató de hacer coincidir el centro de gravedad de la zapata con el de las cargas para el caso de cargas gravitacionales (D+L), adicionalmente en todos los casos se dimensiono tratando de tener volados iguales en ambas direcciones para uniformizar el diseño en concreto armado.\\
Después de realizar un análisis iterativo se obtiene las áreas de cimentación mostradas en la figura  para no superar la presión admisible tanto para cargas de gravedad y sísmicas. 
'''
)

presiones =(
r'''\subsubsection{Control de presiones}

15.2.4 Se podrá considerar un incremento del 30\% en el valor de la presión admisible del suelo para los estados de cargas en los que intervengan cargas temporales, tales como sismo o viento.\\
15.2.5 Para determinar los esfuerzos en el suelo o las fuerzas en pilotes, las acciones sísmicas podrán reducirse al 80\% de los valores provenientes del análisis, ya que las solicitaciones sísmicas especificadas en la NTE E.030 Diseño Sismorresistente están especificadas al nivel de resistencia de la estructura.

\newpage
\noindent Por lo tanto las combinaciones para el control de presiones en condiciones de servicio sera:
\begin{center}
    S1= CM + CV\\
    S2= ( CM+CV + 0.8 SX )/1.3\\
    S3= ( CM+CV - 0.8 SX )/1.3\\
    S4= ( CM+CV + 0.8 SY )/1.3\\
    S5= ( CM+CV - 0.8 SY )/1.3 
\end{center}
\noindent 
Donde:\\
CM: Carga muerta en servicio\\
CV: Carga viva en servicio\\
SX: Carga sísmica en dirección X\\
SY: Carga sísmica en dirección Y\\

\begin{figure}[h!]
    \centering
    \subfigure[Sin vigas de conexión]{\includegraphics[width=70mm]{wvc.PNG}}\hspace{10mm}
    \subfigure[Con vigas de conexión de 30x70]{\includegraphics[width=70mm]{co1.PNG}}
    \caption{Presiones para la combinación D+L }
    \label{corw}
\end{figure}
\newpage
\begin{figure}[h!]
    \centering
    \subfigure[D+L+SX]{\includegraphics[width=70mm]{co2.PNG}}\hspace{10mm}
    \subfigure[D+L-SX]{\includegraphics[width=70mm]{co3.PNG}}
    \caption{Presiones para la combinación con sismo en X}
    \label{corw}
\end{figure}

\begin{figure}[h!]
    \centering
    \subfigure[D+L+SY]{\includegraphics[width=70mm]{co4.PNG}}\hspace{10mm}
    \subfigure[D+L-SY]{\includegraphics[width=70mm]{co5.PNG}}
    \caption{Presiones para la combinación con sismo en Y}
    \label{corw}
\end{figure}
\noindent
La capacidad portante admisible del terreno a -2.8m donde se cimienta la parte frontal del edifico es de $1.82\mathrm{~kg/cm^2} $.\\
En la parte posterior a una cota de +0.50m la capacidad portante admisible del terreno es $1.42\mathrm{~kg/cm^2}$.\\
En todos los casos se cumple con la condición: $q_{u}\leq q_{n}$, siendo el caso mas critico la combinación de cargas gravitacionales dado que las cargas sísmicas se reducen considerablemente debido a lo mencionado en los artículos 15.2.4 y 15.2.5 de la \cite{E-060}.\\
Las dimensiones finales se muestran en la figura \ref{dim}:
\begin{figure}[h!]
    \centering
    \caption{Dimensiones de la cimentación}
    \includegraphics[scale=0.9]{dimensiones.png}
    %\caption*{\small Fuente: \it \cite{empuje}}
    \label{dim}
\end{figure} 
'''
)

req_min = (
r'''\newpage
\subsubsection{Diseño en concreto armado}
\noindent 
Según el articulo 10.5.4 la cuantía mínima en zapatas sera de 0.0018, y cuando el refuerzo se distribuya en 2 capas la cuantía mínima en la cara en tracción sera 0.0012.\\
Después de realizar el diseño en concreto armado con los requisitos mínimos de la norma se obtuvo los siguientes armados en la cimentación:
% Please add the following required packages to your document preamble:
% \usepackage{multirow}
\begin{table}[h!]
\caption{Refuerzo en cimentación}
{
\extrarowheight = 0ex
\renewcommand{\arraystretch}{1.2}
\begin{tabular}{|cc|cc|c|c|c|}
\hline
\multicolumn{2}{|c|}{\textit{\textbf{CIMENTACION}}}                       & \multicolumn{2}{c|}{\textit{\textbf{Refuerzo}}}                    & \textit{\textbf{Espesor}} & \textit{\textbf{Ancho}} & \textit{\textbf{Largo}} \\ \hline
\multicolumn{1}{|c|}{\textit{\textbf{N°}}} & \textit{\textbf{Ubicación:}} & \multicolumn{1}{c|}{\textit{\textbf{X-X}}} & \textit{\textbf{Y-Y}} & \textit{\textbf{e (cm)}}  & \textit{\textbf{B (m)}} & \textit{\textbf{L (m)}} \\ \hline
\multicolumn{1}{|c|}{\multirow{2}{*}{1}}   & Inferior                     & \multicolumn{1}{c|}{1/2"@17.5cm}           & 1/2"@17.5cm           & 55                        & \multirow{2}{*}{var}    & \multirow{2}{*}{var}    \\ \cline{2-5}
\multicolumn{1}{|c|}{}                     & Superior                     & \multicolumn{1}{c|}{5/8"@22.5cm}           & 5/8"@22.5cm           & 55                        &                         &                         \\ \hline
\multicolumn{1}{|c|}{\multirow{2}{*}{2}}   & Inferior                     & \multicolumn{1}{c|}{1/2"@17.5cm}           & 5/8"@22.5cm           & 55                        & \multirow{2}{*}{1.425}  & \multirow{2}{*}{var}    \\ \cline{2-5}
\multicolumn{1}{|c|}{}                     & Superior                     & \multicolumn{1}{c|}{1/2"@17.5cm}           & 1/2"@17.5cm           & 55                        &                         &                         \\ \hline
\multicolumn{1}{|c|}{\multirow{2}{*}{3}}   & Inferior                     & \multicolumn{1}{c|}{5/8"@22.5cm}           & 1/2"@17.5cm           & 55                        & \multirow{2}{*}{1.6}    & \multirow{2}{*}{5}      \\ \cline{2-5}
\multicolumn{1}{|c|}{}                     & Superior                     & \multicolumn{1}{c|}{5/8"@22.5cm}           & 1/2"@17.5cm           & 55                        &                         &                         \\ \hline
\multicolumn{1}{|c|}{\multirow{2}{*}{4}}   & Inferior                     & \multicolumn{1}{c|}{5/8"@22.5cm}           & 1/2"@17.5cm           & 55                        & \multirow{2}{*}{1.5}    & \multirow{2}{*}{2}      \\ \cline{2-5}
\multicolumn{1}{|c|}{}                     & Superior                     & \multicolumn{1}{c|}{1/2"@17.5cm}           & 1/2"@17.5cm           & 55                        &                         &                         \\ \hline
\multicolumn{1}{|c|}{\multirow{2}{*}{5}}   & Inferior                     & \multicolumn{1}{c|}{1/2"@17.5cm}           & 5/8"@20cm             & 60                        & \multirow{2}{*}{1.5}    & \multirow{2}{*}{5.2}    \\ \cline{2-5}
\multicolumn{1}{|c|}{}                     & Superior                     & \multicolumn{1}{c|}{1/2"@17.5cm}           & 1/2"@17.5cm           & 60                        &                         &                         \\ \hline
\multicolumn{1}{|c|}{\multirow{2}{*}{6}}   & Inferior                     & \multicolumn{1}{c|}{5/8"@20cm}             & 5/8"@20cm             & 55                        & \multirow{2}{*}{1.4}    & \multirow{2}{*}{1.6}    \\ \cline{2-5}
\multicolumn{1}{|c|}{}                     & Superior                     & \multicolumn{1}{c|}{---}                   & ---                   & 55                        &                         &                         \\ \hline
\multicolumn{1}{|c|}{\multirow{2}{*}{7}}   & Inferior                     & \multicolumn{1}{c|}{1/2"@17.5cm}           & 5/8"@20cm             & 60                        & \multirow{2}{*}{var}    & \multirow{2}{*}{5.9}    \\ \cline{2-5}
\multicolumn{1}{|c|}{}                     & Superior                     & \multicolumn{1}{c|}{1/2"@17.5cm}           & 1/2"@17.5cm           & 60                        &                         &                         \\ \hline
\end{tabular}
}
\end{table}
'''
)

datos = (
r'''\subsubsection{Datos para el diseño de una zapata aislada con carga y momentos}

\begin{table}[h!]
    \centering

    \begin{tabular}{lcl} %\toprule
        Dimensiones de la columna               &:& $C_1        = \hcol$m \quad $C_2 = \bcol$m\\
        Profundidad de cimentación              &:& $D_f        = 1.70 $m\\
        Altura de piso terminado                &:& $h_p        = 0.10$m\\
        Resistencia a compresión del concreto   &:& $f'_c       = 210$ kg/cm$^2$ \\
        Resistencia a la fluencia del acero     &:& $f_y        = 4200$ kg/cm$^2$ \\
        Peso específico del relleno             &:& $\gamma_m   = 2.1$ ton/m$^3$ \\
        Peso específico del concreto            &:& $\gamma_c   = 2.4$ ton/m$^3$ \\
        Sobrecarga de piso                      &:& $S/C_{piso}$= 500 kg/m$^2$ \\ 
        Capacidad portante del terreno          &:& $\sigma_t$  = 3 kg/cm$^2$  \\ %= 30 ton/m$^2$
        
    \end{tabular}
\end{table}

\textbf{Cargas:}


\begin{table}[h!]
    \centering
    \begin{tabular}{cccc} \toprule
         & Carga en la dirección Z & Momento en la dirección X & Momento en la dirección Y  \\ 
         & $F_z$ & $M_x $ & $M_y$ \\ \midrule
        $P_m$ & 130& 10 & 2 \\
        $P_v$ & 70 & 6 & 1 \\
        $S_x$ & 10 & 15 & 0 \\
        $S_y$ & 9 & 0 & 13 \\
        $V_x$ & 180 & 16 & 11 \\
        $V_y$ & 180 & 16 & 11 \\
        $P_p$ & 180 & 16 & 11 \\\bottomrule
    \end{tabular}
    \caption{Cargas y momentos para el diseño}
    \label{tab:my_label}
\end{table}

\begin{table}[h!]
    \centering
    \begin{tabular}{lll}
        $P_m$ &=&   Carga muerta\\
        $P_v$ &=&   Carga viva\\
        $S_x$ &=&   Carga sísmica debido al sismo en la dirección x\\
        $S_y$ &=&   Carga sísmica debido al sismo en la dirección y\\
        $V_x$ &=&   Carga por viento en la dirección x\\
        $V_y$ &=&   Carga por viento en la dirección y\\
        $P_p$ &=&   Peso propio\\
    \end{tabular}
\end{table}
'''
)


cap_portante = (
r'''\subsubsection{Capacidad portante neta del terreno}

El concepto de capacidad portante neta que es la capacidad del terreno reducida por efecto de la sobrecarga, el peso del suelo y el peso de la zapata. La capacidad portante neta es igual a:
\begin{align}
	\sigma_{sn} =&\qn \\
	\sigma_{sn} =&\qn[\sigmat][\gammac][\hz][\gammam][\hs][\hp][\SC]\\
	\sigma_{sn} =& \sigmas%
\end{align}

\textbf{Donde:}

\begin{table}[h!]
    \centering
    \begin{tabular}{lll}
        $\sigma_{sn}$ &=&    Capacidad portante neta.\\
        $\sigma_t$ &=&   Carga admisible del terreno.\\
        $\gamma_c$ &=&    Peso específico del concreto\\
        $h_s$ &=&   Altura del suelo sobre la zapata.\\
    \end{tabular}
\end{table}
'''
)

def cap_portante_2(σt,γc,hz,γm,hs,hp,SCpiso,σsn):
    return fr'''\subsubsection{{Capacidad portante neta del terreno}}

    El concepto de capacidad portante neta que es la capacidad del terreno reducida por efecto de la sobrecarga, el peso del suelo y el peso de la zapata. La capacidad portante neta es igual a:
    \begin{{align}}
        \sigma_{{sn}} =&\qn \\
        \sigma_{{sn}} =&\qn[{σt.to('kgf/cm**2').magnitude:.2f}][{γc.magnitude:.2f}][{hz.magnitude:.2f}][{γm.magnitude:.2f}][{hs.magnitude:.2f}][{hp.magnitude:.2f}][{SCpiso.magnitude:.2f}]\\
        \sigma_{{sn}} =& {σsn.magnitude:.2f}
    \end{{align}}

    \textbf{{Donde:}}

    \begin{{table}}[h!]
        \centering
        \begin{{tabular}}{{lll}}
            $\sigma_{{sn}}$ &=&    Capacidad portante neta.\\
            $\sigma_t$ &=&   Carga admisible del terreno.\\
            $\gamma_c$ &=&    Peso específico del concreto\\
            $h_s$ &=&   Altura del suelo sobre la zapata.\\
        \end{{tabular}}
    \end{{table}}
    '''