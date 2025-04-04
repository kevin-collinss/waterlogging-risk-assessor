import requests
import json
import time

# Replace with your actual endpoint
url = "http://localhost:5000/get_data"

# Sample test payload (adjust to match your model’s input format)
test_payload = {
    "easting": 315000,
    "northing": 235000
}

# Store results
timings = []

for i in range(50):  # Run 50 tests
    start = time.time()
    response = requests.post(url, json=test_payload)
    end = time.time()
    
    elapsed = round(end - start, 3)
    timings.append(elapsed)
    
    print(f"Test {i+1}: {elapsed} seconds - Status {response.status_code}")

# Summarise results
import numpy as np

print("\n--- Summary ---")
print(f"Mean response time: {np.mean(timings):.3f} s")
print(f"Median response time: {np.median(timings):.3f} s")
print(f"Max response time: {np.max(timings):.3f} s")
print(f"Min response time: {np.min(timings):.3f} s")
print(f"% of responses < 4 seconds: {100 * sum(t < 4 for t in timings) / len(timings):.1f}%")
