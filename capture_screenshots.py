import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        # 1. Login
        print("Capturing Login...")
        await page.goto("http://localhost:3000/login")
        await page.screenshot(path="screenshot_core_login.png")

        # Login
        try:
            await page.fill("input[name='username']", "admin")
            await page.fill("input[name='password']", "medicadmin")
            await page.click("button[type='submit']")
            await page.wait_for_timeout(5000)
        except Exception as e:
            content = await page.content()
            with open("error.html", "w", encoding="utf-8") as f:
                f.write(content)
            print("Failed to login. Saved error.html")
            raise e

        # 2. Core Dashboard
        print("Capturing Dashboard...")
        await page.goto("http://localhost:3000/")
        await page.screenshot(path="screenshot_core_dashboard.png")

        # 3. Core Patients
        print("Capturing Patients List...")
        await page.goto("http://localhost:3000/patients")
        await page.wait_for_timeout(2000)
        await page.screenshot(path="screenshot_core_patients.png")

        # Open patient registration modal
        print("Capturing Patient Registration Modal...")
        try:
            await page.click("button:has-text('Registrar Paciente')")
        except Exception as e:
            print("Failed to click Registrar Paciente, saving HTML...")
            content = await page.content()
            with open("error_patients.html", "w", encoding="utf-8") as f:
                f.write(content)
            raise e
        await page.wait_for_timeout(1000)
        await page.screenshot(path="screenshot_core_new_patient.png")
        await page.keyboard.press("Escape")
        await page.wait_for_timeout(1000)

        # Go to a patient detail
        print("Capturing Patient Detail...")
        links = await page.locator("td.px-6.py-4.whitespace-nowrap").all()
        if links:
            await links[0].click()
            await page.wait_for_timeout(2000)
            await page.screenshot(path="screenshot_core_patient_detail.png")

        # 4. Core Memberships
        print("Capturing Memberships List...")
        await page.goto("http://localhost:3000/memberships")
        await page.wait_for_timeout(2000)
        await page.screenshot(path="screenshot_core_memberships.png")

        # Open membership new plan modal
        print("Capturing New Plan Modal...")
        await page.click("button:has-text('Nuevo Plan')")
        await page.wait_for_timeout(1000)
        await page.screenshot(path="screenshot_core_new_plan.png")
        await page.keyboard.press("Escape")
        await page.wait_for_timeout(1000)

        # 5. Patient Portal
        print("Capturing Patient Portal...")
        await page.goto("http://localhost:5173/")
        await page.wait_for_timeout(2000)
        await page.screenshot(path="screenshot_patient_portal.png")

        await browser.close()
        print("Done capturing screenshots.")

asyncio.run(run())
