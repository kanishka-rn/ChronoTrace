import os
import shutil
from video_downloader import download_video

def cleanup():
    if os.path.exists("data"):
        for f in os.listdir("data"):
            if f.startswith("dl_"):
                try: os.remove(os.path.join("data", f))
                except: pass

def run_tests():
    cleanup()
    
    # 1. Known public YouTube video (Short simple video, e.g., YouTube's standard test video or a trailer)
    print("TEST 1: Known public YouTube video")
    # https://www.youtube.com/watch?v=jNQXAC9IVRw (Me at the zoo - first youtube video)
    url1 = "https://www.youtube.com/watch?v=jNQXAC9IVRw"
    success, path, err_cat, msg, raw = download_video(url1)
    if success:
        print("RESULT 1: PASS")
        print(f"Path: {path}")
    else:
        print(f"RESULT 1: FAIL (Category: {err_cat}, Msg: {msg})")
        
    cleanup()

    # 2. Second public YouTube video
    print("\nTEST 2: Second public YouTube video")
    # Big Buck Bunny
    url2 = "https://www.youtube.com/watch?v=aqz-KE-bpKQ"
    success, path, err_cat, msg, raw = download_video(url2)
    if success:
        print("RESULT 2: PASS")
        print(f"Path: {path}")
    else:
        print(f"RESULT 2: FAIL (Category: {err_cat}, Msg: {msg})")

    cleanup()

    # 3. Public accessible Instagram reel
    print("\nTEST 3: Public Instagram Reel")
    # A generic public reel URL (Using instagram's official account post for stability if possible, but any works. I'll use a random known one, or just catch gracefully if blocked by instagram)
    url3 = "https://www.instagram.com/reel/C8_c18XOF-M/" # just a random public reel format
    success, path, err_cat, msg, raw = download_video(url3)
    if success:
        print("RESULT 3: PASS")
    else:
        print(f"RESULT 3: FAIL or BLOCKED (Category: {err_cat}, Msg: {msg})")
        if err_cat in ["LOGIN_REQUIRED", "PLATFORM_BLOCKED"]:
            print("Note: Handled gracefully.")

    cleanup()

    # 4. Intentionally inaccessible/private URL
    print("\nTEST 4: Intentionally inaccessible URL")
    url4 = "https://www.youtube.com/watch?v=nonexistent123"
    success, path, err_cat, msg, raw = download_video(url4)
    if not success and err_cat == "VIDEO_UNAVAILABLE":
        print("RESULT 4: PASS (Correctly identified as unavailable)")
    else:
        print(f"RESULT 4: FAIL (Category: {err_cat}, Msg: {msg})")
        
    cleanup()

if __name__ == "__main__":
    run_tests()
