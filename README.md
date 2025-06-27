# Air Conditioning Management System

## Table of Contents

1. [Project Overview](#project-overview)
2. [Project Structure & File Organization](#project-structure--file-organization)
   1. [Django Project Structure](#django-project-structure)
   2. [ESP32 Firmwares Organization](#esp32-firmwares-organization)
3. [Technologies Used](#technologies-used)
4. [Features & Functionalities](#features--functionalities)
   1. [Web Interface](#web-interface)
   2. [ESP32 Control](#esp32-control)
5. [System Architecture](#system-architecture)
   1. [Architecture Overview](#architecture-overview)
6. [Architectural Decisions](#architectural-decisions)
7. [System Demo](#system-demo)
8. [Running the Applications](#running-the-applications)
   1. [Django Project](#django-project)
      - [Requirements](#requirements)
      - [macOS](#macos)
      - [Windows](#windows)
   2. [ESP32 Firmware](#esp32-firmware)
9. [Final Considerations](#final-considerations)

---

## Project Overview

The Air Conditioner Management System aims to develop an embedded device that automates the control of air conditioners using an ESP32 microcontroller. By copying infrared signals from the air conditioner’s remote control, the ESP32 can remotely manage the air conditioner’s operation, reducing energy waste and optimizing usage in shared environments such as schools, offices, and universities.

---

## Project Structure & File Organization

The project is organized into a **main directory** containing two primary folders and a README.md file:

```bash
📦 air_conditioning_management_system 
┣ 📂 ac_mm_system
┣ 📂 esp32
┃ ┣ 📂 esp32_project
┃ ┣ 📂 esp32_validated_modules
┣ 📄 README.md
```

- ```ac_mm_system```: Contains the Django project that provides the backend logic, API endpoints, and web interface.

- ```esp32```: Holds all ESP32 firmware and hardware-related code.
   - ```esp32_validated_modules```: Contains tested and validated ESP32 modules.
   - ```esp32_project```: The final ESP32 firmware integrated with the Django system.

### Django Project Structure

```bash
📦 ac_mm_system                            # Main project folder
┣ 📂 certificates                          # Folder for certificates used by the project (it's NOT monitored by git)
┃ ┣ 📄 hivemq-ca.pem                       # CA certificate for MQTT broker (HiveMQ)
┣ 📂 website                               # Folder for the main web application (frontend + backend)
┣ 📂 accounts                              # Folder for user authentication and management
┣ 📂 ac_mm_system                          # Project-specific Django application
┣ 🐍 manage.py                             # Django management script for running the server, migrations, etc.
┣ 💾 db.sqlite3                            # SQLite database for local development (or you can use PostgreSQL), (it's NOT monitored by git)
┣ 📄 secrets.json                          # File containing sensitive information like API keys or passwords (it's NOT monitored by git)
┣ 📄 requirements.txt                      # File listing all Python dependencies for the project
```

### ESP32 Firmwares Organization

```bash
📦 esp32                                  # Root directory for all ESP32-related code
┣ 📂 esp32_project                        # Final ESP32 project files, including main code
┣ 📂 esp32_validated_modules              # Folder containing tested and validated ESP32 modules
┃ ┣ 📂 push_buttons                       # Module for handling button presses (user input)
┃ ┣ 📂 mqtt_subscriber_publisher          # Module for handling MQTT communication (subscribe/publish)
┃ ┣ 📂 led_rgb                            # Module to control RGB LED lights
┃ ┣ 📂 ir_sender                          # Module for infrared (IR) signal sending
┃ ┣ 📂 ir_receiver                        # Module for infrared (IR) signal receiving
┃ ┣ 📂 ir_receiver_and_send               # Module that combines both IR receiver and sender functionalities
┃ ┣ 📂 esp32_mac_address                  # Module to fetch and handle the ESP32 MAC address
```

---

## Technologies Used

- **Web Platform:**
   - **Frontend:** HTML, CSS, Chart.js
   - **Backend:** Django 
   - **CSS Framework:** Bootstrap
- **Database:** SQLite
- **Communication Protocol:** 
   - MQTT (Paho-mqtt with HiveMQ)
   - HTTP
- **Task Scheduling:** Celery with RabbitMQ
- **Microcontroller:** ESP32
<!-- - **Deployment:** Railway -->

---

## Features & Functionalities

### Web Interface:

- **Schedule Management:** Allows users to configure on/off times for air conditioners.

- **Remote Control:** Provides direct control of air conditioners via the web interface.

- **Energy Consumption Graphs:** Displays energy usage data in a visually appealing format using Chart.js.

- **Visual Feedback:** Provides real-time status updates on the air conditioners.

- **Responsive Design:** Optimized interface that adapts seamlessly to small screen devices.

### ESP32 Control:

- **Infrared Signal Copying:** The ESP32 copies the air conditioner's remote signals and relays commands based on the web configuration.

- **MQTT Communication:** The ESP32 subscribes to topics to receive commands via MQTT and executes the corresponding infrared signals.

- **Manual Configuration:** Users can configure the system using physical buttons on the ESP32 device.

---

## System Architecture

The following diagram illustrates the complete architecture of the Air Conditioning Management System, showing the communication flow between all components:

![System Architecture Diagram](imgs/ChronoAir-SystemDesign.png)

### Architecture Overview

The system architecture is composed of several interconnected components that work together to provide automated air conditioning management:

#### **1. Django Backend (Left Side)**
- **Monolithic Producer**: The Django application acts as the central control unit that generates tasks and schedules
- **Celery Beat**: Runs periodically (every 1 minute and 30 minutes) to execute scheduled tasks and monitor system status
- **Database Integration**: Connected to SQLite database for storing user configurations, schedules, and historical data

#### **2. Message Broker Layer (Center)**
- **RabbitMQ**: Serves as the message broker for task distribution between Django and Celery workers
- **Task Queue**: Manages the execution of background tasks including MQTT communication and scheduling operations
- **Consumer Workers**: Multiple Celery workers process tasks from the queue, enabling scalable task execution

#### **3. MQTT Communication Layer**
- **HiveMQ Broker**: Cloud-based MQTT broker that facilitates real-time communication between the web application and ESP32 devices
- **Publish/Subscribe Pattern**: Django publishes commands to specific topics, while ESP32 devices subscribe to receive instructions
- **Unidirectional Communication**: ESP32 devices only listen to commands from the Django application via MQTT topics

#### **4. ESP32 Devices (Right Side)**
- **Multiple ESP32 Controllers**: Each device manages one or more air conditioning units
- **MQTT Subscriber**: Each ESP32 subscribes to its specific topic to receive commands from the Django application
- **Infrared Control**: ESP32 devices use IR communication to send commands directly to air conditioners

#### **5. Data Flow**
1. **User Interaction**: Users configure schedules and send commands through the Django web interface
2. **Task Generation**: Django creates tasks that are queued in RabbitMQ
3. **Task Processing**: Celery workers pick up tasks and execute MQTT publish operations
4. **Command Transmission**: Commands are sent via HiveMQ to the appropriate ESP32 devices
5. **Device Response**: ESP32 devices receive commands via MQTT subscription and execute IR commands to control air conditioners
6. **Data Storage**: System logs and command history are stored in the SQLite database for monitoring and analytics

This architecture ensures **scalability**, **reliability**, and **real-time communication** between the web application and the distributed ESP32 devices, enabling efficient management of multiple air conditioning units across different locations.

## Architectural Decisions

- **MQTT Broker:** HiveMQ was selected as the MQTT broker for handling communication between the Django server and the ESP32 devices due to its reliability and scalability.

- **ESP32:** The choice of ESP32 allows for an efficient and flexible solution due to its low cost, Wi-Fi capabilities, and compatibility with the infrared modules needed for remote control.

- **Django Framework:** Django was chosen for its robustness, ease of development, and excellent support for handling tasks such as scheduling, database management, and MQTT integration.

---

## System Demo

Watch a complete demonstration of the Air Conditioning Management System in action:

[![Air Conditioning Management System Demo](https://img.youtube.com/vi/PDNEwkL1ijo/0.jpg)](https://www.youtube.com/watch?v=PDNEwkL1ijo)

The video showcases the system's main features, including:
- The web interface for controlling air conditioners
- Schedule management functionality
- Real-time control through MQTT
- ESP32 device responding to commands
- Energy consumption monitoring

This demonstration provides a practical view of how all components work together to create an effective air conditioning management solution.

---

## Running the Applications

### Django Project

#### Requirements

Before running the Django project, ensure you have all the required dependencies installed:

1. Install Python 3.8+

2. VSCode or PyCharm

3. RabbitMQ 

   - Windows:

      1. Install the Erlang version compatible with RabbitMQ

      2. Install RabbitMQ

      3. Add the RabbitMQ ````sbin```` folder to the system Path

      4. Enable the management plugin:

         ````
         rabbitmq-plugins enable rabbitmq_management
         ````

      5. Start the service:

         ````
         rabbitmq-service start
         ````

      6. Access the management panel:

         - ```http://localhost:15672```
         - User: guest
         - Password: guest
      
   - MacOS:

      1. Install RabbitMQ:

         ````
         brew install rabbitmq
         ````
      
      2. Add the path to your shell.

      3. Start RabbitMQ:

         ````
         brew services start rabbitmq
         ````

      4. Enable the management panel:

         ````
         rabbitmq-plugins enable rabbitmq_management
         ````

      5. Access the management panel:

         - ```http://localhost:15672```
         - User: guest
         - Password: guest

#### macOS

1. Clone the repository and navigate to your project folder:

   ```bash
   git clone https://github.com/HielSaraiva/project-air-conditioning-management-system.git
   ```
   ```bash
   cd air_conditioning_management_system/ac_mm_system
   ```

2. Set up a virtual enviroment:

   ```bash
   python3 -m venv .venv
   ```
   ```bash
   source .venv/bin/activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Important files to configure:

   1. ```hivemq-ca.pem:``` Create this file with the CA certificate for the HiveMQ MQTT broker:

      1. You can create this file following this guide: [HiveMQ TLS Certificate Guide](https://www.hivemq.com/blog/end-to-end-encryption-in-the-cloud/)

      2. Or you can use the standart tls certificate:

         1. Open the terminal (macOS) or PowerShell (Windows):

         2. Download the CA certificate from HiveMQ:

            - macOS/Linux

               ```
               curl -o hivemq-ca.pem https://letsencrypt.org/certs/isrgrootx1.pem
               ```
            
            - Windows (PowerShell)

               ```
               Invoke-WebRequest -Uri "https://letsencrypt.org/certs/isrgrootx1.pem" -OutFile "hivemq-ca.pem"
               ```

         3. Move the file to the correct folder:

            The file will be in the root folder of your computer, in the folder with your user name.

            ```
            mv hivemq-ca.pem /caminho/do/seu/projeto/ac_mm_system/certificates/
            ```


   2. ```secrets.json:```This file contains sensitive project data like API keys and MQTT credentials. The structure of the file should be as follows:

      ```json
      {
         "SECRET_KEY": "<your_django_secret_key>",
         "EMAIL_HOST_PASSWORD": "<your_google_email_external_app_password>",
         "EMAIL_HOST_USER": "<your_email_for_password_recovery>",
         "MQTT_BROKER_HOST": "<your_mqtt_broker_host>",
         "MQTT_PORT_TLS": <tls_port>,
         "MQTT_USERNAME_HIVE_MQ": "<your_hivemq_username>",
         "MQTT_PASSWORD_HIVE_MQ": "<your_hivemq_password>"
      }
      ```

   3. ```db.sqlite3:``` The database is created automatically when you ```run python manage.py migrate```.

5. Set up the database and run migrations:

   ```bash
   python manage.py migrate
   ```

6. To start the development server:

   ```bash
   python manage.py runserver
   ```

7. Visit ```http://localhost:8000``` in your browser to access the Django web interface.

8. Run Celery Worker: 

   ````
   celery -A ac_mm_system worker --pool=prefork --loglevel=INFO
   ````

   ````
   celery -A ac_mm_system worker --pool=threads --loglevel=info
   ````

   ````
   celery -A ac_mm_system worker --pool=solo --loglevel=info
   ````

9. Run Celery Beat: 

   ````
   celery -A ac_mm_system beat --loglevel=INFO
   ````

#### Windows

1. Clone the repository and navigate to your project folder:

   ```bash
   git clone https://github.com/HielSaraiva/project-air-conditioning-management-system.git
   ```
   ```bash
   cd air_conditioning_management_system/ac_mm_system
   ```

2. Set up a virtual enviroment:

   ```bash
   python -m venv .venv
   ```
   ```bash
   .venv\Scripts\Activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Important files to configure:

   1. ```hivemq-ca.pem:``` Create this file with the CA certificate for the HiveMQ MQTT broker:

      1. You can create this file following this guide: [HiveMQ TLS Certificate Guide](https://www.hivemq.com/blog/end-to-end-encryption-in-the-cloud/)

      2. Or you can use the standart tls certificate:

         1. Open the terminal (macOS) or PowerShell (Windows):

         2. Download the CA certificate from HiveMQ:

            - macOS/Linux

               ```
               curl -o hivemq-ca.pem https://letsencrypt.org/certs/isrgrootx1.pem
               ```
            
            - Windows (PowerShell)

               ```
               Invoke-WebRequest -Uri "https://letsencrypt.org/certs/isrgrootx1.pem" -OutFile "hivemq-ca.pem"
               ```

         3. Move the file to the correct folder:

            The file will be in the root folder of your computer, in the folder with your user name.

            ```
            mv hivemq-ca.pem /caminho/do/seu/projeto/ac_mm_system/certificates/
            ```


   2. ```secrets.json:```This file contains sensitive project data like API keys and MQTT credentials. The structure of the file should be as follows:

      ```json
      {
         "SECRET_KEY": "<your_django_secret_key>",
         "EMAIL_HOST_PASSWORD": "<your_google_email_external_app_password>",
         "EMAIL_HOST_USER": "<your_email_for_password_recovery>",
         "MQTT_BROKER_HOST": "<your_mqtt_broker_host>",
         "MQTT_PORT_TLS": <tls_port>,
         "MQTT_USERNAME_HIVE_MQ": "<your_hivemq_username>",
         "MQTT_PASSWORD_HIVE_MQ": "<your_hivemq_password>"
      }
      ```

   3. ```db.sqlite3:``` The database is created automatically when you ```run python manage.py migrate```.

5. Set up the database and run migrations:

   ```bash
   python manage.py migrate
   ```

6. To start the development server:

   ```bash
   python manage.py runserver
   ```

7. Visit ```http://localhost:8000``` in your browser to access the Django web interface.

8. Run Celery Worker: 

   ````
   celery -A ac_mm_system worker --pool=threads --loglevel=info
   ````

   ````
   celery -A ac_mm_system worker --pool=solo --loglevel=info
   ````

9. Run Celery Beat: 

   ````
   celery -A ac_mm_system beat --loglevel=INFO
   ````

### ESP32 Firmware

1. Install the Arduino IDE: [Arduino IDE Download](https://www.arduino.cc/en/software)

2. Follow the instructions in the official [ESP32 setup guide](https://docs.espressif.com/projects/arduino-esp32/en/latest/installing.html) to set up the ESP32 development environment on your computer.

3. Open the ESP32 firmware defined on esp32_project folder and write it to esp32.

4. Perform the necessary initial configurations via serial terminal.

---

## Final Considerations

This project demonstrates a practical application of embedded systems and web technologies to automate and optimize the operation of air conditioners in shared environments. By using the ESP32 microcontroller and MQTT for communication, the system is both flexible and scalable. The Django web application provides an intuitive interface for users to manage their air conditioners, track energy consumption, and contribute to energy savings and sustainability.

Future improvements may include:

🔹 **Data Persistence:** Implement monthly consumption data storage to allow comparative analysis between different time periods.

🔹 **Mobile Configuration App:** Develop a mobile application for initial ESP32 setup via Bluetooth connection, facilitating Wi-Fi network registration and MQTT topic configuration.

🔹 **System Expansion:** Extend the system to include other infrared-controllable electronic devices such as televisions and projectors.

🔹 **Production Deployment:** Deploy the web system in a production environment, enabling remote and continuous access to the platform, making the system even more efficient and adaptable.

This project is an excellent example of IoT (Internet of Things) applied to smart automation using Django and embedded systems. 🚀💡