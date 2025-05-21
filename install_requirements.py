"""
Installation script for required packages
Run this script to install all necessary dependencies
"""

import subprocess
import sys

def install_package(package):
    """Install a package using pip."""
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

def main():
    print("Installing required packages for article summarization...")
    
    # List of required packages
    packages = [
        "requests",
        "beautifulsoup4",
        "nltk",
        "newspaper3k",
        "tqdm",
        "numpy"
    ]
    
    # Optional transformer-based summarization (resource-intensive)
    transformer_packages = [
        "transformers", 
        "torch"
    ]
    
    # Install base packages
    for package in packages:
        print(f"Installing {package}...")
        try:
            install_package(package)
            print(f"✓ {package} installed successfully")
        except Exception as e:
            print(f"✗ Failed to install {package}: {e}")
    
    # Ask if user wants to install transformer-based summarization
    install_transformers = input(
        "\nDo you want to install transformer-based summarization? " 
        "This provides better quality summaries but requires more computational resources. (y/n): "
    )
    
    if install_transformers.lower() == 'y':
        print("\nInstalling transformer packages (this may take a while)...")
        for package in transformer_packages:
            print(f"Installing {package}...")
            try:
                install_package(package)
                print(f"✓ {package} installed successfully")
            except Exception as e:
                print(f"✗ Failed to install {package}: {e}")
        print("\nTransformer packages installed. You can use either summarization method.")
    else:
        print("\nSkipping transformer packages. You'll be using the lightweight summarization method.")
    
    print("\nInstallation complete. You can now run the news extraction script.")

if __name__ == "__main__":
    main()