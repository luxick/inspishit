import re
from threading import Thread
import tkinter
import requests
from io import BytesIO
from PIL import Image, ImageTk
import argparse


class App(tkinter.Tk):
    def __init__(self, delay, url, width=None, height=None):
        tkinter.Tk.__init__(self)
        self.title('inspishit')
        self.resizable(False, False)
        self.focus_set()
        if not (width and height):
            self.attributes('-fullscreen', True)
            self.w = self.winfo_screenwidth()
            self.h = self.winfo_screenheight()
        else:
            self.w = width
            self.h = height
        self.bind('<Escape>', lambda e: self.quit())

        self.geometry('{}x{}+0+0'.format(self.w, self.h))
        self.delay = delay
        self.url = url
        self.img = None
        self.canvas = tkinter.Canvas(self, width=self.w, height=self.h)
        self.canvas.pack()
        self.canvas.configure(background='black')
        self.show_text('Now Loading...')
        self.load_new_image()

    def run(self):
        self.mainloop()

    def resize_to_fit(self, pil_image):
        img_width, img_height = pil_image.size
        # scale the image to maximum available size
        ratio = min(self.w / img_width, self.h / img_height)
        img_width = int(img_width * ratio)
        img_height = int(img_height * ratio)
        return pil_image.resize((img_width, img_height), Image.ANTIALIAS)

    def show_text(self, msg):
        self.canvas.delete('all')
        self.canvas.create_text(self.w / 2, self.h / 2,
                                text=msg, fill='#fff', font='80')

    def update_img(self, pil_image):
        self.img = ImageTk.PhotoImage(self.resize_to_fit(pil_image))
        self.canvas.delete('all')
        img_area = self.canvas.create_image(self.w / 2, self.h / 2)
        self.canvas.itemconfig(img_area, image=self.img)
        self.after(self.delay, self.load_new_image)

    def load_new_image(self):
        print('Starting image refresh...')
        thread = Thread(target=self.get_img, args=(self.update_img, self.url))
        thread.start()

    @staticmethod
    def get_img(callback, url):
        response = requests.get(url)
        print(f'Got image url {response.content}')
        img_url = response.content
        img_response = requests.get(img_url)
        print('Got image data')
        callback(Image.open(BytesIO(img_response.content)))
        print('Image refresh successful\n')


if __name__ == '__main__':

    def check_positive(value):
        i_value = int(value)
        if i_value <= 0:
            raise argparse.ArgumentTypeError(f'{value} is an invalid positive int value')
        return i_value
    
    def check_window_size(value):
        if not re.compile(r'[0-9]+x[0-9]+').match(value):
            raise argparse.ArgumentTypeError('Window size must be passed like 1920x1080')
        return value

    parser = argparse.ArgumentParser(description='Display random bullshit inspirational quotes.')
    parser.add_argument('-i', metavar='seconds', dest='interval', type=check_positive,
                        help='Time interval between image changes in seconds. Default: 360',
                        default=360)
    parser.add_argument('-w', metavar='window_size', dest='window_size', type=check_window_size,
                        help='Start in windowed mode')
    parser.add_argument('-x', '--xmas-mode', dest='xmas',
                        help='Show shitty christmas themed inspiration.',
                        action='store_true')
    args = parser.parse_args()

    api_url = 'http://inspirobot.me/api?generate=true'
    if args.xmas:
        api_url = f'{api_url}&season=xmas'

    w, h = args.window_size.split('x')

    app = App(args.interval * 1000, api_url, int(w), int(h))
    app.run()
