**GoogleGmailSkill**
===================



Installation
-------------------
Is necesary to make this procedure

    sudo pip install google-api-python-client apiclient oauth2client httplib2


Now go to Onyx skills folder

    cd  $HOME/skills

    git clone  https://github.com/Onyx-Skills/gmail_skill.git


Authorize Google GMail Skill in distro with local web browser, wait web browse open and select "Allow"

    From your command line go to onyx skills folder

    cd  $HOME/skills

    python gmail_skill


Authorize Google GMail Skill in distro without local web browser

    From your command line go to onyx skills folder

    cd  $HOME/skills

    python gmail_skill --noauth_local_webserver

Open the generated link in computer with browser and wait the verification code and paste

     Enter verification code: 4/oxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx   

Restart Skills

    ./start.sh skills

----------


Features
--------------------

Currently this skill can do the following things to get information from your Gmail Inbox, un-read e-mails (with some variation):

- Check my gmail
- Get my last gmail
- Get my last gmail complete
- Get my last gmail detailed
- Get my last gmail with detail
- Get my last gmail with body   
- Get my last 5 gmail
- Get my last 6 gmail complete
- Get my last 7 gmail detailed
- Get my last 8 gmail with detail
- Get my last 9 gmail with body
- Get my gmail


> **Note:**

> - You can toggle key word with:
> - The words: complete, detailed, with detail, with body; offer the same results

--------
