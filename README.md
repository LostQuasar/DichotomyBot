# Dichotomy Bot

## Requirements

- [Shocklink](https://shocklink.net/) account
- [OpenShock](https://openshock.org/) Shocker and Controller
- [Intiface](https://intiface.com/) with a connected device

## How to use

1. Create a .env in the root directory with these values

    ```env
    TOKEN="REPLACE THIS WITH YOUR DISCORD BOT TOKEN"
    CHANNEL_ID="THE CHANNEL ID OF WHICH TO LIMIT THE BOT TO"
    SUB_ID="THE USER WHICH IS GETTING SHOCKED"
    SHOCK_KEY="THE SHOCKLINK API KEY FOR THE BOT TO EXECUTE SHOCK TO"
    SHOCK_ID="THE ID OF THE SHOCKER TO SHOCK"
    ```

2. Start Intiface and connect a device
3. Ensure the Openshock controller is connected and online
4. Start the script and check for any errors
5. Listen for the beep, the shocker should beep if it is succesfully connected
