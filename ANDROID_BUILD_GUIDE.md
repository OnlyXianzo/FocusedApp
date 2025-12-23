# Android Build and Debug Guide

## Prerequisites

### For Windows Users:
**Note**: Building Android APKs on Windows is complex and often problematic. Consider using WSL2 or a Linux VM.

### Option 1: Using WSL2 (Recommended)
1. Install WSL2 with Ubuntu
2. Install the project in WSL2
3. Follow the Linux build instructions

### Option 2: Using Linux VM
1. Set up a Linux VM (Ubuntu 20.04+ recommended)
2. Copy the project to the VM
3. Follow the Linux build instructions

### Option 3: Using GitHub Actions (Easiest)
1. Push your code to GitHub
2. Use GitHub Actions to build the APK
3. Download the built APK

## Linux Build Process

### Step 1: Install Dependencies
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and pip
sudo apt install python3 python3-pip python3-dev -y

# Install build tools
sudo apt install git unzip default-jdk -y

# Install buildozer
pip3 install buildozer
```

### Step 2: Compatibility Patches (Critical for Python 3.11+)

The project uses `pyjnius` and `kivy` which have compatibility issues with Python 3.11 due to the removal of the `long` type. Our build config expects local patched versions.

#### Patch Pyjnius

1. Clone `pyjnius` into the project root:
   ```bash
   git clone https://github.com/kivy/pyjnius.git
   ```

2. Patch the source code:
   ```bash
   # Replace 'long' with 'int' in the utility file
   sed -i 's/\blong\b/int/g' pyjnius/jnius/jnius_utils.pxi
   ```

3. Ensure `buildozer.spec` points to it (already configured):
   ```ini
   requirements.source.pyjnius = ./pyjnius
   ```

#### Patch Kivy

1. Clone `kivy` (version 2.3.0) into the project root:
   ```bash
   git clone --depth 1 --branch 2.3.0 https://github.com/kivy/kivy.git
   ```

2. Patch the `weakproxy.pyx` file:
   ```bash
   # Replace 'return long(' with 'return int('
   sed -i 's/return long(/return int(/g' kivy/kivy/weakproxy.pyx
   ```

3. Ensure `buildozer.spec` points to it:
   ```ini
   requirements.source.kivy = ./kivy
   ```

### Step 3: Build Debug APK
```bash
# Navigate to project directory
cd FocusedApp

# Build debug APK (first time will take 30-60 minutes)
buildozer android debug
```

### Step 4: Build Release APK
```bash
# Build release APK
buildozer android release

# Sign the APK (optional, for distribution)
# You'll need to create a keystore first
```

## Testing on Android

### Method 1: Physical Device
1. Enable Developer Options on your Android device
2. Enable USB Debugging
3. Connect device to computer
4. Install APK: `adb install bin/focusapp-1.0.0-debug.apk`

### Method 2: Android Emulator
1. Install Android Studio
2. Create an AVD (Android Virtual Device)
3. Start emulator
4. Install APK: `adb install bin/focusapp-1.0.0-debug.apk`

## Debugging

### View Logs
```bash
# View all logs
adb logcat

# View Python logs only
adb logcat | grep python

# View app-specific logs
adb logcat | grep focusapp
```

### Common Issues and Solutions

#### 1. Build Fails - Missing Dependencies
```bash
# Install missing system dependencies
sudo apt install python3-dev libffi-dev libssl-dev
```

#### 2. Build Fails - Java Issues
```bash
# Set JAVA_HOME (Java 17 recommended for API 33+)
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
```

#### 3. Pyjnius Compilation Error
If you see `undeclared name not builtin: long`, ensure you have performed **Step 2: Pyjnius Compatibility Patch** correctly.

#### 4. App Usage Monitoring Not Working
- Grant "Usage Access" permission manually in Settings if not prompted.
- Check logs for permission denial errors.

### Android-Specific Modifications

The app automatically detects Android and uses `UsageStatsManager` to monitor apps.

#### 1. Permissions
The app requests permissions automatically. If monitoring fails, check `Settings > Apps > Special App Access > Usage Access` and ensure Focus Mode App is allowed.

## File Structure After Build
```text
FocusedApp/
├── .buildozer/          # Build cache
├── bin/                 # Built APK files
│   ├── focusapp-1.0.0-debug.apk
│   └── focusapp-1.0.0-release.apk (if built)
├── buildozer.spec       # Build configuration
└── [project files]
```

## Performance Tips

1. **First Build**: Takes 30-60 minutes (downloads Android SDK/NDK)
2. **Subsequent Builds**: 5-15 minutes
3. **Clean Build**: `buildozer android clean` then rebuild
4. **Faster Builds**: Use `buildozer android debug` instead of release

## Troubleshooting

### Build Errors
1. Check `buildozer.spec` configuration
2. Verify all requirements are spelled correctly
3. Clean build cache: `buildozer android clean`
4. Update buildozer: `pip3 install --upgrade buildozer`

### Runtime Errors
1. Check Android logs: `adb logcat`
2. Test on different Android versions
3. Verify permissions are granted
4. Check if all Python packages work on Android

## Testing Checklist

- [ ] App installs without errors
- [ ] App starts and shows home screen
- [ ] Manual focus mode works
- [ ] Timer counts down properly
- [ ] Emergency unlock works
- [ ] App permissions are requested
- [ ] Background monitoring works (if supported)
- [ ] App doesn't crash on different screens
- [ ] UI scales properly on different devices
