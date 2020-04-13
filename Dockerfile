FROM python:3

RUN useradd -ms /bin/bash app

WORKDIR /home/app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

USER app
COPY expect_header.txt expect_footer.txt empty_footer.txt ./
COPY *.py ./

CMD python ./download-records-s3.py
