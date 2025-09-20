"""
Airline Dashboard Launcher
========================

This script helps you launch the airline analytics dashboard with proper setup.
"""

import subprocess
import sys
import os
from pathlib import Path

def check_file_exists(filename):
    """Check if required data file exists"""
    if not os.path.exists(filename):
        print(f"❌ Error: {filename} not found!")
        print(f"💡 Please ensure '{filename}' is in the current directory:")
        print(f"   Current directory: {os.getcwd()}")
        return False
    return True

def install_requirements():
    """Install required packages"""
    print("🔧 Installing required packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements_advanced.txt"])
        print("✅ Packages installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing packages: {e}")
        print("💡 Try installing manually with: pip install streamlit pandas matplotlib seaborn plotly")
        return False
    except FileNotFoundError:
        print("⚠️ requirements_advanced.txt not found, installing core packages...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", 
                                 "streamlit", "pandas", "matplotlib", "seaborn", "plotly", "scipy", "scikit-learn"])
            print("✅ Core packages installed!")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Error installing core packages: {e}")
            return False

def launch_dashboard():
    """Launch the Streamlit dashboard"""
    print("🚀 Launching Airline Analytics Dashboard...")
    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", "advanced_airline_dashboard.py"])
    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped by user")
    except Exception as e:
        print(f"❌ Error launching dashboard: {e}")

def main():
    """Main launcher function"""
    print("✈️ Airline Experience Analytics Dashboard Launcher")
    print("=" * 50)
    
    # Check if data file exists
    if not check_file_exists("Airline Review.csv"):
        print("\n📋 Next steps:")
        print("1. Place 'Airline Review.csv' in this directory")
        print("2. Run this launcher again")
        return
    
    # Check if dashboard file exists
    if not check_file_exists("advanced_airline_dashboard.py"):
        print("❌ Dashboard file not found!")
        return
    
    print("✅ Data file found!")
    
    # Ask if user wants to install requirements
    install_deps = input("\n🔧 Install/update required packages? (y/n): ").lower().strip()
    if install_deps in ['y', 'yes']:
        if not install_requirements():
            print("⚠️ Continuing without package installation...")
    
    # Launch dashboard
    print(f"\n📊 Found {check_csv_rows()} reviews in dataset")
    launch_input = input("🚀 Launch dashboard? (y/n): ").lower().strip()
    if launch_input in ['y', 'yes']:
        launch_dashboard()
    else:
        print("👋 Dashboard launch cancelled")

def check_csv_rows():
    """Quick check of CSV file size"""
    try:
        import pandas as pd
        df = pd.read_csv("Airline Review.csv")
        return len(df)
    except:
        return "unknown number of"

if __name__ == "__main__":
    main()