import tkinter as tk
import traci

row = 10
column = 10


class GridWin(tk.Tk):
	def __init__(self, row, column):
		super(GridWin, self).__init__()
		self.row = row
		self.column = column
		self.grid_frame = tk.Frame(self, height=500, width=100)
		self.grid_frame.pack()
		for i in range(row):
			for j in range(column):
				b= tk.Button(self.grid_frame, text=str(i)+' '+str(j))
				b.grid(row=row, column=column)


if __name__ == "__main__":
	root = GridWin(row, column)
	root.mainloop()