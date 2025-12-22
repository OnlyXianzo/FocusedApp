from plyer import notification
from config import BLOCKED_APPS
import time
import threading
from kivy.logger import Logger
from kivy.utils import platform

if platform == 'android':
    try:
        from jnius import autoclass
        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        Context = autoclass('android.content.Context')
        UsageStatsManager = autoclass('android.app.usage.UsageStatsManager')
        System = autoclass('java.lang.System')
        AppOpsManager = autoclass('android.app.AppOpsManager')
        Process = autoclass('android.os.Process')
        Intent = autoclass('android.content.Intent')
        Settings = autoclass('android.provider.Settings')
        Uri = autoclass('android.net.Uri')
    except ImportError:
        Logger.error("AppUsageChecker: jnius not found, Android specific features disabled")
else:
    import psutil

class AppUsageChecker:
    def __init__(self):
        self.focus_mode_running = False
        self.is_monitoring = False
        self.monitoring_thread = None
        self.usage_stats_manager = None

        if platform == 'android':
            self._init_android()

    def _init_android(self):
        try:
            activity = PythonActivity.mActivity
            self.usage_stats_manager = activity.getSystemService(Context.USAGE_STATS_SERVICE)
        except Exception as e:
            Logger.error(f"AppUsageChecker: Error initializing Android services: {e}")

    def check_permission(self):
        """Check if PACKAGE_USAGE_STATS permission is granted"""
        if platform == 'android':
            try:
                activity = PythonActivity.mActivity
                app_ops = activity.getSystemService(Context.APP_OPS_SERVICE)
                mode = app_ops.checkOpNoThrow(
                    AppOpsManager.OPSTR_GET_USAGE_STATS,
                    Process.myUid(),
                    activity.getPackageName()
                )
                return mode == AppOpsManager.MODE_ALLOWED
            except Exception as e:
                Logger.error(f"AppUsageChecker: Error checking permission: {e}")
                return False
        return True

    def request_permission(self):
        """Open settings to grant permission"""
        if platform == 'android':
            try:
                activity = PythonActivity.mActivity
                intent = Intent(Settings.ACTION_USAGE_ACCESS_SETTINGS)
                # Ideally we would check if we can direct to our package
                # uri = Uri.fromParts("package", activity.getPackageName(), None)
                # intent.setData(uri)
                # Note: ACTION_USAGE_ACCESS_SETTINGS doesn't always support package data
                activity.startActivity(intent)
            except Exception as e:
                Logger.error(f"AppUsageChecker: Error requesting permission: {e}")

    def check_app_usage(self):
        """Legacy method for continuous monitoring"""
        while self.is_monitoring:
            blocked = self.get_blocked_apps_running()
            if blocked:
                if not self.focus_mode_running:
                    self.start_focus_mode()
            time.sleep(60)  # Check every minute

    def get_blocked_apps_running(self):
        """Get list of currently running blocked apps"""
        if platform == 'android':
            return self._get_android_blocked_apps()
        else:
            return self._get_desktop_blocked_apps()

    def _get_desktop_blocked_apps(self):
        try:
            running_blocked_apps = []
            
            for process in psutil.process_iter(['pid', 'name']):
                try:
                    process_name = process.info['name'].lower()
                    
                    # Check if this process matches any blocked app
                    for app in BLOCKED_APPS:
                        # Assuming BLOCKED_APPS contains names or substrings to match
                        if isinstance(app, dict):
                            app_name = app.get('name', '').lower()
                            package_name = app.get('package_name', '').lower()
                            if (app_name and app_name in process_name) or (package_name and package_name in process_name):
                                running_blocked_apps.append(app.get('name', process_name))
                        elif isinstance(app, str):
                             if app.lower() in process_name:
                                running_blocked_apps.append(app)

                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
                    
            return list(set(running_blocked_apps))
            
        except Exception as e:
            Logger.error(f"AppUsageChecker: Error getting blocked apps (Desktop): {e}")
            return []

    def _get_android_blocked_apps(self):
        """Check usage stats for blocked apps on Android"""
        try:
            if not self.usage_stats_manager:
                return []

            end_time = System.currentTimeMillis()
            start_time = end_time - (1000 * 60 * 2) # Look back 2 minutes

            # Query usage stats
            stats = self.usage_stats_manager.queryUsageStats(
                UsageStatsManager.INTERVAL_DAILY, start_time, end_time
            )

            if not stats:
                Logger.warning("AppUsageChecker: No usage stats available. Permission might be missing.")
                return []

            running_blocked_apps = []

            # Convert Java list to Python
            stats_list = stats.toArray()

            for usage_stat in stats_list:
                package_name = usage_stat.getPackageName()
                last_time_used = usage_stat.getLastTimeUsed()

                # Check if used in the last minute
                if (end_time - last_time_used) < (1000 * 60):
                    # Check if it's a blocked app
                    for app in BLOCKED_APPS:
                         # Handle both dict (from blocked_apps.json) and str (if any)
                        if isinstance(app, dict):
                             target_package = app.get('package_name', '')
                             if target_package and target_package == package_name:
                                 running_blocked_apps.append(app.get('name', package_name))
                        elif isinstance(app, str):
                            if app in package_name:
                                running_blocked_apps.append(app)

            return list(set(running_blocked_apps))

        except Exception as e:
            Logger.error(f"AppUsageChecker: Error getting blocked apps (Android): {e}")
            return []

    def start_monitoring(self):
        """Start monitoring in background thread"""
        if self.is_monitoring:
            return
            
        self.is_monitoring = True
        self.monitoring_thread = threading.Thread(target=self.check_app_usage, daemon=True)
        self.monitoring_thread.start()
        Logger.info("AppUsageChecker: Started monitoring")

    def stop_monitoring(self):
        """Stop monitoring"""
        self.is_monitoring = False
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            self.monitoring_thread.join(timeout=2.0)
        Logger.info("AppUsageChecker: Stopped monitoring")

    def start_focus_mode(self):
        self.focus_mode_running = True
        notification.notify(title="Focus Mode Started", message="Distraction detected. Focus Mode started.")
        # Further logic to start focus mode is handled by BackgroundService usually

    def end_focus_mode(self):
        self.focus_mode_running = False
        notification.notify(title="Focus Mode Ended", message="Focus session completed. Meet you next time!")
