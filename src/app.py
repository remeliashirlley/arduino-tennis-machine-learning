from customtkinter import *
from BLEDataReceiver import BLEDataReceiverThread
import os
import queue
from PIL import Image
import random

class MainWindow:
    """
    UI for Arduino Ace Tennis game
    Initialize the game window and integrate with BLEDataReceiverThread class to receive inference and play the game in real-time

    Args:
        None

    Return:
        None
    """

    def __init__(self):
        self.root=CTk(fg_color='#0C0D0D') #fg_color='#0C0D0D'
        self.root.state('zoomed')
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()
        self.root.grid_columnconfigure(0, weight=1)

        self.debug_mode=False
        self.sleep_time=60

        self.start_page()

        self.root.mainloop()

    def clear_widgets(self):
        '''fn to delete all children widgets from window'''
        for widget in self.root.winfo_children():
            widget.destroy()

    def start_page(self):
        '''widgets for game start page (home screen)'''
        #self.clear_widgets()
        self.home_frame=CTkFrame(self.root,fg_color='#0C0D0D')
        self.home_frame.grid(row=0, column=0, sticky='nsew') 
        self.home_frame.grid_columnconfigure(0, weight=1)
        
        self.home_left=CTkFrame(self.home_frame,fg_color='#0C0D0D')
        self.home_left.grid(row=0, column=0, sticky='ew') 

        home_img=CTkImage(dark_image=Image.open(os.path.dirname(os.path.realpath(__file__))+ "/assets/kevin-mueller-Q-fL04RhuMg-unsplash.jpg"), size=(self.screen_height/2772*1848,self.screen_height))
        CTkLabel(self.home_frame, image=home_img, text='').grid(row=0, column=1, sticky='ns')

        CTkLabel(self.home_left, text='Arduino Ace Tennis', font=("Helvetica", 54)).grid(row=0, column=0, sticky='sw', padx=100, pady=20)
        CTkLabel(self.home_left, text='Dive into the ultimate fusion of tennis finesse and tech wizardry! Harness the power of Arduino-driven gestures on your racquet to perfect your swings. Elevate your game, sharpen your control, and groove to the rhythm of victory!', font=("Helvetica", 18), wraplength=500, justify="left").grid(row=1, column=0, sticky='nw', padx=100)
        CTkLabel(self.home_left, text='CE4172\nInternet of Things: Tiny ML\nRemelia Shirlley', font=("Helvetica", 14), justify="left").grid(row=2, column=0, sticky='sw', padx=100, pady=40)
        self.switch_var = StringVar(value="off")
        CTkSwitch(self.home_left, text="Debug Mode", command=self.debug_switch, variable=self.switch_var, onvalue="on", offvalue="off").grid(row=3, column=0, sticky='w', padx=100, pady=50)
        CTkButton(self.home_left, text='Start Game', command=self.start_game, font=("Helvetica", 18), height=60, width=240, fg_color='#DFDD00', hover_color='#848303', text_color='black').grid(row=4, column=0, sticky='nw', padx=100, pady=20)
        
    def debug_switch(self):
        '''fn to modify sleep time during game program to debug/test inference'''
        if self.switch_var.get()=='on':
            self.sleep_time=600
            self.debug_mode=True
        else:
            self.sleep_time=30
            self.debug_mode=False

    def start_game(self):
        '''main fn executed when start game button is clicked'''
        self.end_flag=False
        self.clear_widgets()
        self.tile_frame()
        self.lives=5
        self.life_display()
        
        self.queue=queue.Queue()
        self.thread=BLEDataReceiverThread(self.queue, self.sleep_time)
        self.thread.start()
        self.round()

    def tile_frame(self):
        '''widgets for game frame; declares tiles'''
        self.game_frame=CTkFrame(self.root,fg_color='#0C0D0D')
        self.game_frame.grid(row=0, column=0, padx=10, pady=30, sticky='ns') 

        #self.prediction_label=CTkLabel(self.root, text='Forehand Low', fg_color="#0C0D0D", padx=10, pady=10)
        #self.prediction_label.place(relx=0.1,rely=0.15)

        self.tiles={}
        for i in range(4):
            self.tiles[f'{i}']=CTkLabel(self.game_frame, text='', fg_color="lightblue", padx=150, pady=150)      

        for key,val in self.tiles.items():
            row=1 if key in ('1', '3') else 2
            col=1 if key in ('2', '3') else 2
            val.grid(row=row, column=col, padx=30, pady=30)

        stroke_labels={'Backhand':(3,1), 'Forehand':(3,2), 'High':(1,0), 'Low':(2,0)}
        for key, value in stroke_labels.items():
            CTkLabel(self.game_frame, text=key, font=("Helvetica", 20), width=50).grid(row=value[0], column=value[1])
        CTkLabel(self.game_frame, text='', width=50).grid(row=0, column=3) #dummy widget to center tiles

        CTkButton(self.game_frame, text='End Game', command=self.set_end, font=("Helvetica", 14), height=40, width=120, fg_color='#DFDD00', hover_color='#848303', text_color='black').grid(row=4, column=1, columnspan=2, sticky='', pady=20)
        
    def set_end(self):
        '''fn executed when end game button clicked in the middle of game'''
        self.lives=0
        self.end_flag=True

    def draw_heart(self, canvas, x, y, size, colour):
        '''fn to draw a single heart for the lives feature'''
        coords = [
        (x, y - size),                        # Top center
        (x + size, y - size // 2),            # Top right
        (x + size // 2, y + size // 3),       # Right middle
        (x, y + size),                        # Bottom center
        (x - size // 2, y + size // 3),       # Left middle
        (x - size, y - size // 2)             # Top left
        ]

        # Draw the heart shape
        return canvas.create_polygon(coords, fill=colour)
    
    def draw_hearts(self, canvas_width, canvas_height):
        '''canvas with all the hearts/lives drawn with draw_heart fn'''
        # Draw five hearts in a row
        heart_size = 20
        padding = 20
        total_hearts_width = 5 * heart_size * 2 + 4 * padding  # Total width occupied by hearts and padding
        start_x = (canvas_width - total_hearts_width) // 2 + padding # Center the hearts horizontally
        start_y = canvas_height // 2
        
        for i in range(5):
            colour='red' if i<self.lives else 'grey'
            self.draw_heart(self.canvas, start_x + i * (heart_size * 2 + padding), start_y, heart_size, colour)

    def life_display(self):
        '''update no of lives/hearts throughout game'''
        canvas_width = 300  # Specify canvas width
        canvas_height = 60  # Specify canvas height
        self.canvas = CTkCanvas(self.game_frame, width=canvas_width, height=canvas_height, highlightthickness=0, bg='#0C0D0D')
        self.canvas.grid(row=0, column=1, columnspan=2, pady=20, sticky='n') 

        # Delay accessing canvas dimensions until after mainloop starts
        self.root.after(100, lambda: self.draw_hearts(canvas_width, canvas_height))
    
    def tile_select(self):
        '''fn to change colour of tile if selected'''
        if self.select!=None:
            self.tiles[f'{self.select}'].configure(fg_color="#3f6eab")

    def reset_tiles(self):
        '''reset colours of all tiles back to initial'''
        for i in range(4):
            self.tiles[f'{i}'].configure(fg_color="lightblue")

    def tile_check(self):
        '''change tile colour to green/red based on inference prediction'''
        self.tiles[f'{self.select}'].configure(fg_color="#68ad83" if self.action else "#d17575")

    def create_confetti(self):
        for _ in range(self.confetti_count):
            x = random.randint(0, self.screen_width)
            y = random.randint(0, self.screen_height)
            color = random.choice(self.confetti_colors)
            confetti = self.canvas.create_rectangle(x, y, x+15, y+15, fill=color, outline='')
            self.confetti_particles.append(confetti)

    def move_confetti(self):
        '''confetti animation for win screen after game over'''
        for confetti in self.confetti_particles:
            dx = random.randint(-3, 3)
            dy = random.randint(-3, 3)
            self.canvas.move(confetti, dx, dy)

        self.root.after(500, self.move_confetti)

    def game_over(self):
        '''fn to display game over screen based on win/lose results'''
        self.end_flag=True
        self.reset_tiles()
        outcome='win' if self.lives>0 else 'lose'

        self.canvas = CTkCanvas(self.root, bg="#0C0D0D",highlightthickness=0)
        self.canvas.grid(row=0,column=0, sticky='nsew')
        if outcome=='win':
            CTkLabel(self.root, text='You Win!', font=("Helvetica", 80)).place(relx=0.5, rely=0.5, anchor=CENTER)
            self.confetti_colors = ["#ff3155", "green", "#77c3dd", "#DFDD00", "#ffaf42", "purple"]
            self.confetti_count = 50
            self.confetti_particles = []
            self.create_confetti()
            self.move_confetti()
        elif outcome=='lose':
            CTkLabel(self.root, text='Game Over', font=("Helvetica", 80)).place(relx=0.5, rely=0.4, anchor=CENTER)
            CTkLabel(self.root, text='LOSER', font=("Helvetica", 60)).place(relx=0.5, rely=0.6, anchor=CENTER)

        self.root.after(5000,self.start_page)

    def process_queue(self):
        '''recursive fn to continuously check queue for inference results for each round in game'''
        if self.timer_count>70:
            print('timer up')
            while not self.queue.empty():
                self.queue.get()
            self.action=False
            if not self.action: 
                self.lives-=1 #lose a life
                self.life_display()
            self.tile_check()
            self.root.after(3000, self.round)
        else:
            try:       
                if self.thread.subscribe==False or self.end_flag==True:
                    self.game_over()

                result = self.queue.get_nowait()
                print(f'Result: {result}')

                self.action=True if result==self.select else False
                if not self.action: 
                    self.lives-=1 #lose a life
                    self.life_display()
                self.tile_check()
                #label_map={'0':'Forehand Low', '1':'Forehand High', '2':'Backhand Low', '3':'Backhand High'}
                #self.prediction_label.configure(text=label_map[str(result)])
                self.root.after(3000, self.round)

            except queue.Empty:
                self.timer_count+=1
                self.root.after(100, self.process_queue)

    def round(self):
        '''fn for each round in game; a round refers to random tile selected and wait for inference prediction/timeout'''
        self.timer_count=0
        while not self.queue.empty():
            self.queue.get()
        if self.end_flag==False and (self.lives>0 or self.debug_mode):
            self.reset_tiles()
            self.select=random.randint(0,3)
            print(self.select)
            self.tile_select()
 
            self.root.after(100,self.process_queue)
        else:
            self.game_over()