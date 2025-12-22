# Release Notes - v1.0.0

## Features
- **Android Support**: First official release with full Android support.
- **Focus Mode**: App usage monitoring using native Android APIs (`UsageStatsManager`).
- **App Blocking**: Automatically triggers focus mode when blocked apps (Instagram, Facebook, etc.) are used.
- **Permissions**: properly configured permissions for usage access and overlay windows.

## Automation
- **GitHub Actions**: Automated APK building and releasing.
- **Release Trigger**: Pushing a tag starting with `v` (e.g., `v1.0.0`) automatically builds and uploads the APK.

## Usage
1. Install the APK.
2. Grant "Usage Access" and "Display over other apps" permissions when prompted.
3. The app will monitor usage of blocked apps and intervene to help you stay focused.
