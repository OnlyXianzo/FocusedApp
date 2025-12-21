#!/usr/bin/env python3
"""
Focus Mode App - Main Application
A Kivy-based app that helps students stay focused by monitoring app usage
and triggering focus mode when necessary.
"""

import os
import sys
import threading
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.clock import Clock
from kivy.config import Config
from kivy.logger import Logger

# Import our custom screens
from screens.home_screen import HomeScreen
from screens.focus_mode import FocusModeScreen
from screens.unlock_input import UnlockInputScreen

# Import utilities
from utils.app_usage_checker import AppUsageChecker
from utils.telegram_bot import telegram_bot
from background_service import BackgroundService

__version__ = "1.0.0"

# Configure Kivy settings
Config.set('graphics', 'resizable', False)
Config.set('graphics', 'width', '360')
Config.set('graphics', 'height', '640')

class FocusApp(App):
    """
    Main application class for the Focus Mode App
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = "Focus Mode App"
        self.screen_manager = None
        self.background_service = None
        self.app_usage_checker = None
        
    def build(self):
        """
        Build the main application UI
        """
        # Create screen manager
        self.screen_manager = ScreenManager()
        
        # Create and add screens
        home_screen = HomeScreen(name='home')
        focus_screen = FocusModeScreen(name='focus_mode')
        unlock_screen = UnlockInputScreen(name='unlock')
        
        self.screen_manager.add_widget(home_screen)
        self.screen_manager.add_widget(focus_screen)
        self.screen_manager.add_widget(unlock_screen)
        
        # Set initial screen
        self.screen_manager.current = 'home'
        
        # Initialize background services
        self.initialize_background_services()
        
        Logger.info("FocusApp: Application built successfully")
        return self.screen_manager
    
    def initialize_background_services(self):
        """
        Initialize background services for app monitoring
        """
        try:
            # Initialize app usage checker
            self.app_usage_checker = AppUsageChecker()
            
            # Initialize background service
            self.background_service = BackgroundService(
                app_usage_checker=self.app_usage_checker,
                screen_manager=self.screen_manager
            )
            
            # Start background monitoring
            self.start_background_monitoring()
            
            Logger.info("FocusApp: Background services initialized")
            
        except Exception as e:
            Logger.error(f"FocusApp: Error initializing background services: {e}")
    
    def start_background_monitoring(self):
        """
        Start background monitoring in a separate thread
        """
        def monitor_thread():
            try:
                self.background_service.start_monitoring()
            except Exception as e:
                Logger.error(f"FocusApp: Error in background monitoring: {e}")
        
        # Start monitoring thread
        monitor_thread = threading.Thread(target=monitor_thread, daemon=True)
        monitor_thread.start()
        
        Logger.info("FocusApp: Background monitoring started")
    
    def trigger_focus_mode(self, manual=False):
        """
        Trigger focus mode from external sources
        """
        try:
            if self.screen_manager:
                self.screen_manager.current = 'focus_mode'
                focus_screen = self.screen_manager.get_screen('focus_mode')
                focus_screen.start_focus_session(manual=manual)
                Logger.info(f"FocusApp: Focus mode triggered (manual={manual})")
        except Exception as e:
            Logger.error(f"FocusApp: Error triggering focus mode: {e}")
    
    def emergency_unlock(self):
        """
        Emergency unlock function
        """
        try:
            if self.screen_manager:
                focus_screen = self.screen_manager.get_screen('focus_mode')
                if focus_screen.timer.is_running:
                    focus_screen.emergency_unlock()
                    Logger.info("FocusApp: Emergency unlock activated")
        except Exception as e:
            Logger.error(f"FocusApp: Error in emergency unlock: {e}")
    
    def on_start(self):
        """
        Called when the app starts
        """
        Logger.info("FocusApp: Application started")
        
        # Schedule periodic checks
        Clock.schedule_interval(self.periodic_check, 60.0)  # Check every minute
    
    def periodic_check(self, dt):
        """
        Periodic check for app status
        """
        try:
            # This can be used for periodic maintenance tasks
            pass
        except Exception as e:
            Logger.error(f"FocusApp: Error in periodic check: {e}")
    
    def on_stop(self):
        """
        Called when the app stops
        """
        Logger.info("FocusApp: Application stopping")
        
        # Clean up background services
        if self.background_service:
            self.background_service.stop_monitoring()
        
        # Clean up app usage checker
        if self.app_usage_checker:
            self.app_usage_checker.stop_monitoring()
    
    def on_pause(self):
        """
        Called when the app is paused (Android)
        """
        Logger.info("FocusApp: Application paused")
        return True  # Return True to allow pause
    
    def on_resume(self):
        """
        Called when the app resumes from pause (Android)
        """
        Logger.info("FocusApp: Application resumed")


def main():
    """
    Main entry point for the application
    """
    try:
        # Create and run the app
        app = FocusApp()
        app.run()
    except Exception as e:
        Logger.error(f"FocusApp: Fatal error: {e}")
        print(f"Error starting application: {e}")
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
