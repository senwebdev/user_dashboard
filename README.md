# Haiku

```bash
pip3 install virtualenv
virtualenv -p /usr/bin/python3.5 venv
source venv/bin/activate
cd haiku
cp env_settings_example.py env_settings.py
```

Fill env_settings.py with yours credentials

```bash
cd ../
pip3 install -r requirements.txt
./manage.py migrate
echo "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@example.com', 'adminadmin')" | python manage.py shell
cd ~/haiku_user_dashboard
nohup ./manage.py runserver 0.0.0.0:8000 > webserver.log
# test from host
curl -L localhost:8000
netstat -nltp | grep 8000
```

### DEPLOYMENT

```bash
# Create instance
$ gcloud beta compute --project=haiku-214713 instances create valley-dashboard \
--zone=europe-west3-b \
--machine-type=n1-standard-1 \
--scopes=https://www.googleapis.com/auth/cloud-platform \
--tags=valley-dashboard,http-server,https-server \
--image=ubuntu-1604-xenial-v20180612 \
--image-project=ubuntu-os-cloud \
--boot-disk-size=50GB \
--boot-disk-type=pd-standard \
--boot-disk-device-name=valley-dashboard

# Add `valley-dashboard` firewall rule
$ gcloud compute --project=haiku-214713 firewall-rules create valley-dashboard --direction=INGRESS --priority=1000 --network=default --action=ALLOW --rules=tcp:8000 --source-ranges=0.0.0.0/0 --target-tags=valley-dashboard

# Reserve static IP (free of charge as long as the instance is not stopped)
$ gcloud compute --project=haiku-214713 addresses create valley-dashboard --addresses 35.234.109.110 --region europe-west3

# SSH into instance
$ gcloud compute --project haiku-214713 ssh --zone "europe-west3-b" haiku@valley-dashboard

# Add git repo
$ ssh-keygen -t rsa -b 4096 -C "<your github email>" # (on instance, save as /home/haiku/.ssh/github)
# github/repo --> settings --> deploy keys --> add keys (github.pub)
$ ssh -T git@github.com # check if successful authentication
$ echo \
"""host github.com
        HostName github.com
        IdentityFile ~/.ssh/github
        User git
""" > ~/.ssh/config && chmod 600 ~/.ssh/config

# Python
sudo apt-get update -yqq \
&& apt-get upgrade -yqq \
&& apt-get install -yqq --no-install-recommends python3-pip
```
