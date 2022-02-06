
FROM python:3.8
EXPOSE 3111
COPY techtrends /app
WORKDIR /app
RUN pip install -r requirements.txt
RUN python init_db.py
# cmd to run on container start
CMD [ "python", "app.py" ]