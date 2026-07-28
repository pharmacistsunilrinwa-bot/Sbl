# 🚀 Trmex APK Build - Quick Reference

## One-Command Build

```bash
cd Trmex-1 && chmod +x BUILD_APK.sh && ./BUILD_APK.sh
```

---

## Build Commands

| Command | Output | Size | Time |
|---------|--------|------|------|
| `flutter build apk --debug` | `app-debug.apk` | ~70MB | ~2 min |
| `flutter build apk --release` | `app-release.apk` | ~50MB | ~3 min |
| `flutter build apk --split-per-abi --release` | `app-*-release.apk` | ~30MB each | ~3 min |
| `flutter build appbundle --release` | `app-release.aab` | ~20MB | ~3 min |

---

## Installation

```bash
# Physical Device
adb install -r build/app/outputs/flutter-apk/app-release.apk

# Emulator
flutter run
```

---

## Configuration Checklist

- [ ] Backend URL updated in `lib/main.dart` (line 41)
- [ ] Backend server running: `python backend/main.py`
- [ ] Flutter dependencies installed: `flutter pub get`
- [ ] Android SDK updated
- [ ] JDK 17+ installed

---

## Key Files Modified

✅ `backend/services/analysis_service.py` - Fixed JSON serialization  
✅ `frontend/android/app/build.gradle.kts` - Build configuration  
✅ `frontend/android/app/src/main/AndroidManifest.xml` - Permissions  
✅ `frontend/pubspec.yaml` - Dependencies documented  
✅ `frontend/android/gradle.properties` - Build optimization  

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Build fails | `flutter clean && flutter pub get && flutter build apk --release` |
| Permission denied | `chmod +x BUILD_APK.sh` |
| Gradle error | `export GRADLE_OPTS="-Xmx4g"` |
| Backend not found | Check backend URL in `lib/main.dart` |

---

## Documentation

📖 **Full Guide**: `SETUP_AND_DEPLOYMENT.md`  
📖 **Build Details**: `APK_BUILD_GUIDE.md`  
📖 **Automated Script**: `BUILD_APK.sh`

---

## App Specs

- **Min SDK**: Android 5.0 (API 21)
- **Target SDK**: Android 14 (API 34)
- **Package**: `com.trmex.personal_ai_assistant`
- **Size**: 30-70MB (varies by build type)

---

## Support

Backend URL template for `lib/main.dart`:
- Local: `http://192.168.X.X:8000`
- Production: `https://your-domain.com`
- Ngrok: `https://your-ngrok-url.ngrok.io`

Verify connection:
```bash
curl http://your-backend-url/docs
```

---

**Status**: ✅ Ready to build and deploy!
