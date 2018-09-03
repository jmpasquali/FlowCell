## File: FlowCell.py 
## Author: Joana Pasquali
## Graphic interface for pumps control
## Inclui GPIOS

import Tkinter as tk
import ttk
import time
import threading	
import tkMessageBox
import RPi.GPIO as GPIO

def pararBombas(): 
	
	for i in pinList: 
		GPIO.output(i, GPIO.HIGH)

def qualMotor(processo): 

	if(processo == '1a limpeza de EtOH' or '2a limpeza de EtOH' or 'Limpeza de EtOH'):
		motor = 2
	if(processo == 'Dosagem de Tiol'):
		motor = 3
	if(processo == 'Dosagem de Suporte'):
		motor = 6
	if(processo == 'Secagem'):
		motor = 5

	return motor

class FlowCell(tk.Tk):
	
	def __init__(self, *args, **kwargs):
			
		tk.Tk.__init__(self, *args, **kwargs)	
		tk.Tk.wm_title(self, "FlowCell 2.0")
		tk.Tk.wm_geometry(self, '350x215')
		tk.Tk.wm_resizable(self, width=False, height=False)
		
		container = tk.Frame(self)
		container.pack(side="top", fill="both", expand = True)
		container.grid_rowconfigure(0, weight=1)
		container.grid_columnconfigure(0, weight=1)

		menu = tk.Menu(container)


		listaTiol = 	[	['1a limpeza de EtOH', 0],
			       		['Dosagem de Tiol', 0],
			  		['2a limpeza de EtOH', 0],
			       		['Secagem', 0]
				 ]


		listaSuporte = 	[	['1a limpeza de EtOH', 0],
			       		['Dosagem de Suporte', 0],
			  		['2a lavagem de EtOH', 0],				
			  		['Secagem', 0],
				 ]


		listaLimpeza =  [	['Limpeza com EtOh', 0],
			       		['Secagem', 0],
			 	]

       		menuProcessos = tk.Menu(menu, tearoff=0)
       		menu.add_cascade(menu=menuProcessos, label="Processo")

		menuProcessos.add_command(label="Dosagem de Tiol", command= lambda: self.show_frame(1))
		menuProcessos.add_command(label="Dosagem de Suporte",command= lambda: self.show_frame(2))
		menuProcessos.add_command(label="Limpar Sistema",command= lambda: self.show_frame(3))


       		menuAjuda = tk.Menu(menu, tearoff=0)
       		menu.add_cascade(menu=menuAjuda, label="Ajuda")
		menuAjuda.add_command(label="Sobre", command = lambda: tkMessageBox.showinfo('Sobre', '\n FlowCell \n LCM @ UCS \n Versao 2.0 '))

        	tk.Tk.config(self, menu=menu)

		self.frames = {}

		i = 1
		for lista in (listaTiol, listaSuporte, listaLimpeza):

			frame = NovaPagina(container, self, lista)
			self.frames[i] = frame
			frame.grid(row=0, column=0, sticky="nsew")
			i+= 1

		frame = StartPage(container, self)
		self.frames[StartPage] = frame
		frame.grid(row = 0, column = 0, sticky = "nsew")

		self.show_frame(StartPage)
		
	def show_frame(self, cont):

		frame = self.frames[cont]
		frame.tkraise()
	
class StartPage(tk.Frame):

	def __init__(self, parent, controller):

		tk.Frame.__init__(self,parent)

class NovaPagina(tk.Frame):

	def __init__(self, parent, controller, lista):

		tk.Frame.__init__(self,parent)
       		self.grid(sticky="news")

		## Labels auxiliares sao pra ficar mais bonito 
		auxLbl0 = ttk.Label(self, text= "                         ")
		auxLbl0.grid(column=0, row=0) 

		lbl0 = ttk.Label(self, text="    Defina os TEMPOS(s) para:    ")
		lbl0.grid(column=0, row=1, sticky='e') 

		auxLbl1 = ttk.Label(self, text= "                         ")
		auxLbl1.grid(column=0, row=2) 

		rowPosition = 3
		i=0
		listaEntrys = []

		## Cria pagina e text boxes 
		for processo, tempo in lista:

			## Cria Labels
			string = "lbl" + str(i+1)
			string = ttk.Label(self, text=processo+ ": ")
			string.grid(column = 0, row = rowPosition, sticky = 'e')
			
			## Cria TextEntrys
			string = "txt" + str(i+1)
			string = ttk.Entry(self, width=10) 
			string.grid(column = 1, row = rowPosition, sticky = 'e')
			listaEntrys.append(string) 

			## Itera			
			i+=1
			rowPosition+=1
			
		auxLbl1 = ttk.Label(self, text= "                         ")
		auxLbl1.grid(column=0, row=rowPosition) 
		
		def ThreadCancelar(): 

		    	t1 = threading.Thread(target= cancelar)
			t1.start()

		def ThreadIniciar(): 

		    	t2 = threading.Thread(target= iniciar)
			t2.start()

		def cancelar(): 

			global running
			running = 0
			#tkMessageBox.showinfo('Aviso', 'Voce clicou cancelar')
			btn.config(state = 'normal')
			btn2.config(state = 'disabled')
			
		def iniciar(): 
			
			GPIO.setmode(GPIO.BCM)

			pinList = [2, 3, 5, 6]

			for i in pinList: 
			    GPIO.setup(i, GPIO.OUT) 
			    GPIO.output(i, GPIO.HIGH)

			def DelayComProgressBar(tempo, texto): 

				## Cria progress bar e passa valores de sleep time
				global running 

				tempo = tempo * 100
				auxLbl4 = ttk.Label(self, text= "                         ")
				auxLbl4.grid(column=0, row=12) 

				progressVar = tk.DoubleVar() 
 				self.columnconfigure(4, weight = 1)
 				self.rowconfigure(rowPosition, weight = 1)
				progressbar = ttk.Progressbar(self, variable=progressVar, maximum=tempo)
				progressbar.grid(columnspan = 7, row = 14, sticky='senw')

				lblProgressBar.configure(text = texto)
				
				progressbar.maximum = tempo
				k = 1

				while k <= tempo:
				
					if running == 1: 					
						progressVar.set(k)
						k += 1
						time.sleep(0.01)
						self.update_idletasks()
						self.update_idletasks()
					else:  
						progressVar.set(0)
						lblProgressBar.configure(text = "Procedimento Cancelado!")
						break

			global running 
			running = 1
			
			i = 0
			error = 0

			for item in listaEntrys:
				
				try:
					lista[i][1] = float(item.get())
					i += 1
				except ValueError:
					error =1
		
			if(error == 0):
			
				## Desabilita botao iniciar, habilita cancelar
				btn.config(state = 'disabled')
				btn2.config(state = 'normal')

				tkMessageBox.showinfo('Aviso', 'Insira o SPE no modulo 1 da FlowCell')

				for processo, tempo in lista:

					pin = qualMotor(processo)
  					GPIO.output(pin, GPIO.LOW)
					DelayComProgressBar(tempo, processo)
					GPIO.output(pin, GPIO.HIGH)


				## Desabilita botao cancelar, habilita iniciar
				btn.config(state = 'normal')
				btn2.config(state = 'disabled')
			
				#t1.join()
				#t2.join()

				GPIO.cleanup()
			else:
				tkMessageBox.showinfo('Aviso', "Preenchimento invalido")


		btn2 = ttk.Button(self, text="Cancelar", state = 'disabled', command= ThreadCancelar)
		btn2.grid(column=0, row=rowPosition+1, sticky='e')

		btn = ttk.Button(self, text="Iniciar", command = ThreadIniciar)
		btn.grid(column=1, row=rowPosition+1)
		
		auxLbl2 = ttk.Label(self, text= "                         ")
		auxLbl2.grid(column=0, row=rowPosition+2) 

		lblProgressBar = tk.Label(self)
		lblProgressBar.grid(columnspan = 8, row = 13)


if __name__ == "__main__":

	app = FlowCell()
	app.geometry("350x215")
	app.mainloop()
