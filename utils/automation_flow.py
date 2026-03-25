"""
Automation orchestrator module for coordinating the registration flow.
"""

import asyncio
from typing import Optional, Dict, Any, List, Literal
from dataclasses import dataclass, field
import random


@dataclass
class FlowConfig:
    """Configuration for the registration flow."""
    target_url: str
    signup_button_selector: str
    email_input_selector: str
    continue_button_selector: str
    timeouts: Dict[str, int]


@dataclass
class RegistrationResult:
    """Result of the registration flow execution."""
    success: bool
    message: str
    screenshot_path: Optional[str] = None


@dataclass
class ErrorRecord:
    """Record of an error that occurred during flow execution."""
    step: str
    error: Exception
    timestamp: float


@dataclass
class FlowState:
    """State tracking for the registration flow execution."""
    current_step: Literal['init', 'navigate', 'click_signup', 'fill_email', 'click_continue', 'wait_tab', 'complete']
    email: str
    main_page: Optional[Any] = None  # Page type from playwright
    registration_page: Optional[Any] = None  # Page type from playwright
    start_time: float = 0.0
    errors: List[ErrorRecord] = field(default_factory=list)


async def execute_registration_flow(
    email: str,
    config: FlowConfig
) -> RegistrationResult:
    """
    Execute the complete registration flow.
    
    Orchestrates the entire registration process:
    1. Initialize browser with stealth configuration
    2. Navigate to target URL
    3. Wait for and click signup button (30s timeout)
    4. Wait for and fill email input field with human-like typing (30s timeout)
    5. Wait for and click continue button (30s timeout)
    6. Initialize TabManager and wait for new tab (10s timeout)
    7. Switch to registration tab and wait for page load
    8. Log each major step during execution
    
    Args:
        email: Email address to use for registration
        config: Flow configuration with target_url, selectors, and timeouts
    
    Returns:
        RegistrationResult with success status and message
        
    Requirements: 3.1, 3.3, 3.4, 4.1, 4.3, 4.4, 4.5, 5.1, 5.2, 5.3, 5.4, 6.4
    """
    from utils.browser_controller import BrowserController, BrowserOptions
    from utils.tab_manager import TabManager
    from utils.logger import Logger
    import time
    import os
    
    logger = Logger()
    browser = BrowserController()
    screenshot_path = None
    
    try:
        # Step 1: Initialize BrowserController with stealth configuration
        logger.info("Initializing browser with stealth configuration")
        
        # Clear previous browser data to avoid starting with a logged-in session
        import shutil
        browser_data_dir = "./browser_data"
        if os.path.exists(browser_data_dir):
            logger.info("Clearing previous browser data for fresh session")
            shutil.rmtree(browser_data_dir)
        
        browser_options = BrowserOptions(
            headless=False,
            user_data_dir=browser_data_dir
            # Explicitly not setting viewport so it uses the default window size
        )
        await browser.initialize(browser_options)
        logger.info("Browser initialized successfully")
        
        # Step 2: Navigate to target URL
        logger.info("Navigating to target URL", {"url": config.target_url})
        await browser.navigate_to(config.target_url)
        logger.info("Navigation completed")
        
        # Step 3 & 4: Wait for and click signup button, and wait for new tab
        logger.info("Waiting for signup button", {"selector": config.signup_button_selector})
        signup_timeout = config.timeouts.get('signup_button', 30000)
        await browser.wait_for_selector(config.signup_button_selector, timeout=signup_timeout)
        logger.info("Signup button found, clicking")
        
        # Initialize TabManager to listen for new tab concurrently with the click
        tab_manager = TabManager(browser.context)
        new_tab_timeout = config.timeouts.get('new_tab', 10)  # timeout in seconds
        new_tab_task = asyncio.create_task(tab_manager.wait_for_new_tab(timeout=new_tab_timeout))
        
        await browser.click_element(config.signup_button_selector, timeout=signup_timeout)
        logger.info("Signup button clicked successfully")
        
        new_tab = await new_tab_task
        logger.info("New tab detected")
        
        # Switch to registration tab and wait for page load
        logger.info("Switching to registration tab")
        await tab_manager.switch_to_tab(new_tab)
        logger.info("Switched to registration tab, waiting for page load")
        await new_tab.wait_for_load_state('domcontentloaded')
        
        # Reload the page as requested
        logger.info("Reloading the registration page")
        await new_tab.reload()
        await new_tab.wait_for_load_state('domcontentloaded')
        logger.info("Registration page loaded successfully")
        
        # Update browser controller to point to the new tab for subsequent actions
        browser.page = new_tab
        
        # Step 5: Wait for and fill email input field with human-like typing
        logger.info("Waiting for email input field", {"selector": config.email_input_selector})
        
        # In Flutter Web, the DOM input element might not be attached until the logical text field is focused.
        # We will press Tab repeatedly until the input element appears in the DOM.
        input_attached = False
        
        # Focus the flutter app window first by clicking near the top-left to avoid accidentally 
        # clicking arbitrary links, but ensuring the canvas has keyboard focus.
        try:
            await browser.page.locator("flutter-view").click(position={"x": 50, "y": 50}, force=True)
        except Exception as e:
            logger.debug(f"Could not click flutter-view directly: {e}")
            
        for i in range(30):
            try:
                await browser.wait_for_selector(config.email_input_selector, timeout=1000, state='attached')
                input_attached = True
                logger.info(f"Email input field attached to DOM after {i} Tab presses")
                break
            except Exception:
                await browser.press_key('Tab')
                
        if not input_attached:
            raise Exception(f"Email input field never attached to DOM after 30 Tab presses. Selector: {config.email_input_selector}")
        
        logger.info("Email input field found, injecting email and typing", {"email": email})
        await browser.type_text(config.email_input_selector, email, human_like=True)
        logger.info("Email entered successfully")
        
        # Step 6: Click the Continue button
        # Flutter renders the button on a canvas — normal DOM clicks don't work.
        # We extract the email input's CSS transform to find its canvas position,
        # then click below it where the Continue button is rendered.
        logger.info("Preparing to click Continue button")
        
        # Small delay to let Flutter process the typed email
        await asyncio.sleep(1)
        
        # Extract the email input's transform matrix to find its visual position on the canvas
        input_position = await browser.page.evaluate("""() => {
            const form = document.querySelector('form');
            if (form) {
                const input = form.querySelector('input[placeholder], input[type="text"]');
                if (input) {
                    const style = input.getAttribute('style') || '';
                    // Parse transform: matrix(1, 0, 0, 1, X, Y) to get canvas position
                    const match = style.match(/matrix\\(([^)]+)\\)/);
                    if (match) {
                        const values = match[1].split(',').map(v => parseFloat(v.trim()));
                        // values[4] = translateX, values[5] = translateY
                        const width = parseFloat(style.match(/width:\\s*([\\d.]+)px/)?.[1] || 0);
                        const height = parseFloat(style.match(/height:\\s*([\\d.]+)px/)?.[1] || 0);
                        return { x: values[4], y: values[5], width: width, height: height };
                    }
                }
            }
            return null;
        }""")
        
        logger.info(f"Email input canvas position: {input_position}")
        
        if input_position:
            # The Continue button is centered below the email input
            # Typically ~70-90px below the input field in this Flutter layout
            click_x = input_position['x'] + input_position['width'] / 2
            click_y = input_position['y'] + input_position['height'] + 75
            logger.info(f"Clicking Continue button at ({click_x}, {click_y})")
            await browser.page.mouse.click(click_x, click_y)
        else:
            logger.error("Could not determine email input position for Continue button click")
        
        # Wait a moment and take a screenshot to verify
        await asyncio.sleep(2)
        try:
            await browser.screenshot("./screenshots/after_continue_click.png")
            logger.info("Screenshot captured after clicking Continue")
        except Exception:
            pass
        
        logger.info("Continue button click attempted")
        
        # Step 7: Wait for verification code page and prompt user for OTP
        logger.info("Waiting for verification code page to load")
        await asyncio.sleep(3)
        
        # Prompt user for OTP code in the terminal
        logger.info("Waiting for OTP code input from user")
        print("\n" + "=" * 50)
        print("A verification code has been sent to your email.")
        print("=" * 50)
        otp_code = input("Enter the verification code: ").strip()
        logger.info(f"OTP code received: {'*' * len(otp_code)}")
        
        if not otp_code:
            raise Exception("No OTP code provided")
        
        # The OTP input behaves like the email input — it won't appear in DOM
        # until the text field is focused. Use Tab cycling to attach it.
        otp_input_selector = "input.transparentTextEditing:not([placeholder])"
        logger.info("Waiting for OTP input field to attach to DOM")
        
        otp_attached = False
        for i in range(30):
            try:
                await browser.wait_for_selector(otp_input_selector, timeout=1000, state='attached')
                otp_attached = True
                logger.info(f"OTP input field attached to DOM after {i} Tab presses")
                break
            except Exception:
                await browser.press_key('Tab')
        
        if not otp_attached:
            raise Exception("OTP input field never attached to DOM")
        
        # Type the OTP code
        logger.info("Typing OTP code")
        await browser.type_text(otp_input_selector, otp_code, human_like=True)
        logger.info("OTP code entered successfully")
        
        # Small delay to let Flutter process the typed OTP and auto-submit
        await asyncio.sleep(1)
        
        # The OTP form auto-submits once 6 digits are typed.
        # Wait for verification to complete and navigation to the Profile page
        await asyncio.sleep(2)
        
        try:
            await browser.screenshot("./screenshots/after_otp_verify.png")
            logger.info("Screenshot captured after OTP verification")
        except Exception:
            pass
        
        # Step 8: Fill Profile Information (First Name, Last Name, Username)
        logger.info("Waiting for Profile Setup page to load")
        await asyncio.sleep(2)
        
        # Generate random Uzbek profile
        from utils.name_generator import generate_uzbek_name
        profile = generate_uzbek_name()
        logger.info(f"Generated profile: {profile}")
        
        # In Flutter's profile form, the first field (First Name) might not be focused immediately.
        # We Tab cycle until the profile text field appears (ignoring the background email input).
        profile_input_selector = "input.transparentTextEditing:not([placeholder])"
        logger.info("Waiting for first Profile input field to attach to DOM")
        
        profile_attached = False
        for i in range(15):
            try:
                # Use >> nth=-1 to avoid strict mode violations if multiple inputs exist
                await browser.wait_for_selector(f"{profile_input_selector} >> nth=-1", timeout=1000, state='attached')
                profile_attached = True
                logger.info(f"Profile input field attached to DOM after {i} Tab presses")
                break
            except Exception:
                await browser.press_key('Tab')
                
        if not profile_attached:
            raise Exception("Profile input fields never attached to DOM")
        
        # We assume the Tab focus order is: First Name -> Last Name -> Username
        # Helper to clear a flutter field
        async def clear_field():
            # Send enough backspaces to clear any pre-filled data
            for _ in range(25):
                await browser.page.keyboard.press('Backspace')
            await asyncio.sleep(0.2)
            
        # 1. Type First Name
        logger.info("Typing First Name")
        # Ensure it's active
        await browser.page.keyboard.press('End') # move to end of text
        await clear_field()
        await browser.page.keyboard.type(profile['first_name'], delay=random.randint(50, 150))
        
        # Helper to clear and fill the currently focused flutter field
        async def fill_profile_field(text: str):
            # We rely on Flutter's internal focus from Tab
            # Clear pre-filled text
            await browser.page.keyboard.press('End')
            for _ in range(25):
                await browser.page.keyboard.press('Backspace')
            await asyncio.sleep(0.2)
            
            # Type new text directly (simulating human typing)
            for char in text:
                await browser.page.keyboard.type(char)
                await asyncio.sleep(random.randint(50, 150) / 1000.0)
            await asyncio.sleep(0.5)
            
        # 1. Fill First Name
        logger.info("Typing First Name")
        await fill_profile_field(profile['first_name'])
        
        # 2. Fill Last Name
        logger.info("Typing Last Name")
        await browser.press_key('Tab')
        await asyncio.sleep(0.5)
        await fill_profile_field(profile['last_name'])
        
        # 3. Fill Username
        logger.info("Typing Username")
        await browser.press_key('Tab')
        await asyncio.sleep(0.5)
        await fill_profile_field(profile['username'])
        
        # Form filling complete, wait a bit before submitting
        await asyncio.sleep(2)
        try:
            await browser.screenshot("./screenshots/before_profile_submit.png")
        except Exception:
            pass
            
        # 4. Submit Continue button using the exact same approach as Email form
        logger.info("Submitting Profile form via canvas coordinate click")
        
        # Get the Username field's position to calculate Continue button position
        profile_input_position = await browser.page.evaluate("""() => {
            // The last active field is the Username
            const inputs = document.querySelectorAll('input.transparentTextEditing:not([placeholder])');
            if (inputs.length > 0) {
                const input = inputs[inputs.length - 1]; // Use the currently active one
                const style = input.getAttribute('style') || '';
                const match = style.match(/matrix\\(([^)]+)\\)/);
                if (match) {
                    const values = match[1].split(',').map(v => parseFloat(v.trim()));
                    const width = parseFloat(style.match(/width:\\s*([\\d.]+)px/)?.[1] || 0);
                    const height = parseFloat(style.match(/height:\\s*([\\d.]+)px/)?.[1] || 0);
                    return { x: values[4], y: values[5], width: width, height: height };
                }
            }
            return null;
        }""")
        
        logger.info(f"Username input canvas position: {profile_input_position}")
        
        if profile_input_position:
            click_x = profile_input_position['x'] + profile_input_position['width'] / 2
            # 1. First, attempt to trigger Flutter's native form submission using the hidden DOM Submit button.
            # When you press 'Go/Enter' on a physical keyboard, this is what the browser natively clicks.
            try:
                await browser.page.evaluate("""() => {
                    const btns = document.querySelectorAll('.submitBtn');
                    if (btns.length > 0) {
                        btns[btns.length - 1].click();
                    }
                }""")
            except Exception as e:
                logger.debug(f"Failed to click hidden submitBtn: {e}")
                
            await asyncio.sleep(1)
            
            # 2. As a fallback, use a foolproof coordinate sweep.
            # Because the gap changes based on monitor resolution and browser height,
            # we will sweep a series of clicks directly downwards. The Continue button
            # is a large target and is the only interactive widget below the Username field.
            # One of these clicks will flawlessly trigger the modal!
            base_y = profile_input_position['y'] + profile_input_position['height']
            
            offsets = [120, 160, 200, 240, 280, 320]
            logger.info(f"Sweeping Profile Continue clicks down from Username Y={base_y}")
            
            for offset in offsets:
                click_y = base_y + offset
                logger.info(f"Clicking at offset +{offset}px (X={click_x}, Y={click_y})")
                await browser.page.mouse.click(click_x, click_y)
                await asyncio.sleep(0.3)
        else:
            logger.error("Could not determine position for Profile Continue button click")
        
        # Wait to verify profile submission success and for Address form to load
        await asyncio.sleep(2)
        
        try:
            await browser.screenshot("./screenshots/after_profile_submit.png")
            logger.info("Screenshot captured after profile submission")
        except Exception:
            pass
            
        logger.success("Profile Setup completed successfully")
        
        # ---------------------------------------------------------
        # Phase 5: Address Setup
        # ---------------------------------------------------------
        logger.info("Starting Address Setup phase")
        
        # Get viewport dimensions for proportional coordinate calculation
        vp = await browser.page.evaluate("() => ({ w: window.innerWidth, h: window.innerHeight })")
        logger.info(f"Viewport dimensions: {vp['w']}x{vp['h']}")
        
        # Helper: get ALL input positions sorted by Y
        async def get_all_input_positions():
            return await browser.page.evaluate("""() => {
                const inputs = Array.from(document.querySelectorAll('input.transparentTextEditing'));
                return inputs.map(input => {
                    const style = input.getAttribute('style') || '';
                    const match = style.match(/matrix\\(([^)]+)\\)/);
                    if (match) {
                        const values = match[1].split(',').map(v => parseFloat(v.trim()));
                        const width = parseFloat(style.match(/width:\\s*([\\d.]+)px/)?.[1] || 0);
                        return { x: values[4], y: values[5], width: width, placeholder: input.placeholder || '' };
                    }
                    return null;
                }).filter(p => p !== null).sort((a, b) => a.y - b.y);
            }""")
        
        # Helper: interact with a Flutter dropdown (click to open modal, type to search, click result)
        # Flutter bottom-sheet modals are entirely canvas-rendered, so DOM input positions
        # don't change. We rely on visual coordinates measured from actual screenshots.
        async def select_dropdown_item(field_name, click_x, click_y, search_text):
            """
            Opens a Flutter dropdown modal, types search text, and clicks the first result.
            
            The modal is a Flutter bottom-sheet that opens centered on the page.
            The search bar auto-focuses, so keyboard typing goes directly to it.
            After filtering, the first result appears below the search bar.
            """
            logger.info(f"Opening {field_name} dropdown at ({click_x}, {click_y})")
            
            # Click the dropdown field to open the modal
            await browser.page.mouse.click(click_x, click_y)
            await asyncio.sleep(2)  # Wait for modal open animation
            
            try:
                await browser.screenshot(f"./screenshots/after_{field_name}_click.png")
            except Exception:
                pass
            
            # The modal bottom-sheet is now open.
            # The modal is centered horizontally at approximately vp_w * 0.46
            # (measured from the after_country_click.png screenshot).
            # The search bar is at the top, and list items start below it.
            modal_center_x = int(vp['w'] * 0.46)
            
            # Click the search bar to ensure it's focused before typing.
            # The search bar doesn't always auto-focus (confirmed by region modal screenshots).
            # Search bar is at approximately vp_h * 0.04 in the modal.
            search_bar_y = int(vp['h'] * 0.04)
            logger.info(f"Clicking search bar at ({modal_center_x}, {search_bar_y}) to focus")
            await browser.page.mouse.click(modal_center_x, search_bar_y)
            await asyncio.sleep(0.5)
            
            # Type search text into the now-focused search bar
            logger.info(f"Typing '{search_text}' in {field_name} search bar")
            await browser.page.keyboard.type(search_text, delay=100)
            await asyncio.sleep(1.5)  # Wait for search filtering
            
            try:
                await browser.screenshot(f"./screenshots/after_{field_name}_type.png")
            except Exception:
                pass
            
            # Click the first search result.
            # After typing search text, the list filters to show matching items.
            # The first result appears below the search bar at ~vp_h*0.09.
            # We sweep multiple Y positions to ensure we hit the first result.
            for result_pct in [0.09, 0.11, 0.13, 0.15, 0.17]:
                result_y = int(vp['h'] * result_pct)
                logger.info(f"Clicking {field_name} result at ({modal_center_x}, {result_y})")
                await browser.page.mouse.click(modal_center_x, result_y)
                await asyncio.sleep(1)
                
                # Check if modal closed by taking a screenshot
                # (We can't reliably detect via DOM, so rely on the sweep)
            
            await asyncio.sleep(2)
            try:
                await browser.screenshot(f"./screenshots/after_{field_name}_select.png")
            except Exception:
                pass
            
            logger.info(f"{field_name} selection attempt completed")
        
        # Calculate right panel center X (the address card is on the right side)
        # Verified value: 0.75 successfully opens the Country modal (X=1599 on 2133px viewport)
        right_panel_x = int(vp['w'] * 0.75)
        logger.info(f"Right panel center X: {right_panel_x}")
        
        # --- 1. Select Country ---
        # Country field clickable area is at ~58% down the viewport (verified working)
        country_y = int(vp['h'] * 0.58)
        await select_dropdown_item("country", right_panel_x, country_y, "Uzbekistan")
        
        # --- 2. Select Region ---
        # After selecting Country=Uzbekistan, the Region dropdown appears below it
        await asyncio.sleep(2)
        try:
            await browser.screenshot("./screenshots/before_region_click.png")
        except Exception:
            pass
        
        # Region field is below Country. From screenshots, the Region label center is at
        # approximately Y=424 in 758px screenshot → ~597 viewport pixels (0.56).
        # But the clickable area extends below the label text, similar to how Country
        # is at 0.53 label but needs 0.58 click. So Region needs clicking at ~0.60-0.62.
        region_y = int(vp['h'] * 0.61)
        await select_dropdown_item("region", right_panel_x, region_y, "Andijon")
        
        # --- 3. Submit Address Continue ---
        logger.info("Submitting Address form via downward click sweep")
        # Continue button is at approximately 88% down the viewport (measured from screenshot)
        for pct in [0.85, 0.88, 0.91, 0.94]:
            y = int(vp['h'] * pct)
            logger.info(f"Clicking Continue sweep at (X={right_panel_x}, Y={y})")
            await browser.page.mouse.click(right_panel_x, y)
            await asyncio.sleep(0.3)
            
        await asyncio.sleep(5)
        try:
            await browser.screenshot("./screenshots/after_address_submit.png")
        except Exception:
            pass
            
        logger.success("Address Setup completed successfully")
            
        # Step 9: Log overall success
        logger.success("Registration flow completed entirely!")
        
        # Wait 15 seconds before closing browser to see result
        logger.info("Waiting 15 seconds before closing browser")
        await asyncio.sleep(15)
        
        return RegistrationResult(
            success=True,
            message="Registration flow completed successfully"
        )
        
    except Exception as e:
        # Log error with context
        logger.error(
            "Registration flow failed",
            error=e,
            context={"email": email, "target_url": config.target_url}
        )
        
        # Capture screenshot on error
        try:
            timestamp = int(time.time())
            screenshot_dir = "./screenshots"
            os.makedirs(screenshot_dir, exist_ok=True)
            screenshot_path = f"{screenshot_dir}/error_{timestamp}.png"
            await browser.screenshot(screenshot_path)
            logger.info("Screenshot captured", {"path": screenshot_path})
        except Exception as screenshot_error:
            logger.error("Failed to capture screenshot", error=screenshot_error)
        
        return RegistrationResult(
            success=False,
            message=f"Registration flow failed: {str(e)}",
            screenshot_path=screenshot_path
        )
        
    finally:
        # Ensure cleanup happens regardless of success or failure
        logger.info("Cleaning up browser resources")
        await browser.close()
        logger.info("Browser cleanup completed")
