import re
from playwright.sync_api import Page, expect

def test_streamlit_interface(page: Page):
    page.goto("http://localhost:8501")
    expect(page).to_have_title(re.compile("BimBam Buy", re.IGNORECASE))
