# FCM Push Sender

A desktop application to send Firebase Cloud Messaging (FCM) push notifications directly from your computer, available in two versions: **Python (PyQt6)** or **B4J (JavaFX)**.

<img width="1089" height="802" alt="image" src="https://github.com/user-attachments/assets/f6685e7a-5d92-448c-a146-e35ea351b516" />


## Features

- Send push notifications via Firebase Cloud Messaging (FCM v1 API)
- Support for **Android** and **iOS** platforms
- Configure Android priority (high / normal)
- Set iOS badge value (0-5)
- Toggle alert sound on/off
- Reset badge on iOS device (silent background notification)
- View the exact JSON payload sent to FCM in real time
- Multiple apps with individual Firebase credentials

## Requirements

### Python Version

- Python 3.10+
- PyQt6, google-auth, requests

```bash
pip install -r Python/requirements.txt
```

### B4J Version

- [B4J](https://www.b4x.com) (free)
- Java 8+
- Required JARs listed in `PushNotification.b4j`

## Setup

1. **Create a Firebase project** at [console.firebase.google.com](https://console.firebase.google.com/)
2. **Get service account credentials**: Project Settings > Service Accounts > Generate New Private Key
3. **Configure the apps** in the source code:

**Python** (`Python/pushnotification.py`):

```python
APPS = [
    {"name": "Android - MyApp", "platform": "Android",
     "project": "your-project-id", "key_path": "/path/to/key.json"},
    {"name": "iOS - MyApp", "platform": "iOS",
     "project": "your-project-id", "key_path": "/path/to/key.json"},
]
```

**B4J** (`PushNotification.b4j`):

```vb
Sub SetupConfigs
    AddApp("Android - MyApp", "Android", "your-project-id", "/path/to/key.json")
    AddApp("iOS - MyApp", "iOS", "your-project-id", "/path/to/key.json")
End Sub

Private Sub AddApp (Name As String, Platform As String, Project As String, ServiceKey As String)
    AppNames.Add(Name)
    Platforms.Add(Platform)
    ProjectIds.Add(Project)
    ServiceAccountPaths.Add(ServiceKey)
End Sub
```

## Usage

Run the Python version:

```bash
python Python/pushnotification.py
```

Or open `PushNotification.b4j` in B4J and press **F5**.

1. Select the **App**
2. Enter **Topic** (default: `teste12345`), **Title**, and **Message**
3. Adjust Android Priority, iOS Badge, and Sound
4. Click **Send notification**
5. Check the status and JSON payload preview

For iOS, the `ios_` prefix is added automatically to the topic.

## Compile Python Executable

```bash
pip install pyinstaller
cd Build
pyinstaller --onefile --noconsole pushnotification.py --name PushNotification
```

## Project Structure

```
PushNotification.b4j       # B4J project
PushNotification.b4j.meta
Files/MainPage.bjl         # B4J form layout
Python/pushnotification.py  # Python implementation
Python/requirements.txt     # Python dependencies
.gitignore
README.md
```

## License

Unlicense
