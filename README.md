
# **D**jango **R**epository for **ME**vo**L**ib **W**eb-based **G**raphical **U**ser **I**nterface

First of all, MEvoLib is a library of freely available Python tools for molecular evolution.
This project has been developed based on the use of that library, keeping in mind to provide users:
    - An easier and more visual way to interact with MEvoLib.
    - A more controlled process, not only because of custom stages that will be run within the workflow (Fetch, Cluster, Align and Inference,
    for now), but also by providing all the available parameters for each stage in a single sight, listing the possibilities for each one.
    - A simplier way to get the results, as they will be stored in a ZIP that will be downloaded in the local machine after each requested
    process has finished. Even if it fails, a filtered log message will be displayed, so that the user has a clue of what went wrong. 

# **L**icense **T**erms

This Django package is open source software made available under the Apache 2.0 License terms. Please see the LICENSE file for further details.

# **I**nstallation **P**rocess

- The first step is to clone this library. You can do it by typing this line in your console:
```bash
git clone https://github.com/nachorequeno/mevolib-ui.git
```

- After that, you have to enter to the folder:
```bash
cd mevolib-ui
```

- Then, you have to install all of the dependencies:
```bash
pip install -e.
```

- When you are done with this, the next step make sure you have installed python-dotenv to store the secret key provided by Django.
If you have not it, you can type:
```bash
pip install python-dotenv
```

- Before going into the next step, you have to go to the MEvoLibGUI folder:
```bash
cd MEvoLibGUI
```

- The next step is to generate the secret key. You can do it by running:
```bash
python manage.py shell -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

- Then, copy the value and create a file named ".env", like this:
```bash
touch .env
```

- Go to this folder, and paste this:
```bash
SECRET_KEY = (your secret key value)
```

- After that, clone the MEvoLib library in the MEvoLibGUI folder you were:
```bash
git clone https://github.com/JAlvarezJarreta/MEvoLib.git
```

- Next, move to /nextflowFiles:
```bash
cd nextflowFiles/
```

- Clone mevolib-workflow repository too:
```bash
git clone https://github.com/JAlvarezJarreta/mevolib-workflow.git
```

- Move to both, MEvoLib and mevolib-workflow folders and install the dependencies:
```bash
pip install -e.
```

- You are ready to use the interface!!

# **E**xecution **P**rocess

In order to launch the web-based interface for MEvoLIB, three tasks have to run together: Django server execution,
Redis server (to communicate Django and Celery) and Celery (to run the tasks in a queue, in an asynchronously way).
To do that, you have to go to mevolib-ui/MEvolibGUI folder, and from there, run this command:

```bash
 python manage.py runserver & redis-server & python -m celery -A MEvoLibGUI worker -l info 
```

When you do this, both three demons will be launched. If you do CTRL + S in views.py of Django, a line like this 
should appear in your terminal:

```bash
 Starting development server at http://127.0.0.1:8000/
```
If you do CTRL + left click on it, the GUI will be opened in a browser (as, for now, works locally, via localhost).

# **P**ossible **E**rrors

Redis-server command might fail the first time you execute it in a server, throwing an error like this:
```bash
  Could not create server TCP listening socket *:6379: bind: Address already in use
```
This is a really common bug this tool has. To fix it, you should run this command:

```bash
  sudo service redis-server stop
```
This will stop redis service, just in case it was running in the background. 
It should be enough, but if the error persists, then you can type this in your console:
```bash
  ps -ef | grep redis
```
This will give you a list of processes that are using redis, alongside with their matching PID.
You have to copy the identifier of the process on top of both (a pair of them normally appear), and run:
```bash
  kill -9 (your PID value)
```
That must do it.

After that, the only thing that remains is interacting with the interface.
You can open the full workflow form by clicking the button named after this, and then select the stages
you want to run by clicking on the checkboxes, and filling mandatory fields.
Do not worry if you do not know how to do it, when you press "Send", the GUI will tell you if there is
any error, empty/invalid field or whatever goes bad.
The last step is just to wait until your process has finished, and the results of each stage, alongside
with a brief report of CPU and memory usage (if all goes fine) or a log indicating the cause of the failure
(if there is any problem).

So, enjoy it!!