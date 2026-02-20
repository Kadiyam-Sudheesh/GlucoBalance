import os
import requests

def download_image(url, filename):
    try:
        response = requests.get(url)
        response.raise_for_status()
        with open(filename, 'wb') as f:
            f.write(response.content)
        print(f"Downloaded {filename}")
    except Exception as e:
        print(f"Failed to download {filename}: {e}")

if __name__ == "__main__":
    os.makedirs("static/images", exist_ok=True)
    
    # Hero Image - Man checking glucose (Diabetes context)
    print("Downloading Hero Image (Glucose Check)...")
    download_image("https://images.unsplash.com/photo-1579684385127-1ef15d508118?q=80&w=2000&auto=format&fit=crop", "static/images/hero_image.png")
    
    # Feature Image - For lower section (keep existing or update? Let's keep distinct)
    download_image("https://images.unsplash.com/photo-1490645935967-10de6ba17061?q=80&w=2053&auto=format&fit=crop", "static/images/feature_image.png")

    # Slideshow Images (Matching User Request)
    print("Downloading Slideshow Images...")
    
    # 1. Veggie Platter / Healthy Snack
    download_image("https://images.unsplash.com/photo-1623428187969-5da2dcea5ebf?q=80&w=1000&auto=format&fit=crop", "static/images/slide1.jpg") 
    
    # 2. Oatmeal / Healthy Breakfast
    download_image("https://images.unsplash.com/photo-1517093720228-2748374240ac?q=80&w=1000&auto=format&fit=crop", "static/images/slide2.jpg") 
    
    # 3. Woman Walking / Active Lifestyle
    download_image("https://images.unsplash.com/photo-1518609878373-06d740f60d8b?q=80&w=1000&auto=format&fit=crop", "static/images/slide3.jpg")
    
    # 4. Drinking Water / Hydration (User Requested 5th Image)
    print("Downloading 5th Image (Hydration)...")
    download_image("https://images.unsplash.com/photo-1548839140-29a749e1cf4d?q=80&w=1000&auto=format&fit=crop", "static/images/slide4.jpg")
