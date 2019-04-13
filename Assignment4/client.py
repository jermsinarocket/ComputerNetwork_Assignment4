#!/usr/bin/env python3

import socket
from threading import Thread
import pyaudio
from ctypes import *
import tkinter
from PIL import Image
from PIL import ImageTk
import threading
import sys
import cv2
import io

# Audio quality
CHUNK = 8192
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
WIDTH = 2
ERROR_HANDLER_FUNC = CFUNCTYPE(None, c_char_p, c_int, c_char_p, c_int, c_char_p)

#Capture for Webcam
cap = cv2.VideoCapture(0)

#Work around in case webcam is not opened
if cap.read() == False:
	cap.open()

# Prevents the ALSA debug information from spamming stdout
def py_error_handler(filename, line, function, err, fmt):
	pass


# PyAudio configurations
c_error_handler = ERROR_HANDLER_FUNC(py_error_handler)

p = pyaudio.PyAudio()

#For sending stream over to the server
stream_send = p.open(
	format=pyaudio.paInt16,
	channels=CHANNELS,
	rate=RATE,
	input=True,
	frames_per_buffer=CHUNK)

#For receving stream from the server and playing the stream
stream_recv = p.open(
	format=p.get_format_from_width(WIDTH),
	channels=CHANNELS,
	rate=RATE,
	output=True,
	frames_per_buffer=CHUNK)


# For Receiving Text
def receive_text():
	while True:
		try:
			msg = client_socket_text.recv(BUFSIZ).decode("utf8")
			msg_list.insert(tkinter.END,msg)
		except OSError:
			break


# For Receiving Voice
def receive_voice():
	while True:
		try:
			data = client_socket_voice.recv(BUFSIZ)
			stream_recv.write(data)
		except OSError:
			break

# For Receiving Video
def receive_video():
	global panel
	while not stop_video.is_set():
		try:
			ttlrec = 0
			metarec = 0

			msgArray = []
			metaArray = []

			while metarec < 8:
				chunk = client_socket_video.recv(8 - metarec).decode("utf8")
				if chunk == '':
					raise RuntimeError("Socket Connection has been broken")
				metaArray.append(chunk)
				metarec += len(chunk)

			lengthstr = ''.join(metaArray)
			length = int(lengthstr)

			while ttlrec < length:
				chunk = client_socket_video.recv(length - ttlrec)
				if chunk == '':
					raise RuntimeError("Socket Connection has been broken")
				msgArray.append(chunk)
				ttlrec += len(chunk)

			frame = b''.join(msgArray)
			pil_bytes = io.BytesIO(frame)
			pil_img = Image.open(pil_bytes)
			img = ImageTk.PhotoImage(pil_img)

			if panel is None:
				panel = tkinter.Label(video_frame, image =img)
				panel.image = img
				panel.pack(side=tkinter.TOP, expand = True)
			else:
				panel.configure(image = img)
				panel.image = img

		except OSError:
			break

# Send Text to the Server
def send_text(a=1):
	msg = my_msg.get()
	client_socket_text.send(bytes(msg,"utf8"))

	if msg == "{quit}":
		client_socket_text.close()
		client_socket_voice.close()
		top.destroy()
		top.quit()
		stop_video.set()
		quit()
	my_msg.set("")


# Send voice to the server
def send_voice():
	while True:
		try:
			data = stream_send.read(CHUNK)
			client_socket_voice.sendall(data)
		except OSError:
			break


#Send Video to the server
def send_video():
	global cap

	while not stop_video.is_set():
		ret_val, img = cap.read()
		img = cv2.resize(img, (360,360))

		cv2_im = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
		pil_im = Image.fromarray(cv2_im)
		b_io = io.BytesIO()
		pil_im.save(b_io,'jpeg')
		framestr = b_io.getvalue()

		ttlsent = 0
		metasent = 0
		length = len(framestr)
		lengthstr = str(length).zfill(8)

		while metasent < 8:
			sent = client_socket_video.send(lengthstr[metasent::].encode("utf8"))
			if sent == 0:
				raise RuntimeError("Socket Connection has broken")
			metasent += sent

		while ttlsent < length:
			sent = client_socket_video.send(framestr[ttlsent::])
			if sent == 0:
				raise RuntimeError("Socket Connection has broken")
			ttlsent += sent

# Handler when windows is closed
def on_closing(event=None):
	my_msg.set("{quit}")
	send_text(1)


#Cam Capture to Screen
def show_my_video():
	global cap
	panel = None

	while not stop_video.is_set():
		ret_val, img = cap.read()

		img = cv2.resize(img, (120, 120))

		image = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
		image = Image.fromarray(image)
		image = ImageTk.PhotoImage(image)

		if panel is None:
			panel = tkinter.Label(image=image)
			panel.image = image
			panel.place(height=110,width=110,x=256,y=5)
		else:
			panel.configure(image=image)
			panel.image = image

#TKinter Settings
top = tkinter.Tk()
top.title("Internet Voice,Video and Text Chatting Programme")

video_frame = tkinter.Frame(top)
video_frame.pack(side=tkinter.TOP)

messages_frame = tkinter.Frame(top)
messages_frame.pack(side=tkinter.TOP)

button_frame = tkinter.Frame(top)
button_frame.pack(side=tkinter.TOP)

my_msg = tkinter.StringVar()
my_msg.set("Enter your Name")

scrllBar = tkinter.Scrollbar(messages_frame)

entry_field = tkinter.Entry(button_frame, textvariable=my_msg)
entry_field.bind("<Return>", send_text)
entry_field.pack(side=tkinter.LEFT, padx = 10)

send_button = tkinter.Button(button_frame, text="Send", command = send_text)
send_button.pack(side=tkinter.LEFT, padx = 10)

send_button = tkinter.Button(button_frame, text="test", command = send_text)
send_button.pack(side=tkinter.LEFT, padx = 10)

msg_list = tkinter.Listbox(messages_frame, height = 15, width =50, yscrollcommand = scrllBar.set)
scrllBar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
msg_list.pack(side=tkinter.TOP, fill=tkinter.BOTH)

top.protocol("WM_DELETE_WINDOW, on_closing")

try:
	HOST = sys.argv[1]
except IndexError:
	print("Usage: ./client [Host]")
	quit()

PORT_TEXT = 2222   # Text port of server being connected to
PORT_VOICE = 55555 # Voice port of the server being connected to
PORT_VIDEO = 1026  # Video port of the server being connected to

BUFSIZ = 1024

ADDR_TEXT = (HOST, PORT_TEXT)
ADDR_VOICE = (HOST, PORT_VOICE)
ADDR_VIDEO = (HOST, PORT_VIDEO)

#For Video
panel = None

stop_video = threading.Event()

"""
Attempts to connect to the server Text Port
"""
client_socket_text = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket_text.connect(ADDR_TEXT)

"""
Attempts to connect to the server Voice Port
"""
client_socket_voice = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket_voice.connect(ADDR_VOICE)

"""
Attempts to connect to the server Video Port
"""
client_socket_video = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket_video.connect(ADDR_VIDEO)


receive_text_thread = Thread(target=receive_text).start()

receive_voice_thread = Thread(target=receive_voice).start()
send_voice_thread = Thread(target=send_voice).start()

send_video_thread = Thread(target=send_video).start()
receive_video_thread = Thread(target=receive_video).start()

show_myvideo_thread = Thread(target=show_my_video).start()

tkinter.mainloop()
