# SPDX-License-Identifier: MIT

# Copyright (c) 2025 Maxim Strekolovskiy

"""

Launcher for the Website Analyzer desktop application.

It performs a minimal dependency check and then starts the GUI app.

"""

import importlib.util
import os
import subprocess
import sys


def check_dependencies():
    """Check required dependencies."""
    required_packages = [
        "tkinter",
        "requests",
        "json",
        "threading",
        "datetime",
        "webbrowser",
    ]
    missing_packages = []
    for package in required_packages:
        if package == "tkinter":
            # tkinter is part of the Python standard library
            try:
                import tkinter
            except ImportError:
                missing_packages.append("tkinter")
        else:
            spec = importlib.util.find_spec(package)
            if spec is None:
                missing_packages.append(package)
    return missing_packages


def install_missing_packages(packages):
    """Install missing packages via pip."""
    for package in packages:
        if package == "tkinter":
            print(
                "tkinter must be installed with Python. Please verify your Python installation."
            )
            return False
        try:
            print(f"Installing {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"{package} installed successfully.")
        except subprocess.CalledProcessError:
            print(f"Failed to install {package}")
            return False
    return True


def check_services():
    """Check availability of microservices."""
    import requests

    from .settings import settings

    services = [
        ("SEO Analysis", settings.SEO_SERVICE_PORT),
        ("Text Analysis", settings.TEXT_SERVICE_PORT),
        ("Convenience Analysis", settings.CONVENIENCE_SERVICE_PORT),
        ("Senior Analysis", settings.SENIOR_SERVICE_PORT),
    ]
    available_services = []
    for service_name, port in services:
        try:
            response = requests.get(f"http://localhost:{port}/", timeout=2)
            if response.status_code == 200:
                available_services.append(service_name)
                print(f"[OK] {service_name} is available on port {port}")
            else:
                print(f"[X] {service_name} is unavailable on port {port}")
        except Exception:
            print(f"[X] {service_name} is unavailable on port {port}")
    return available_services


def main():
    """Main entrypoint."""
    print("=" * 60)
    print("Website Analyzer - Desktop Application")
    print("=" * 60)
    # Check Python version
    if sys.version_info < (3, 7):
        print("Error: Python 3.7+ is required")
        sys.exit(1)
    print(f"Python version: {sys.version}")
    # Check dependencies
    print("\nChecking dependencies...")
    missing_packages = check_dependencies()
    if missing_packages:
        print(f"Missing packages: {', '.join(missing_packages)}")
        response = input("Install missing packages? (y/n): ")
        if response.lower() in ["y", "yes"]:
            if not install_missing_packages(missing_packages):
                print("Package installation failed. Exiting.")
                sys.exit(1)
        else:
            print("Install the missing packages manually and run the app again.")
            sys.exit(1)
    else:
        print("All dependencies are installed.")
    # Check microservices
    print("\nChecking microservices...")
    available_services = check_services()
    if len(available_services) < 4:
        print(
            f"\nWarning: only {len(available_services)} out of 4 microservices are available."
        )
        print("For full functionality, start all microservices via Docker Compose.")
        response = input("Continue launching the desktop app? (y/n): ")
        if response.lower() not in ["y", "yes"]:
            sys.exit(0)
    # Launch app
    print("\nLaunching desktop application...")
    try:
        from desktop_app import main as run_app

        run_app()
    except ImportError as e:
        print(f"Import error: {e}")
        print("Make sure desktop_app.py is in the same directory.")
        sys.exit(1)
    except Exception as e:
        print(f"Failed to launch application: {e}")
        sys.exit(1)


if __name__ == "__main__":

    main()
