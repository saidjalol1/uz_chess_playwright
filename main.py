"""
Main entry point for Flutter app registration automation script.
"""

import sys
import argparse
import asyncio
from utils.validators import validate_email


async def main(email: str) -> None:
    """
    Main entry point for the automation script.
    
    Args:
        email: Email address to use for registration
    """ 
    from utils.automation_flow import execute_registration_flow, FlowConfig
    
    try:
        # Create FlowConfig with target URL and selectors
        config = FlowConfig(
            target_url="https://uzchesss.uz/en",
            signup_button_selector="a[href*='https://play.uzchesss.uz/'], button:has-text('Sign up')",
            email_input_selector="input[placeholder='name@email.uz'], input[type='email']",
            continue_button_selector="button:has-text('Continue'), input[type='submit']",
            timeouts={
                'signup_button': 60000,    # 30 seconds in milliseconds
                'email_input': 60000,      # 30 seconds in milliseconds
                'continue_button': 30000,  # 30 seconds in milliseconds
                'new_tab': 10              # 10 seconds
            }
        )
        
        # Call execute_registration_flow() with email and config
        result = await execute_registration_flow(email, config)
        
        # Handle RegistrationResult and set appropriate exit code
        if result.success:
            print(f"Success: {result.message}")
            sys.exit(0)
        else:
            print(f"Failed: {result.message}")
            if result.screenshot_path:
                print(f"Screenshot saved to: {result.screenshot_path}")
            sys.exit(1)
            
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Automate Flutter app registration process'
    )
    parser.add_argument(
        'email',
        nargs='?',
        help='Email address for registration'
    )
    parser.add_argument(
        '--email',
        dest='email_flag',
        help='Email address for registration (alternative syntax)'
    )
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_arguments()
    email = args.email or args.email_flag
    
    if not email:
        print('Error: Email address is required')
        print('Usage: python main.py <email> or python main.py --email <email>')
        sys.exit(1)
    
    # Validate email format
    validation_result = validate_email(email)
    if not validation_result['valid']:
        print(f"Error: {validation_result['error']}")
        sys.exit(1)
    
    try:
        asyncio.run(main(email))
    except KeyboardInterrupt:
        print('\nAutomation interrupted by user')
        sys.exit(130)
    except Exception as e:
        print(f'Error: {e}')
        sys.exit(1)
