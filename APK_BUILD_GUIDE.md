# Trmex AI Assistant - APK Build Guide

## Prerequisites

Before building the APK, ensure you have:

1. **Flutter SDK**: Download from https://flutter.dev/docs/get-started/install
2. **Android SDK**: Installed via Android Studio
3. **JDK 17+**: For Android compilation
4. **Git**: For version control

## Environment Setup

### 1. Verify Flutter Installation
```bash
flutter --version
flutter doctor
```

### 2. Clone and Navigate to Project
```bash
git clone https://github.com/pharmacistsunilrinwa-bot/Trmex-1.git
cd Trmex-1/frontend
```

### 3. Install Dependencies
```bash
flutter pub get
```

## Building the APK

### Option 1: Debug APK (Development)
Build a debug APK quickly for testing:

```bash
flutter build apk --debug
```

**Output**: `build/app/outputs/flutter-apk/app-debug.apk`

### Option 2: Release APK (Production)
Build an optimized release APK for distribution:

```bash
flutter build apk --release
```

**Output**: `build/app/outputs/flutter-apk/app-release.apk`

### Option 3: Split APKs (Smaller Download Size)
Build split APKs for different architectures:

```bash
flutter build apk --split-per-abi --release
```

**Output**: 
- `app-armeabi-v7a-release.apk` (32-bit)
- `app-arm64-v8a-release.apk` (64-bit)

### Option 4: App Bundle (Google Play Store)
Build an app bundle for Play Store distribution:

```bash
flutter build appbundle --release
```

**Output**: `build/app/outputs/bundle/release/app-release.aab`

## Signing the Release APK

For production releases, you need to sign the APK with a keystore:

### Create a Keystore (First Time Only)
```bash
keytool -genkey -v -keystore ~/my-release-key.keystore \
  -keyalg RSA -keysize 2048 -validity 10000 -alias my-key-alias
```

### Configure Signing in Android Studio or Gradle

Edit `android/key.properties`:
```properties
storeFile=/path/to/my-release-key.keystore
storePassword=your_store_password
keyPassword=your_key_password
keyAlias=my-key-alias
```

Then build with:
```bash
flutter build apk --release
```

## App Configuration

### Update API Endpoint
Edit `frontend/lib/main.dart` line 41:
```dart
final String _baseUrl = "YOUR_NGROK_URL"; // Replace with your backend URL
```

### Backend URL Examples
- **Local Development**: `http://192.168.1.100:8000` (replace with your IP)
- **Ngrok Tunnel**: `https://your-ngrok-url.ngrok.io`
- **Production Server**: `https://your-domain.com`

## Installation on Device/Emulator

### Install Debug APK
```bash
flutter install
```
or
```bash
adb install build/app/outputs/flutter-apk/app-debug.apk
```

### Install Release APK
```bash
adb install build/app/outputs/flutter-apk/app-release.apk
```

## Testing

### Run on Emulator
```bash
flutter emulators --launch Pixel_4_API_30
flutter run
```

### Run on Physical Device
```bash
# Connect device via USB
adb devices
flutter run
```

## Build Troubleshooting

### Clear Build Cache
```bash
flutter clean
flutter pub get
cd android
./gradlew clean
cd ..
```

### Gradle Build Issues
```bash
cd android
./gradlew build --stacktrace
cd ..
```

### Permission Issues
```bash
flutter build apk --release --verbose
```

## APK Specifications

- **Min SDK**: Android 5.0 (API 21)
- **Target SDK**: Android 14 (API 34)
- **Architecture**: ARM64-v8a, ARMv7
- **Size**: ~50-100MB (varies with features)

## Permissions Included

- `INTERNET` - Backend API communication
- `RECORD_AUDIO` - Voice-to-text feature
- `READ_EXTERNAL_STORAGE` - Access uploaded files
- `WRITE_EXTERNAL_STORAGE` - Save analysis reports
- `ACCESS_NETWORK_STATE` - Network monitoring

## Play Store Upload Checklist

- [ ] Create Google Play Developer Account
- [ ] Create app listing
- [ ] Generate signing key
- [ ] Build App Bundle (AAB format)
- [ ] Add screenshots and descriptions
- [ ] Set pricing and distribution
- [ ] Submit for review

## Post-Build Verification

Verify the APK integrity:
```bash
# Check APK contents
unzip -l build/app/outputs/flutter-apk/app-release.apk | head -20

# Get APK info
aapt dump badging build/app/outputs/flutter-apk/app-release.apk
```

## Support & Resources

- Flutter Documentation: https://flutter.dev/docs
- Android Development: https://developer.android.com
- Issue Tracker: https://github.com/flutter/flutter/issues

## Next Steps

1. ✅ Ensure backend is running (FastAPI server)
2. ✅ Update API endpoint in main.dart
3. ✅ Build and test on emulator
4. ✅ Install on physical device
5. ✅ Configure for production deployment
