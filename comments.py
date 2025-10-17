"""# GeoTIFF Viewer
        self.geotiff_viewer_can = GeoTIFFViewer(geotiff_path)
        self.geotiff_viewer_can.setParent(self.central_widget)

        #OpenGL Widget
        self.gl_widget = GLWidget.GLWidget(self)
        self.gl_widget.setParent(self.central_widget)
        self.gl_widget.setStyleSheet("background: transparent;")

        # Speed Dial (for updating velocity)
        self.speed_dial = SpeedDial(self)
        self.speed_dial.setParent(self.central_widget)

        self.output_display = QTextEdit(self)
        self.output_display.setReadOnly(True)
        self.output_display.setStyleSheet( "background-color: black; color: lime; font-family: monospace; font-size: 20px;")
        self.output_display.setParent(self.central_widget)

        # Timer to simulate live reading
        self.bus_receiver_timer = QTimer(self)
        self.bus_receiver_timer.setInterval(5000)
        #self.bus_receiver_timer.timeout.connect(self.init_serial_port_read)
        self.bus_receiver_timer.start()

        # Create a unique log file name with timestamp at startup

        # self.serial_timer = QTimer(self)
        # self.serial_timer.setInterval(10)
        # self.serial_timer.timeout.connect(self.read_from_serial)
        # call(["python", "Bus_Receiver.py"])
        self.read_timer = QTimer(self)
        self.read_timer.setInterval(1000)

        # self.serial_timer.start()


        #Sliders for controlling rotation of the OpenGL widget
        #self.sliderX = QSlider(Qt.Horizontal, self.central_widget)
        #self.sliderX.setRange(0, 360)
        #self.sliderX.valueChanged.connect(lambda val: self.gl_widget.setRotX(val))

        #self.sliderY = QSlider(Qt.Horizontal, self.central_widget)
        #self.sliderY.setRange(0, 360)
        #self.sliderY.valueChanged.connect(lambda val: self.gl_widget.setRotY(val))

        #self.sliderZ = QSlider(Qt.Horizontal, self.central_widget)
        #self.sliderZ.setRange(0, 360)
        #self.sliderZ.valueChanged.connect(lambda val: self.gl_widget.setRotZ(val))

        #timer = QTimer(self)
        #timer.setInterval(100)
        #timer.timeout.connect(self.gl_widget.update)
        #timer.start()



        self.geotiff_viewer_can.setGeometry(5, 210, 2100, 1350)

        self.gl_widget.setGeometry(2130, 230, 1680, 1400)

        self.speed_dial.setGeometry(5, 1570, 1280, 9000)

        self.output_display.setGeometry(2130, 1620, 1680, 700)

        #self.sliderX.setGeometry(2000, 100, 500, 20)
        #self.sliderY.setGeometry(2000, 150, 500, 20)
        #self.sliderZ.setGeometry(2000, 200, 500, 20)

    def init_serial_port_read(self):
        if not self.serial_port or self.serial_port.in_waiting <= 0:
            print("Waiting for serial port to open...")

            return
        print("Port received, initializing read timer...")
        self.bus_receiver_timer.stop()
        self.log_filename = f"log\\CANLOG_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        self.bus_receiver_timer = QTimer(self)
        self.bus_receiver_timer.setInterval(1)
        self.bus_receiver_timer.timeout.connect(self.read_uart)
        self.bus_receiver_timer.start()

        self.geotiff_viewer_can.port_open = True
        self.read_timer.timeout.connect(self.update_data)
        self.read_timer.start()  # Update every 100 ms


    def read_uart(self):
        # with serial.Serial(PORT, BaudRate, timeout=2) as ser:
        if not self.serial_port or self.serial_port.in_waiting <= 0:
            print("(read_uart) Waiting for serial port to open...")
            self.bus_receiver_timer.setInterval(50)
            return

        ser = self.serial_port
        with open(self.log_filename, "a") as f:
            # print("Waiting for data...")
            # line = list(map(lambda e: e.decode("utf-8").strip(), ser.readlines()))
            line = ser.readline().decode('utf-8').strip()
            if line:
                self.output_display.append(line)

                # Use the same log file for all writes
                timestamp = datetime.now().isoformat()
                # f.write(f"{timestamp},{new_data[0]},{new_data[1]},{new_data[2]},{new_data[3]}\n")
                f.write(f"{timestamp},{line}\n")

    def update_data(self):
        log_dir = os.path.join(os.path.dirname(__file__), "log")
        txt_files = [f for f in os.listdir(log_dir) if f.endswith(".txt")]
        if not txt_files:
            raise FileNotFoundError("No .txt files found in /log folder")
        latest_file = max(txt_files, key=lambda f: os.path.getmtime(os.path.join(log_dir, f)))
        with open(os.path.join(log_dir, latest_file), "r") as file:
            file.seek(self.cursor)
            lines = file.readlines()
            blocks = []
            block = []
            block_start_pattern = lambda line: (
                "," in line and "Name:" in line and "dtype:" in line
            )
            block_start_positions = []
            for idx, line in enumerate(lines):
                if block_start_pattern(line):
                    if block:
                        blocks.append(block)
                        block = []
                    block_start_positions.append(idx)
                block.append(line.rstrip('\n'))
            # Handle last block
            if block:
                if len(block) == 14:
                    blocks.append(block)
                    self.cursor = file.tell()
                else:
                    # Incomplete block: set cursor to its start
                    if block_start_positions:
                        # The last start position is the start of this incomplete block
                        incomplete_start = block_start_positions[-1]
                        # Calculate byte offset for cursor
                        file.seek(self.cursor)
                        offset = sum(len(lines[i]) for i in range(incomplete_start))
                        self.cursor += offset
                    else:
                        # No valid block start found, reset cursor to file start
                        self.cursor = file.tell() - sum(len(l) for l in lines)
                    new_data = blocks

            else:
                self.cursor = file.tell()
            new_data = blocks



        final_data = []
        for new_datum in new_data:
            if len(new_datum) != 14:
                continue
            pattern = r"Time.+[0-9]+\.[0-9]+(\n.*)*Altitude.+[0-9]+\.[0-9]+(\n.*)*Latitude.+[0-9]+\.[0-9]+(\n.*)*Longitude.+[0-9]+\.[0-9]+(\n.*)*"
            # if not re.fullmatch(pattern, "\n".join(new_datum), re.DOTALL):
            #     continue
            print(new_datum)
            time = float(re.findall(r'\s{2,}.+', new_datum[1])[0])
            alt = float(re.findall(r'\s{2,}.+', new_datum[2])[0])
            lat = float(re.findall(r'\s{2,}.+', new_datum[5])[0])
            lon = float(re.findall(r'\s{2,}.+', new_datum[6])[0])
            vel = float(re.findall(r'\s{2,}.+', new_datum[3])[0])
            final_data.append([time, alt, lat, lon])

        self.speed_dial.set_altitude(alt)
        self.speed_dial.set_Lat(lat)
        self.speed_dial.set_Lon(lon)

        self.speed_dial.update_velocity(vel)

        self.geotiff_viewer_can.update_coordinate_data(final_data)"""