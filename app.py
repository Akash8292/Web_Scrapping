from flask import Flask, request, render_template_string
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import os

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form.get('url')
        if url:
            return extract_reviews(url)
    return render_template_string('''
        <form method="POST">
            Amazon Product URL: <input type="text" name="url">
            <input type="submit" value="Get Reviews">
        </form>
    ''')

def extract_reviews(url):
    # Set up Selenium WebDriver with headless option
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--disable-gpu")  # Disable GPU acceleration (may not be necessary)
    chrome_options.add_argument("--no-sandbox")  # Bypass OS security model (useful in some environments)

    # Manually specify the path to the Chrome binary (update if necessary)
    chrome_options.binary_location = "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"

    # Automatically manage ChromeDriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    driver.get(url)
    driver.set_window_size(1552, 832)

    reviews = []

    try:
        # Wait for the reviews section to load and click "See more reviews"
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="reviews-medley-footer"]/div[2]/a'))
        ).click()

        while True:
            time.sleep(5)  # Wait for the reviews to load
            review_elements = driver.find_elements(By.CSS_SELECTOR, ".review")
            for review_element in review_elements:
                try:
                    username = review_element.find_element(By.CSS_SELECTOR, ".a-profile-name").text
                    review_date = review_element.find_element(By.CSS_SELECTOR, ".review-date").text
                    review_text = review_element.find_element(By.CSS_SELECTOR, ".review-text-content span").text

                    # Format the review
                    formatted_review = f"""
                    <div>
                        <strong>Reviewer:</strong> {username}<br>
                        <strong>Date:</strong> {review_date}<br>
                        <strong>Review:</strong><br>{review_text}<br><br>
                    </div>
                    <hr>
                    """
                    reviews.append(formatted_review)
                except Exception as e:
                    print(f"Error extracting review: {e}")
            
            # Check for the next button and click if it exists
            try:
                next_button = driver.find_element(By.CSS_SELECTOR, ".a-last a")
                if 'a-disabled' in next_button.get_attribute('class'):
                    break
                next_button.click()
            except Exception as e:
                print(f"No more pages of reviews: {e}")
                break

    finally:
        driver.quit()

    if reviews:
        # Return formatted reviews as HTML
        return f"<h2>Reviews:</h2>{''.join(reviews)}"
    else:
        return "No reviews found"

if __name__ == '__main__':
    app.run(debug=True)