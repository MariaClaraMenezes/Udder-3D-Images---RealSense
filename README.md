
1. Clone repository (only necessary if this project was uploaded to github)

2. Create virtual environment
   ```bash
   python3.11 -m venv venv
   ```
   ```bash
   venv\Scripts\activate
   ```

3. Install requirements

    ```bash
    python.exe -m pip install --upgrade pip
    python.exe -m pip install -r requirements.txt
    ```

### Step-by-step (short)

1. Configure and run `rename_reallocate_bag.py` to reduce errors due folder/filename heterogeneity;
2. EXECUTE `get_frames.py`to extract color_images (.png) and depth_images (.tif) - NO CHANGES NEEDED; 
3. Configure and run `udder_frame_class.py` to label extracted frames - it can be done only a few images at the time;