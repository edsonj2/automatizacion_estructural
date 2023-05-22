def tex_py(texto):
    return texto.replace('{', '{{').replace('}', '}}').replace('[','[{').replace(']','}]')

texto_sin_variable = tex_py(r'''
\begin{align*}
	L &= \LongitudZapL[7.77][0.80][0.40] = 3.10\\
	B &= \LongitudZapB[7.77][0.80][0.40] = 2.70\\
	A &= \Area[3.10][2.70] = 
\end{align*}
''')

print(texto_sin_variable)