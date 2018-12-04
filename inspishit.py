from threading import Thread
import tkinter
import requests
from io import BytesIO
from PIL import Image, ImageTk
import argparse


class App(tkinter.Tk):
    def __init__(self, delay, url):
        tkinter.Tk.__init__(self)
        self.focus_set()
        self.attributes('-fullscreen', True)
        self.bind('<Escape>', lambda e: self.quit())
        self.w = self.winfo_screenwidth()
        self.h = self.winfo_screenheight()

        self.geometry('{}x{}+0+0'.format(self.w, self.h))
        self.delay = delay
        self.url = url
        self.canvas = tkinter.Canvas(self, width=self.w, height=self.h)
        self.img = tkinter.PhotoImage()
        self.img_area = self.canvas.create_image(self.w / 2, self.h / 2, image=self.img)
        self.canvas.pack()
        self.canvas.configure(background='black')
        self.update_img(Image.open('dummy.png'))

    def update_img(self, pil_image):
        img_width, img_height = pil_image.size
        # scale the image to maximum available size
        ratio = min(self.w/img_width, self.h/img_height)
        img_width = int(img_width*ratio)
        img_height = int(img_height*ratio)
        pil_image = pil_image.resize((img_width, img_height), Image.ANTIALIAS)

        self.img = ImageTk.PhotoImage(pil_image)
        self.canvas.itemconfig(self.img_area, image=self.img)
        self.after(self.delay, self.load_new_image)

    def run(self):
        self.mainloop()

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

    parser = argparse.ArgumentParser(description='Display random bullshit inspirational quotes.')
    parser.add_argument('-i', metavar='seconds', dest='interval', type=check_positive,
                        help='Time interval between image changes in seconds. Default: 360',
                        default=360)
    parser.add_argument('-x', '--xmas-mode', dest='xmas',
                        help='Show shitty christmas themed inspiration.',
                        action='store_true')
    args = parser.parse_args()

    api_url = 'http://inspirobot.me/api?generate=true'
    if args.xmas:
        api_url = f'{api_url}&season=xmas'

    app = App(args.interval * 1000, api_url)
    app.run()
