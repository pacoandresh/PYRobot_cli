#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ____________developed by paco andres____________________
# _________collaboration with cristian vazquez____________

import threading
import time
import cv2
import numpy as np
import io
import socket
import struct
import sys
from PYRobot_cli.botlogging.botlogging import Logging

class ClientCamera(Logging):
    def __init__(self, camera, show=True):
        self.cam = camera
        self._etc={}
        self._etc["name"]="client_camera"
        super().__init__(level=50)
        self.L_info("Connecting to Server. Waiting for IP and PORT...")
        self.ip, self.port = self.cam.image()
        self.L_info("Client: " + self.ip + ":" + str(self.port))
        self.show=show
        self.buffer=0
        
        self.cam_t = threading.Thread(target=self._execute_camera, args=())
        self.cam_t.setDaemon(True)
        self.cam_t.start()

    def _execute_camera(self):
        client_socket = socket.socket()
        try:
            client_socket.connect((self.ip, self.port))
            try:
                connection = client_socket.makefile("rb")
                # Construct a stream to hold the image data and read the image
                # data from the connection
                image_stream = io.BytesIO()
                while True:
                    # Read the length of the image as a 32-bit unsigned int. If the
                    # length is zero, quit the loop
                    image_len = struct.unpack(
                        '<L', connection.read(struct.calcsize('<L')))[0]
                    if not image_len:
                        self.L_warning(" No image len")
                        break
                    image_stream.write(connection.read(image_len))
                    # Rewind the stream, open it as an image with PIL and do some
                    # processing on it
                    image_stream.seek(0)

                    # BytesIO
                    self.buffer = np.fromstring(
                        image_stream.getvalue(), dtype=np.uint8)
                    sal= cv2.imdecode(self.buffer, 1)
                    cv2.imshow("CAM:" + str(self.port), sal)
                    if cv2.waitKey(1) == 27:
                        exit(0)
            except Exception:
                raise
                self.L_error(" in cam receiving")
            finally:
                connection.close()
        except Exception:
            self.L_error(" cam connecting " + ip + ":" + str(self.port))
        finally:
            self.L_info(" Cam disconecting")
            client_socket.close()
