# crud_streamlit
sudo apt update

sudo apt-get update

sudo apt upgrade -y

sudo apt install git curl unzip tar make sudo vim wget -y

git clone https://github.com/FacuBoladeras/crud_streamlit.git

sudo apt install python3-pip

pip3 install -r requirements.txt

python3 -m streamlit run app.py

nohup python3 -m streamlit run app.py


# detener y hacer update

ps aux | grep "python3 -m streamlit run app.py"
kill -9 24122
git pull origin main