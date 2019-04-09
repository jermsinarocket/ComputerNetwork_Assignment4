Ensure that the following libraries are being installed (Python Version 3.6.7)
--------------------------------------------------------

-PyAudio
  ===============================
  # On Ubuntu Terminal
  $ sudo apt-get install python-pyaudio python3-pyaudio

  ===============================
-Threading
  ===============================
  # On Ubuntu Terminal
  $ sudo apt install python3-pip # Only if pip is not installed
  $ pip install threaded

  ===============================
-libasound
  ===============================
  # On Ubuntu Terminal
  $ sudo apt-get install libasound2-dev 

  ===============================
-Pillow
  ===============================
  # On Ubuntu Terminal
  $ pip install Pillow==2.2.1

  ===============================
-OpenCV
  ===============================
  # On Ubuntu Terminal
  $ pip install opencv-python

Running the Program
------------------
1. Run the server using the terminal with <python server.py>.
2. Run the client using the terminal with <python client.py #hostname> The default host name is 127.0.0.1
3. Run the client using the terminal with <python client.py #hostname> on another device
4. You can now communicate through video, voice and text.
