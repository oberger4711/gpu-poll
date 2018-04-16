# Summary
A hacky script that checks if NVIDIA GPUs are available.
If so, a mail can be sent automatically using a configured Google Mail account.
Additionally it is possible to execute an arbitary command as simple as:
```
python3 gpu_poll.py && python3 train.py
```
This exploits the fact that the polling script stops as soon as a free GPU is detected.

## Setup
In order to use the mail service, you have to generate an authentication key for your Google Mail account.
This allows the script to send (and only send i. e. not read) mails using your account.

1. Goto [your Google Developer Console](https://console.developers.google.com/start/api?id=gmail) and automatically turn on the API. Click Continue, then Go to credentials.
2. On the Add credentials to your project page, click the Cancel button.
3. At the top of the page, select the OAuth consent screen tab. Select an Email address, enter a Product name if not already set, and click the Save button.
4. Select the Credentials tab, click the Create credentials button and select OAuth client ID.
5. Select the application type Other, enter the name `poll_gpu`, and click the Create button.
6. Click OK to dismiss the resulting dialog.
7. Click the 'Download JSON' button to the right of the client ID.
8. Move this file to your working directory and rename it `client_secret.json`.

Install the dependencies:
```
pip3 install --user -r requirements.txt
```

## Execution
Read the CLI documentation:
```
python3 gpu_poll.py --help
```
