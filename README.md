
# Django Repository for MEvoLib Web-based Graphical User Interface

First of all, MEvoLib is a library of freely available Python tools for molecular evolution.

This project has been developed based on the use of that library, keeping in mind to provide users:
- An easier and more visual way to interact with MEvoLib.
- A more controlled process, not only because of custom stages that will be run within the workflow (Fetch, Cluster, Align and Inference, for now), but also by providing all the available parameters for each stage in a single sight, listing the possibilities for each one.
- A simpler way to get the results, as they will be stored in a ZIP that will be downloaded in the local machine after each requested process has finished. Even if it fails, a filtered log message will be displayed, so that the user has a clue of what went wrong.

## License terms

This Django package is open source software made available under the Apache 2.0 License terms. Please see the LICENSE file for further details.

## Installation

The first step is to clone this library. You can do it by typing this line in your console:
```bash
git clone https://github.com/nachorequeno/mevolib-ui.git
```

Next, you have to install all of the dependencies:
```bash
pip install mevolib-ui/MEvoLibGUI/.
```

After that, generate the secret key and save it in a file named `.env`. You can do it by running the following command:
```bash
python manage.py shell -c "from django.core.management.utils import get_random_secret_key; print(f'SECRET_KEY = {get_random_secret_key()}')" > .env
```

Now clone `mevolib-workflow` repository too:
```bash
git clone https://github.com/JAlvarezJarreta/mevolib-workflow.git mevolib-ui/MEvoLibGUI/nextflowFiles/mevolib-workflow
```

Finally, make sure you have redis-server installed. To do so, you can run
```bash
redis-server --version
```
And it should return something like
```
Redis server v=7.2.4 sha=00000000:0 malloc=libc bits=64 build=2d86b7859915655e
```
If that is not the case, please refer to the [Redis website](https://redis.io/docs/install/install-redis/) to install it.

You are now ready to use MEvoLib's interface!!

## Execution

In order to launch the web-based interface for MEvoLib, three tasks have to run together: a Django server, a Redis server (to communicate Django and Celery) and Celery (to run the tasks in a queue, in an asynchronous way). To do that, run the following command:
```bash
cd mevolib-ui/MEvolibGUI
python manage.py runserver & redis-server & python -m celery -A MEvoLibGUI worker -l info 
```

When you do this, both three daemons will be launched. If you do CTRL + S in views.py of Django, a line like this should appear in your terminal:
```bash
Starting development server at http://127.0.0.1:8000/
```

If you do CTRL + left click on it, the GUI will be opened in a browser (as, for now, works locally, via localhost).

### Troubleshooting

#### 1. Redis-server command fails

Redis-server command might fail the first time you execute it in a server, throwing an error like this:
```bash
Could not create server TCP listening socket *:6379: bind: Address already in use
```

This is a really common bug this tool has. To fix it, you should run this command:
```bash
sudo service redis-server stop
```

This will stop redis service, just in case it was running in the background.  It should be enough, but if the error persists, then you can type this in your console:
```bash
ps -ef | grep redis
```

This will give you a list of processes that are using redis, alongside with their matching PID. You have to copy the identifier of the process on top of both (a pair of them normally appear), and run:
```bash
kill -9 (your PID value)
```

That should fix it.

#### 2. OSError

Another error you may run into is something like `"OSError: [Errno 12] Cannot allocate memory..."`. This means your RAM memory is overused, and you might have many processes running in background without realizing it, so make sure to kill the processes by using the same redis technique, as loads of celery workers could be draining your resources.

After that, the only thing that remains is interacting with the interface. You can open the full workflow form by clicking the button named after this, and then select the stages you want to run by clicking on the checkboxes, and filling mandatory fields. Do not worry if you do not know how to do it, when you press "Send", the GUI will tell you if there is any error, empty/invalid field or whatever goes bad, guiding you every single time. The last step is just to wait until your process has finished, and the results of each stage, alongside with a brief report of CPU and memory usage (if all goes fine) or a log indicating the cause of the failure (if there is any problem) will be donwloaded.

So, enjoy it!!