FROM python:3.10

ADD mainGUI2.py api.py Canvas.py ConfigEditor.py ConfigReader.py
# RUN apt-get update
# RUN apt-get install ffmpeg libsm6 libxext6  -y
RUN pip install numpy pandas colorama PyQt5 xlsxwriter openpyxl mysql-connector-python

CMD ["python", "./mainGUI2.py"]