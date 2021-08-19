import odrive
import RPi.GPIO as GPIO
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
import time
from time import sleep
import pigpio

host_name = '10.1.2.154'    # Change this to your Raspberry Pi IP address
host_port = 8000


class MyServer(BaseHTTPRequestHandler):
    """ A special implementation of BaseHTTPRequestHander for reading data from
        and control GPIO of a Raspberry Pi
    """

    os.system("sudo killall pigpiod")
    sleep(1)
    os.system("sudo pigpiod")
    sleep(1)

    GPIO.setmode(GPIO.BCM)
    pi = pigpio.pi()

    # Shadowcat Motor - ODrive Config on Raspberry Pi
    VAC_GPIO = 16
    BRS_GPIO = 12

    od1 = odrive.find_any(serial_number="2064344D4230")
    print("Detected ODrive with serial number=", od1.serial_number)
    od2 = odrive.find_any(serial_number="2068344C4230")
    print("Detected ODrive with serial number=", od2.serial_number)
    print("Rebooting them just for a fresh start...")

    try:
        od1.reboot()
        sleep(1.5)
        od2.reboot()
        sleep(1.5)
    except:
        print('Lost connection because of reboot...')

    od1 = odrive.find_any(serial_number="2064344D4230")
    print("Detected ODrive with serial number=", od1.serial_number)
    od2 = odrive.find_any(serial_number="2068344C4230")
    print("Detected ODrive with serial number=", od2.serial_number)

    # requested_state for ODrive
    """
    AXIS_STATE_UNDEFINED  —  0

    * AXIS_STATE_IDLE  —  1

    AXIS_STATE_STARTUP_SEQUENCE  —  2

    * AXIS_STATE_FULL_CALIBRATION_SEQUENCE  —  3 

    * AXIS_STATE_MOTOR_CALIBRATION  —  4 

    AXIS_STATE_ENCODER_INDEX_SEARCH  —  6

    AXIS_STATE_ENCODER_OFFSET_CALIBRATION  —  7

    * AXIS_STATE_CLOSED_LOOP_CONTROL  —  8     <-- gets motor ready for being controlled

    AXIS_STATE_LOCKIN_SPIN  —  9

    AXIS_STATE_ENCODER_DIR_FIND  —  10

    AXIS_STATE_HOMING  —  11

    AXIS_STATE_ENCODER_HALL_POLARITY_CALIBRATION  —  12

    AXIS_STATE_ENCODER_HALL_PHASE_CALIBRATION  —  13
    """

    print("Calibrating...")
    # initialize rotation to this always
    od1.axis0.requested_state = 8
    sleep(1)
    od1.axis1.requested_state = 8
    sleep(1)
    od2.axis0.requested_state = 8
    sleep(1)
    od2.axis1.requested_state = 8
    sleep(1)
    pi.write(VAC_GPIO, 0)
    pi.write(BRS_GPIO, 0)

    print("Complete!")
    # Start the Raspberry Pi Camera Stream (Andy's Laptop directory)
    try:
        rasp_cam_status = os.system(
            "./mjpg-streamer/mjpg-streamer-experimental/mjpg_streamer -o 'output_http.so -w ./www' -i 'input_raspicam.so -x 480 -y 360 -fps 25'")
    except:
        print("Camera not connected")

    suc = False
    brush = False

    cw = True
    cw2 = True

    b1 = False
    b2 = False

    def do_HEAD(self):
        """ do_HEAD() can be tested use curl command
            'curl -I http://server-ip-address:port'
        """
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        print("DOING HEAD")

    def _redirect(self, path):
        self.send_response(303)
        self.send_header('Content-type', 'text/html')
        self.send_header('Location', path)
        self.end_headers()

    def do_GET(self):
        """ do_GET() can be tested using curl command
            'curl http://server-ip-address:port'
        """
        html = '''
            <html>
                <head>
                <title>ShadowCat v0.2</title>
                    <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.5.1/jquery.min.js"></script>
                    <script>
                        function myFunction() {{
                            var x = document.getElementById("mspeed").value;
                            console.log(x);
                        }}

                        var JoyStick = function (container, parameters) {{
                            parameters = parameters || {{}};
                            var title =
                                    typeof parameters.title === "undefined" ? "joystick" : parameters.title,
                                width = typeof parameters.width === "undefined" ? 0 : parameters.width,
                                height = typeof parameters.height === "undefined" ? 0 : parameters.height,
                                internalFillColor =
                                    typeof parameters.internalFillColor === "undefined"
                                        ? "#00AA00"
                                        : parameters.internalFillColor,
                                internalLineWidth =
                                    typeof parameters.internalLineWidth === "undefined"
                                        ? 2
                                        : parameters.internalLineWidth,
                                internalStrokeColor =
                                    typeof parameters.internalStrokeColor === "undefined"
                                        ? "#003300"
                                        : parameters.internalStrokeColor,
                                externalLineWidth =
                                    typeof parameters.externalLineWidth === "undefined"
                                        ? 2
                                        : parameters.externalLineWidth,
                                externalStrokeColor =
                                    typeof parameters.externalStrokeColor === "undefined"
                                        ? "#008000"
                                        : parameters.externalStrokeColor,
                                autoReturnToCenter =
                                    typeof parameters.autoReturnToCenter === "undefined"
                                        ? true
                                        : parameters.autoReturnToCenter;

                            // Create Canvas element and add it in the Container object
                            var objContainer = document.getElementById(container);
                            var canvas = document.createElement("canvas");
                            canvas.id = title;
                            if (width === 0) {{
                                width = objContainer.clientWidth;
                            }}
                            if (height === 0) {{
                                height = objContainer.clientHeight;
                            }}
                            canvas.width = width;
                            canvas.height = height;
                            objContainer.appendChild(canvas);
                            var context = canvas.getContext("2d");

                            var pressed = 0; // Bool - 1=Yes - 0=No
                            var circumference = 2 * Math.PI;
                            var internalRadius = (canvas.width - (canvas.width / 2 + 10)) / 2.5;
                            var maxMoveStick = internalRadius + 5;
                            var externalRadius = internalRadius + 50;
                            var centerX = canvas.width / 2;
                            var centerY = canvas.height / 2;
                            var directionHorizontalLimitPos = canvas.width / 10;
                            var directionHorizontalLimitNeg = directionHorizontalLimitPos * -1;
                            var directionVerticalLimitPos = canvas.height / 10;
                            var directionVerticalLimitNeg = directionVerticalLimitPos * -1;
                            // Used to save current position of stick
                            var movedX = centerX;
                            var movedY = centerY;

                            // Check if the device support the touch or not
                            if ("ontouchstart" in document.documentElement) {{
                                canvas.addEventListener("touchstart", onTouchStart, false);
                                document.addEventListener("touchmove", onTouchMove, false);
                                document.addEventListener("touchend", onTouchEnd, false);
                            }} else {{
                                canvas.addEventListener("mousedown", onMouseDown, false);
                                document.addEventListener("mousemove", onMouseMove, false);
                                document.addEventListener("mouseup", onMouseUp, false);
                            }}
                            // Draw the object
                            drawExternal();
                            drawInternal();

                            /******************************************************
                            * Private methods
                            *****************************************************/

                            /**
                            * @desc Draw the external circle used as reference position
                            */
                            function drawExternal() {{
                                context.beginPath();
                                context.arc(centerX, centerY, externalRadius, 0, circumference, false);
                                context.lineWidth = externalLineWidth;
                                context.strokeStyle = externalStrokeColor;
                                context.shadowColor = "#39FF87";
                                context.shadowBlur = 5;
                                context.stroke();
                            }}

                            /**
                            * @desc Draw the internal stick in the current position the user have moved it
                            */
                            function drawInternal() {{
                                context.beginPath();
                                if (movedX < internalRadius) {{
                                    movedX = maxMoveStick;
                                }}
                                if (movedX + internalRadius > canvas.width) {{
                                    movedX = canvas.width - maxMoveStick;
                                }}
                                if (movedY < internalRadius) {{
                                    movedY = maxMoveStick;
                                }}
                                if (movedY + internalRadius > canvas.height) {{
                                    movedY = canvas.height - maxMoveStick;
                                }}
                                context.arc(movedX, movedY, internalRadius, 0, circumference, false);
                                context.fillStyle = "#FFFFFF";
                                context.fill();
                                context.lineWidth = internalLineWidth;
                                context.strokeStyle = internalStrokeColor;
                                context.shadowColor = "transparent";
                                context.shadowBlur = 0;
                                context.stroke();
                            }}

                            /**
                            * @desc Events for manage touch
                            */
                            function onTouchStart(event) {{
                                pressed = 1;
                            }}

                            function onTouchMove(event) {{
                                // Prevent the browser from doing its default thing (scroll, zoom)
                                event.preventDefault();
                                if (pressed === 1 && event.targetTouches[0].target === canvas) {{
                                    movedX = event.targetTouches[0].pageX;
                                    movedY = event.targetTouches[0].pageY;
                                    // Manage offset
                                    if (canvas.offsetParent.tagName.toUpperCase() === "BODY") {{
                                        movedX -= canvas.offsetLeft;
                                        movedY -= canvas.offsetTop;
                                    }} else {{
                                        movedX -= canvas.offsetParent.offsetLeft;
                                        movedY -= canvas.offsetParent.offsetTop;
                                    }}
                                    // Delete canvas
                                    context.clearRect(0, 0, canvas.width, canvas.height);
                                    // Redraw object
                                    drawExternal();
                                    drawInternal();
                                }}
                            }}

                            function onTouchEnd(event) {{
                                pressed = 0;
                                // If required reset position store variable
                                if (autoReturnToCenter) {{
                                    movedX = centerX;
                                    movedY = centerY;
                                }}
                                // Delete canvas
                                context.clearRect(0, 0, canvas.width, canvas.height);
                                // Redraw object
                                drawExternal();
                                drawInternal();
                                //canvas.unbind('touchmove');
                            }}

                            /**
                            * @desc Events for manage mouse
                            */
                            function onMouseDown(event) {{
                                pressed = 1;
                            }}

                            function onMouseMove(event) {{
                                if (pressed === 1) {{
                                    movedX = event.pageX;
                                    movedY = event.pageY;
                                    // Manage offset
                                    if (canvas.offsetParent.tagName.toUpperCase() === "BODY") {{
                                        movedX -= canvas.offsetLeft;
                                        movedY -= canvas.offsetTop;
                                    }} else {{
                                        movedX -= canvas.offsetParent.offsetLeft;
                                        movedY -= canvas.offsetParent.offsetTop;
                                    }}
                                    // Delete canvas
                                    context.clearRect(0, 0, canvas.width, canvas.height);
                                    // Redraw object
                                    drawExternal();
                                    drawInternal();
                                }}
                            }}

                            function onMouseUp(event) {{
                                pressed = 0;
                                // If required reset position store variable
                                if (autoReturnToCenter) {{
                                    movedX = centerX;
                                    movedY = centerY;
                                }}
                                // Delete canvas
                                context.clearRect(0, 0, canvas.width, canvas.height);
                                // Redraw object
                                drawExternal();
                                drawInternal();
                                //canvas.unbind('mousemove');
                            }}

                            /******************************************************
                            * Public methods
                            *****************************************************/

                            /**
                            * @desc The width of canvas
                            * @return Number of pixel width
                            */
                            this.GetWidth = function () {{
                                return canvas.width;
                            }};

                            /**
                            * @desc The height of canvas
                            * @return Number of pixel height
                            */
                            this.GetHeight = function () {{
                                return canvas.height;
                            }};

                            /**
                            * @desc The X position of the cursor relative to the canvas that contains it and to its dimensions
                            * @return Number that indicate relative position
                            */
                            this.GetPosX = function () {{
                                return movedX;
                            }};

                            /**
                            * @desc The Y position of the cursor relative to the canvas that contains it and to its dimensions
                            * @return Number that indicate relative position
                            */
                            this.GetPosY = function () {{
                                return movedY;
                            }};

                            /**
                            * @desc Normalizzed value of X move of stick
                            * @return Integer from -100 to +100
                            */
                            this.GetX = function () {{
                                return (100 * ((movedX - centerX) / maxMoveStick)).toFixed();
                            }};

                            /**
                            * @desc Normalizzed value of Y move of stick
                            * @return Integer from -100 to +100
                            */
                            this.GetY = function () {{
                                return (100 * ((movedY - centerY) / maxMoveStick) * -1).toFixed();
                            }};

                            /**
                            * @desc Get the direction of the cursor as a string that indicates the cardinal points where this is oriented
                            * @return String of cardinal point N, NE, E, SE, S, SW, W, NW and C when it is placed in the center
                            */
                            this.GetDir = function () {{
                                var result = "";
                                var orizontal = movedX - centerX;
                                var vertical = movedY - centerY;

                                if (
                                    vertical >= directionVerticalLimitNeg &&
                                    vertical <= directionVerticalLimitPos
                                ) {{
                                    result = "C";
                                }}
                                if (vertical < directionVerticalLimitNeg) {{
                                    result = "N";
                                }}
                                if (vertical > directionVerticalLimitPos) {{
                                    result = "S";
                                }}

                                if (orizontal < directionHorizontalLimitNeg) {{
                                    if (result === "C") {{
                                        result = "W";
                                    }} else {{
                                        result += "W";
                                    }}
                                }}
                                if (orizontal > directionHorizontalLimitPos) {{
                                    if (result === "C") {{
                                        result = "E";
                                    }} else {{
                                        result += "E";
                                    }}
                                }}

                                return result;
                            }};
                        }};
                    </script>
                    <style>
                        * {{
                            font-family: Arial, Helvetica, sans-serif;
                        }}
                        h1 {{
                            text-align: center;
                        }}
                        .logo {{
                            width: 250px;
                            display: block;
                            margin: auto;
                            cursor: none;
                        }}
                        .container {{
                            margin: auto;
                            width: 80%;
                            display: flex;
                            justify-content: space-evenly;
                        }}
                        .buttons_vertical {{
                            display: flex;
                            align-items: center;
                            width: 200px;
                        }}
                        .buttons_vertical form {{
                            display: flex;
                            flex-direction: column;
                            justify-content: space-around;
                        }}
                        form input {{
                            width: 100px;
                            height: 100px;
                            border-radius: 100%;
                            margin: 15px;
                            background-color: white;
                            border: none;
                            font-size: 17px;
                            font-weight: 600;
                        }}
                        #brush {{
                            border: #FF7A00 5px solid;
                            background-color: #FFEFD8;
                            color: #FF7A00;
                            box-shadow: 0px 0px 10px rgba(255, 122, 0, 0.5);
                        }}
                        #vacuum {{
                            border: #00DEC0 5px solid;
                            background-color: #E7FFFE;
                            color: #00DEC0;
                            box-shadow: 0px 0px 15px rgba(0, 255, 255, 0.5);
                        }}
                        .video {{
                            width: 480px;
                            height: 360px;
                            border: #000000 5px solid;
                            margin: 0 50px;
                        }}
                        .speed {{
                            display: flex;
                            flex-direction: column;
                            justify-content: center;
                            text-align: center;
                            width: 200px;
                        }}
                        .XY input {{
                            width: 80px;
                            margin: 10px;
                            padding: 15px;
                            border-radius: 15px;
                            border: none;
                            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.25);
                            text-align: center;
                            font-weight: bold;
                            font-size: 25px;
                        }}
                        #joystick {{
                            padding-left: 0;
                            padding-right: 0;
                            margin-left: auto;
                            margin-right: auto;
                            display: block;  
                        }}
                        img:hover {{
                            cursor: pointer;
                        }}
                        #text {{
                            margin: auto;
                            margin-top: 100px;
                        }}
                    </style>
                </head>
                <body>
                     <img class="logo" src="https://www.avalonsteritech.com/wp-content/uploads/2020/09/Avalon_logo_final_V_eng-1.png"/>
                    <h1>ShadowCat Control Panel</h1>
                    <div class="container">
                        <div class="buttons_vertical">
                            <form>
                                <input id="brush" type="submit" name="brush" value="BRUSH" onclick="activate_brush()">
                                <input id="vacuum" type="submit" name="vacuum" value="VACUUM" onclick="activate_vacuum()">
                            </form>
                        </div>
                        <img class="video" src="http://raspberrypi.local:8080/?action=stream" />
                        <div class="speed">
                            <h3>Joystick Readings:</h3>
                            <div class="XY">
                                <div>
                                    X :<input id="joy1X" type="text" />
                                </div>
                                <div>
                                    Y :<input id="joy1Y" type="text" />
                                </div>
                                
                                
                            </div>
                        </div>
                    </div>

                    <div id="joyDiv"></div>

                    <script>
                        function activate_brush() {{
                            console.log(data);
                            d = document.getElementById('brush').value;
                            $.post("/", {{m1: d, m2: 0}});
                        }}
                        function activate_vacuum() {{
                            d = document.getElementById('vacuum').value;
                            $.post("/", {{m1: d, m2: 0}});
                        }}
                        var joy = new JoyStick('joyDiv',{{
                            // The ID of canvas element
                            title: 'joystick',

                            // width/height
                            width: 450,
                            height: 450,

                            // Internal color of Stick
                            internalFillColor: '#FFFFFF',

                            // Border width of Stick
                            internalLineWidth: 10,

                            // Border color of Stick
                            internalStrokeColor: '#EDEDED',

                            // External reference circonference width
                            externalLineWidth: 10,

                            //External reference circonference color
                            externalStrokeColor: '#39FF87',

                            // Sets the behavior of the stick
                            autoReturnToCenter: true

                        }});
                        var joy1X = document.getElementById("joy1X");
                        var joy1Y = document.getElementById("joy1Y");
                        var Xb = false;
                        var Yb = false;

                        // SPEED FACTOR. DEFAULT IS 100. So if you want 255 then = 2.55, if you want 64 then = 0.64, etc..
                        var speed_factor = 0.01;

                        setInterval(function(){{
                            joy1X.value=parseInt(joy.GetX() * speed_factor);
                            // Xb = true;
                        }}, 50);
                        setInterval(function(){{
                            joy1Y.value=parseInt(joy.GetY() * speed_factor);
                            // Yb = true;
                        }}, 50);

                        var count = 0;
                        setInterval(function () {{
                            data = [];

                            if (parseInt(joy1Y.value) > 0) {{
                                count = 0
                                console.log("FORWARD")
                            }} else if (parseInt(joy1Y.value) < 0) {{
                                count = 0
                                console.log("REVERSE")
                            }}
                            data.push(parseInt(joy1Y.value));
                            if (parseInt(joy1X.value) > 0) {{
                                count = 0
                                console.log("RIGHT");
                                console.log("MOTOR L: ", joy1X.value);
                            }} else if (parseInt(joy1X.value) < 0) {{
                                count = 0
                                console.log("LEFT");
                                console.log("MOTOR R: ", joy1X.value);
                            }}
                            data.push(parseInt(joy1X.value));
                            if (data[0] == 0 && data[1] == 0) {{
                                // count = count + 1;
                                console.log(count, data);
                                $.post("/", {{m1: data[0], m2: data[1]}});
                            }}
                            else if (data[0] !== 0 || data[1] !== 0) {{
                                console.log(data);
                                // POST
                                $.post("/", {{m1: data[0], m2: data[1]}});
                            }}

                        }}, 100)
                    </script>
                </body>
            </html>
        '''
        temp = os.popen("/opt/vc/bin/vcgencmd measure_temp").read()
        self.do_HEAD()
        status = ''
        self.wfile.write(html.format(temp[5:], status).encode("utf-8"))

    def do_POST(self):
        """ do_POST() can be tested using curl command
            'curl -d "submit=On" http://server-ip-address:port'
        """
        content_length = int(
            self.headers['Content-Length'])  # Get the size of data
        post_data = self.rfile.read(
            content_length).decode("utf-8")  # Get the data
        # print("POST_DATA : ", post_data)
        post_data = post_data.split("&")

        for i in range(len(post_data)):
            post_data[i] = post_data[i].split("=")[1]

        print(post_data)

        if post_data[0] == "VACUUM":
            print("VRRRRUUUUUMMMM")
            print(self.pi.read(self.VAC_GPIO))
            print("/n/n")
            # self.pi.write(self.VAC_GPIO, 0)
            if self.pi.read(self.VAC_GPIO) == 0:
                # if self.suc == False:
                print("vacuum worrr")
                self.pi.write(self.VAC_GPIO, 1)
                sleep(0.55)
                self.pi.write(self.VAC_GPIO, 0)
                # self.suc = True
            else:
                print("vacuum not worrr")
                self.pi.write(self.VAC_GPIO, 1)
                sleep(0.55)
                self.pi.write(self.VAC_GPIO, 0)
                # sleep(0.55)
                # self.pi.write(self.VAC_GPIO, 0)
                # self.suc = False
        elif post_data[0] == "BRUSH":
            print("BRUSH SOUNDS")
            print(self.pi.read(self.BRS_GPIO))
            print("/n/n")
            # self.pi.write(self.BRS_GPIO, 0)
            if self.pi.read(self.BRS_GPIO) == 0:
                # if self.brush == False:
                print("brush worrr")
                self.pi.write(self.BRS_GPIO, 1)
                sleep(0.55)
                # self.pi.write(self.VAC_GPIO, 1)
                # self.brush = True
            else:
                print("brush not worrr")
                self.pi.write(self.BRS_GPIO, 0)
                sleep(0.55)
                # self.pi.write(self.BRS_GPIO, 0)
                # sleep(0.55)
                # self.pi.write(self.BRS_GPIO, 1)
                # self.brush = False

        """
        The ODrive and the config atm for ShadowCat
        
                     BRUSH
        [] od2.axis1       [] od1.axis0


        [] od2.axis0       [] od1.axis1

        """

        # Easier control over our maximum speed with a variable
        N = 1

        # Joystick control
        try:
            Y = int(post_data[0])
            X = int(post_data[1])
            # All the motor control here!!!
            # Joystick can register out of bound values sometimes
            if (X > N or Y > N or X < -N or Y < -N):
                pass
            elif (Y > 0 and X == 0):  # FORWARD
                self.od1.axis0.controller.input_vel = -N
                self.od1.axis1.controller.input_vel = -N
                self.od2.axis0.controller.input_vel = N
                self.od2.axis1.controller.input_vel = N
            elif (Y < 0 and X == 0):  # BACKWARD
                self.od1.axis0.controller.input_vel = N
                self.od1.axis1.controller.input_vel = N
                self.od2.axis0.controller.input_vel = -N
                self.od2.axis1.controller.input_vel = -N
            elif (Y == 0 and X == 0):   # HALT
                self.od1.axis0.controller.input_vel = 0
                self.od1.axis1.controller.input_vel = 0
                self.od2.axis0.controller.input_vel = 0
                self.od2.axis1.controller.input_vel = 0
            # elif (Y > 0 and X > 0):  # TURN RIGHT FORWARD
            #     print("RIGHT")
            #     self.od1.axis0.controller.input_vel = 0
            #     self.od1.axis1.controller.input_vel = -X
            #     self.od2.axis0.controller.input_vel = 0
            #     self.od2.axis1.controller.input_vel = X
            # elif (Y > 0 and X < 0):  # TURN LEFT FORWARD
            #     print("LEFT")
            #     self.od1.axis0.controller.input_vel = 0
            #     self.od1.axis1.controller.input_vel = X
            #     self.od2.axis0.controller.input_vel = 0
            #     self.od2.axis1.controller.input_vel = -X
            # elif (Y < 0 and X > 0):  # TURN RIGHT BACKWARD
            #     print("RIGHT BACK")
            #     self.od1.axis0.controller.input_vel = 0
            #     self.od1.axis1.controller.input_vel = X
            #     self.od2.axis0.controller.input_vel = 0
            #     self.od2.axis1.controller.input_vel = -X
            # elif (Y < 0 and X < 0):  # TURN LEFT BACKWARD
            #     print("LEFT BACK")
            #     self.od1.axis0.controller.input_vel = 0
            #     self.od1.axis1.controller.input_vel = -X
            #     self.od2.axis0.controller.input_vel = 0
            #     self.od2.axis1.controller.input_vel = X
            else:   # All the TURNS handled by this
                self.od1.axis0.controller.input_vel = -(X/2)
                self.od1.axis1.controller.input_vel = -(X/2)
                self.od2.axis0.controller.input_vel = -(X/2)
                self.od2.axis1.controller.input_vel = -(X/2)
        except:
            pass

        self._redirect('/')  # Redirect back to the root url


if __name__ == '__main__':
    http_server = HTTPServer((host_name, host_port), MyServer)
    print("Server Starts - %s:%s" % (host_name, host_port))

    try:
        http_server.serve_forever()
    except KeyboardInterrupt:
        http_server.server_close()
