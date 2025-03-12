from import_all import *
github_repo = "https://api.github.com/repos/VannyLD/AllinOneUpdate/contents/"

def resource_path(relative_path):

    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class CustomInputDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Enter Password")
        
        self.layout = QVBoxLayout(self)
        self.label = QLabel("Enter the Password:", self)
        self.layout.addWidget(self.label)
        
        self.line_edit = QLineEdit(self)
        self.line_edit.setEchoMode(QLineEdit.Password)
        self.layout.addWidget(self.line_edit)
        
        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        self.layout.addWidget(self.buttons)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

    def get_password(self):
        return self.line_edit.text()


class MaxKeyApp(QMainWindow):
    SALT_FILE = os.path.join(os.path.expanduser("~"), ".devmax_secret_salt")

    def __init__(self):
        super().__init__()
        self.setWindowTitle("MaxKey - Machine ID Generator")
        self.setGeometry(100, 100, 400, 300)
        # Set the window icon
        icon = QIcon(resource_path("File/ico.ico"))
        self.setWindowIcon(icon)

        # Check for saved salt or prompt the user
        self.secret_salt = self.get_or_prompt_secret_salt()

        # Main widget and layout
        main_widget = QWidget()
        main_layout = QVBoxLayout()

        # Set main layout
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        # Optionally, change title dynamically based on status
        if self.secret_salt:
            self.setWindowTitle(f"MaxKey - Salt Set: {self.secret_salt[:5]}...")  

    def get_or_prompt_secret_salt(self):
        """Fetch the SECRET_SALT from the file or prompt the user to enter it."""
        if os.path.exists(self.SALT_FILE):
            with open(self.SALT_FILE, "r") as file:
                salt = file.read().strip()
            return salt
        else:
            # Prompt user for salt if not found
            salt, ok = self.prompt_for_salt()
            if not ok or not salt.strip():
                QMessageBox.critical(self, "Error", "Password is required. Exiting.")
                sys.exit(1)

            try:
                # Save the salt if entered
                with open(self.SALT_FILE, "w") as file:
                    file.write(salt.strip())
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save salt file: {e}")
                sys.exit(1)

            # Exit after saving the salt
            sys.exit(0)

            return salt.strip()

    def prompt_for_salt(self):
        """Show a dialog to prompt the user for SECRET_SALT."""
        # Set the window title before showing the dialog
        self.setWindowTitle("MaxKey - Enter the Password")
        QApplication.processEvents()  # Force UI to update with the new title

        # Create the custom input dialog
        dialog = CustomInputDialog(self)

        # Make sure the title updates before the dialog is shown
        QApplication.processEvents()

        # Show the dialog and block until the user enters something
        result = dialog.exec()

        salt = dialog.get_password()

        # After the dialog is closed, restore the title with the entered salt or canceled message
        if result == QDialog.Accepted and salt.strip():
            self.setWindowTitle(f"MaxKey - Salt Set: {salt[:5]}...")  # Optionally show part of the salt
        else:
            self.setWindowTitle("MaxKey - Password Entry Canceled")

        # Force UI to update after dialog interaction
        QApplication.processEvents()

        return salt, result == QDialog.Accepted


class Max_key:
    SALT_FILE = os.path.join(os.path.expanduser("~"), ".devmax_secret_salt")

    def __init__(self, secret_salt=None):
        self.creation_flags = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
        self.SECRET_SALT = secret_salt or self.load_salt_from_file()  # Load from file if not passed

    def load_salt_from_file(self):
        """Load the salt from the salt file."""
        if os.path.exists(self.SALT_FILE):
            with open(self.SALT_FILE, "r") as file:
                salt = file.read().strip()
            return salt
        else:
            pass
        
    def get_machine_uuid(self):
        """Fetch the machine UUID using PowerShell."""
        try:
            command = ["powershell", "-Command", "(Get-CimInstance -Class Win32_ComputerSystemProduct).UUID"]
            result = subprocess.check_output(command, text=True, creationflags=self.creation_flags).strip()
            return result if result else "UnknownUUID"
        except Exception as e:
            print(f"Error Machine UUID: {e}")
            return "UnknownUUID"

    def get_bios_serial_number(self):
        """Fetch the BIOS serial number using PowerShell."""
        try:
            command = ["powershell", "-Command", "(Get-CimInstance -Class Win32_BIOS).SerialNumber"]
            result = subprocess.check_output(command, text=True, creationflags=self.creation_flags).strip()
            return result if result else "UnknownBIOS"
        except Exception as e:
            print(f"Error BIOS Serial Number: {e}")
            return "UnknownBIOS"

    def get_cpu_id(self):
        """Fetch the CPU ID."""
        return platform.processor() or "UnknownCPU"

    def get_cpu_type(self):
        """Fetch the CPU type."""
        try:
            return platform.uname().processor or "UnknownCPUType"
        except Exception as e:
            print(f"Error CPU Type: {e}")
            return "UnknownCPUType"

    def get_motherboard_info(self):
        """Fetch the motherboard manufacturer and model using PowerShell."""
        try:
            command = [
                "powershell", 
                "-Command", 
                "(Get-CimInstance -Class Win32_BaseBoard | Select-Object -ExpandProperty Manufacturer) + ' ' + (Get-CimInstance -Class Win32_BaseBoard | Select-Object -ExpandProperty Product)"
            ]
            result = subprocess.check_output(command, text=True, creationflags=self.creation_flags).strip()
            return result if result else "UnknownMotherboard"
        except Exception as e:
            print(f"Error retrieving Motherboard Information: {e}")
            return "UnknownMotherboard"

    def get_disk_serial(self):
        """Fetch the internal disk serial number using PowerShell."""
        try:
            command = [
                "powershell", 
                "-Command", 
                "Get-PhysicalDisk | Select-Object -ExpandProperty SerialNumber"
            ]
            result = subprocess.check_output(command, text=True, creationflags=self.creation_flags).strip()
            if result:
                return result.splitlines()[0]  # Take the first valid serial number
            else:
                return "UnknownDisk"
        except Exception as e:
            print(f"Error retrieving Disk Serial Number: {e}")
            return "UnknownDisk"

    def generate_machine_id(self):
        """Generate a machine ID based on multiple hardware attributes with a secret salt."""
        uuid = self.get_machine_uuid()
        bios_serial = self.get_bios_serial_number()
        cpu_id = self.get_cpu_id()
        cpu_type = self.get_cpu_type()
        motherboard = self.get_motherboard_info()

        # Handle missing or default BIOS Serial Number
        if bios_serial.lower() == "default string":
            bios_serial = hashlib.sha256(uuid.encode()).hexdigest()[:8]  # Fallback to hashed UUID

        # Combine attributes with the secret salt
        combined_id = f"{uuid}-{bios_serial}-{cpu_id}-{cpu_type}-{motherboard}-{self.SECRET_SALT}"

        # Generate the machine ID and convert it to uppercase for consistency
        machine_id = hashlib.sha256(combined_id.encode()).hexdigest().upper()
        return machine_id



    def get_machine_id(self):
        """Retrieve the stable machine ID."""
        return self.generate_machine_id()

    # URL where the JSON data is hosted
    pin = "https://vannyld.github.io/allinonedevmax/data.json"

    def fetch_and_check_id(self, search_id):
        """Fetch and validate a given ID against data from a JSON URL."""
        try:
            # Fetch data from the JSON file URL
            response = requests.get(self.pin)
            response.raise_for_status()
            data = response.json()  # Parse the response as JSON

            # Check if the ID exists in the data
            result = data.get(search_id.upper(), data.get(search_id.lower(), "ID not found"))

            # If result is found, split it to get parts
            if result != "ID not found":
                parts = result.split()  # Split by space
                
                # Check the number of parts and return accordingly
                if len(parts) >= 3:  # Ensure there are at least three parts
                    first_value = parts[0]  # TRUE or FAIL
                    second_value = parts[1]  # VANNY_SAMBATH_1, etc.
                    date_value = parts[2]    # ExDate:11-04-2025
                    return first_value, second_value, date_value
                else:
                    return "Unexpected result format"
            else:
                return result
        except requests.exceptions.RequestException as e:
            return f"An error occurred: {e}"



class MainWindow(QMainWindow):
    update_signal = Signal(str)
    update_success_count = Signal(int)
    update_success_count_img = Signal(int)
    pin_image_downloaded_signal = Signal(int)
    create_folder_signal = Signal() 
    download_complete_signal = Signal() 
    update_success_count_IG = Signal(int)
    download_complete_instagram = Signal()
    create_folder_instagram = Signal()
    dev_max = Max_key()


    def __init__(self):
        super().__init__()
        self.main = Ui_Form()
        self.setFixedSize(950, 600)
        self.main.setupUi(self)
        MainWindow.clear_console()
        self.setup_resource_paths()
        
        # Load the secret salt
        salt_file = os.path.join(os.path.expanduser("~"), ".devmax_secret_salt")
        if os.path.exists(salt_file):
            with open(salt_file, "r") as file:
                salt = file.read().strip()
            # Pass the loaded salt to the Max_key instance
            self.dev_max = Max_key(secret_salt=salt)
        else:
            # Handle case where salt file is not found
            raise ValueError("SECRET_SALT file not found. Please provide the secret salt.")


        self.loader = instaloader.Instaloader()

        computer_id = self.dev_max.generate_machine_id()


        # Initializing variables
        self.stop_flag = False
        self.seen_urls = set()
        self.pin_image_count = 0
        self.image_count = 0
        self.folder_path = "" 

        # Default Settings
        self.download_all = True
        self.download_videos = False
        self.download_images = False
        self.main.radioButton_allpost.setChecked(True)

        # IG LOGIN
        self.session_file_path = r"File\ig.session"
        self.destination_folder = ""

        self.disable_ui_elements()
        try:
            with open("license.txt", "w") as file:
                file.write(f"{computer_id}\n")

            result = self.dev_max.fetch_and_check_id(computer_id)  

            if isinstance(result, tuple) and len(result) > 0:
                if result[0] == "ON":
                    self.enable_ui_elements()
                else:
                    QMessageBox.warning(self, "ព្រមាន!", "មិនមាន license សម្រាប់ប្រើប្រាស់ទេ! កម្មវិធីនិងបិទឆាប់ៗ!! សូមទាក់ទងទៅកាន់ Admin ជាមុនសិន។")
                    self.disable_ui_elements()
                    QtCore.QTimer.singleShot(15000, QtWidgets.QApplication.quit)
            else:
                QMessageBox.warning(self, "ព្រមាន!", "មិនមាន license សម្រាប់ប្រើប្រាស់ទេ! កម្មវិធីនិងបិទឆាប់ៗ!! សូមទាក់ទងទៅកាន់ Admin ជាមុនសិន​។")
                self.disable_ui_elements()
                QtCore.QTimer.singleShot(15000, QtWidgets.QApplication.quit)

        except FileNotFoundError:
            with open("license.txt", "w") as file:
                file.write(f"{computer_id}\n")
            QMessageBox.warning(self, "ព្រមាន!", "មិនមាន license សម្រាប់ប្រើប្រាស់ទេ! កម្មវិធីនិងបិទឆាប់ៗ!! សូមទាក់ទងទៅកាន់ Admin ជាមុនសិន។")
            self.disable_ui_elements()
            QtCore.QTimer.singleShot(15000, QtWidgets.QApplication.quit)


        # Connect UI buttons
        self.main.radioButton_pinterest.toggled.connect(self.pin_check)
        self.main.radioButton_fb_img.toggled.connect(self.pin_check)
        self.main.radioButton_google.toggled.connect(self.pin_check)
        self.main.pushButton_update.clicked.connect(self.update_ver)
        self.main.pushButton_grabber.clicked.connect(self.Grabber_UI)
        self.main.radioButton_instargram.toggled.connect(self.pin_check)
        self.main.radioButton_tiktok.toggled.connect(self.pin_check)
        self.main.radioButton_youtube.toggled.connect(self.pin_check)
        self.main.radioButton_facebook.toggled.connect(self.pin_check)

        self.main.pushButton_update.clicked.connect(self.check_for_updates)

        # Radio Button IG Events
        self.main.radioButton_allpost.toggled.connect(self.check_all_posts)
        self.main.radioButton_videos.toggled.connect(self.check_only_videos)
        self.main.radioButton_images.toggled.connect(self.check_only_images)

        # IG Thread Handling
        self.download_thread = None
        self.stop_flag = False

        # Main UI buttons
        self.main.checkBox_title.toggled.connect(self.check_title)
        self.main.checkBox_title_id.toggled.connect(self.check_title)

        # Hide Main IG
        self.main.checkBox_save_txt_ig.setVisible(False)
        self.main.checkBox_video_img_main.setVisible(False)
        self.main.label_title_main_path.setVisible(True)

        # hide
        self.main.spinBox_google.setVisible(False)
        self.main.label_google_title.setVisible(False)
        self.main.label_google_title_bar.setVisible(False)
        self.main.progressBar_google.setVisible(False)
        self.main.radioButton_allpost.setVisible(False)
        self.main.radioButton_videos.setVisible(False)
        self.main.radioButton_images.setVisible(False)

        #connect the signal to the method that updates the success count.
        self.pin_image_downloaded_signal.connect(self.update_success_count_pin)

        # connect signal IG img
  #      self.update_success_count_IG.connect(self.update_success_count_slot)

        # connect signal Main IG
  #      self.download_complete_instagram.connect(self.move_downloaded_folder_instagram)
  #      self.create_folder_instagram.connect(self.move_files_to_folders_instagram)
        self.main.pushButton_btn_yt.clicked.connect(self.yt)
        self.main.pushButton_btn_fb.clicked.connect(self.fb)
        self.main.pushButton_btn_tk.clicked.connect(self.tk)
        self.main.pushButton_btn_tg.clicked.connect(self.tg)
        self.main.pushButton_extentions.clicked.connect(self.grabber)
        self.initialize_app()
        

        # connect the signal
        self.update_success_count.connect(self.update_success_label)
        self.folder_path_var = ""

    def pin_check(self):
        if self.main.radioButton_pinterest.isChecked():
            print("Pinterest selected")
            self.main.label_show_title.setVisible(True)
            self.main.lineEdit_keyword.setEnabled(True)
            self.main.textEdit_input_links_pic.setEnabled(False)
            self.main.label_login_text.setVisible(True)
            self.main.label_login.setVisible(True)
            self.main.label_count_links_pic.setVisible(True)
            self.main.label_count_link_success_pic.setVisible(True)
            self.main.spinBox_google.setVisible(False)
            self.main.label_google_title.setVisible(False)
            self.main.label_google_title_bar.setVisible(False)
            self.main.progressBar_google.setVisible(False)
            # Handle Pinterest actions
            self.main.lineEdit_path_pic.clear()
            self.main.lineEdit_keyword.clear()
            self.main.textEdit_input_links_pic.clear()
            self.main.pushButton_start_pic.clicked.disconnect()
            self.main.pushButton_start_pic.clicked.connect(self.start)
            self.main.pushButton_past_pic.clicked.disconnect()
            self.main.pushButton_past_pic.clicked.connect(self.past_pin)
            self.main.pushButton_set_path_pic.clicked.disconnect()
            self.main.pushButton_set_path_pic.clicked.connect(self.select_folder_pin)
            self.main.pushButton_stop_pic.clicked.disconnect
            self.main.pushButton_stop_pic.clicked.connect(self.stop_scraping_pin)
            self.main.lineEdit_keyword.setPlaceholderText(f"សូមបញ្ចូល Pinterest URL")
            MainWindow.clear_console()

        if self.main.radioButton_fb_img.isChecked():
            print("Facebook selected")
            self.main.label_show_title.setVisible(True)
            self.main.lineEdit_keyword.setEnabled(False)
            self.main.textEdit_input_links_pic.setEnabled(True)
            self.main.label_login_text.setVisible(True)
            self.main.label_login.setVisible(True)
            self.main.label_count_links_pic.setVisible(True)
            self.main.label_count_link_success_pic.setVisible(True)
            self.main.spinBox_google.setVisible(False)
            self.main.label_google_title.setVisible(False)
            self.main.label_google_title_bar.setVisible(False)
            self.main.progressBar_google.setVisible(False)
            # Handle Facebook actions
            self.main.lineEdit_path_pic.clear()
            self.main.lineEdit_keyword.clear()
            self.main.textEdit_input_links_pic.clear()
            self.main.pushButton_start_pic.clicked.disconnect()
            self.main.pushButton_start_pic.clicked.connect(self.start_scraping_thread)
            self.main.pushButton_past_pic.clicked.disconnect()
            self.main.pushButton_past_pic.clicked.connect(self.past_pic)
            self.main.pushButton_set_path_pic.clicked.disconnect()
            self.main.pushButton_set_path_pic.clicked.connect(self.select_folder)
            self.main.pushButton_stop_pic.clicked.disconnect
            self.main.pushButton_stop_pic.clicked.connect(self.stop_scraping_fb)
            self.main.lineEdit_keyword.setPlaceholderText(f" ")
            MainWindow.clear_console()

        if self.main.radioButton_fbv2.isChecked():
            self.main.lineEdit_keyword.setEnabled(True)
            self.main.textEdit_input_links_pic.setEnabled(False)
            self.main.label_login_text.setVisible(True)
            self.main.label_login.setVisible(True)
            self.main.label_count_links_pic.setVisible(True)
            self.main.label_count_link_success_pic.setVisible(True)
            self.main.spinBox_google.setVisible(False)
            self.main.label_google_title.setVisible(False)
            self.main.label_google_title_bar.setVisible(False)
            self.main.progressBar_google.setVisible(False)
            self.main.pushButton_stop_pic.clicked.disconnect()
            #self.main.pushButton_stop_pic.clicked.connect(self.stop_ig_img)
            self.main.pushButton_start_pic.clicked.disconnect()
            #self.main.pushButton_start_pic.clicked.connect(self.start_download_IG_img)
            self.main.pushButton_set_path_pic.clicked.disconnect()
            #self.main.pushButton_set_path_pic.clicked.connect(self.set_folder_img)
            self.main.pushButton_past_pic.clicked.disconnect()
            #self.main.pushButton_past_pic.clicked.connect(self.paste_instagram_img)
            self.main.lineEdit_keyword.setPlaceholderText(f"សូមបញ្ចូល Instargram Profile URL")
            MainWindow.clear_console()

        if self.main.radioButton_google.isChecked():
            self.main.spinBox_google.setVisible(True)
            self.main.label_google_title.setVisible(True)
            self.main.label_google_title_bar.setVisible(True)
            self.main.progressBar_google.setVisible(True)
            self.main.textEdit_input_links_pic.setEnabled(False)
            self.main.lineEdit_keyword.setEnabled(True)
            self.main.label_count_links_pic.setVisible(False)
            self.main.label_count_link_success_pic.setVisible(False)
            self.main.pushButton_set_path_pic.clicked.disconnect()
            self.main.pushButton_set_path_pic.clicked.connect(self.set_google_path)
            self.main.pushButton_start_pic.clicked.disconnect() 
            self.main.pushButton_start_pic.clicked.connect(self.google_start) 
            self.main.lineEdit_keyword.setPlaceholderText(f"សូមបញ្ចូល Key Word: Cat,Dog,Cute")
            MainWindow.clear_console()

        if self.main.radioButton_instargram.isChecked():
            self.main.textEdit_input_links.clear()
            self.main.lineEdit_path.clear()
            self.main.checkBox_save_txt_ig.setChecked(True)
            self.main.radioButton_allpost.setVisible(True)
            self.main.radioButton_videos.setVisible(True)
            self.main.radioButton_images.setVisible(True)
            self.main.label_title_main_path.setVisible(False)
            self.main.checkBox_video_img_main.setVisible(True)
            self.main.checkBox_title.setVisible(False)
            self.main.checkBox_title_id.setVisible(False)
            self.main.textEdit_input_links.setEnabled(True)
            self.main.pushButton_set_path.setEnabled(False)
            self.main.groupBox_ig.setVisible(True)
            self.main.lineEdit_path.setPlaceholderText(f"សូមបញ្ចូល Instargram Profile URL")
            self.main.label_14.setText(r"បញ្ចូលខូកឃីសម្រាប់ទាញយក")

            # Button Actions
            self.main.pushButton_past.clicked.disconnect()
            self.main.pushButton_past.clicked.connect(self.paste_instagram)
            self.main.pushButton_start.clicked.disconnect()
            self.main.pushButton_start.clicked.connect(self.start_download_v2)
            self.main.pushButton_stop.clicked.disconnect()
            self.main.pushButton_stop.clicked.connect(self.stop_download_v2)
            #self.main.pushButton_set_path.clicked.connect(self.set_folder_instagram)
            self.main.checkBox_save_txt_ig.setVisible(True)
            MainWindow.clear_console()

        if self.main.radioButton_tiktok.isChecked():
            self.main.label_14.setText(r"តំណបភ្ជាប់សម្រាប់ទាញយក")
            self.main.textEdit_input_links.clear()
            self.main.label_title_main_path.setVisible(True)
            self.main.radioButton_allpost.setVisible(False)
            self.main.radioButton_videos.setVisible(False)
            self.main.radioButton_images.setVisible(False)
            self.main.checkBox_save_txt_ig.setVisible(False)
            self.main.checkBox_video_img_main.setVisible(False)
            self.main.checkBox_title.setEnabled(True)
            self.main.checkBox_title_id.setEnabled(True)
            self.main.checkBox_title.setVisible(True)
            self.main.groupBox_ig.setVisible(False)
            self.main.checkBox_title_id.setVisible(True)
            self.main.pushButton_set_path.setEnabled(True)
            self.main.pushButton_past.clicked.disconnect()
            self.main.pushButton_past.clicked.connect(self.past_main_download)
            self.main.pushButton_start.clicked.disconnect()
            self.main.pushButton_start.clicked.connect(self.start_download)
            self.main.pushButton_set_path.clicked.disconnect()
            self.main.pushButton_set_path.clicked.connect(self.setfolder)
            self.main.pushButton_stop.clicked.disconnect()
            self.main.pushButton_stop.clicked.connect(self.stop_btn)
            self.main.lineEdit_path.setPlaceholderText(r"C:\Users\Dev\Max\Tools")
            MainWindow.clear_console()

        if self.main.radioButton_youtube.isChecked():
            self.main.label_14.setText(r"តំណបភ្ជាប់សម្រាប់ទាញយក")
            self.main.textEdit_input_links.clear()
            self.main.textEdit_input_links.clear()
            self.main.groupBox_ig.setVisible(False)
            self.main.pushButton_set_path.setEnabled(True)
            self.main.radioButton_allpost.setVisible(False)
            self.main.radioButton_videos.setVisible(False)
            self.main.radioButton_images.setVisible(False)
            self.main.label_title_main_path.setVisible(True)
            self.main.checkBox_save_txt_ig.setVisible(False)
            self.main.checkBox_video_img_main.setVisible(False)
            self.main.checkBox_title.setEnabled(True)
            self.main.checkBox_title_id.setEnabled(True)
            self.main.checkBox_title.setVisible(True)
            self.main.checkBox_title_id.setVisible(True)
            self.main.pushButton_past.clicked.disconnect()
            self.main.pushButton_past.clicked.connect(self.past_main_download)
            self.main.pushButton_start.clicked.disconnect()
            self.main.pushButton_start.clicked.connect(self.start_download)
            self.main.pushButton_set_path.clicked.disconnect()
            self.main.pushButton_set_path.clicked.connect(self.setfolder)
            self.main.pushButton_stop.clicked.disconnect()
            self.main.pushButton_stop.clicked.connect(self.stop_btn)
            self.main.lineEdit_path.setPlaceholderText(r"C:\Users\Dev\Max\Tools")
            MainWindow.clear_console()

        if self.main.radioButton_facebook.isChecked():
            self.main.label_14.setText(r"តំណបភ្ជាប់សម្រាប់ទាញយក")
            self.main.textEdit_input_links.clear()
            self.main.textEdit_input_links.clear()
            self.main.groupBox_ig.setVisible(False)
            self.main.pushButton_set_path.setEnabled(True)
            self.main.radioButton_allpost.setVisible(False)
            self.main.radioButton_videos.setVisible(False)
            self.main.radioButton_images.setVisible(False)
            self.main.label_title_main_path.setVisible(True)
            self.main.checkBox_save_txt_ig.setVisible(False)
            self.main.checkBox_video_img_main.setVisible(False)
            self.main.checkBox_title.setEnabled(True)
            self.main.checkBox_title_id.setEnabled(True)
            self.main.checkBox_title.setVisible(True)
            self.main.checkBox_title_id.setVisible(True)
            self.main.pushButton_past.clicked.disconnect()
            self.main.pushButton_past.clicked.connect(self.past_main_download)
            self.main.pushButton_start.clicked.disconnect()
            self.main.pushButton_start.clicked.connect(self.start_download)
            self.main.pushButton_set_path.clicked.disconnect()
            self.main.pushButton_set_path.clicked.connect(self.setfolder)
            self.main.pushButton_stop.clicked.disconnect()
            self.main.pushButton_stop.clicked.connect(self.stop_btn)
            self.main.lineEdit_path.setPlaceholderText(r"C:\Users\Dev\Max\Tools")
            MainWindow.clear_console()

    def initialize_app(self):
        """Update UI components based on device information and license status."""
        mac_address = self.dev_max.generate_machine_id()
        result = self.dev_max.fetch_and_check_id(mac_address)
        if isinstance(result, tuple):
            # Update UI labels if the result is valid
            khmer_font = QFont("Kh Koulen", 10) 
            self.main.label_member_name.setFont(khmer_font)
            self.main.label_member_name.setText(f"សមាជិក:  {result[1]}")
            self.main.label_date.setFont(khmer_font)
            self.main.label_date.setText(f"ផុតកំណត់:  {result[2]}")
        else:
            # Update UI labels if the result is valid
            khmer_font = QFont("Kh Koulen", 10) 
            self.main.label_member_name.setFont(khmer_font)
            self.main.label_member_name.setText(f"សមាជិក: DEV MAX TOOLS")
            self.main.label_date.setFont(khmer_font)
            self.main.label_date.setText(f"ផុតកំណត់:  Expired")

    def disable_ui_elements(self):
        self.main.tabWidget.setEnabled(False)
    def enable_ui_elements(self):
        self.main.tabWidget.setEnabled(True)
    def update_ver(self):
        pass

    def yt(self):
        url_yt = "https://www.youtube.com/playlist?list=PLQ8B4AgbfhA6DXHQlBX5M1QGzYISJGXw_"
        webbrowser.open(url_yt)
    
    def fb(self):
        url_fb = "https://www.facebook.com/devmaxtools"
        webbrowser.open(url_fb)

    def tk(self):
        url_tk = "https://www.tiktok.com/@dev.max.tools"
        webbrowser.open(url_tk)

    def tg(self):
        url_tg = "https://t.me/devmaxtools"
        webbrowser.open(url_tg)

    def grabber(self):
        url_tg = "https://chromewebstore.google.com/detail/link-grabber/caodelkhipncidmoebgbbeemedohcdma"
        webbrowser.open(url_tg)

    def clear_console():
        if platform.system() == "Windows":
            os.system("cls")  
        else:
            os.system("clear")

    # UI GRABBER
    def Grabber_UI(self):
        try:
            if not hasattr(self, 'dialog_grabber'):
                self.dialog_grabber = QtWidgets.QDialog(self)
                self.ui_grabber = Ui_UI3()
                self.ui_grabber.main.setupUi(self.dialog_grabber)

                self.dialog_grabber.setFixedSize(950, 600)
                self.ui_grabber.main.pushButton_start_graber.clicked.connect(self.handle_button_Grabber)
                self.ui_grabber.main.pushButton_copy_graber.clicked.connect(self.past_copy_url_btn)
                self.ui_grabber.main.pushButton_extentions.clicked.connect(self.past_extention_btn)
                self.ui_grabber.main.pushButton_past_graber.clicked.connect(self.past_grabber_btn)
                self.ui_grabber.main.radioButton_tiktok_graber.toggled.connect(self.past_tiktok_btn)
                self.ui_grabber.main.radioButton_youtube_graber.toggled.connect(self.past_youtube_btn)
                self.ui_grabber.main.textEdit_input_links_graber.textChanged.connect(self.links_grabber_count)

                # Initialize UI actions
                self.ui_grabber.clear_console()
                self.ui_grabber.count_links()

            self.dialog_grabber.setWindowModality(QtCore.Qt.ApplicationModal)
            self.dialog_grabber.show()
            self.dialog_grabber.exec()

        except Exception as e:
            print(f"Error: {e}")

    def links_grabber_count(self):
        try:
            self.ui_grabber.count_links()
        except Exception:
            print(f"Error login")

    def past_tiktok_btn(self, checked):
        try:
            if checked:
                self.ui_grabber.grab_TikTok()
        except Exception as e:
            print(f"Error: {e}")

    def past_youtube_btn(self, checked):
        try:
            if checked:
                self.ui_grabber.grab_YT()
        except Exception as e:
            print(f"Error: {e}")

    def past_extention_btn(self):
        try:
            self.ui_grabber.grabber_extension()
        except Exception:
            print(f"Error login")

    def past_copy_url_btn(self):
        try:
            self.ui_grabber.copy_url()
        except Exception:
            print(f"Error login")

    def past_grabber_btn(self):
        try:
            self.ui_grabber.past_url()
        except Exception:
            print(f"Error login")

    def handle_button_Grabber(self):
        try:
            self.ui_grabber.start()
            self.ui_grabber.main.textEdit_input_links_graber.clear()
        except Exception:
            print(f"Error login")

    #============Update version=================#
    def extract_version(self, file_name):
        match = re.search(r'v(\d+(\.\d+)*)', file_name)
        return match.group(1) if match else "0"

    def get_latest_version(self, file_name):
        base_name, ext = os.path.splitext(file_name)
        try:
            response = requests.get(github_repo)
            if response.status_code == 200:
                files = response.json()
                matching_files = [f["name"] for f in files if base_name in f["name"] and f["name"].endswith(ext)]
                
                if matching_files:
                    latest_file = max(matching_files, key=self.extract_version)
                    return latest_file
        except Exception as e:
            QMessageBox.critical(None, "Error", f"Error checking latest version: {e}")
        return None

    def download_latest_file(self, latest_file):
        url = f"https://raw.githubusercontent.com/VannyLD/AllinOneUpdate/main/{latest_file}"
        try:
            response = requests.get(url, stream=True)
            if response.status_code == 200:
                file_path = os.path.join(os.getcwd(), latest_file)
                with open(file_path, "wb") as file:
                    for chunk in response.iter_content(1024):
                        file.write(chunk)
                
                QMessageBox.information(None, "Update", f"Update successful! New version saved as {latest_file}. Restarting...")
                os.startfile(file_path)
                sys.exit()
            else:
                QMessageBox.critical(None, "Error", "Failed to download the new version.")
        except Exception as e:
            QMessageBox.critical(None, "Error", f"Error downloading update: {e}")

    def check_for_updates(self):
        file_name = os.path.basename(sys.argv[0])  # Get the current script/executable name
        latest_version = self.get_latest_version(file_name)
        
        if latest_version and self.extract_version(latest_version) > self.extract_version(file_name):
            reply = QMessageBox.question(None, "Update Available", f"A new version ({latest_version}) is available. Do you want to update?", 
                                         QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.download_latest_file(latest_version)
        else:
            QMessageBox.information(None, "Up to Date", "Your application is already up to date!")
        
    #============FACEBOOK VERSION 1.0============#

    # Update the label when signal is emitted
    def update_success_label(self, count):
        self.main.label_count_link_success_pic.setText(f"ចំនួនទាញយកជោគជ័យ៖ {count}")

    # Sanitize file names
    def sanitize_filename_fb(self, filename):
        return re.sub(r'[<>:"/\\|?*]', '_', filename)
    

    def download_image(self, image_url, folder_path):
        try:
            # Sanitize the file name
            base_name = self.sanitize_filename_fb(image_url.split('/')[-1].split('?')[0])
            file_path = os.path.join(folder_path, base_name)

            # Check if the file exists and generate a unique name
            if os.path.exists(file_path):
                base, ext = os.path.splitext(base_name)
                count = 1
                while os.path.exists(file_path):  # Check for existing files and create a new name
                    file_path = os.path.join(folder_path, f"{base}({count}){ext}")
                    count += 1

            # Download image only if it's not already in the seen_urls set
            if image_url in self.seen_urls:
                print(f"Image already downloaded: {image_url}")
                return

            # Download the image
            r = requests.get(image_url, stream=True)
            if r.status_code == 200:
                with open(file_path, 'wb') as f:
                    for chunk in r.iter_content(1024):
                        if chunk:
                            f.write(chunk)
                print(f"Downloaded: {image_url} to {file_path}")

                # Add to the set of seen URLs
                self.seen_urls.add(image_url)

                # Update count
                self.image_count += 1
                self.update_success_count.emit(self.image_count)
            else:
                print(f"Failed to download: {image_url}")

        except Exception as e:
            print(f"Error downloading image {image_url}: {e}")


    # Extract Facebook image URL
    def extract_facebook_image_url(self, driver, facebook_url):
        try:
            driver.get(facebook_url)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'img')))
            image_element = driver.find_element(By.TAG_NAME, 'img')
            return image_element.get_attribute('src')
        except Exception as e:
            print(f"Error extracting image URL: {e}")
            return None

    def process_urls_in_batch(self, queue, folder_path):
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-webgl")
        options.add_argument("--log-level=3")

        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

        try:
            with ThreadPoolExecutor(max_workers=10) as executor:
                while not queue.empty():
                    if self.stop_flag:
                        break

                    facebook_url = queue.get()
                    if facebook_url in self.seen_urls:
                        continue
                    self.seen_urls.add(facebook_url)

                    image_url = self.extract_facebook_image_url(driver, facebook_url)
                    if image_url:
                        executor.submit(self.download_image, image_url, folder_path)
        finally:
            driver.quit()
            self.update_signal.emit("Scraping finished.")


    def start_scraping_thread(self):
        if self.main.radioButton_fb_img.isChecked():
            facebook_urls = self.main.textEdit_input_links_pic.toPlainText().splitlines()
            folder_path = self.folder_path_var

            if not folder_path:
                QMessageBox.warning(self, "Warning", "Please select a folder first.")
                return

            # Reset the image count and seen_urls to allow new downloads
            self.image_count = 0
            self.update_success_label(self.image_count)
            self.seen_urls.clear()  # Clear the set to allow re-downloads

            self.stop_flag = False
            queue = Queue()

            for url in facebook_urls:
                queue.put(url)

            threading.Thread(target=self.process_urls_in_batch, args=(queue, folder_path)).start()
        else:
            QMessageBox.warning(self, "Warning", "Please select a valid scraping mode.")


    # Stop scraping
    def stop_scraping_fb(self):
        self.stop_flag = True
        MainWindow.clear_console()
        print("Funtion stopped.")

    # Select folder
    def select_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder_path:
            self.folder_path_var = folder_path
            self.main.lineEdit_path_pic.setText(folder_path)

    def past_pic(self):
        self.main.textEdit_input_links_pic.setText("")
        clipboard = QApplication.clipboard()
        countLinkDown = 0

        try:
            # Get copied text from the clipboard
            copied_text = clipboard.text()
            
            # Remove spaces and split the text into lines
            remove_spaces = copied_text.replace(" ", "")
            links = remove_spaces.splitlines()
            
            # Filter the links based on the substring "photo.php?fbid="
            filtered_links = [link for link in links if "photo.php?fbid=" in link]
            
            # Count the filtered links
            countLinkDown = len(filtered_links)
            
            # Set the filtered links back to the textEdit
            self.main.textEdit_input_links_pic.setText("\n".join(filtered_links))
            
            # Update the count label
            self.main.label_count_links_pic.setText(f"ចំនួនទាញយក៖ {countLinkDown}")

        except Exception as e:
            print(f"Error Pasting: {e}")


    #============FACEBOOK VERSION 2.0============#


    #============DOWNLOAD PINTEREST============#

    def download_image_pin(self, image_url, folder_path):
        try:
            r = requests.get(image_url, stream=True)
            if r.status_code == 200:
                file_name = os.path.join(folder_path, image_url.split('/')[-1])
                with open(file_name, 'wb') as f:
                    for chunk in r.iter_content(1024):
                        if chunk:
                            f.write(chunk)
                print(f"Downloaded: {image_url}")
        except Exception as e:
            print(f"Error downloading image {image_url}: {e}")

    def scroll_until_no_more_content(self, driver):
        last_height = driver.execute_script('return document.body.scrollHeight')
        scroll_attempts = 0
        max_scroll_attempts = 5 
        delay_between_scrolls = 5

        while True:
            if self.stop_flag:
                print('Stopping process.')
                return

            # Scroll down to the bottom of the page
            driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
            time.sleep(delay_between_scrolls)  # Wait for images to load after scrolling

            # Wait for images to load (you can increase the waiting time if needed)
            try:
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'img')))
            except Exception:
                print('Error images load.')

            images = driver.find_elements(By.TAG_NAME, 'img')
            new_images_found = False  # Flag to check if new images are found

            for image in images:
                if self.stop_flag:
                    break
                src = image.get_attribute('src')
                if src and '30x30_RS' not in src and '280x280_RS' not in src:
                    high_quality_src = re.sub('/\\d+x/', '/736x/', src)
                    if high_quality_src not in self.seen_urls:
                        self.seen_urls.add(high_quality_src)
                        self.download_image_pin(high_quality_src, self.folder_path)
                        self.pin_image_count += 1
                        self.pin_image_downloaded_signal.emit(self.pin_image_count)  # Emit the signal with the updated count
                        new_images_found = True  # New images were found and processed

            if self.stop_flag:
                return

            # After scrolling, check if new content was loaded
            new_height = driver.execute_script('return document.body.scrollHeight')
            if new_height == last_height:
                scroll_attempts += 1  # No new content loaded
            else:
                scroll_attempts = 0  # Reset attempts if new content was loaded

            last_height = new_height

            # Stop scrolling after multiple attempts without new content
            if scroll_attempts >= max_scroll_attempts:
                print('No new content')
                return

            # If no new images were found, also stop to avoid infinite scrolling
            if not new_images_found:
                print("No new images found")
                return


    def start(self):
        run = threading.Thread(target=self.start_scraping_pin)
        run.start()

    def start_scraping_pin(self):
        # Check if the Pinterest radio button is checked
        if self.main.radioButton_pinterest.isChecked():  # No need to pass 'self' to isChecked()
            try:

                self.stop_flag = False
                self.pin_image_count = 0
                self.seen_urls.clear()

                # Update UI for the image download process
                self.main.label_count_links_pic.setText(f"ទាញយករូបភាព៖ 1 Pinterest")
                self.main.label_count_link_success_pic.setText(f"ចំនួនទាញយកជោគជ័យ៖ 0")

                # Set up Chrome options for headless browsing
                options = Options()
                options.add_argument("--headless")
                options.add_argument("--disable-gpu")
                options.add_argument("--no-sandbox")
                options.add_argument("--disable-dev-shm-usage")

                # Initialize the Chrome driver
                driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

                # Go to the Pinterest URL from the UI
                driver.get(self.main.lineEdit_keyword.text())
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "img")))

                # Start scraping and scrolling until no more content is found
                self.scroll_until_no_more_content(driver)

                # Quit the driver after scraping
                driver.quit()
                print("Finished.")
                self.update_signal.emit(f"Total images: {self.pin_image_count}")

            except Exception:
                print(f"Failed")

        else:
            print("Plese Select Checkbox")


 
    def update_status_pin(self, message):
        self.main.label_count_link_success_pic.setText(message)


    def update_success_count_pin(self, count):
        self.main.label_count_link_success_pic.setText(f"ចំនួនទាញយកជោគជ័យ៖ {count}")


    def stop_scraping_pin(self):
        self.stop_flag = True
        print("stopped.")
        MainWindow.clear_console()
        self.update_status_pin(f"ចំនួនទាញយកជោគជ័យ៖ {self.pin_image_count}")


    def select_folder_pin(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder_path:
            self.folder_path = folder_path 
            self.main.lineEdit_path_pic.setText(folder_path)


    def past_pin(self):
        self.main.textEdit_input_links.setText("")  
        clipboard = QApplication.clipboard() 
        countLinkDown = 0  

        try:
            copied_text = clipboard.text()  
            remove_spaces = copied_text.replace(" ", "")  
            link = remove_spaces.splitlines()  
            
            # Filter out only Pinterest links
            pinterest_links = [l for l in link if l.startswith("https://www.pinterest.com") or l.startswith("www.pinterest.com")]

            countLinkDown = len(pinterest_links)  
            self.main.lineEdit_keyword.setText("\n".join(pinterest_links))  

            # Update the label with the count of Pinterest links
            self.main.label_count_links_pic.setText(f"ទាញយករូបភាព៖ {countLinkDown} ​តំណបភ្ជាប់")

        except Exception as e:
            print(f"Error Pasting: {e}")

    #============GOOGLE DOWNLOAD============#
    def set_google_path(self):
        folder_selected = QFileDialog.getExistingDirectory(self, "Select Folder")
        self.main.lineEdit_path_pic.setText(folder_selected)
    
    def google_start(self):
        run = threading.Thread(target=self.start_google)
        run.start()
    
    def start_google(self):
        keywords = self.main.lineEdit_keyword.text()
        limit = self.main.spinBox_google.value()
        directory = self.main.lineEdit_path_pic.text()

        if not keywords:
            QMessageBox.warning(self, "Input Error", "Please enter at least one keyword.")
            return

        self.main.pushButton_start_pic.setEnabled(False)
        self.google_images(keywords, limit, directory)


    def google_images(self, keywords, limit, directory='', extensions={'.ico', '.jpg', '.png', '.jpeg', '.gif'}):
        keyword_to_search = [str(item).strip() for item in keywords.split(',')]
        main_directory = directory if directory != '' else 'images/'

        total_images = len(keyword_to_search) * limit
        progress_value = 0
        logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")

        for keyword in keyword_to_search:
            sub_directory = self._create_directories(main_directory, keyword)
            search_url = (
                'https://www.google.com/search?q=' +
                urllib.parse.quote(keyword.encode('utf-8')) +
                '&tbm=isch'
            )
            logging.debug(f"Search URL: {search_url}")
            try:
                raw_html = self._download_page(search_url)
            except Exception as e:
                logging.error(f"Error fetching search results page: {e}")
                continue

            end_object = -1
            google_image_seen = False
            downloaded_count = 0

            while downloaded_count < limit:
                try:
                    new_line = raw_html.find('\"https://', end_object + 1)
                    end_object = raw_html.find('\"', new_line + 1)
                    buffer = raw_html.find('\\', new_line + 1, end_object)

                    if buffer != -1:
                        object_raw = raw_html[new_line + 1:buffer]
                    else:
                        object_raw = raw_html[new_line + 1:end_object]

                    if any((extension in object_raw for extension in extensions)):
                        try:
                            r = requests.get(object_raw, allow_redirects=True, timeout=5)
                            if 'html' not in str(r.content):
                                file_extension = os.path.splitext(object_raw)[1]
                                if file_extension not in extensions:
                                    raise ValueError("Invalid file extension")
                                if file_extension == '.png' and not google_image_seen:
                                    google_image_seen = True
                                    raise ValueError("Skipping Google-related image")

                                file_name = f"{keyword}_{downloaded_count + 1}{file_extension}"
                                file_path = os.path.join(sub_directory, file_name)
                                with open(file_path, 'wb') as file:
                                    file.write(r.content)
                                downloaded_count += 1
                                progress_value += 1
                                self.update_progress(progress_value, total_images)
                                logging.info(f"Image saved: {file_path}")
                        except Exception as e:
                            logging.error(f"Error downloading image: {e}")
                except Exception as e:
                    logging.error(f"Error parsing HTML or processing image URL: {e}")

            time.sleep(2)
            self.main.pushButton_start_pic.setEnabled(True)
            MainWindow.clear_console()

    def _create_directories(self, main_dir, sub_dir):
        path = os.path.join(main_dir, sub_dir)
        os.makedirs(path, exist_ok=True)
        return path
    
    def _download_page(self, url):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                          '(KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.text

    def update_progress(self, current, total):
        self.main.progressBar_google.setValue(int((current / total) * 100))



    #============FILE IMPORT============#
    def resource_path(self, relative_path):
        """Get the absolute path to a resource."""
        try:
            if hasattr(sys, '_MEIPASS'):
                return os.path.join(sys._MEIPASS, relative_path)
        except Exception as e:
            print(f"Error accessing sys._MEIPASS: {e}")
        return os.path.join(os.path.dirname(__file__), relative_path)
    

    def setup_resource_paths(self):
        """Set up paths to required resources."""
        self.ytdl_path = self.resource_path(r"File/yt-dlp.exe")
        self.ico_path = self.resource_path(r"File/ico.ico")
        self.IGL_path = self.resource_path(r"IGL.py")

    #============MAIN DOWNLOAD INSTAGRAM V2============#
    def remove_unwanted_files(self, profile_name):
        # Find unwanted files
        unwanted_files = glob.glob(os.path.join(profile_name, '*.json')) + \
                        glob.glob(os.path.join(profile_name, '*.xz')) + \
                        glob.glob(os.path.join(profile_name, '*.json.xz'))

        # Only add .txt files if the checkbox is unchecked
        if not self.main.checkBox_save_txt_ig.isChecked():
            unwanted_files += glob.glob(os.path.join(profile_name, '*.txt'))

        # Only add .txt files if the checkbox is unchecked
        if self.main.checkBox_video_img_main.isChecked():
            unwanted_files += glob.glob(os.path.join(profile_name, '*.txt'))

        # Only add .txt files if the checkbox is unchecked
        if self.main.radioButton_images.isChecked():
            unwanted_files += glob.glob(os.path.join(profile_name, '*.mp4'))
            unwanted_files += glob.glob(os.path.join(profile_name, '*.avi'))
            unwanted_files += glob.glob(os.path.join(profile_name, '*.mvk'))

        # Remove each unwanted file
        for file in unwanted_files:
            try:
                os.remove(file)
                print(f"Removed: {file}")
                MainWindow.clear_console()
            except Exception as e:
                print(f"Error removing {file}: {str(e)}")
                
    def rename_files_with_txt_content(self, profile_name):
        MAX_FILENAME_LENGTH = 50  # Adjust as needed

        def sanitize_filename_ig(filename):
            return re.sub(r'[<>:"/\\|?*\x00-\x1F]', '', filename)

        # Get all .txt files in the directory
        txt_files = glob.glob(os.path.join(profile_name, '*.txt'))
        
        for txt_file in txt_files:
            try:
                with open(txt_file, 'r', encoding='utf-8') as f:
                    new_name = sanitize_filename_ig(f.read().strip())
                
                # Truncate new_name if too long
                if len(new_name) > MAX_FILENAME_LENGTH:
                    new_name = new_name[:MAX_FILENAME_LENGTH].rsplit(' ', 1)[0]

                # Get base name without extension
                base_name = os.path.splitext(os.path.basename(txt_file))[0]

                # Rename matching files (including .txt)
                for file_path in glob.glob(os.path.join(profile_name, base_name + "*")):
                    # Skip processing if the current txt_file has already been renamed
                    if not os.path.exists(file_path):
                        continue
                    
                    extension = os.path.splitext(file_path)[1]
                    new_file_path = os.path.join(profile_name, new_name + extension)

                    # Handle name conflicts
                    count = 1
                    while os.path.exists(new_file_path):
                        new_file_path = os.path.join(profile_name, f"{new_name} ({count}){extension}")
                        count += 1

                    os.rename(file_path, new_file_path)
                    print(f"Renamed: {file_path} -> {new_file_path}")
                    MainWindow.clear_console()

            except FileNotFoundError:
                print(f"File not found: {txt_file}")
            except Exception as e:
                print(f"Error processing {txt_file}: {str(e)}")

    def start_download_v2(self):
        """Start download process."""
        username = self.main.lineEdit_path.text().strip()
        cookies = self.main.textEdit_input_links.toPlainText().strip()

        if not username:
            QMessageBox.warning(self, 'Warning', 'Please enter an Instagram username.')
            return
        if not cookies:
            QMessageBox.warning(self, 'Warning', 'Please enter cookies.')
            return

        self.main.label_14.setText("កំពុងដំណើរការទាញយក...")
        
        # Reset the stop flag
        self.stop_flag = False  

        def run_download():
            try:
                self.download_instagram_v2(username, cookies)
                
                # Rename downloaded files based on text content
                self.rename_files_with_txt_content(username)
                # After download completes, remove unwanted files
                self.remove_unwanted_files(username)

                self.main.label_14.setText("តំណបភ្ជាប់សម្រាប់ទាញយក")
            except Exception as e:
                QMessageBox.critical(self, 'Error', f'Error: {str(e)}')

        # Run the download in a separate thread
        self.download_thread = threading.Thread(target=run_download)
        self.download_thread.start()


    def stop_download_v2(self):
        """Stop the download process."""
        self.stop_flag = True
        if self.download_thread and self.download_thread.is_alive():
            self.download_thread.join()
        self.main.label_14.setText("តំណបភ្ជាប់សម្រាប់ទាញយក")
        QMessageBox.information(self, 'ការទាញយកបានបញ្ឃប់', 'ការទាញយកបានបញ្ឃប់!!!')

    def check_all_posts(self):
        """Download all posts."""
        self.download_all = True
        self.download_videos = True
        self.download_images = True

    def check_only_videos(self):
        """Download only videos."""
        self.download_all = False
        self.download_videos = True
        self.download_images = False

    def check_only_images(self):
        """Download only images."""
        self.download_all = False
        self.download_videos = False
        self.download_images = True

    def set_cookies(self, cookies):
        """Set session cookies."""
        for cookie in cookies.split(';'):
            cookie = cookie.strip()
            if '=' in cookie:
                name, value = cookie.split('=', 1)
                self.loader.context._session.cookies.set(name.strip(), value.strip())

    def download_instagram_v2(self, username, cookies):
        """Download posts from Instagram."""
        try:
            self.set_cookies(cookies)
            profile = instaloader.Profile.from_username(self.loader.context, username)
            total_posts = profile.mediacount
            self.main.label_count_links.setText(f"ចំនួនទាញយក៖ {total_posts} ផុស")

            successful_downloads = 0
            with ThreadPoolExecutor(max_workers=5) as executor:
                futures = []
                for post in profile.get_posts():
                    if self.stop_flag:
                        break
                    if self.download_all:
                        futures.append(executor.submit(self.download_post, post, username))
                    elif self.download_images:
                        futures.append(executor.submit(self.download_post, post, username))
                    elif self.download_videos and post.typename == 'GraphVideo':
                        futures.append(executor.submit(self.download_post, post, username))

                for future in futures:
                    if self.stop_flag:
                        break
                    if future.result():
                        successful_downloads += 1
                        self.main.label_count_link_success.setText(f"ចំនួនទាញយកជោគជ័យ៖ {successful_downloads} ផុស")

            self.main.label_14.setText("តំណបភ្ជាប់សម្រាប់ទាញយក")

        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Error downloading: {str(e)}')

    def download_post(self, post, target):
        """Download a single post."""
        try:
            self.loader.download_post(post, target=target)
            return True
        except Exception as e:
            logging.error(f"Failed to download post {post.mediaid}: {e}")
            return False
        
    def paste_instagram(self):
        """Paste Instagram profile link from clipboard and extract username."""
        try:
            clipboard = QApplication.clipboard()
            copied_text = clipboard.text().strip()

            if "instagram.com" in copied_text:
                # Split the URL by slashes and get the username part
                parts = copied_text.split("/")
                
                # Username is typically the second part, whether it ends in a slash or contains additional segments like '/tagged/'
                if len(parts) >= 3:
                    username = parts[3] if parts[3] else parts[2]  # Extract username, either from the third or second part
                    if username:
                        self.main.lineEdit_path.setText(username)  # Set the extracted username in the text edit
                    else:
                        QMessageBox.warning(self, "ការព្រមាន!", "មិនមាន URL Instagram សម្រាប់ចម្លងទេ")
                else:
                    QMessageBox.warning(self, "ការព្រមាន!", "មិនមាន URL Instagram សម្រាប់ចម្លងទេ")
            else:
                QMessageBox.warning(self, "ការព្រមាន!", "មិនមាន URL Instagram សម្រាប់ចម្លងទេ")
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to extract Instagram username: {str(e)}")




    #============MAIN DOWNLOAD TIKOK YOUTUBE FACEBOOK============#
    def check_title(self):
        # Disable the other checkbox when one is checked
        if self.main.checkBox_title.isChecked():
            self.main.checkBox_title_id.setEnabled(False)
        else:
            self.main.checkBox_title_id.setEnabled(True)

        if self.main.checkBox_title_id.isChecked():
            self.main.checkBox_title.setEnabled(False)
        else:
            self.main.checkBox_title.setEnabled(True)

    def setfolder(self):
        save_folder = QtWidgets.QFileDialog.getExistingDirectory(None, "Select Folder")
        if save_folder:
            self.main.lineEdit_path.setText(save_folder)

    def past_main_download(self):
        self.main.textEdit_input_links.setText("")
        clipboard = QApplication.clipboard()
        CountLinkDown = 0

        try:
            copied_text = clipboard.text()
            remove_spaces = copied_text.replace(" ", "") 


            links = remove_spaces.splitlines()
            CountLinkDown = len(links) 
            
            self.main.textEdit_input_links.setText("\n".join(links)) 
            self.main.label_count_links.setText(f"ចំនួនទាញយក៖ {CountLinkDown}")

        except Exception as e:
            print(f"Error in Past Button Click: {e}")

    def stop_btn(self):
        self.pause = True  # Pause the download
        for proc in psutil.process_iter(attrs=['pid', 'name']):
            if 'ffmpeg.exe' in proc.info['name'].lower() or 'yt-dlp.exe' in proc.info['name'].lower():
                proc.terminate()  # Kill the process
        self.main.label_14.setText("ការទាញយកបានផ្អាក!")  # "Download Paused!"


    def sanitize_filename(title):
        invalid_chars = '<>:\"/\\|?*'
        sanitized_title = ''.join((c if c not in invalid_chars else '_' for c in title))
        return sanitized_title

    def get_unique_filename(download_folder, filename):
        """ Check if file exists, and if so, append a counter to the filename. """  # inserted
        base_name, ext = os.path.splitext(filename)
        counter = 1
        new_filename = filename
        while os.path.exists(os.path.join(download_folder, new_filename)):
            new_filename = f'{base_name} ({counter}){ext}'
            counter += 1
        return new_filename

    def get_output_template(self, download_folder, save_folder):
        download_folder = os.path.join(save_folder)
        """Determine the output template based on the checkbox selections."""
        if self.main.checkBox_title.isChecked():
            return f'{os.path.join(download_folder)}/%(title)s.%(ext)s'
        elif self.main.checkBox_title_id.isChecked():
            return f'{os.path.join(download_folder)}/%(title)s.%(id)s.%(ext)s'
        else:
            return f'{os.path.join(download_folder)}/%(title)s.%(ext)s'
        

    def start_download(self):
        run = threading.Thread(target=self.start_main_download)
        run.start()


    def start_main_download(self):
        self.pause = False
        save_folder = self.main.lineEdit_path.text()
        video_type = self.main.comboBox_type.currentText()
        video_quality =  self.main.comboBox_quality.currentText()

        # Ensure download_folder is initialized before passing it to get_output_template
        download_folder = os.path.join(save_folder)  # Ensure download_folder is initialized here

        # Get the output template based on the checkbox selections
        output_template = self.get_output_template(download_folder, save_folder)
        
        #============TIKTOK DOWLOAD============#
        if self.main.radioButton_tiktok.isChecked():
            self.main.label_14.setText(f"កំពុងដំណើរការទាញយក!")  # "Downloading..."
            print("TikTok Checked")
            download_folder = os.path.join(save_folder)
            ytdl_path = self.resource_path("File/yt-dlp.exe")
            labe_download_success = 0

            # Determine video quality
            if video_quality == "1080p":
                video_height = 1080
            elif video_quality == "720p":
                video_height = 720
            else:
                video_height = 'best'

            # Choose download command based on title option
            if self.main.checkBox_title.isChecked():
                print("Title Checked")
                video_cmd = f'"{ytdl_path}" {{}} -f "bestvideo[height<={video_quality}]+bestaudio[ext=m4a]/best" --merge-output-format {video_type} -o "{download_folder}/%(title)s.%(ext)s"'
            elif self.main.checkBox_title_id.isChecked():
                print("Title+ID Checked")
                video_cmd = f'"{ytdl_path}" {{}} -f "bestvideo[height<={video_quality}]+bestaudio[ext=m4a]/best" --merge-output-format {video_type} -o "{download_folder}/%(title)s_%(id)s.%(ext)s"'

            # Get list of links
            link_list = self.main.textEdit_input_links.toPlainText().split("\n")

            for line in link_list:
                link = line.strip()

                if link:
                    try:
                        # Extract the video title using yt-dlp
                        result = subprocess.run(
                            [ytdl_path, "--get-title", link],
                            capture_output=True, text=True, encoding="utf-8", errors="replace"
                        )

                        if result.stdout:
                            title = result.stdout.strip()

                            # Truncate and sanitize title for filenames
                            if len(title) > 50:
                                title = title[:50]
                            title = (
                                title.replace(":", "")
                                .replace(" ", " ")
                                .replace("#", "#")
                                .replace("/", "#")
                                .replace("<", "")
                                .replace(">", "")
                                .replace("|", "")
                            )

                            # Construct the final file path with unique naming
                            file_name = f"{title}"  # Start with the video title
                            unique_id = f"_{link.split('/')[-1]}"  # Extract TikTok ID from the URL
                            extension = ""  # Use the appropriate extension for video/audio

                            # Ensure file name includes a unique ID
                            file_name = f"{file_name}{unique_id}{extension}"

                            # Check if the file already exists
                            file_path = os.path.join(download_folder, file_name)
                            counter = 1

                            # Keep appending a counter to the filename if it already exists
                            while os.path.exists(file_path):
                                file_name = f"{title}{unique_id}({counter}){extension}"
                                file_path = os.path.join(download_folder, file_name)
                                counter += 1

                            # Use the final unique file name in the download command
                            download_cmd = video_cmd.format(link).replace("%(title)s", file_name)

                            # Execute the download command
                            subprocess.run(download_cmd, shell=True, check=True, encoding="utf-8", errors="replace")

                            labe_download_success += 1
                            self.main.label_count_link_success.setText(f"ចំនួនទាញយកជោគជ័យ៖ {labe_download_success}") 
                            print(f"Download Success: {link}")
                        else:
                            print(f"Failed to extract title for {link}")

                    except subprocess.CalledProcessError as e:
                        print(f"Error: {e}")

                    if self.pause:
                        print("Stop Download....")
                        break

        #============YOUTUBE DOWLOAD============#
        if self.main.radioButton_youtube.isChecked():
            self.main.label_14.setText(f"កំពុងដំណើរការទាញយក!")  # "Downloading..."
            print("TikTok Checked")
            download_folder = os.path.join(save_folder)
            ytdl_path = self.resource_path("File/yt-dlp.exe")
            labe_download_success = 0

            if video_quality == "1080p":
                video_height = 1080
            elif video_quality == "720p":
                video_height = 720
            else:
                video_height = 'best'

            # Title Checked
            if self.main.checkBox_title.isChecked():
                print("Title Checked")
                video_cmd = f'"{ytdl_path}" {{}} -f "bestvideo[height<={video_quality}]+bestaudio[ext=m4a]/best" --merge-output-format {video_type} -o "{download_folder}/%(title)s.%(ext)s"'

            # Title+ID Checked
            if self.main.checkBox_title_id.isChecked():
                print("Title+ID Checked")
                video_cmd = f'"{ytdl_path}" {{}} -f "bestvideo[height<={video_quality}]+bestaudio[ext=m4a]/best" --merge-output-format {video_type} -o "{download_folder}/%(title)s_%(uploader)s.%(ext)s"'

            link_list = self.main.textEdit_input_links.toPlainText().split("\n")

            for line in link_list:
                link = line.strip()

                if link:
                    try:
                        # First, extract the video title using yt-dlp without downloading
                        result = subprocess.run([ytdl_path, "--get-title", link], capture_output=True, text=True)
                        title = result.stdout.strip()

                        # Truncate title if it exceeds 50 characters
                        if len(title) > 50:
                            title = title[:50]

                        # Construct the final download command using the truncated title
                        download_cmd = video_cmd.format(link).replace("%(title)s", title)

                        # Run the download command
                        subprocess.run(download_cmd, shell=True, check=True)
                        labe_download_success += 1
                        self.main.label_count_link_success.setText(f"ចំនួនទាញយកជោគជ័យ៖ {labe_download_success}")  # "Success downloads:"
                        print(f"Download Success: {link}")

                    except subprocess.CalledProcessError as e:
                        print(f"Error: {e}")

                    if self.pause:
                        print("Stop Download....")    
                        break


        #============FACEBOOK DOWLOAD============#       
        if self.main.radioButton_facebook.isChecked():
            print('Facebook Checked')

            # Set the download folder and yt-dlp path
            download_folder = os.path.join(save_folder)  # Ensure save_folder is defined correctly
            ytdl_path = self.resource_path("File/yt-dlp.exe")
            label_download_success = 0
            video_height = {'1080p': 1080, '720p': 720}.get(video_quality, 'best')  # Ensure video_quality is set

            # Determine the output template based on checkbox selections
            if self.main.checkBox_title.isChecked():
                output_template = f'{os.path.join(download_folder, "%(title)s.%(ext)s")}'
                print(f'Output template with title and hashtags: {output_template}')
            elif self.main.checkBox_title_id.isChecked():
                output_template = f'{os.path.join(download_folder, "%(title)s.%(id)s.%(ext)s")}'
                print(f'Output template with title and video ID: {output_template}')
            else:
                output_template = f'{os.path.join(download_folder, "%(title)s.%(ext)s")}'
                print(f'Default output template (title only): {output_template}')

            # Get the list of links from the input
            link_list = self.main.textEdit_input_links.toPlainText().strip().splitlines()
            total_links = len(link_list)
            self.main.label_count_link_success.setText(f'ចំនួនទាញយកជោគជ័យ៖ {label_download_success}')
            print(f'Total links to process: {total_links}')

            title_count = {}

            for line in link_list:
                link = line.strip()

                # Skip empty lines
                if not link:
                    print('Skipping empty line.')
                    continue

                clean_link = link.split('?')[0]
                print(f'Processing link: {clean_link}')

                # Extract title and ID using yt-dlp
                try:
                    video_info = subprocess.run([ytdl_path, '--get-title', '--get-id', clean_link], capture_output=True, text=True, check=True)
                except subprocess.CalledProcessError as e:
                    print(f'Error extracting title or ID for {clean_link}. Skipping this link.')
                    continue

                output_lines = video_info.stdout.strip().splitlines()
                print(f'yt-dlp output: {output_lines}')

                if len(output_lines) < 2:
                    print(f'Missing title or ID for {clean_link}. Skipping this link.')
                    continue

                title = output_lines[0]
                video_id = output_lines[1]

                # Clean the title to make it a valid filename
                cleaned_title = re.sub(r'^\d+\.\s*', '', title)
                cleaned_title = re.sub(r'\s*·\s*(\d+\.\s*)?', '', cleaned_title)
                cleaned_title = re.sub(r'[\d+][K|M|B]?\s*(views?|reactions?|likes?|shares?|comments?)', '', cleaned_title)
                cleaned_title = re.sub(r'[<>:\"/\\|?*]', '', cleaned_title).strip()
                print(f'Cleaned title: {cleaned_title}')

                # Extract hashtags from the title
                hashtags = re.findall(r'#\w+', cleaned_title)
                hashtag_string = ' '.join(hashtags)
                formatted_title = f'{cleaned_title} {hashtag_string}'.strip()
                formatted_title = re.sub(r'[<>:\"/\\|?*]', '', formatted_title)

                # Ensure the filename is unique by appending a counter if necessary
                base_name, ext = os.path.splitext(formatted_title)
                counter = 1
                unique_title = f'{formatted_title}{ext}'

                while os.path.exists(os.path.join(download_folder, unique_title)):
                    unique_title = f'{base_name} ({counter}){ext}'
                    counter += 1

                # Prepare yt-dlp command
                if video_height != 'best':
                    yt_dlp_command = f'\"{ytdl_path}\" \"{clean_link}\" -f \"bestvideo[height<={video_height}]+bestaudio\" --merge-output-format mp4 -o \"{os.path.join(download_folder, unique_title)}\"'
                else:
                    yt_dlp_command = f'\"{ytdl_path}\" \"{clean_link}\" -f \"bestvideo+bestaudio\" --merge-output-format mp4 -o \"{os.path.join(download_folder, unique_title)}\"'

                # Execute yt-dlp command
                try:
                    print(f'Executing command: {yt_dlp_command}')
                    subprocess.run(yt_dlp_command, shell=True, check=True)
                    label_download_success += 1
                    self.main.label_count_link_success.setText(f'ចំនួនទាញយកជោគជ័យ៖ {label_download_success}')
                    print(f'Download successful for: {clean_link}')
                except subprocess.CalledProcessError as e:
                    print(f'Error downloading {clean_link}. Skipping this link.')

                # Check for pause condition
                if self.pause:
                    print('Stopping Downloads...')
                    break


def main():
    app = QApplication(sys.argv)

    # Set global font for the application
    font = QFont("Kh Koulen", 12)
    app.setFont(font)

    salt_file = os.path.join(os.path.expanduser("~"), ".devmax_secret_salt")
    if os.path.exists(salt_file):
        main_window = MainWindow()
        main_window.show()  
    else:
        max_key_app = MaxKeyApp()
        max_key_app.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()